from config import settings
import httpx
from urllib.parse import quote

def get_login_url():
    """Returns the Auth0 authorization URL to start the OAuth2 flow."""
    callback_url = f"{settings.BASE_URL}/auth/callback"
    url = (
        f"https://{settings.AUTH0_DOMAIN}/authorize?"
        f"response_type=code&"
        f"client_id={settings.AUTH0_CLIENT_ID}&"
        f"redirect_uri={callback_url}&"
        f"scope=openid%20profile%20email"
    )
    print(f"[AUTH] Generated Redirect URL: {url}", flush=True)
    return url

async def exchange_code_for_token(code: str):
    """Exchanges the Auth0 authorization code for an access token."""
    callback_url = f"{settings.BASE_URL}/auth/callback"
    url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.AUTH0_CLIENT_ID,
        "client_secret": settings.AUTH0_CLIENT_SECRET,
        "code": code,
        "redirect_uri": callback_url,
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
    returnTo = quote(f"{settings.BASE_URL}/login")
    return f"https://{settings.AUTH0_DOMAIN}/v2/logout?client_id={settings.AUTH0_CLIENT_ID}&returnTo={returnTo}"



