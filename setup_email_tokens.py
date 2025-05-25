#!/usr/bin/env python3

import os
import sys
import json
from pathlib import Path

# ─── Load .env from project root ─────────────────────────────────────────
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

# ─── Add project root to sys.path to resolve utils/ and config_agentic ──
sys.path.insert(0, str(PROJECT_ROOT))

# ─── Import flags from config ────────────────────────────────────────────
try:
    from config_agentic import EMAIL_ENABLED_GMAIL, EMAIL_ENABLED_HOTMAIL
except ImportError as e:
    print("❌ Error: Could not import EMAIL_ENABLED_GMAIL or EMAIL_ENABLED_HOTMAIL from config_agentic.py")
    raise e

# ─── Gmail Authentication (uses utils.gmail_auth) ───────────────────────
def authenticate_gmail():
    print("🔐 Starting Gmail authentication...")
    from utils.gmail_auth import get_gmail_service
    get_gmail_service()  # handles OAuth flow and saves token
    print("✅ Gmail token saved.")

# ─── Hotmail Authentication (Device Code Flow) ──────────────────────────
def authenticate_hotmail():
    import msal

    client_id = os.getenv("HOTMAIL_CLIENT_ID")
    authority = os.getenv("HOTMAIL_AUTHORITY")
    scope = os.getenv("HOTMAIL_SCOPE")
    token_cache_path = os.getenv("TOKEN_CACHE_PATH")

    if not all([client_id, authority, scope, token_cache_path]):
        raise ValueError("❌ Missing one or more Hotmail config values in .env")

    cache = msal.SerializableTokenCache()
    app = msal.PublicClientApplication(
        client_id=client_id,
        authority=authority,
        token_cache=cache
    )

    flow = app.initiate_device_flow(scopes=[scope])
    if "user_code" not in flow:
        raise Exception("❌ Failed to create device flow")

    print(f"🔐 Visit: {flow['verification_uri']}")
    print(f"🔑 Enter code: {flow['user_code']}")
    result = app.acquire_token_by_device_flow(flow)

    if "access_token" in result:
        with open(token_cache_path, "w") as f:
            f.write(cache.serialize())
        print(f"✅ Hotmail token saved to {token_cache_path}")
    else:
        print("❌ Hotmail authentication failed.")
        print(result)

# ─── Entrypoint ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🔧 Running setup_email_tokens.py\n")

    if EMAIL_ENABLED_GMAIL:
        authenticate_gmail()
    else:
        print("⏭️ Skipping Gmail (disabled in config_agentic.py)")

    if EMAIL_ENABLED_HOTMAIL:
        authenticate_hotmail()
    else:
        print("⏭️ Skipping Hotmail (disabled in config_agentic.py)")

    print("\n✅ Token setup complete.")
