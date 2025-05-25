#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 21:23:29 2025

@author: saurabh.agarwal
"""

import subprocess
import json
import re
from config_agentic import VERBOSE, OLLAMA_PATH


def normalize_llm_keys(result, expected_label_key="label", known_label_keys=["category", "action"]):
    if not result:
        return result

    # Normalize label key
    for alt in known_label_keys:
        if alt in result and expected_label_key not in result:
            result[expected_label_key] = result.pop(alt)

    # Normalize rationale key
    if "rationale" not in result and "description" in result:
        result["rationale"] = result.pop("description")

    # Optional: Normalize confidence (e.g., "87%" → 87.0)
    if "confidence" in result and isinstance(result["confidence"], str):
        result["confidence"] = float(result["confidence"].replace("%", "").strip())

    return result



def run_llm(prompt, model="llama3"):
    try:
        result = subprocess.run(
            [OLLAMA_PATH, "run", model],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120  # seconds
        )
        raw_output = result.stdout.decode("utf-8").strip()

        if VERBOSE:
            # print("🧠 Actual prompt :")
            # print(prompt)
            print("🧠 Raw LLM output:")
            print(raw_output)

        
        parsed = parse_model_output(raw_output)

        if VERBOSE:
            print("🧠 Final Parsed JSON:")
            print(parsed if parsed else "❌ No valid JSON parsed.")

        return normalize_llm_keys(parsed)

    except Exception as e:
        print(f"❌ LLM execution failed: {e}")
        return {}


def parse_model_output(raw_output):
    raw_output = raw_output.strip()
    raw_output = re.sub(r"```(json)?", "", raw_output).strip()

    # Step 1: Try clean regex match
    match = re.search(r"\{.*\}", raw_output, re.DOTALL)
    
    
    if VERBOSE:
        # print("🧠 JSON  output:")
        # print(raw_output)
        print("🧠 Match output:")
        print(match)
    
    
    if match:
        json_str = match.group(0)
    else:
        # Step 2: Try manual recovery
        open_idx = raw_output.find("{")
        close_idx = raw_output.rfind("}")
        json_str = ""

        if open_idx != -1 and close_idx > open_idx:
            json_str = raw_output[open_idx:close_idx + 1]
            if VERBOSE:
                print("🧩 Recovered JSON block by slice")
        elif open_idx != -1 and "}" not in raw_output:
            json_str = raw_output[open_idx:] + "}"
            if VERBOSE:
                print("🛠 Reconstructed JSON block with closing }")

        if not json_str:
            print("⚠️ No valid JSON structure found.")
            return {}

    try:
        parsed = json.loads(json_str)
        return parsed
    except Exception as e:
        print(f"❌ JSON parse error: {e}")
        if VERBOSE:
            print(f"🚫 Failed JSON: {json_str}")
        return {}
