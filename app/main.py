import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, status
from pydantic import BaseModel
from .ai_brain import get_joke, get_quote, get_humorous_reply
from .scheduler import set_send_message_func, add_reminder, clear_reminders, get_active_reminders
import requests

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment variables
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
ADMIN_NUMBERS = [num.strip() for num in os.getenv("ADMIN_NUMBERS", "").split(",") if num.strip()]
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Check for essential environment variables
if not all([WHATSAPP_TOKEN, VERIFY_TOKEN, PHONE_NUMBER_ID]):
    logger.error("Missing essential environment variables (WHATSAPP_TOKEN, VERIFY_TOKEN, PHONE_NUMBER_ID)")
    # In a real deployment, you might want to exit or raise an error here.
    # For now, we'll proceed but log the error.

# --- FastAPI App Initialization ---
app = FastAPI(
    title="WhatsApp HOC Bot",
    description="An AI-powered WhatsApp bot for Class HOCs and Assistant HOCs.",
    version="1.0.0"
)

# Inject the send_whatsapp_message function into the scheduler module
set_send_message_func(send_whatsapp_message)
    title="WhatsApp HOC Bot",
    description="An AI-powered WhatsApp bot for Class HOCs and Assistant HOCs.",
    version="1.0.0"
)

# --- Helper Functions ---

def send_whatsapp_message(recipient_id: str, message_body: str, message_type: str = "text"):
    """Sends a message back to the WhatsApp user/group."""
    if not WHATSAPP_TOKEN or not PHONE_NUMBER_ID:
        logger.error("Cannot send message: WHATSAPP_TOKEN or PHONE_NUMBER_ID is missing.")
        return False

    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    
    # Basic text message structure
    # Note: WhatsApp Cloud API uses 'individual' for both individual and group chats
    # The 'to' number is the ID of the user/group that sent the message.
    # The API automatically handles sending to the right place.
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_id,
        "type": message_type,
        "text": {"body": message_body}
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        logger.info(f"Message sent successfully to {recipient_id}. Response: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send message to {recipient_id}: {e}")
        return False

def is_admin(sender_number: str) -> bool:
    """Checks if the sender's number is in the list of authorized admin numbers."""
    # WhatsApp API numbers often come with a '+' prefix and country code.
    # We will check if the sender number (or a variant without '+') is in the admin list.
    sender_number = sender_number.lstrip('+')
    admin_list = [num.lstrip('+') for num in ADMIN_NUMBERS]
    return sender_number in admin_list

def handle_command(sender_id: str, message_text: str):
    """Parses and executes bot commands."""
    
    # 1. Parse command and arguments
    parts = message_text.strip().split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    # 2. Check for admin commands and permissions
    admin_commands = ["/announce", "/poll", "/remind", "/clear"]
    is_authorized = is_admin(sender_id)
    
    if command in admin_commands and not is_authorized:
        reply = "🚫 *Permission Denied*. Only HOCs and Assistant HOCs can use this command."
        send_whatsapp_message(sender_id, reply)
        logger.warning(f"Unauthorized command attempt: {sender_id} tried {command}")
        return

    # 3. Execute command
    if command == "/help":
        reply = (
            "🤖 *HOC Bot Commands* 🤖\n\n"
            "**Admin Commands (HOC/Asst HOC only):**\n"
            "• `/announce <message>`: Send a formal announcement.\n"
            "• `/poll <question> | <opt1>, <opt2>`: Create a quick poll (WIP - not fully implemented).\n"
            "• `/remind <time> <message>`: Set a timed reminder (e.g., `/remind 10m Submit report`).\n"
            "• `/clear`: Clear all scheduled reminders.\n\n"
            "**General Commands (Everyone):**\n"
            "• `/joke`: Get a random funny student-related joke.\n"
            "• `/quote`: Get a motivational quote.\n"
            "• `/help`: Show this list of commands."
        )
        send_whatsapp_message(sender_id, reply)
        
    elif command == "/announce":
        if args:
            # Announcement logic
            announcement_text = f"📣 *CLASS ANNOUNCEMENT*\n\n{args}"
            send_whatsapp_message(sender_id, announcement_text)
            logger.info(f"Announcement sent by {sender_id}: {args}")
        else:
            send_whatsapp_message(sender_id, "⚠️ Usage: `/announce <message>`")

    elif command == "/remind":
        if args:
            try:
                time_str, message = args.split(maxsplit=1)
                response = add_reminder(sender_id, time_str, message)
                send_whatsapp_message(sender_id, response)
            except ValueError:
                send_whatsapp_message(sender_id, "⚠️ Usage: `/remind <time> <message>` (e.g., `/remind 10m Submit report`)")
        else:
            send_whatsapp_message(sender_id, "⚠️ Usage: `/remind <time> <message>`")
            
    elif command == "/clear":
        response = clear_reminders(sender_id)
        send_whatsapp_message(sender_id, response)

    elif command == "/joke":
        joke = get_joke()
        send_whatsapp_message(sender_id, f"😂 *Joke Time* 😂\n\n{joke}")

    elif command == "/quote":
        quote = get_quote()
        send_whatsapp_message(sender_id, f"💡 *Motivation Boost* 💡\n\n{quote}")
            
    elif command == "/poll":
        # Placeholder for poll functionality - requires more complex API interaction
        send_whatsapp_message(sender_id, "🚧 *Poll Command (WIP)* 🚧\n\nThis feature is complex and requires specific WhatsApp API templates. For now, please use an external tool or the `/announce` command.")
            
    else:
        # Unknown command
        reply = "⚠️ *Unknown command*. Type `/help` to see available commands."
        send_whatsapp_message(sender_id, reply)
    """Parses and executes bot commands."""
    
    # 1. Parse command and arguments
    parts = message_text.strip().split(maxsplit=1)
    command = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    # 2. Check for admin commands and permissions
    admin_commands = ["/announce", "/poll", "/remind", "/clear"]
    is_authorized = is_admin(sender_id)
    
    if command in admin_commands and not is_authorized:
        reply = "🚫 *Permission Denied*. Only HOCs and Assistant HOCs can use this command."
        send_whatsapp_message(sender_id, reply)
        logger.warning(f"Unauthorized command attempt: {sender_id} tried {command}")
        return

    # 3. Execute command
    if command == "/help":
        reply = (
            "🤖 *HOC Bot Commands* 🤖\n\n"
            "**Admin Commands (HOC/Asst HOC only):**\n"
            "• `/announce <message>`: Send a formal announcement.\n"
            "• `/poll <question> | <opt1>, <opt2>`: Create a quick poll (WIP).\n"
            "• `/remind <time> <message>`: Set a timed reminder (e.g., `/remind 10m Submit report`).\n"
            "• `/clear`: Clear all scheduled reminders.\n\n"
            "**General Commands (Everyone):**\n"
            "• `/joke`: Get a random funny student-related joke.\n"
            "• `/quote`: Get a motivational quote.\n"
            "• `/help`: Show this list of commands."
        )
        send_whatsapp_message(sender_id, reply)
        
    elif command == "/announce":
        if args:
            # Placeholder for actual announcement logic (e.g., formatting, logging)
            announcement_text = f"📣 *CLASS ANNOUNCEMENT*\n\n{args}"
            send_whatsapp_message(sender_id, announcement_text)
            logger.info(f"Announcement sent by {sender_id}: {args}")
        else:
            send_whatsapp_message(sender_id, "⚠️ Usage: `/announce <message>`")
            
    # Add other command handlers here (e.g., /joke, /remind, /poll) in Phase 3
    
    else:
        # Unknown command
        reply = "⚠️ *Unknown command*. Type `/help` to see available commands."
        send_whatsapp_message(sender_id, reply)

def handle_ai_reply(sender_id: str, message_text: str):
    """Handles non-command messages with an AI-generated, humorous reply."""
    logger.info(f"Non-command message from {sender_id}. Engaging AI reply...")
    
    # Check if the message is a direct reply to the bot's number (DM)
    # The WhatsApp API often sends messages from a group as if they were from the user
    # to the bot's number. For simplicity, we'll assume any non-command message
    # is a candidate for an AI reply, as per the user's request.
    
    reply = get_humorous_reply(message_text)
    send_whatsapp_message(sender_id, reply)


# --- WhatsApp Webhook Schema ---
# This is a simplified model to parse the incoming message event
class ChangeValue(BaseModel):
    messaging_product: str
    metadata: dict
    statuses: list = []
    messages: list = []

class Change(BaseModel):
    value: ChangeValue
    field: str

class Entry(BaseModel):
    id: str
    changes: list[Change]

class WebhookPayload(BaseModel):
    object: str
    entry: list[Entry]


# --- FastAPI Routes ---

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Simple health check endpoint, includes active reminders."""
    active_reminders = get_active_reminders()
    return {
        "status": "ok", 
        "message": "WhatsApp HOC Bot is running.",
        "active_reminders": active_reminders
    }
async def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "message": "WhatsApp HOC Bot is running."}

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Endpoint for WhatsApp/Meta webhook verification."""
    
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("WEBHOOK_VERIFIED")
            return challenge
        else:
            logger.warning("Webhook verification failed: Invalid token or mode.")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification failed")

    logger.warning("Webhook verification failed: Missing parameters.")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing parameters")


@app.post("/webhook")
async def handle_webhook(payload: WebhookPayload):
    """Endpoint to receive incoming WhatsApp messages."""
    
    try:
        # Iterate over entries and changes to find the message
        for entry in payload.entry:
            for change in entry.changes:
                if change.field == "messages":
                    # Check for incoming messages
                    if change.value.messages:
                        message_data = change.value.messages[0]
                        sender_id = message_data.get("from")
                        message_type = message_data.get("type")
                        
                        if message_type == "text":
                            message_text = message_data.get("text", {}).get("body", "").strip()
                            logger.info(f"Received text message from {sender_id}: {message_text}")
                            
                            if message_text.startswith("/"):
                                # It's a command
                                handle_command(sender_id, message_text)
                            else:
                                # It's a normal chat message
                                handle_ai_reply(sender_id, message_text)
                                
                        elif message_type in ["image", "video", "audio", "sticker"]:
                            # Handle media messages if needed, for now, just acknowledge
                            logger.info(f"Received media message ({message_type}) from {sender_id}")
                            # send_whatsapp_message(sender_id, f"Thanks for the {message_type}! I'm focusing on text commands for now.")
                            
                        else:
                            logger.warning(f"Unhandled message type: {message_type}")
                            
                    # Check for status updates (e.g., message delivered, read)
                    if change.value.statuses:
                        status_data = change.value.statuses[0]
                        logger.info(f"Status update: ID {status_data.get('id')}, Status: {status_data.get('status')}")

    except Exception as e:
        logger.error(f"Error processing webhook payload: {e}")
        # Return 200 OK even on error to prevent Meta from retrying indefinitely
        
    return {"status": "ok"}


# --- Entry Point for Local Development ---
if __name__ == "__main__":
    import uvicorn
    # This is for local testing. The deployment will use a separate entry point (e.g., gunicorn/uvicorn command).
    uvicorn.run(app, host="0.0.0.0", port=8000)
