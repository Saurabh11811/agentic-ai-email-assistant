#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 16:10:31 2025

@author: saurabh.agarwal
"""

from pymongo import MongoClient
from config_agentic import MONGO_URI, MONGO_DB, VERBOSE

def get_mongo_collection(collection_name):
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    
    if VERBOSE and collection_name not in db.list_collection_names():
        print(f"📁 Collection '{collection_name}' not found — will be created on first insert.")

    
    return db[collection_name]
