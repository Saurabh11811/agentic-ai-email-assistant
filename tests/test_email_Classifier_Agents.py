#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from EmailCategoryClassifier import main as classify_categories
from EmailActionClassifier import main as classify_actions

def run_agent(skip_category=False, skip_action=False):
    if not skip_category:
        print("🔍 Running category classification...")
        classify_categories()
    if not skip_action:
        print("🤖 Running action classification...")
        classify_actions()

if __name__ == "__main__":
    run_agent()
