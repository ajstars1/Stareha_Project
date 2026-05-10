"""
Claude Code OAuth provider — use your claude.ai Pro/Max subscription.

Flow: PKCE (S256) against claude.ai. No local callback server needed.
After authorizing, claude.ai redirects to console.anthropic.com which
shows the code; user pastes it into the terminal.

Copied from hermes-agent/agent/anthropic_adapter.py (MIT license).
"""
import base64
import hashlib
import json
import os
import secrets
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

_OAUTH_CLIENT_ID    = "9d1c250a-e61b-44d9-88ed-5944d1962f5e"
_OAUTH_TOKEN_URL    = "https://console.anthropic.com/v1/oauth/token"
_OAUTH_REDIRECT_URI = "https://console.anthropic.com/oauth/code/callback"
_OAUTH_SCOPES       = "org:create_api_key user:profile user:inference"
_OAUTH_AUTH_URL     = "https://claude.ai/oauth/authorize"
_TOKEN_REFRESH_SKEW = 120  # seconds before expiry to trigger refresh

_TOKEN_FILE = Path.home() / ".stareha" / "claude_code_oauth.json"


def _generate_pkce() -> tuple[str, str]:
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode()
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode()
    return verifier, challenge


def _load_tokens() -> dict:
    """Load tokens from file, falling back to config."""
    if _TOKEN_FILE.exists():
        try:
            return json.loads(_TOKEN_FILE.read_text())
        except Exception:
            pass
    try:
        from packages.core.config import load_config
        return load_config().provider_configs.get("claude_code_oauth", {})
    except Exception:
        return {}


def _save_tokens(access_token: str, refresh_token: str, expires_at: int) -> None:
    _TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "expires_at": expires_at,
    }
    _TOKEN_FILE.write_text(json.dumps(data, indent=2))
    try:
        from packages.core.config import save_config
        save_config({"provider_configs": {"claude_code_oauth": data}})
    except Exception:
        pass


def _exchange_code(code: str, verifier: str, state: str) -> Optional[dict]:
    """Exchange auth code for tokens. Returns dict with access_token etc."""
    payload = json.dumps({
        "grant_type": "authorization_code",
        "client_id": _OAUTH_CLIENT_ID,
        "code": code,
        "state": state,
        "redirect_uri": _OAUTH_REDIRECT_URI,
        "code_verifier": verifier,
    }).encode()
    req = urllib.request.Request(
        _OAUTH_TOKEN_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "stareha-cli/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def _refresh_token(refresh_token: str) -> Optional[dict]:
    """Refresh an expired access token."""
    payload = json.dumps({
        "grant_type": "refresh_token",
        "client_id": _OAUTH_CLIENT_ID,
        "refresh_token": refresh_token,
    }).encode()
    req = urllib.request.Request(
        _OAUTH_TOKEN_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "stareha-cli/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def run_oauth_flow() -> bool:
    """
    Run the interactive PKCE OAuth flow in the terminal.
    Opens claude.ai in the browser, prompts user to paste the code.
    Returns True if credentials were saved successfully.
    """
    import webbrowser

    verifier, challenge = _generate_pkce()
    params = {
        "code": "true",
        "client_id": _OAUTH_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": _OAUTH_REDIRECT_URI,
        "scope": _OAUTH_SCOPES,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": verifier,
    }
    auth_url = f"{_OAUTH_AUTH_URL}?{urllib.parse.urlencode(params)}"

    print()
    print("Connecting to your Claude Pro/Max subscription.")
    print()
    print("  Opening browser to: https://claude.ai/oauth/authorize")
    print("  After you authorize, you'll be shown a code. Paste it here.")
    print()

    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    print(f"  (If browser didn't open, visit: {auth_url})")
    print()

    try:
        raw = input("  Paste the authorization code: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        return False

    if not raw:
        print("No code entered.")
        return False

    parts = raw.split("#", 1)
    code = parts[0].strip()
    state = parts[1].strip() if len(parts) > 1 else verifier

    result = _exchange_code(code, verifier, state)
    if not result or not result.get("access_token"):
        print("Token exchange failed. Check your code and try again.")
        return False

    expires_at = int(time.time()) + int(result.get("expires_in", 3600))
    _save_tokens(result["access_token"], result.get("refresh_token", ""), expires_at)
    print()
    print("  Connected. Using claude.ai subscription for inference.")
    return True


class ClaudeCodeOAuthProvider:
    PROVIDER_ID = "claude_code_oauth"

    def _get_valid_token(self) -> Optional[str]:
        tokens = _load_tokens()
        access_token = tokens.get("access_token", "")
        if not access_token:
            return None

        expires_at = tokens.get("expires_at", 0)
        if expires_at and time.time() > (expires_at - _TOKEN_REFRESH_SKEW):
            refresh = tokens.get("refresh_token", "")
            if refresh:
                result = _refresh_token(refresh)
                if result and result.get("access_token"):
                    new_expires = int(time.time()) + int(result.get("expires_in", 3600))
                    _save_tokens(
                        result["access_token"],
                        result.get("refresh_token", refresh),
                        new_expires,
                    )
                    return result["access_token"]
            return None  # expired and refresh failed

        return access_token

    def get_configured_model(self) -> str:
        try:
            from packages.core.config import load_config
            return (
                load_config()
                .provider_configs.get("claude_code_oauth", {})
                .get("model", "claude-sonnet-4-6")
            )
        except Exception:
            return "claude-sonnet-4-6"

    def is_available(self) -> bool:
        return bool(self._get_valid_token())

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        system: Optional[str] = None,
        max_tokens: int = 1500,
    ) -> Optional[str]:
        token = self._get_valid_token()
        if not token:
            return None
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=token)
            kwargs: dict = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system:
                kwargs["system"] = system
            resp = client.messages.create(**kwargs)
            return resp.content[0].text.strip() or None
        except Exception:
            return None

    def chat(
        self,
        messages: list[dict],
        *,
        model: str,
        system: Optional[str] = None,
        max_tokens: int = 2000,
    ) -> Optional[str]:
        token = self._get_valid_token()
        if not token:
            return None
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=token)
            kwargs: dict = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": messages,
            }
            if system:
                kwargs["system"] = system
            resp = client.messages.create(**kwargs)
            return resp.content[0].text.strip() or None
        except Exception:
            return None
