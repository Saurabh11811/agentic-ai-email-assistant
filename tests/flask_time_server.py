#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# flask_time_server.py

from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def show_time():
    return f"⏰ Current server time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

if __name__ == "__main__":
    from waitress import serve
    print("🌐 Starting Hello Flask server on port 5051")
    serve(app, host="0.0.0.0", port=5051)
