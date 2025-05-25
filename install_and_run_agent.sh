#!/bin/bash

echo "📁 Moving to project directory..."
cd "$(dirname "$0")"
PROJECT_DIR=$(pwd)

echo "📦 Creating logs directory..."
mkdir -p "$PROJECT_DIR/logs"

echo "🐍 Creating virtual environment..."
python3 -m venv .venv

echo "🐍 Activating virtual environment and installing requirements..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate


echo "🔧 Installing Homebrew dependencies..."
which brew >/dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "❌ Homebrew not found. Please install Homebrew first: https://brew.sh"
  exit 1
fi

brew install terminal-notifier || true
brew install ollama || true

echo "🔧 Reading configuration from config_agentic.py..."
# Extract flags from config
DOWNLOAD_LLAMA=$(python3 -c "from config_agentic import DOWNLOAD_LLAMA; print(DOWNLOAD_LLAMA)")
DOWNLOAD_MISTRAL=$(python3 -c "from config_agentic import DOWNLOAD_MISTRAL; print(DOWNLOAD_MISTRAL)")
DOWNLOAD_DEEPSEEK=$(python3 -c "from config_agentic import DOWNLOAD_DEEPSEEK; print(DOWNLOAD_DEEPSEEK)")
AGENT_INTERVAL=$(python3 -c "from config_agentic import AGENT_RUN_INTERVAL_SECONDS; print(AGENT_RUN_INTERVAL_SECONDS)")
EMAIL_ENABLED_GMAIL=$(python3 -c "from config_agentic import EMAIL_ENABLED_GMAIL; print(EMAIL_ENABLED_GMAIL)")
EMAIL_ENABLED_HOTMAIL=$(python3 -c "from config_agentic import EMAIL_ENABLED_HOTMAIL; print(EMAIL_ENABLED_HOTMAIL)")

echo "🧠 Downloading LLM models as configured..."
if [ "$DOWNLOAD_LLAMA" = "True" ]; then ollama pull llama3; fi
if [ "$DOWNLOAD_MISTRAL" = "True" ]; then ollama pull mistral; fi
if [ "$DOWNLOAD_DEEPSEEK" = "True" ]; then ollama pull deepseek-r1:latest; fi

# Load .env into environment
export $(grep -v '^#' .env | xargs)

# Determine if auth setup is needed
run_auth_setup=false

if [[ "$EMAIL_ENABLED_GMAIL" == "True" && ! -f "$GMAIL_TOKEN_PATH" ]]; then
  run_auth_setup=true
fi

if [[ "$EMAIL_ENABLED_HOTMAIL" == "True" && ! -f "$TOKEN_CACHE_PATH" ]]; then
  run_auth_setup=true
fi

if $run_auth_setup; then
  echo "🔐 Running email authentication setup..."
  source .venv/bin/activate
  python setup_email_tokens.py
  deactivate
else
  echo "✅ All required tokens exist. Skipping auth setup."
fi




echo "📝 Creating orchestrator launch agent plist..."
cat <<EOF > com.agentic.mail.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.agentic.mail</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_DIR/.venv/bin/python</string>
        <string>$PROJECT_DIR/agentic_ai_orchestrator.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>StartInterval</key>
    <integer>$AGENT_INTERVAL</integer>
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/orchestrator.out</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/orchestrator.err</string>
</dict>
</plist>
EOF

echo "📝 Creating Flask server launch agent plist..."
cat <<EOF > com.agentic.mail.flask.plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.agentic.mail.flask</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_DIR/.venv/bin/python</string>
        <string>-m</string>
        <string>waitress</string>
        <string>--host=0.0.0.0</string>
        <string>--port=5050</string>
        <string>notifications.notify_flask_popup:app</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/flask_popup.out</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/flask_popup.err</string>
</dict>
</plist>
EOF


# Unload first
launchctl unload ~/Library/LaunchAgents/com.agentic.mail.plist 2>/dev/null || true
launchctl unload ~/Library/LaunchAgents/com.agentic.mail.flask.plist 2>/dev/null || true


echo "📂 Moving plists to LaunchAgents and reloading..."
mkdir -p ~/Library/LaunchAgents/
mv com.agentic.mail.plist ~/Library/LaunchAgents/
mv com.agentic.mail.flask.plist ~/Library/LaunchAgents/

# Ensure files are written
sleep 1

launchctl load ~/Library/LaunchAgents/com.agentic.mail.plist
launchctl load ~/Library/LaunchAgents/com.agentic.mail.flask.plist

# Use 'bootout' if needed to force reset
#launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.agentic.mail.plist 2>/dev/null || true
#launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.agentic.mail.flask.plist 2>/dev/null || true

# Final load (GUI session-safe)
#launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.agentic.mail.plist
#launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.agentic.mail.flask.plist

#launchctl unload ~/Library/LaunchAgents/com.agentic.mail.plist 2>/dev/null || true
#launchctl unload ~/Library/LaunchAgents/com.agentic.mail.flask.plist 2>/dev/null || true
#launchctl load ~/Library/LaunchAgents/com.agentic.mail.plist
#launchctl load ~/Library/LaunchAgents/com.agentic.mail.flask.plist

echo "✅ Setup complete."
echo "💡 Orchestrator runs every $AGENT_INTERVAL seconds."
echo "🌐 Flask feedback UI (If flask notification is enabled, default True )available at http://localhost:5050/feedback"
echo "📁 Logs saved in: $PROJECT_DIR/logs/"