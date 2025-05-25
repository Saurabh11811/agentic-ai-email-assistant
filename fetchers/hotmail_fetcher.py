import requests
from datetime import datetime, timedelta
from config_agentic import (
    TIMESTAMP_FILE_HOTMAIL, MAX_EMAILS, FETCH_LOOKBACK_DAYS,
    VERBOSE, FORCE_FETCH, HOTMAIL_MESSAGES_ENDPOINT
)
from utils.ms_auth import get_hotmail_access_token
from utils.timestamp_tracker import get_last_timestamp, update_timestamp
from utils.email_utils import construct_email_doc
from utils.display_utils import print_progress

def fetch_hotmail_emails(force=None):
    force_fetch = force if force is not None else FORCE_FETCH
    token = get_hotmail_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Determine timestamp filter
    last_ts = None if force_fetch else get_last_timestamp(TIMESTAMP_FILE_HOTMAIL)
    if not last_ts:
        last_ts = (datetime.utcnow() - timedelta(days=FETCH_LOOKBACK_DAYS)).isoformat() + "Z"
        if VERBOSE:
            if force_fetch:
                print_progress(f"⏩ Force fetch enabled. Using fallback of last {FETCH_LOOKBACK_DAYS} days: {last_ts}")
            else:
                print_progress(f"⚠️ No previous timestamp found. Using fallback: {last_ts}")
            print()
    else:
        if VERBOSE:
            print_progress(f"📅 Using last timestamp: {last_ts}")
            print()

    url = HOTMAIL_MESSAGES_ENDPOINT
    params = {
        "$orderby": "receivedDateTime desc",
        "$filter": f"receivedDateTime gt {last_ts}",
        "$top": str(MAX_EMAILS)
    }

    all_emails = []
    page_count = 0

    print_progress("📡 Starting Hotmail fetch...")
    print()

    while url:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Graph API error: {response.status_code} - {response.text}")

        batch = response.json().get("value", [])
        batch_count = len(batch)
        page_count += 1

        if VERBOSE:
            print_progress(f"📨 Page {page_count}: Fetched {batch_count} emails (Total so far: {len(all_emails) + batch_count})")
            print()

        for i, msg in enumerate(batch, 1):
            
            if len(all_emails) >= MAX_EMAILS:
                break  # ✅ Manual limit reached
            
            doc = construct_email_doc(msg, "hotmail")
            all_emails.append(doc)

            if VERBOSE:
                percent = round((i / batch_count) * 100)
                print(f"\r🔄 Downloaded {i}/{batch_count} emails ({percent}%)", end=" " * 20, flush=True)

        print()  # newline after batch loop
        url = response.json().get("@odata.nextLink", None)
        params = None  # only for first page

    if all_emails:
        update_timestamp(TIMESTAMP_FILE_HOTMAIL, all_emails[0].get("receivedDateTime"))
        if VERBOSE:
            print_progress(f"🕒 Updated timestamp to: {all_emails[0].get('receivedDateTime', 'unknown')}")
            print()

    print_progress(f"✅ Done. Total Hotmail emails fetched: {len(all_emails)}")
    print()  # Ensure clean line ending
    return all_emails
