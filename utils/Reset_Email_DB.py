#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from pymongo import MongoClient
from config_agentic import MONGO_URI, MONGO_DB, MONGO_COLLECTION

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

def show_classification_breakdown(field_name: str, label: str):
    total_emails = collection.count_documents({})
    attempted = collection.count_documents({f"{field_name}.status": {"$exists": True}})
    success = collection.count_documents({f"{field_name}.status": "Success"})
    failed = collection.count_documents({f"{field_name}.status": "Failed"})
    remaining = total_emails - attempted

    print(f"\n🔍 {label} Classification Overview:")
    print(f"   📬 Total Emails:        {total_emails}")
    print(f"   🧪 Attempted:            {attempted}")
    print(f"   ✅ Success:              {success}")
    print(f"   ❌ Failed:               {failed}")
    print(f"   🕳️  Remaining (Not Tried): {remaining}")



def delete_entire_collection():
    collection.drop()
    print(f"🧹 Deleted entire collection: {MONGO_COLLECTION}")

def delete_emails_by_account(account_name):
    result = collection.delete_many({"account": account_name})
    print(f"✂️ Deleted {result.deleted_count} emails from account: {account_name}")

def show_collection_stats():
    total = collection.count_documents({})
    hotmail = collection.count_documents({"account": "hotmail"})
    gmail = collection.count_documents({"account": "gmail"})
    empty_subjects = collection.count_documents({"subject": {"$in": [None, ""]}})
    empty_senders = collection.count_documents({"sender": {"$in": [None, ""]}})
    empty_bodies = collection.count_documents({"body": {"$in": [None, ""]}})

    classified_cat_count = collection.count_documents({"category_classification.label": {"$exists": True}})
    classified_act_count = collection.count_documents({"action_classification.label": {"$exists": True}})
    notified = collection.count_documents({"notification_status.shown": True})
    feedback_total = collection.count_documents({"user_feedback.userResponse": {"$exists": True}})


    print("\n📊 Email Collection Stats:")
    print(f"   Total emails:      {total}")
    print(f"   From Hotmail:      {hotmail}")
    print(f"   From Gmail:        {gmail}")
    print(f"   Empty subjects:    {empty_subjects}")
    print(f"   Empty senders:     {empty_senders}")
    print(f"   Empty bodies:      {empty_bodies}")
    
    
    print("\n🔍 Category Classification Stats:")
    print(f"   ✅ Classified: {classified_cat_count}")
    for row in collection.aggregate([
        {"$match": {"category_classification.label": {"$exists": True}}},
        {"$group": {"_id": "$category_classification.label", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]):
        print(f"   • {row['_id']}: {row['count']}")
 
    print("\n🔍 Action Classification Stats:")
    print(f"   ✅ Classified: {classified_act_count}")
    for row in collection.aggregate([
        {"$match": {"action_classification.label": {"$exists": True}}},
        {"$group": {"_id": "$action_classification.label", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]):
        print(f"   • {row['_id']}: {row['count']}")
    
    
    from collections import Counter
    def top_counts(field):
        pipeline = [
            {"$match": {f"{field}.label": {"$exists": True}}},
            {"$group": {"_id": f"${field}.label", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        return list(collection.aggregate(pipeline))
    
    
    print("\n📂 Top Categories:")
    for item in top_counts("category_classification"):
        print(f"   - {item['_id']}: {item['count']}")

    print("\n🧠 Top Actions:")
    for item in top_counts("action_classification"):
        print(f"   - {item['_id']}: {item['count']}")
    
    
    print("\n🔔 Notification Stats:")
    for row in collection.aggregate([
        {"$match": {"notification_status.shown": True}},
        {"$group": {"_id": "$notification_status.mode", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]):
        print(f"   • {row['_id'] or 'unknown'}: {row['count']}")
    print(f"   ✅ Total notified: {notified}")

    print("\n👍👎 Feedback Stats:")
    print(f"   ✅ Feedback submitted: {feedback_total}")
    for row in collection.aggregate([
        {"$match": {"user_feedback.userResponse": {"$exists": True}}},
        {"$group": {"_id": "$user_feedback.userResponse", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]):
        print(f"   • {row['_id']}: {row['count']}")
    
    
    
    print("\n📈 Average Confidence by Category Label (sorted by count):")
    for row in collection.aggregate([
        {"$match": {
            "category_classification.label": {"$exists": True},
            "category_classification.confidence": {"$exists": True}
        }},
        {"$group": {
            "_id": "$category_classification.label",
            "avg_conf": {"$avg": "$category_classification.confidence"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}  # ✅ changed from avg_conf
    ]):
        print(f"   • {row['_id']}: {round(row['avg_conf'], 2)}% (n={row['count']})")

    
    print("\n📈 Average Confidence by Action Label (sorted by count):")
    for row in collection.aggregate([
        {"$match": {
            "action_classification.label": {"$exists": True},
            "action_classification.confidence": {"$exists": True}
        }},
        {"$group": {
            "_id": "$action_classification.label",
            "avg_conf": {"$avg": "$action_classification.confidence"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}}  # ✅ changed from avg_conf
    ]):
        print(f"   • {row['_id']}: {round(row['avg_conf'], 2)}% (n={row['count']})")
        
    show_classification_breakdown("category_classification", "Category")
    show_classification_breakdown("action_classification", "Action")


    

def backup_collection():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{MONGO_COLLECTION}_backup_{timestamp}"
    pipeline = [{"$match": {}}, {"$out": backup_name}]
    db[MONGO_COLLECTION].aggregate(pipeline)
    print(f"🗂 Backup created as collection: {backup_name}")



def reset_category_classification():
    result = collection.update_many(
        {"category_classification": {"$exists": True}},
        {"$unset": {"category_classification": ""}}
    )
    print(f"♻️ Reset category_classification on {result.modified_count} emails")

def reset_action_classification():
    result = collection.update_many(
        {"action_classification": {"$exists": True}},
        {"$unset": {"action_classification": ""}}
    )
    print(f"♻️ Reset action_classification on {result.modified_count} emails")

def clear_notification_status():
    result = collection.update_many(
        {"notification_status": {"$exists": True}},
        {"$unset": {"notification_status": ""}}
    )
    print(f"🧹 Cleared notification status on {result.modified_count} emails.")

def clear_user_feedback():
    result = collection.update_many(
        {"user_feedback": {"$exists": True}},
        {"$unset": {"user_feedback": ""}}
    )
    print(f"🧽 Cleared user feedback on {result.modified_count} emails.")


# -------------------------------
# You can call the desired function(s) below
# -------------------------------
def main():
    show_collection_stats() 
    # delete_entire_collection()
    # delete_emails_by_account("hotmail")
    # delete_emails_by_account("gmail")
    # show_collection_stats()
    # backup_collection()
    # reset_category_classification()
    # reset_action_classification()
    # clear_notification_status()
    # clear_user_feedback()

if __name__ == "__main__":
    main()
