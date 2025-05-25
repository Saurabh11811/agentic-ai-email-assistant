from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from config_agentic import GMAIL_SCOPES, VERBOSE

# ─── Resolve absolute paths ─────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
GMAIL_CREDENTIALS_PATH = SCRIPT_DIR.parent / "gmail_credentials.json"
GMAIL_TOKEN_PATH = SCRIPT_DIR.parent / "gmail_token.json"

def get_gmail_service():
    creds = None

    if GMAIL_TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_PATH, GMAIL_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(GMAIL_CREDENTIALS_PATH), GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)

        with open(GMAIL_TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
        if VERBOSE:
            print("✅ Gmail token saved")

    from googleapiclient.discovery import build
    return build("gmail", "v1", credentials=creds)
