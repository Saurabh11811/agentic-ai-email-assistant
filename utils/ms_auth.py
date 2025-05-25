import os
import msal
from pathlib import Path
from config_agentic import HOTMAIL_CLIENT_ID, HOTMAIL_SCOPE, HOTMAIL_AUTHORITY, VERBOSE

# Ensure scope is a list
if isinstance(HOTMAIL_SCOPE, str):
    HOTMAIL_SCOPE = [HOTMAIL_SCOPE]

# ───── Resolve token cache path relative to project ─────
SCRIPT_DIR = Path(__file__).resolve().parent
TOKEN_CACHE_PATH = SCRIPT_DIR.parent / ".msal_token_cache.bin"

def get_hotmail_access_token():
    cache = msal.SerializableTokenCache()
    if TOKEN_CACHE_PATH.exists():
        cache.deserialize(TOKEN_CACHE_PATH.read_text())

    if VERBOSE:
        print(f"🔐 HOTMAIL_CLIENT_ID: {HOTMAIL_CLIENT_ID}")
        print(f"🔐 HOTMAIL_SCOPE: {HOTMAIL_SCOPE}")
        print(f"🔐 TOKEN_CACHE_PATH: {TOKEN_CACHE_PATH}")
        print(f"🔐 HOTMAIL_AUTHORITY: {HOTMAIL_AUTHORITY}")

    app = msal.PublicClientApplication(
        client_id=HOTMAIL_CLIENT_ID,
        authority=HOTMAIL_AUTHORITY,
        token_cache=cache
    )

    accounts = app.get_accounts()
    if accounts:
        if VERBOSE:
            print(f"🔄 Using cached credentials for {accounts[0].get('username', 'unknown user')}")
        result = app.acquire_token_silent(HOTMAIL_SCOPE, account=accounts[0])
    else:
        if VERBOSE:
            print("🆕 No cached account found. Initiating device code flow.")
        flow = app.initiate_device_flow(scopes=HOTMAIL_SCOPE)
        if "user_code" not in flow:
            raise Exception("❌ Failed to initiate device flow")
        print(f"🔐 Please authenticate:\n{flow['message']}")
        result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        raise Exception(f"Token error: {result.get('error_description')}")

    # ✅ Always write back the updated cache
    TOKEN_CACHE_PATH.write_text(cache.serialize())

    if VERBOSE:
        print("✅ Access token acquired successfully")

    return result["access_token"]
