# utils/response_sanitizer.py

"""Utility to sanitize LLM responses before displaying to the user.

Removes internal log tokens, JSON blocks, and other developer annotations.
"""
import re

def sanitize_response(text: str) -> str:
    """Clean *text* for user display.

    Removes:
    - Bracketed tags like [LOG: ...], [INFO], [DEBUG], [VOICE], [SYSTEM], [TRACE]
    - JSON fenced code blocks (```json ... ```)
    - Generic fenced code blocks (``` ... ```)
    - Excess whitespace.
    """
    # Remove bracketed tags
    text = re.sub(r"\[\s*(?:LOG|INFO|DEBUG|VOICE|SYSTEM|TRACE)[^\]]*\]", "", text, flags=re.IGNORECASE)
    # Remove fenced JSON blocks
    text = re.sub(r"```json.*?```", "", text, flags=re.DOTALL | re.IGNORECASE)
    # Remove generic fenced code blocks
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text
