# 🤖 WhatsApp HOC Bot

A production-ready, AI-powered WhatsApp bot built with FastAPI and Python, designed to assist Class HOCs (Heads of Class) and Assistant HOCs with communication, announcements, and coordination tasks within student WhatsApp groups.

## 🌟 Features

*   **Command Handling:** Easy-to-use commands starting with `/` for administrative tasks.
*   **Permissions:** Restricts sensitive commands (`/announce`, `/remind`, `/clear`) to authorized HOC/Asst HOC numbers.
*   **AI Integration:** Uses OpenAI to generate:
    *   Funny, student-friendly jokes (`/joke`).
    *   Motivational quotes (`/quote`).
    *   Humorous, casual replies to non-command messages.
*   **Reminders:** Scheduled reminders using `APScheduler` (`/remind <time> <message>`).
*   **Webhooks:** Securely handles WhatsApp Cloud API webhooks for incoming messages and verification.
*   **Deployment Ready:** Includes `Procfile` and `requirements.txt` for easy deployment on platforms like Render or Railway.

## 🛠️ Tech Stack

*   **Language:** Python 3.11+
*   **Framework:** FastAPI
*   **Scheduler:** APScheduler
*   **AI:** OpenAI (with fallbacks)
*   **API:** WhatsApp Cloud API (or Twilio)

## 🚀 Setup and Deployment

### 1. Local Setup

1.  **Clone the repository:**
    ```bash
    git clone [REPO_URL]
    cd whatsapp_hoc_bot
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3.11 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    Rename the `.env.example` (or just use the existing `.env`) file to `.env` and fill in your credentials.

    ```bash
    # .env file content:

    # --- WhatsApp API Configuration ---
    WHATSAPP_TOKEN="YOUR_WHATSAPP_ACCESS_TOKEN" # Permanent or temporary token
    VERIFY_TOKEN="YOUR_WEBHOOK_VERIFY_TOKEN"   # A secret string for webhook verification
    PHONE_NUMBER_ID="YOUR_WHATSAPP_PHONE_NUMBER_ID"

    # --- Admin Configuration ---
    # Comma-separated list of authorized phone numbers (HOC & Asst HOC)
    ADMIN_NUMBERS="+2348012345678,+2348098765432"

    # --- AI Configuration ---
    OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

    # --- Deployment Configuration ---
    PORT=8000
    ```

5.  **Run the application locally:**
    ```bash
    uvicorn app:app --reload --host 0.0.0.0 --port 8000
    ```
    The app will be running at `http://localhost:8000`.

### 2. Webhook Testing (Local)

To receive messages from the WhatsApp Cloud API, you need a publicly accessible URL.

1.  **Install and run ngrok:**
    ```bash
    ngrok http 8000
    ```
    This will give you a public HTTPS URL (e.g., `https://xxxxxx.ngrok-free.app`).

2.  **Configure WhatsApp Cloud API:**
    *   Go to your Meta Developer App Dashboard.
    *   Navigate to **WhatsApp** -> **Configuration**.
    *   Set the **Webhook URL** to your ngrok URL + `/webhook` (e.g., `https://xxxxxx.ngrok-free.app/webhook`).
    *   Set the **Verify Token** to the value you set in your `.env` file (`VERIFY_TOKEN`).
    *   Click **Verify and Save**.

### 3. Production Deployment (Render/Railway)

1.  **Create a GitHub Repository:**
    Push your local project to a new GitHub repository.

2.  **Deploy to Platform:**
    *   Connect your Render/Railway account to your GitHub repository.
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command (Procfile):** `uvicorn app:app --host 0.0.0.0 --port $PORT` (The `Procfile` handles this automatically).
    *   **Environment Variables:** Set the environment variables (`WHATSAPP_TOKEN`, `VERIFY_TOKEN`, `PHONE_NUMBER_ID`, `ADMIN_NUMBERS`, `OPENAI_API_KEY`) on the hosting platform's dashboard. **Do not rely on the `.env` file in production.**

3.  **Final Webhook Configuration:**
    *   Once deployed, get the public URL of your service (e.g., `https://my-hoc-bot.onrender.com`).
    *   Update the **Webhook URL** in your Meta Developer App to your final deployed URL + `/webhook` (e.g., `https://my-hoc-bot.onrender.com/webhook`).

## ⚙️ Commands

| Command | Description | Example | Permissions |
| :--- | :--- | :--- | :--- |
| `/announce <message>` | Sends a formal announcement to the group. | `/announce Class meeting tomorrow at 8AM in Hall B.` | HOC/Asst HOC |
| `/remind <time> <message>` | Sets a timed reminder. Time format: `10m`, `1h`. | `/remind 10m Submit group report now!` | HOC/Asst HOC |
| `/clear` | Clears all scheduled reminders set by the user. | `/clear` | HOC/Asst HOC |
| `/joke` | Sends a random funny student-related joke. | `/joke` | All Users |
| `/quote` | Sends a motivational quote. | `/quote` | All Users |
| `/help` | Lists all available commands. | `/help` | All Users |
| `/poll` | Placeholder for a poll. (WIP) | `/poll` | HOC/Asst HOC |

---
*Built by an expert AI software engineer.*
