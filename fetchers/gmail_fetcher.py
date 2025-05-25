import base64
from datetime import datetime, timezone, timedelta
from config_agentic import (
    VERBOSE, MAX_EMAILS, FETCH_LOOKBACK_DAYS, TIMESTAMP_FILE_GMAIL, FORCE_FETCH
)
from utils.gmail_auth import get_gmail_service
from utils.email_utils import construct_email_doc
from utils.display_utils import print_progress
from utils.timestamp_tracker import get_last_timestamp, update_timestamp

def extract_gmail_body(msg):
    try:
        payload = msg.get("payload", {})
        parts = payload.get("parts", [])
        if parts:
            for part in parts:
                if part.get("mimeType") == "text/plain":
                    return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
        body_data = payload.get("body", {}).get("data")
        if body_data:
            return base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")
    except Exception:
        return ""
    return ""

def fetch_gmail_emails(force=None):
    force_fetch = force if force is not None else FORCE_FETCH
    service = get_gmail_service()

    # Get last fetch timestamp
    last_ts = None if force_fetch else get_last_timestamp(TIMESTAMP_FILE_GMAIL)
    if not last_ts:
        fallback_time = datetime.now(timezone.utc) - timedelta(days=FETCH_LOOKBACK_DAYS)
        last_ts = fallback_time.isoformat()
        if VERBOSE:
            print_progress(f"⏩ No Gmail timestamp found. Using fallback: {last_ts}")
            print()
    else:
        if VERBOSE:
            print_progress(f"📅 Using last Gmail fetch timestamp: {last_ts}")
            print()

    dt = datetime.fromisoformat(last_ts)
    timestamp = int(dt.timestamp())

    results = service.users().messages().list(
        userId='me',
        labelIds=["INBOX"],
        maxResults=MAX_EMAILS,
        q=f"in:inbox after:{timestamp}"
    ).execute()

    messages = results.get("messages", [])
    total = len(messages)
    print_progress(f"📬 Gmail metadata retrieved: {total} messages")
    print()

    all_emails = []
    latest_timestamp = last_ts

    for i, msg in enumerate(messages, 1):
        msg_detail = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()

        headers = {h["name"]: h["value"] for h in msg_detail.get("payload", {}).get("headers", [])}
        full_body = extract_gmail_body(msg_detail)

        msg_detail["sender"] = headers.get("From", "")
        msg_detail["subject"] = headers.get("Subject", "")
        msg_detail["internetMessageId"] = headers.get("Message-ID", msg_detail["id"])

        doc = construct_email_doc(msg_detail, "gmail", full_body)
        all_emails.append(doc)

        # Track latest timestamp (from internalDate)
        internal_ts = int(msg_detail.get("internalDate", "0")) / 1000
        received_dt = datetime.fromtimestamp(internal_ts, tz=timezone.utc).isoformat()
        if not latest_timestamp or received_dt > latest_timestamp:
            latest_timestamp = received_dt

        if VERBOSE:
            percent = round((i / total) * 100)
            print(f"\r🔄 Downloaded {i}/{total} emails ({percent}%)", end=" " * 20, flush=True)

    print_progress(f"✅ Done. Total Gmail emails fetched: {len(all_emails)}")
    print()

    # Save new timestamp
    if latest_timestamp:
        update_timestamp(TIMESTAMP_FILE_GMAIL, latest_timestamp)
        if VERBOSE:
            print_progress(f"🕒 Updated Gmail timestamp to: {latest_timestamp}")
            print()

    return all_emails
