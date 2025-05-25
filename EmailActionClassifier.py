from config_agentic import ACTION_MODEL_NAME, FORCE_ACTION_CLASSIFICATION, RETRY_FAILED_ACTION, ACTION_LABELS, MONGO_COLLECTION, VERBOSE
from utils.mongo_connection import get_mongo_collection
from utils.llm_runner import run_llm
from datetime import datetime
from utils.display_utils import print_progress

from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROMPT_TEMPLATE_PATH = SCRIPT_DIR / "prompts" / "prompt_action_template.txt"

collection = get_mongo_collection(MONGO_COLLECTION)

def load_prompt_template(path, variables: dict):
    with open(path, "r") as f:
        return f.read().format(**variables)

def classify_action(email):
    prompt = load_prompt_template(PROMPT_TEMPLATE_PATH, {
        "valid_labels": ", ".join(ACTION_LABELS),
        "category": email.get("category_classification", {}).get("label", ""),
        "subject": email.get("subject", ""),
        "sender": email.get("sender", ""),
        "body": email.get("body", "")
    })
    return run_llm(prompt, model=ACTION_MODEL_NAME)

def main():
    
    # Build classification query
    if FORCE_ACTION_CLASSIFICATION:
        query = {}
    elif RETRY_FAILED_ACTION:
        query = {
            "$or": [
                {"action_classification": {"$exists": False}},
                {"action_classification.status": "Failed"}
            ]
        }
    else:
        query = {"action_classification": {"$exists": False}}

    
    emails = list(collection.find(query))
    
    total_in_db = collection.count_documents({})
    total_query_matched = len(emails)
    excluded = total_in_db - total_query_matched

    if total_query_matched == 0:
        print_progress("📂 No new emails to classify (all previously processed or failed with retry off).")
        print(f"   📦 Total emails in DB: {total_in_db}")
        print(f"   ⛔ Skipped due to status: {excluded}\n")
        return
    else:
        print_progress(f"📂 {total_query_matched} emails eligible for category classification...")
        print(f"   📦 Total emails in DB: {total_in_db}")
        print(f"   ⛔ Skipped due to status: {excluded}\n")
    
    
    total = len(emails)
    processed = 0
    skipped = 0
    errors = 0

    print_progress(f"📂 Starting action classification on {total} emails...\n")

    for i, email in enumerate(emails, 1):

        result = classify_action(email)

        if not result or not result.get("label"):
            errors += 1
            collection.update_one(
                    {"_id": email["_id"]},
                    {"$set": {
                        "action_classification": {
                            "status": "Failed",
                            "error": "No valid label returned",
                            "model": ACTION_MODEL_NAME,
                            "classified_at": datetime.utcnow().isoformat()
                        }
                    }}
                )
            if VERBOSE:
                print(f"⚠️  Skipped email {email.get('id')} — no valid label.")
            continue

        processed += 1

        collection.update_one(
            {"_id": email["_id"]},
            {"$set": {
                "action_classification": {
                    "status": "Success",
                    "label": result.get("label"),
                    "confidence": result.get("confidence", 0),
                    "rationale": result.get("rationale", ""),
                    "model": ACTION_MODEL_NAME,
                    "classified_at": datetime.utcnow().isoformat()
                }
            }}
        )

        percent = round((i / total) * 100)
        print(f"\r✅ {i}/{total} processed ({percent}%) — {result['label']} | {email.get('subject', '')[:40]}", end=" " * 20, flush=True)

    print("\n\n✅ Classification Summary:")
    print(f"   🟢 Newly classified: {processed}")
    print(f"   ⏭️  Skipped: {skipped}")
    print(f"   ❌ Errors: {errors}")
