import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def call_ai_model(messages, response_format: str | None = None) -> str:
    """
    messages: list of {"role": "system"|"user"|"assistant", "content": "..."}
    Optionally force JSON-only output when response_format == "json_object".
    Returns text or error string.
    """
    if client is None:
        return "Groq API key not configured. Please set GROQ_API_KEY in .env."

    kwargs = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.7,
    }
    if response_format == "json_object":
        # JSON mode for structured outputs
        kwargs["response_format"] = {"type": "json_object"}

    try:
        completion = client.chat.completions.create(**kwargs)
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error calling Groq API: {e}"
