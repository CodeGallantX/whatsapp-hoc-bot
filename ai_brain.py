import os
import random
import logging
from openai import OpenAI
from openai.error import OpenAIError

logger = logging.getLogger(__name__)

# --- Fallback Data ---
# Used if the OpenAI API call fails or is not configured
FALLBACK_JOKES = [
    "Why did the student eat his homework? Because the teacher told him it was a piece of cake!",
    "What do you call a sleeping bull? A bulldozer!",
    "Why don't scientists trust atoms? Because they make up everything!",
    "My teacher told me to stop singing the 'The Lion Sleeps Tonight' in class. I said, 'Wimoweh, wimoweh, wimoweh, wimoweh.'",
    "What's the difference between a teacher and a train? A teacher tells you to study, a train says 'choo-choo'!",
]

FALLBACK_QUOTES = [
    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
    "Education is the most powerful weapon which you can use to change the world. - Nelson Mandela",
    "The mind is not a vessel to be filled but a fire to be kindled. - Plutarch",
]

# --- AI Client Initialization ---
# The OpenAI client will automatically pick up the OPENAI_API_KEY from the environment
try:
    client = OpenAI()
except Exception as e:
    logger.warning(f"Failed to initialize OpenAI client: {e}. AI functions will use fallbacks.")
    client = None

# --- AI Functions ---

def get_ai_response(prompt: str, system_prompt: str, temperature: float = 0.7) -> str:
    """
    Generates a response using the OpenAI API.
    Uses a fallback if the client is not initialized or the API call fails.
    """
    if not client:
        logger.warning("OpenAI client not available. Returning a generic fallback response.")
        return "Sorry, my AI brain is currently offline. Try again later! 🤖"

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini", # Using a fast, capable model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except OpenAIError as e:
        logger.error(f"OpenAI API Error: {e}. Falling back to a generic response.")
        return "Oops! I hit a snag while talking to the AI cloud. Maybe try asking me for a `/joke` instead? 😅"
    except Exception as e:
        logger.error(f"An unexpected error occurred during AI generation: {e}")
        return "My circuits are buzzing! I need a moment. 😵‍💫"

def get_joke() -> str:
    """Gets a student-friendly joke, using AI or a fallback list."""
    system_prompt = (
        "You are a witty, student-friendly AI bot. Generate a single, clean, "
        "humorous joke related to university, class, or student life. "
        "Keep it short and use emojis."
    )
    prompt = "Tell me a funny student-related joke."
    
    try:
        joke = get_ai_response(prompt, system_prompt, temperature=0.8)
        if "Sorry, my AI brain is currently offline" in joke or "Oops! I hit a snag" in joke:
            raise Exception("AI failed, use fallback.")
        return joke
    except:
        return random.choice(FALLBACK_JOKES)

def get_quote() -> str:
    """Gets a motivational quote, using AI or a fallback list."""
    system_prompt = (
        "You are a motivational AI bot. Provide a single, concise, and inspiring "
        "quote suitable for a student. Attribute the quote."
    )
    prompt = "Give me a motivational quote."
    
    try:
        quote = get_ai_response(prompt, system_prompt, temperature=0.6)
        if "Sorry, my AI brain is currently offline" in quote or "Oops! I hit a snag" in quote:
            raise Exception("AI failed, use fallback.")
        return quote
    except:
        return random.choice(FALLBACK_QUOTES)

def get_humorous_reply(user_message: str) -> str:
    """Generates a humorous, casual, and student-friendly reply to a non-command message."""
    system_prompt = (
        "You are a casual, friendly, and slightly witty student-focused AI bot. "
        "Your goal is to respond to the user's message in a natural, empathetic, "
        "and humorous way, relating it to university or class life. Keep the reply "
        "short (1-2 sentences) and use relevant emojis. Do not use markdown formatting."
    )
    prompt = f"User said: '{user_message}'"
    
    try:
        reply = get_ai_response(prompt, system_prompt, temperature=0.9)
        if "Sorry, my AI brain is currently offline" in reply or "Oops! I hit a snag" in reply:
            raise Exception("AI failed, use fallback.")
        return reply
    except:
        # Generic humorous fallback for chat
        return random.choice([
            "😂 I feel you, that lecturer’s 8AM class is built different!",
            "Hang in there 😭, exams don’t kill — they just reduce WiFi strength!",
            "We're all in this together! Maybe a quick nap will fix it? 😴",
            "Don't worry, the weekend is only a few hundred slides away! 😉"
        ])
