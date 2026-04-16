from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from config import settings
import genie_client
import auth0_client
import os
import requests
from itsdangerous import URLSafeSerializer

print(f"[INIT] Starting Genie AI with domain: {settings.AUTH0_DOMAIN}", flush=True)

app = FastAPI(title="Genie AI Upgraded")

# Security Configuration
serializer = URLSafeSerializer(settings.APP_SECRET_KEY)

# Define frontend path for reuse
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if not os.path.exists(frontend_path):
    # Fallback for local development if running from inside backend/
    parent_frontend = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
    if os.path.exists(parent_frontend):
        frontend_path = parent_frontend

# Enable CORS (Updated for local development and credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.BASE_URL, "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

# --- Auth Helper ---
def get_current_user(request: Request):
    token = request.cookies.get("genie_session")
    if not token:
        print("[AUTH] No session cookie found.", flush=True)
        return None
    try:
        user_data = serializer.loads(token)
        return user_data
    except Exception as e:
        print(f"[AUTH] Session decode failed: {e}", flush=True)
        return None

# --- Auth Routes ---
@app.get("/login")
async def login_page():
    print("[NAV] Serving login page.", flush=True)
    return FileResponse(os.path.join(frontend_path, "login.html"))

@app.get("/auth/start")
async def auth_start(teams: bool = False):
    login_url = auth0_client.get_login_url(is_teams=teams)
    print(f"[AUTH] Starting login flow (Teams={teams}). Redirecting to: {login_url}", flush=True)
    return RedirectResponse(url=login_url)

@app.get("/auth/callback")
async def auth_callback(code: str, response: Response, teams: bool = False):
    print(f"[AUTH] Callback received with code: {code[:10]}... (Teams={teams})", flush=True)
    try:
        token_data = await auth0_client.exchange_code_for_token(code, is_teams=teams)
        access_token = token_data.get("access_token")
        user_info = await auth0_client.get_user_info(access_token)
        
        user_session = {
            "name": user_info.get("name"),
            "email": user_info.get("email"),
            "picture": user_info.get("picture")
        }
        signed_session = serializer.dumps(user_session)
        
        print(f"[AUTH] Success! User identified: {user_session['name']}", flush=True)
        
        target_url = "/"
        if teams:
            target_url = "/auth/success"
            
        response = RedirectResponse(url=target_url)
        # Secure cookies for production (HTTPS)
        is_secure = settings.BASE_URL.startswith("https")
        
        response.set_cookie(
            key="genie_session", 
            value=signed_session, 
            httponly=True,
            samesite="lax",
            secure=is_secure
        )
        return response

    except Exception as e:
        print(f"[AUTH] Error in callback: {e}", flush=True)
        return RedirectResponse(url="/login?error=auth_failed")

@app.get("/auth/success")
async def auth_success():
    """Signals Teams that the authentication was successful."""
    return Response(content="""
        <html>
            <body>
                <script src="https://res.cdn.office.net/teams-js/2.19.0/js/MicrosoftTeams.min.js"></script>
                <script>
                    microsoftTeams.app.initialize().then(() => {
                        microsoftTeams.authentication.notifySuccess();
                    });
                </script>
                <h1>Authentication Successful</h1>
                <p>Closing window...</p>
            </body>
        </html>
    """, media_type="text/html")

@app.get("/auth/logout")
async def auth_logout(response: Response):
    print("[AUTH] Logging out user.", flush=True)
    response = RedirectResponse(url=auth0_client.get_logout_url())
    response.delete_cookie("genie_session")
    return response

@app.get("/api/me")
async def api_me(request: Request):
    user = get_current_user(request)
    if not user:
        return Response(status_code=401)
    return user

# --- Protected Chat API ---
@app.post("/api/chat")
async def chat(request: ChatRequest, req: Request):
    user = get_current_user(req)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    response_meta = genie_client.ask_genie(request.question)
    query_data = None
    statement_id = response_meta.get("statement_id")
    
    if statement_id:
        try:
            host = settings.DATABRICKS_HOST.rstrip("/")
            token = settings.DATABRICKS_TOKEN
            url = f"{host}/api/2.0/sql/statements/{statement_id}"
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                data_result = resp.json()
                manifest = data_result.get("manifest", {})
                columns = [c["name"] for c in manifest.get("schema", {}).get("columns", [])]
                result_block = data_result.get("result", {})
                rows = result_block.get("data_array", []) or result_block.get("data", [])
                
                if columns and rows:
                    query_data = {"columns": columns, "rows": rows}
        except Exception as e:
            print(f"DEBUG: Data Error {e}", flush=True)

    return {
        "answer": response_meta.get("answer"),
        "query": response_meta.get("query"),
        "data": query_data,
        "suggested_questions": response_meta.get("suggested_questions")
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

# Serving logic: Mount static files at root AFTER all explicit API/Auth routes
if os.path.exists(frontend_path):
    print(f"[INIT] Mounting frontend from: {frontend_path}", flush=True)
    # This will serve index.html at / by default
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
