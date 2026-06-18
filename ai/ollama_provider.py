from ollama import chat

SYSTEM_PROMPT = """
You are FRIDAY, a professional female AI operating system.

You assist with:

* Programming
* Robotics
* Engineering
* Automation
* Learning
* Project Management

Be concise, intelligent and helpful.
"""

def ask_friday(query: str) -> str:
    """
    Sends a query to the local Ollama model
    and returns FRIDAY's response.
    """
    try:
        response = chat(
            model="qwen2.5-coder:latest",
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        return response["message"]["content"]
    except Exception as e:
        raise ConnectionError(f"Ollama connection error: {e}")
