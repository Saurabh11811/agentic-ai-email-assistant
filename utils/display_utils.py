#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

def print_progress(msg, width=120):
    import sys
    padded_msg = f"\r{msg:<{width}}"
    sys.stdout.write(padded_msg)
    sys.stdout.flush()


def print_header(title):
    print(f"\n{'=' * 30}\n🧠 {title}\n{'=' * 30}")
