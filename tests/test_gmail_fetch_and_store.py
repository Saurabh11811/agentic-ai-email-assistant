from fetchers.gmail_fetcher import fetch_gmail_emails
from utils.mongo_store import store_emails
from utils.display_utils import print_progress

def main():
    print_progress("📥 Fetching Gmail emails...")
    emails = fetch_gmail_emails()
    print_progress(f"✅ Fetched {len(emails)} Gmail emails")
    print()

    print_progress("🗃️ Storing Gmail emails to MongoDB...")
    store_emails(emails, collection_name="agentic_emails")
    print_progress(f"✅ Stored {len(emails)} emails to MongoDB")
    print()

if __name__ == "__main__":
    main()
