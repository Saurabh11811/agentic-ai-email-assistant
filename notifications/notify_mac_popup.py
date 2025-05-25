#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
notifications/notify_mac_popup.py

Refactored Way 1 – Compact summary popup only. No subject/sender lines.
"""

from pync import Notifier

def format_mac_popup_summary(emails):
    summary = f"📬 {len(emails)} emails — "

    # Count by label
    label_count = {}
    for email in emails:
        label = email.get("action_classification", {}).get("label", "Unknown")
        label_count[label] = label_count.get(label, 0) + 1

    summary += ", ".join([f"{k}: {v}" for k, v in label_count.items()])
    return summary  # ✅ Return string only

def notify_mac_summary_popup(emails, link=None):
    if not emails:
        return

    title = "Email Summaries"
    subtitle = format_mac_popup_summary(emails)  # FYI: total + label split
    
    # Notifier.notify(
    #     message=subtitle,
    #     title=title,
    #     group="email-summary",
    #     sound="Pop",
    #     open=link if link else None  # ✅ only adds open if link is provided
    # )
    
    
    kwargs = {
        "message": subtitle,
        "title": title,
        "group": "email-summary",
        "sound": "Pop"
    }

    if link:
        kwargs["open"] = link  # ✅ Only if a link is provided

    Notifier.notify(**kwargs)
