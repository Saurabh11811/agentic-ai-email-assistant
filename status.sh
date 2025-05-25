#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"

echo "🔍 Checking status of Agentic AI services..."

echo ""
echo "🧠 Orchestrator agent (com.agentic.mail):"
launchctl list | grep com.agentic.mail || echo "  ❌ Not running"

echo ""
echo "🌐 Flask server agent (com.agentic.mail.flask):"
launchctl list | grep com.agentic.mail.flask || echo "  ❌ Not running"

echo ""
echo "📄 Recent orchestrator logs:"
tail -n 10 "$LOG_DIR/orchestrator.out" 2>/dev/null || echo "  (no output log found)"
tail -n 10 "$LOG_DIR/orchestrator.err" 2>/dev/null || echo "  (no error log found)"

echo ""
echo "📄 Recent Flask server logs:"
tail -n 10 "$LOG_DIR/flask_popup.out" 2>/dev/null || echo "  (no output log found)"
tail -n 10 "$LOG_DIR/flask_popup.err" 2>/dev/null || echo "  (no error log found)"

echo ""
echo "✅ Done."
