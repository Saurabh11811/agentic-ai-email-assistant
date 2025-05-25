from config_agentic import MONGO_COLLECTION, VERBOSE, FORCE_DB
from utils.mongo_connection import get_mongo_collection

def store_emails(emails: list, force_db: bool = None, collection_name: str = None):
    force = force_db if force_db is not None else FORCE_DB
    target_collection = get_mongo_collection(collection_name or MONGO_COLLECTION)

    if force:
        target_collection.drop()
        if VERBOSE:
            print(f"🗑️ Dropped collection {target_collection.name}")

    if not emails:
        if VERBOSE:
            print("⚠️ No emails to insert")
        return

    inserted_count = 0
    skipped_count = 0
    for email in emails:
        if target_collection.find_one({"messageId": email.get("messageId")}):
            skipped_count += 1
            continue
        target_collection.insert_one(email)
        inserted_count += 1

    if VERBOSE:
        print(f"✅ Emails processed: {len(emails)}")
        print(f"   📥 Inserted: {inserted_count}")
        print(f"   🔁 Skipped (duplicates): {skipped_count}")
