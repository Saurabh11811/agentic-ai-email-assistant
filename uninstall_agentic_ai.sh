#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
LAUNCH_AGENT_DIR="$HOME/Library/LaunchAgents"

echo "🧹 Unloading launch agents..."

launchctl unload "$LAUNCH_AGENT_DIR/com.agentic.mail.plist" 2>/dev/null || echo "  ⚠️ Orchestrator not running"
launchctl unload "$LAUNCH_AGENT_DIR/com.agentic.mail.flask.plist" 2>/dev/null || echo "  ⚠️ Flask server not running"

echo "🗑 Removing agent plist files..."
rm -f "$LAUNCH_AGENT_DIR/com.agentic.mail.plist"
rm -f "$LAUNCH_AGENT_DIR/com.agentic.mail.flask.plist"

echo "🧼 Cleaning project logs and session file..."
rm -f "$PROJECT_DIR/logs/"*.out
rm -f "$PROJECT_DIR/logs/"*.err
rm -f "$PROJECT_DIR/session_ids.json"

echo "✅ Agentic AI background services and logs cleaned up."
