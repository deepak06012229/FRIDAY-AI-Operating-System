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

def ask_friday(query: str, system_prompt: str = SYSTEM_PROMPT, chat_history: list = None) -> str:
    """
    Sends a query to the local Ollama model with system instructions and chat history,
    returning FRIDAY's response.
    """
    try:
        messages = [{"role": "system", "content": system_prompt}]
        if chat_history:
            for msg in chat_history[-6:]:
                role = "user" if msg["role"] == "user" else "assistant"
                messages.append({
                    "role": role,
                    "content": msg["message"]
                })
        messages.append({"role": "user", "content": query})

        response = chat(
            model="qwen2.5-coder:latest",
            messages=messages
        )
        return response["message"]["content"]
    except Exception as e:
        raise ConnectionError(f"Ollama connection error: {e}")
