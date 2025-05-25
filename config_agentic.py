import os
from dotenv import load_dotenv
import json
from pathlib import Path

# ───── Load .env and set base path ─────
load_dotenv()
CONFIG_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CONFIG_DIR  # change if you keep this file deeper in future
LABEL_PATH = PROJECT_ROOT / "classifier_refactor" / "labels"

# ───── Gmail Settings ─────
GMAIL_CREDENTIALS_PATH = PROJECT_ROOT / os.getenv("GMAIL_CREDENTIALS_PATH", "gmail_credentials.json")
GMAIL_TOKEN_PATH = PROJECT_ROOT / os.getenv("GMAIL_TOKEN_PATH", "gmail_token.json")
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TIMESTAMP_FILE_GMAIL = PROJECT_ROOT / "last_fetch_timestamp_gmail.json"

# ───── Hotmail Settings ─────
HOTMAIL_CLIENT_ID = os.getenv("HOTMAIL_CLIENT_ID", "your-client-id")
HOTMAIL_AUTHORITY = os.getenv("HOTMAIL_AUTHORITY", "https://login.microsoftonline.com/consumers")
HOTMAIL_SCOPE = [os.getenv("HOTMAIL_SCOPE", "Mail.Read")]
TOKEN_CACHE_PATH = PROJECT_ROOT / os.getenv("TOKEN_CACHE_PATH", ".msal_token_cache.bin")
HOTMAIL_MESSAGES_ENDPOINT = "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages"
TIMESTAMP_FILE_HOTMAIL = PROJECT_ROOT / "last_fetch_timestamp_hotmail.json"

# ───── Common Fetch Settings ─────
FETCH_LOOKBACK_DAYS = 30
MAX_EMAILS = 10
FORCE_FETCH = False
FORCE_DB = False

# ───── Email Source Control ─────
EMAIL_ENABLED_HOTMAIL = True
EMAIL_ENABLED_GMAIL = True

# ───── MongoDB ─────
MONGO_URI = "mongodb://localhost:27017"
MONGO_DB = "AGENTIC_EMAIL_ANALYSIS"
MONGO_COLLECTION = "agentic_emails"

# ───── Model Settings ─────
CATEGORY_MODEL_NAME = os.getenv("CATEGORY_MODEL_NAME", "llama3")
ACTION_MODEL_NAME = os.getenv("ACTION_MODEL_NAME", "llama3")
OLLAMA_PATH = os.getenv("OLLAMA_PATH", "/usr/local/bin/ollama")

# ───── Classification Control ─────
FORCE_CATEGORY_CLASSIFICATION = False
FORCE_ACTION_CLASSIFICATION = False
RETRY_FAILED_CATEGORY = False
RETRY_FAILED_ACTION = False

# ───── Label Files ─────
with open(LABEL_PATH / "email_categories.json") as f:
    grouped = json.load(f)["categories_by_group"]
    CATEGORY_VALID_LABELS = [label for group in grouped.values() for label in group]

with open(LABEL_PATH / "email_actions.json") as f:
    grouped = json.load(f)["actions_by_group"]
    ACTION_LABELS = [label for group in grouped.values() for label in group]

# ───── Notification Settings ─────
NOTIFY_MODE = "flask"  # "summary", "webview", or "flask"
NOTIFICATION_LABELS = [
    "To-do", "Needs Reply", "Follow-up", "Schedule", "FYI"
]

# ───── Orchestrator Flags ─────
RUN_FETCH = True
RUN_CLASSIFY = True
RUN_NOTIFY = True

# ───── Verbose Logging ─────
VERBOSE = True

# Model download flags
DOWNLOAD_LLAMA = True
DOWNLOAD_MISTRAL = False
DOWNLOAD_DEEPSEEK = False

# Agent run interval in seconds (default 30 mins)
AGENT_RUN_INTERVAL_SECONDS = 1800

