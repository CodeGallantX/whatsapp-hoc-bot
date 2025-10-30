# 🤖 ClassHub AI Bot

A robust, modular, and AI-powered WhatsApp bot built with FastAPI and Python, designed to assist Heads of Class (HOC) and Assistant HOCs with advanced class communication, group management, reminders, and intelligent replies.

This bot operates using an external **WhatsApp Web Bridge** (e.g., Baileys, Go-WhatsApp, or any other REST/WebSocket wrapper) to connect to a personal WhatsApp account.

## 🌟 Key Features

*   **Modular Architecture:** Built with FastAPI, TinyDB (for persistence), and Loguru (for logging).
*   **Advanced Command Handling:** Includes group registration, announcements, reminders, and AI-powered message generation.
*   **Targeted Tagging (New):** Commands to tag all members (`/tagall`) or newly added members (`/tagnew`).
*   **AI Integration:** Uses OpenAI for message rewriting (`/ai_tone`), message generation (`/ai`), jokes, quotes, and humorous auto-replies.
*   **Persistent Reminders:** Uses `APScheduler` and `TinyDB` to ensure reminders survive bot restarts.
*   **Permissions:** Restricts administrative commands to registered HOC/Asst HOC numbers.
*   **Deployment Ready:** Includes `Procfile`, `requirements.txt`, and detailed setup instructions.

## 🛠️ Tech Stack

*   **Language:** Python 3.11+
*   **Framework:** FastAPI
*   **Database:** TinyDB (Local JSON DB for persistence)
*   **Scheduler:** APScheduler
*   **AI:** OpenAI (with fallbacks)
*   **Bridge:** External WhatsApp Web Bridge (via HTTP requests)

## 🚀 Setup and Deployment

### 1. Prerequisites

1.  **External WhatsApp Web Bridge:** You must have an external service (like a Baileys or Go-WhatsApp wrapper) running and connected to your WhatsApp account. This service must expose a REST API for sending messages and a webhook endpoint for receiving messages.
2.  **Clone the repository:**
    ```bash
    git clone https://github.com/CodeGallantX/classhub-ai-bot
    cd classhub-ai-bot
    ```

### 2. Local Setup

1.  **Create and activate a virtual environment:**
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    Copy the example file and fill in your credentials.

    ```bash
    cp .env.example .env
    # Edit the .env file with your specific values
    ```

    **Key Variables to Set:**
    *   `WA_BRIDGE_URL`: The URL of your running WhatsApp Web Bridge (e.g., `http://localhost:4000`).
    *   `ADMINS`: Comma-separated list of HOC/Asst HOC phone numbers (e.g., `+2348012345678`).
    *   `OPENAI_API_KEY`: Your OpenAI API key.
    *   `TZ`: Your timezone (e.g., `Africa/Lagos`).

4.  **Run the application locally:**
    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    The bot will be running at `http://localhost:8000`.

### 3. Webhook Configuration

1.  **Expose your local server:** Use a tool like `ngrok` to expose your local server to the internet.
    ```bash
    ngrok http 8000
    ```
    This will give you a public URL (e.g., `https://xxxxxx.ngrok-free.app`).
2.  **Configure the Bridge:** Set the webhook URL in your **WhatsApp Web Bridge** (Baileys/Go-WhatsApp wrapper) configuration to point to your public URL's `/webhook` endpoint (e.g., `https://xxxxxx.ngrok-free.app/webhook`).

### 4. Production Deployment (Render/Railway)

1.  **Create a GitHub Repository:** Push your local project to a new GitHub repository.
2.  **Deploy to Platform:**
    *   Connect your Render/Railway account to your GitHub repository.
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** The `Procfile` will handle the start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
    *   **Environment Variables:** Set all necessary environment variables (`WA_BRIDGE_URL`, `ADMINS`, `OPENAI_API_KEY`, `TZ`, etc.) on the hosting platform's dashboard.
    *   **Persistent Storage:** If using TinyDB for persistent reminders, ensure your platform provides a persistent volume for the `data/` directory.

## ⚙️ Commands

| Command | Example | Description | Permissions |
| :--- | :--- | :--- | :--- |
| `/register_group <alias>` | `/register_group CSC200` | Saves the current group with an alias. | Admin |
| `/list_groups` | — | Lists all registered groups. | Admin |
| `/announce <alias|all> <msg>` | `/announce all Mid-sem break starts Monday` | Sends an announcement to specified group(s). | Admin |
| `/remind <alias|all> "<msg>" at <time>` | `/remind CSC200 "Submit project" at 8pm` | Sets a persistent, timed reminder. | Admin |
| `/clear` | — | Clears all scheduled reminders for the current group. | Admin |
| `/tagall <alias|current>` | `/tagall CSC200` | Mentions all members in the specified group(s). | Admin |
| `/tagnew <alias> <time_period>` | `/tagnew CSC200 7 days ago` | Tags members who joined since a specified time (e.g., `7 days ago`). | Admin |
| `/ai <instruction>` | `/ai Write a polite reminder` | AI generates a message based on the prompt. | Admin |
| `/ai_tone <tone> <text>` | `/ai_tone motivational Don’t forget to attend` | Rewrites text with a specified tone (`formal`, `casual`, `motivational`, `sarcastic`, `humorous`). | Admin |
| `/joke` | — | Get a random funny student-related joke. | All Users |
| `/quote` | — | Get a motivational quote. | All Users |
| `/help` | — | Lists all available commands. | All Users |

### 💬 Auto-Response Logic

*   **Non-Command Messages:** If a user sends a non-command message, the bot will use AI to generate a casual, humorous, and empathetic reply related to student life.
*   **HOC/Asst HOC Tagging:** The bot is configured to respond when an admin is tagged, though the exact implementation depends on the bridge providing the `mentions` data in the webhook payload. The current code is set up to handle this.

---
*Built by an expert AI software engineer (Manus).*
