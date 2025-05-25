# 📬 Agentic AI Email Assistant

A background automation system that reads your inbox (Gmail & Hotmail), classifies emails with AI, stores them in MongoDB, and alerts you via macOS notifications or browser-based feedback popups. Built to reduce email overwhelm and highlight what truly matters.

---

## 🚀 Features

- 📥 Multi-account email fetcher (Gmail + Hotmail)
- 🧠 AI-based classification: *To-Do*, *Needs Reply*, *FYI*, etc.
- 🗃️ MongoDB storage for search and feedback tracking
- 🔔 Native macOS summary notifications
- 🌐 Optional browser popup for emoji feedback
- 📈 Learns from user feedback to improve over time
- 🧵 Runs as background daemon with auto-install support

---

## 🔐 Email Auth Setup

### 🔑 Gmail (OAuth2)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project → Enable Gmail API
3. Configure OAuth Consent screen (type: *External*)
4. Create OAuth credentials:
   - Type: **Desktop App**
   - Download the JSON file
5. Rename to `gmail_credentials.json` and place in the root
6. Update your `.env`:
   ```env
   GMAIL_CREDENTIALS_PATH=absolute/path/to/gmail_credentials.json
   GMAIL_TOKEN_PATH=absolute/path/to/gmail_token.json [This file will be generated automatically during first auth but you need to provide the path where you want to store this]
   ```

📄 Full guide with screenshots: `docs/Gmail-Setup.docx`

---

### 🔑 Hotmail (Outlook via Microsoft Entra)

1. Visit [entra.microsoft.com](https://entra.microsoft.com/)
2. Go to **App registrations** → **New registration**
3. Name your app and set:
   - Redirect URI: `http://localhost` 
4. Enable *Public client flows* under Authentication
5. Add *Token configuration* for ID token + Graph claims
6. Under *API Permissions*, add:
   - `Mail.Read`
7. From *Overview*, copy:
   - Application (client) ID
8. Add to `.env`:
   ```env
   HOTMAIL_CLIENT_ID=your_client_id
   HOTMAIL_AUTHORITY=https://login.microsoftonline.com/consumers
   HOTMAIL_SCOPE=Mail.Read
   TOKEN_CACHE_PATH=absolute/path/to/.msal_token_cache.bin [This file will be generated automatically during first auth but you need to provide the path where you want to store this]
   ```

📄 Full guide with screenshots: `docs/Hotmail-Setup.docx`

---

## ⚡ Quick Start

1. Please update the flags in config_agentic.py file for enabled emails
    - EMAIL_ENABLED_HOTMAIL = True/False (Default True)
    - EMAIL_ENABLED_GMAIL = True/False (Default True)
    
2. Update the LLMs you would like to download automatically, disable others for faster load time
    - DOWNLOAD_LLAMA = True [Default used]
    
3. Copy the .env.sample to .env and update the entries with absolute paths
    - HOTMAIL_CLIENT_ID=your-hotmail-client-id
    - TOKEN_CACHE_PATH=your-path-to-store-cached-tokn/.msal_token_cache.bin
    
    - GMAIL_CREDENTIALS_PATHGMAIL_CREDENTIALS_PATH=/absolute/path/to/gmail_credentials.json
    - GMAIL_TOKEN_PATH=/absolute/path/to/gmail_token.json
        
4. Install system dependencies (macOS only)

```bash
   brew install mongodb-community@6 terminal-notifier

   brew services start mongodb-community@6


# 4.1. Clone this repo
git clone https://github.com/Saurabh11811/agentic-ai-email-assistant.git
cd agentic-ai-email-assistant

# 4.2. (Optional) Create a virtualenv
python3 -m venv venv
source venv/bin/activate

# 4.3. Install dependencies
pip install -r requirements.txt

# 4.4. Configure credentials
cp .env.example .env
nano .env
#ensure you fill the absolute paths here for these tokens, if you use some text editor, ensure the end line charector is unix style and not windows

# 4.5. Run email token setup interactively
python utils/setup_email_tokens.py

# 4.6. Launch the agent!
python agentic_ai_orchestrator.py
```

5. You can check the status of Agent or Logs using status.sh, first run will take time
---

## 🛠️ Full Installation Guide

### 🔧 A. One-Click Installation (Recommended)

Run the full setup script:

```bash
bash install_and_run_agent.sh
```

This will:
- Install dependencies and virtualenv
- Run token setup
- Auto-generate plist for macOS daemon
- Start Flask server (if enabled)
- Show test notification if no actionable emails found

---


## ⚙️ Configuration Reference

All configuration is managed via the `.env` file and `config_agentic.py`.

| **Key**                         | **Description**                                                             |
| ------------------------------- | --------------------------------------------------------------------------- |
| `CONFIG_DIR`                    | Path to store cache, logs, and timestamp files                              |
| `PROJECT_ROOT`                  | Base path of the project (auto-detected or set manually if needed)          |
| `LABEL_PATH`                    | Path to the YAML/JSON file containing action and category labels            |
| `GMAIL_CREDENTIALS_PATH`        | Absolute path to `gmail_credentials.json` from Google Cloud Console         |
| `GMAIL_TOKEN_PATH`              | Path where Gmail token will be saved after first OAuth login                |
| `GMAIL_SCOPES`                  | OAuth scopes for Gmail access (default: Gmail read-only or read/write)      |
| `TIMESTAMP_FILE_GMAIL`          | Path to file tracking last Gmail fetch time                                 |
| `HOTMAIL_CLIENT_ID`             | Microsoft Entra Application (Client) ID for Hotmail OAuth                   |
| `HOTMAIL_AUTHORITY`             | OAuth authority URL (e.g., `https://login.microsoftonline.com/<tenant_id>`) |
| `HOTMAIL_SCOPE`                 | OAuth scope for Hotmail (default: `Mail.Read Mail.ReadWrite`)               |
| `TOKEN_CACHE_PATH`              | Path to save Hotmail access/refresh tokens                                  |
| `HOTMAIL_MESSAGES_ENDPOINT`     | Microsoft Graph endpoint for fetching messages                              |
| `TIMESTAMP_FILE_HOTMAIL`        | Path to file tracking last Hotmail fetch time                               |
| `FETCH_LOOKBACK_DAYS`           | Number of days to look back if no timestamp file exists                     |
| `MAX_EMAILS`                    | Maximum number of emails to fetch per account per run                       |
| `FORCE_FETCH`                   | If true, fetch all emails ignoring timestamp                                |
| `FORCE_DB`                      | If true, drop MongoDB collection before inserting new data                  |
| `EMAIL_ENABLED_HOTMAIL`         | Enable Hotmail fetching (`true` or `false`)                                 |
| `EMAIL_ENABLED_GMAIL`           | Enable Gmail fetching (`true` or `false`)                                   |
| `MONGO_URI`                     | Full MongoDB connection string                                              |
| `MONGO_DB`                      | Name of the MongoDB database (e.g., `EMAIL_ANALYSIS`)                       |
| `MONGO_COLLECTION`              | Target collection for storing emails (e.g., `hotmail_agentic_emails`)       |
| `CATEGORY_MODEL_NAME`           | Name of the model used for category classification                          |
| `ACTION_MODEL_NAME`             | Name of the model used for action classification                            |
| `OLLAMA_PATH`                   | Path to the local Ollama executable (for running LLMs locally)              |
| `FORCE_CATEGORY_CLASSIFICATION` | If true, reclassify categories even if already done                         |
| `FORCE_ACTION_CLASSIFICATION`   | If true, reclassify actions even if already done                            |
| `RETRY_FAILED_CATEGORY`         | Retry emails where category classification failed (`true` or `false`)       |
| `RETRY_FAILED_ACTION`           | Retry emails where action classification failed (`true` or `false`)         |
| `CATEGORY_VALID_LABELS`         | List of valid labels for top-level category classification                  |
| `ACTION_LABELS`                 | List of valid action labels (e.g., `To-do`, `FYI`, `Needs Reply`)           |
| `NOTIFY_MODE`                   | Mode to use for notification: `"summary"`, `"webview"`, or `"flask"`        |
| `NOTIFICATION_LABELS`           | Only emails with these action labels will trigger notification              |
| `RUN_FETCH`                     | Whether to fetch emails in current run (`true` or `false`)                  |
| `RUN_CLASSIFY`                  | Whether to classify emails in current run (`true` or `false`)               |
| `RUN_NOTIFY`                    | Whether to show notifications in current run (`true` or `false`)            |
| `VERBOSE`                       | Enable detailed logging for debug purposes                                  |
| `DOWNLOAD_LLAMA`                | Download LLaMA model during setup (`true` or `false`)                       |
| `DOWNLOAD_MISTRAL`              | Download Mistral model during setup (`true` or `false`)                     |
| `DOWNLOAD_DEEPSEEK`             | Download DeepSeek model during setup (`true` or `false`)                    |
| `AGENT_RUN_INTERVAL_SECONDS`    | Frequency (in seconds) for the agent to auto-run (used in `.plist`)         |

---

## 🧱 Architecture Overview

```text
+------------------+      +------------------+      +----------------------+
|   Email Fetcher  | ---> | Email Classifier | ---> | MongoDB (Storage)    |
| (Gmail/Hotmail)  |      | (Action & Topic) |      | + Email status       |
+------------------+      +------------------+      | + Feedback updates   |
                                                   +----------------------+
                                                             |
                                                +------------+------------+
                                                |                         |
                                   +---------------------+   +---------------------+
                                   | Notification System |   | Feedback Collector  |
                                   | (macOS / Browser)   |   | (Flask / Webview)   |
                                   +---------------------+   +---------------------+
```

---

## 📁 Project Structure

```
📁 agentic-ai-email-assistant/
├── agentic_ai_orchestrator.py             # Main orchestrator script
├── config_agentic.py            # Configuration flags
├── fetchers/                    # Gmail & Hotmail logic
├── classifiers/                 # Email classification modules (action, topic)
├── notifications/               # macOS + Flask + Webview handlers
├── utils/                       # Shared helper functions
├── tests/                       # Individual test scripts
├── docs/                        # Setup screenshots and instructions
├── .env                         # Local environment config
├── requirements.txt             # Dependencies list
└── install_and_run_agent.sh     # One-click setup & daemon launcher
```

---

## 🧰 Utilities and Scripts

| Script                        | Description                                 |
|------------------------------|---------------------------------------------|
| `install_and_run_agent.sh`   | Full setup & background execution           |
| `setup_email_tokens.py`      | Interactive auth for Gmail & Hotmail        |
| `Reset_Email_DB.py.py`       | Delete, backup, and clean MongoDB entries   |
| `status.sh`                  | Script to check the logs for agent          |
| `uninstall_agentic_ai.sh`    | Script to uninstall the agent and clear logs|

---

## 🧪 Testing & Debugging

```bash
# Test Gmail fetcher
python tests/test_gmail_fetch_and_store.py

# Test Hotmail fetcher
python tests/test_hotmail_fetch_and_store.py

# Test classification pipeline
python tests/test_email_Classifier_Agents.py
```

**Common Fixes**:
- Gmail token errors → delete token file and re-auth
- Flask error on port 5050 → manually kill with `lsof -ti :5050 | xargs kill -9`
- MongoDB not running → check `brew services list`

---



## 🔁 Feedback & Learning Loop

Once you receive a notification or popup, you can provide feedback using 👍 / 👎 or ⏭️ (skip). This data is stored in MongoDB for analysis and potential model refinement in the **future**.

- Emails are updated with `"feedback": "positive"` or `"negative"`
- Used to evaluate classification model performance over time

---


## 💡 Advanced Customization

- Change models in `classifiers/` (supports LLMs via API or local Ollama)
- Modify MongoDB collection logic in `utils/mongo_store.py`
- Adjust notification preferences in `config_agentic.py`

---


## 🧠 Known Issues

- This works only for MAC-OS for now. Windows require some path cleanups / harmonisation
- Gmail projects not in "Test" mode may block consent
- Token file may expire or become corrupted over time, you should delete .msal_token_cache.bin and gmail_token.json file and then run setup_email_tokens.py again
- Flask UI sometimes does not auto-shutdown in dev mode
- Native macOS notifications may not appear if terminal-notifier
- Webview works fine in demon mode, in GUI mode (from IDE), after closing the popup, the task icon still exists and has to close forcefully. Will restart terminal
- Flask notifications works fine in both modes (Agentic and IDE). Agentic will create a separate flask server, with IDE, you need to run notify_flask_popup.py manually
- **This readme file miight be incomplete** [Tried Best btw] :)

---

## 🧪 FAQ / Debugging Tips

| Problem | Fix |
|--------|-----|
| Flask port already in use | `lsof -ti :5050 | xargs kill -9` |
| Gmail auth not working | Delete Gmail token file and re-run setup |
| Hotmail fetch returns 403 | Check if Entra app has proper Mail.Read permissions |
| MongoDB not connecting | Use `brew services list` to confirm MongoDB is running |
| No notification shown | macOS only. Ensure `terminal-notifier` and `pync` installed |
| `.env` values not working | Make sure it's in the root directory and paths are absolute |
| Feedback UI doesn’t refresh | Reload browser, or restart Flask server |

---

## 👨‍💻 Contributors & Credits

- **Saurabh Agarwal** – Architect & Developer  
- **GPT-4** – Coding Assistant AI

---

## 📄 License

MIT License — Free to use, modify, and distribute.


---

## 📄 Feedback

Feel free to provide any feedback you may have, create the issues, happy to fix whenever get time. 

