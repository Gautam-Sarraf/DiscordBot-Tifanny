# Tiffany Bot 🌸

Tiffany Bot is a modern, modular, production-ready Discord bot written in Python 3.12 utilizing the `discord.py` framework and integrated with Ollama (primary, using `gemma3-amoral:latest`) and Google's Gemini AI (fallback).

## Features
- **Slash Commands**: Complete slash command support (`/ping`, `/hello`, `/health`, `/ask`, `/clear`, `/persona`).
- **Ollama Integration with Gemini Fallback**: Prioritizes local Ollama inference (using the unrestricted `gemma3-amoral:latest` model) for chatting, with automatic fallback to Google Gemini (`gemini-2.5-flash` / `gemma-4-31b-it`) in case of server timeouts or connection issues.
- **Dynamic Persona & Memory**: Features sliding-window conversation memory and custom system instructions (e.g. customized flirty response behavior for the server owner).
- **Diagnostics**: Health check and telemetry stats using `psutil`.
- **Clean Logging**: Dual-logging to colorized console output and `data/bot.log`.
- **Modular Design**: Structured using Python package patterns and discord.py Cogs.

---

## Folder Structure
```
tiffany-bot/
├── bot.py                  # Bot entry point and class definition
├── .env                    # Local environment variables (do not commit)
├── .env.example            # Environment variables template
├── requirements.txt        # Package dependencies
├── README.md               # Setup and running instructions
│
├── cogs/                   # Discord Cogs for organized commands
│   ├── __init__.py
│   ├── general.py          # /ping, /hello, /health commands
│   └── ai.py               # AI commands (/ask, /clear, /persona)
│
├── services/               # Core business services
│   ├── __init__.py
│   ├── gemini_service.py   # Ollama & Gemini AI service wrapper
│   └── config.py           # Configuration loader and validator
│
├── utils/                  # Common utilities
│   ├── __init__.py
│   ├── logger.py           # Logging configuration
│   └── helpers.py          # Uptime formats and embed creators
│
└── data/                   # Data and logs storage directory
```

---

## Setup Instructions (macOS)

### 1. Prerequisites
Ensure you have Python 3.12 installed on your system. You can check this by running:
```bash
python3 --version
```
If Python is not installed or is outdated, install it via Homebrew:
```bash
brew install python@3.12
```

### 2. Clone/Move into the Project Directory
```bash
cd /Users/webninjaz-developer/Desktop/tifanny-bot
```

### 3. Create and Activate Virtual Environment
```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Credentials
Copy `.env.example` to `.env` (if not already done) and insert your Discord Bot Token, Google Gemini API Key, and Ollama configuration:
```bash
cp .env.example .env
```
Inside your `.env` file:
```env
DISCORD_BOT_TOKEN=your_token_here
GEMINI_API_KEY=your_gemini_key_here
LOG_LEVEL=INFO
ENVIRONMENT=development

# Ollama Configuration
USE_OLLAMA=true
OLLAMA_MODEL=gemma3-amoral:latest
OLLAMA_HOST=http://localhost:11434
```

> [!IMPORTANT]
> Keep your `.env` file private and never check it into git or public repositories.

---

## Discord Developer Portal Configuration

To ensure your bot functions correctly:
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Select your Application, and navigate to the **Bot** tab on the left sidebar.
3. Scroll down to **Privileged Gateway Intents** and enable:
   - **Presence Intent** (optional, recommended)
   - **Server Members Intent** (required for user counters and member functions)
   - **Message Content Intent** (optional, recommended for future chat triggers)
4. Save your changes.
5. Generate an invite link under the **OAuth2** -> **URL Generator** tab:
   - Check the `bot` and `applications.commands` scopes.
   - Under **Bot Permissions**, select the required permissions (e.g. *Send Messages, Embed Links, Read Message History*).
   - Copy the link and open it in a browser to invite Tiffany to your server.

---

## Running the Bot
Make sure your virtual environment is active, then run:
```bash
python bot.py
```

Upon start, Tiffany will automatically sync all slash commands globally and begin listening for command interactions.
