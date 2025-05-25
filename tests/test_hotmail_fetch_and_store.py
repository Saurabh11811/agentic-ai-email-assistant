#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 16:19:19 2025

@author: saurabh.agarwal
"""

from fetchers.hotmail_fetcher import fetch_hotmail_emails
from utils.mongo_store import store_emails

def main():
    emails = fetch_hotmail_emails()
    print(f"✅ Fetched {len(emails)} Hotmail emails.")
    store_emails(emails, collection_name="agentic_emails")

if __name__ == "__main__":
    main()
