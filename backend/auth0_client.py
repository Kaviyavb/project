from config import settings
import httpx

def get_login_url():
    """Returns the Auth0 authorization URL to start the OAuth2 flow."""
    url = (
        f"https://{settings.AUTH0_DOMAIN}/authorize?"
        f"response_type=code&"
        f"client_id={settings.AUTH0_CLIENT_ID}&"
        f"redirect_uri={settings.AUTH0_CALLBACK_URL}&"
        f"scope=openid%20profile%20email"
    )
    print(f"[AUTH] Generated Redirect URL: {url}", flush=True)
    return url


async def exchange_code_for_token(code: str):
    """Exchanges the Auth0 authorization code for an access token."""
    url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.AUTH0_CLIENT_ID,
        "client_secret": settings.AUTH0_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.AUTH0_CALLBACK_URL,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()

async def get_user_info(access_token: str):
    """Retrieves user profile details using the access token."""
    url = f"https://{settings.AUTH0_DOMAIN}/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()

def get_logout_url():
    """Returns the Auth0 logout URL to clear the Auth0 session."""
    return f"https://{settings.AUTH0_DOMAIN}/v2/logout?client_id={settings.AUTH0_CLIENT_ID}&returnTo={settings.AUTH0_CALLBACK_URL.replace('/auth/callback', '/login')}"

