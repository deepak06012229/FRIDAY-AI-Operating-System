import os
import requests
import json
from utils import logger
import config

from ai.prompts import SYSTEM_INSTRUCTIONS

class LLMClient:
    def __init__(self, memory_manager=None):
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.model = config.GEMINI_MODEL
        self.memory = memory_manager
        
        if not self.api_key:
            logger.warn("GEMINI_API_KEY environment variable not found. FRIDAY will run in offline rule-based mode.")

    def update_api_key(self, api_key):
        self.api_key = api_key
        logger.info("LLM Client: Gemini API key updated.")

    def generate_response(self, user_query, chat_history=None):
        """Generates a text response. Calls Gemini REST endpoint or runs offline logic."""
        if not self.api_key:
            return self.offline_generate_response(user_query)

        # Inject memory facts to system context if available
        context = SYSTEM_INSTRUCTIONS
        if self.memory:
            facts = self.memory.get_all_facts()
            if facts:
                facts_str = "\n".join([f"- {f['fact']} (Category: {f['category']})" for f in facts[:10]])
                context += f"\n\nKnown Facts about the Commander/User:\n{facts_str}"

        # Construct payload for Gemini API
        url = config.GEMINI_REST_URL.format(model=self.model, key=self.api_key)
        headers = {"Content-Type": "application/json"}
        
        # Build contents structure including conversation history if provided
        contents = []
        if chat_history:
            # Add last 6 messages for context
            for msg in chat_history[-6:]:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["message"]}]
                })
        
        # Add current user prompt
        contents.append({
            "role": "user",
            "parts": [{"text": user_query}]
        })

        payload = {
            "contents": contents,
            "systemInstruction": {
                "parts": [{"text": context}]
            },
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 250
            }
        }

        try:
            logger.info("LLMClient: Dispatching query to Gemini...")
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                resp_json = response.json()
                text = resp_json['candidates'][0]['content']['parts'][0]['text']
                logger.info("LLMClient: Response received successfully.")
                return text
            else:
                logger.error(f"Gemini API returned error code {response.status_code}: {response.text}")
                return self.offline_generate_response(user_query) + " [WARNING: API error - offline fallback active]"
        except Exception as e:
            logger.error(f"Exception during LLM connection: {e}")
            return self.offline_generate_response(user_query) + " [WARNING: Connection failed - offline fallback active]"

    def offline_generate_response(self, query):
        """Generates responses locally when no network or API key is active."""
        q = query.lower().strip()
        
        # 1. Check direct greeting requests
        if any(greet in q for greet in ["hello", "hi", "hey friday", "hello friday"]):
            return "Greetings, Commander. All systems are operational. Ready for instructions."
            
        if "who are you" in q or "your name" in q:
            return "I am FRIDAY, a personal AI operating system inspired by Tony Stark's assistant from Marvel. Ready to assist."
            
        if "what can you do" in q or "help" in q:
            return ("I can launch applications (Chrome, VS Code), trigger automated workflow sequences, "
                    "monitor system hardware, store memories in a local database, and query web pages. "
                    "Please configure my Gemini API key in the database settings to enable full speech dialogue.")
            
        # 2. Local rule-based command suggestions
        if "chrome" in q or "browser" in q:
            return "Executing browser initialization. ```json\n{\n  \"action\": \"launch_app\",\n  \"param\": \"chrome\"\n}\n```"
            
        if "code" in q or "vs code" in q:
            return "Initializing coding environment. ```json\n{\n  \"action\": \"launch_app\",\n  \"param\": \"vs code\"\n}\n```"
            
        if "youtube" in q:
            return "Navigating to YouTube. ```json\n{\n  \"action\": \"open_url\",\n  \"param\": \"youtube\"\n}\n```"

        if "morning" in q and "workspace" in q:
            return "Executing morning workspace launch protocol. ```json\n{\n  \"action\": \"execute_workflow\",\n  \"param\": \"Morning Dev Space\"\n}\n```"
            
        if "diagnostics" in q or "health" in q:
            return "Deploying system telemetry scan. ```json\n{\n  \"action\": \"execute_workflow\",\n  \"param\": \"System Diagnostics\"\n}\n```"

        return "Query processed via offline logic. Command unrecognized. Please supply a Gemini API Key in the UI panel."
