import asyncio
import base64
import hashlib
import json
import secrets
import urllib.parse
import webbrowser
from datetime import datetime, timedelta, timezone
from pathlib import Path

from aiohttp import web
import httpx


SWIGGY_BASE_URL = "https://mcp.swiggy.com"
SWIGGY_AUTH_URL = f"{SWIGGY_BASE_URL}/auth"

REDIRECT_PORT = 8765
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}"
SCOPE = "mcp:tools"

TOKEN_FILE = Path(".swiggy_token.json")
CLIENT_FILE = Path(".swiggy_client.json")


async def register_client() -> str:
    """
    Register this application with Swiggy using
    Dynamic Client Registration.
    """

    payload = {
        "client_name": "Grocery Agent",
        "redirect_uris": [REDIRECT_URI],
        "grant_types": ["authorization_code"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{SWIGGY_AUTH_URL}/register",
            json=payload,
        )

    response.raise_for_status()

    data = response.json()

    return data["client_id"]


async def get_client_id() -> str:
    """
    Load the registered client ID.

    Register only if we don't have one yet.
    """

    if CLIENT_FILE.exists():
        data = json.loads(
            CLIENT_FILE.read_text()
        )

        return data["client_id"]

    print("Registering Grocery Agent with Swiggy...")

    client_id = await register_client()

    CLIENT_FILE.write_text(
        json.dumps(
            {
                "client_id": client_id,
            },
            indent=2,
        )
    )

    print("Swiggy client registered.")

    return client_id


def generate_pkce() -> tuple[str, str]:
    """
    Generate PKCE verifier and S256 challenge.
    """

    code_verifier = secrets.token_urlsafe(32)

    digest = hashlib.sha256(
        code_verifier.encode("utf-8")
    ).digest()

    code_challenge = (
        base64.urlsafe_b64encode(digest)
        .decode("utf-8")
        .rstrip("=")
    )

    return code_verifier, code_challenge


def build_authorization_url(
    client_id: str,
    code_challenge: str,
    state: str,
) -> str:
    """
    Build the Swiggy OAuth authorization URL.
    """

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "state": state,
        "scope": SCOPE,
    }

    return (
        f"{SWIGGY_AUTH_URL}/authorize?"
        f"{urllib.parse.urlencode(params)}"
    )


async def exchange_code_for_token(
    client_id: str,
    code: str,
    code_verifier: str,
) -> dict:
    """
    Exchange the OAuth authorization code for an access token.
    """

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "code_verifier": code_verifier,
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{SWIGGY_AUTH_URL}/token",
            json=payload,
        )

    response.raise_for_status()

    return response.json()


async def wait_for_callback(
    expected_state: str,
) -> str:
    """
    Start a temporary localhost server and wait for
    Swiggy's OAuth callback.
    """

    callback_future = asyncio.get_running_loop().create_future()

    async def callback(request: web.Request):
        returned_state = request.query.get("state")

        if returned_state != expected_state:
            if not callback_future.done():
                callback_future.set_exception(
                    RuntimeError(
                        "OAuth state mismatch."
                    )
                )

            return web.Response(
                text="Authentication failed: state mismatch.",
                status=400,
            )

        error = request.query.get("error")

        if error:
            if not callback_future.done():
                callback_future.set_exception(
                    RuntimeError(
                        f"Swiggy authorization failed: {error}"
                    )
                )

            return web.Response(
                text="Swiggy authentication failed.",
                status=400,
            )

        code = request.query.get("code")

        if not code:
            if not callback_future.done():
                callback_future.set_exception(
                    RuntimeError(
                        "No authorization code received."
                    )
                )

            return web.Response(
                text="Authentication failed: no code received.",
                status=400,
            )

        if not callback_future.done():
            callback_future.set_result(code)

        return web.Response(
            text=(
                "Authentication successful. "
                "You can close this browser tab."
            )
        )

    app = web.Application()

    app.router.add_get(
        "/",
        callback,
    )

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        "localhost",
        REDIRECT_PORT,
    )

    await site.start()

    try:
        return await callback_future

    finally:
        await runner.cleanup()


def save_token(token_data: dict) -> None:
    """
    Save the token response locally.
    """

    token_data = dict(token_data)

    expires_in = token_data.get("expires_in")

    if expires_in:
        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(seconds=expires_in)
        ).isoformat()

        token_data["expires_at"] = expires_at

    TOKEN_FILE.write_text(
        json.dumps(
            token_data,
            indent=2,
        )
    )


def load_valid_token() -> str | None:
    """
    Return a cached access token if it is still valid.
    """

    if not TOKEN_FILE.exists():
        return None

    try:
        data = json.loads(
            TOKEN_FILE.read_text()
        )

        access_token = data.get(
            "access_token"
        )

        expires_at = data.get(
            "expires_at"
        )

        if not access_token or not expires_at:
            return None

        expiry = datetime.fromisoformat(
            expires_at
        )

        # Give ourselves a small safety buffer.
        if datetime.now(timezone.utc) >= (
            expiry - timedelta(seconds=60)
        ):
            return None

        return access_token

    except (
        json.JSONDecodeError,
        ValueError,
        OSError,
    ):
        return None


async def authenticate() -> str:
    """
    Perform the complete Swiggy OAuth flow.
    """

    client_id = await get_client_id()

    code_verifier, code_challenge = generate_pkce()

    state = secrets.token_urlsafe(32)

    authorization_url = build_authorization_url(
        client_id=client_id,
        code_challenge=code_challenge,
        state=state,
    )

    print(
        "\nOpening Swiggy authentication "
        "in your browser..."
    )

    webbrowser.open(
        authorization_url
    )

    print(
        "Complete the Swiggy login in your browser."
    )

    code = await wait_for_callback(
        expected_state=state,
    )

    print(
        "Authorization code received."
    )

    print(
        "Exchanging code for access token..."
    )

    token_data = await exchange_code_for_token(
        client_id=client_id,
        code=code,
        code_verifier=code_verifier,
    )

    save_token(token_data)

    print(
        "Swiggy authentication successful."
    )

    return token_data["access_token"]


async def get_access_token() -> str:
    """
    Return a cached Swiggy token or authenticate
    if no valid token exists.
    """

    cached_token = load_valid_token()

    if cached_token:
        return cached_token

    return await authenticate()