import re
from utils import logger
import config

class IntentAnalyzer:
    def __init__(self):
        pass

    def analyze(self, query):
        """
        Analyzes a raw text query.
        Returns a dictionary representing the extracted intent or None.
        """
        q = query.lower().strip()
        logger.info(f"IntentAnalyzer: Analyzing query: '{query}'")

        # 1. Exit Commands
        if q in ["exit", "quit", "shutdown", "stop friday", "turn off"]:
            return {
                "intent": "exit_app",
                "param": "",
                "speak": "Shutting down FRIDAY core systems. Goodbye, Chief."
            }

        # 2. Local Workflows Execution
        if "morning workflow" in q or "morning workspace" in q or "morning dev" in q:
            return {
                "intent": "execute_workflow",
                "param": "Morning Dev Space",
                "speak": "Activating Morning Dev Space workspace."
            }
        
        if "run diagnostics" in q or "system diagnostics" in q or "diagnostic sweep" in q:
            return {
                "intent": "execute_workflow",
                "param": "System Diagnostics",
                "speak": "Initializing core diagnostics."
            }

        if "n8n test" in q or "run webhook test" in q:
            return {
                "intent": "execute_workflow",
                "param": "n8n Core Test",
                "speak": "Testing webhook integration."
            }

        # 3. Learning & Memory Commands
        # Pattern: remember that <fact> [as <category>]
        remember_cat_match = re.match(r"(?:remember that|learn that|save that)\s+(.*?)(?:\s+as\s+(personal|project|preference|goal|task))?$", q)
        if remember_cat_match:
            fact = remember_cat_match.group(1).strip()
            category = remember_cat_match.group(2) or "general"
            return {
                "intent": "learn_fact_category",
                "param": fact,
                "category": category,
                "speak": f"Got it, Chief. Saved that as a {category} fact."
            }

        # Existing simple remember (fallback)
        remember_match = re.match(r"(?:remember that|learn that|save that)\s+(.*)", q)
        if remember_match:
            fact = remember_match.group(1).strip()
            return {
                "intent": "learn_fact",
                "param": fact,
                "speak": f"Understood, Chief. I have committed that fact to memory."
            }

        if q in ["what do you know about me", "who am i", "tell me my profile", "show profile"]:
            return {
                "intent": "get_profile",
                "param": "",
                "speak": "Reading stored user matrices."
            }

        # Show facts by category commands
        show_match = re.match(r"show (my )?(personal|projects|preferences|goals|tasks)", q)
        if show_match:
            cat_map = {
                "personal": "personal",
                "projects": "project",
                "preferences": "preference",
                "goals": "goal",
                "tasks": "task",
            }
            category = cat_map.get(show_match.group(2))
            return {
                "intent": "show_facts_category",
                "param": category,
                "speak": f"Here are your {category} items, Chief."
            }

        if q in ["clear memory", "wipe database", "reset memory", "forget everything"]:
            return {
                "intent": "clear_memory",
                "param": "",
                "speak": "Purging all user databases. [LOG: Cache cleared]"
            }

        # Forget specific fact command
        forget_match = re.match(r"forget (.+)", q)
        if forget_match:
            fact = forget_match.group(1).strip()
            return {
                "intent": "forget_fact",
                "param": fact,
                "speak": f"I've removed that memory, Chief."
            }

        # 4. App Launch Commands
        # Match: "open chrome" or "launch vscode"
        launch_match = re.match(r"(?:open|launch|run|start)\s+(chrome|google chrome|vs code|visual studio code|notepad|calculator|cmd|explorer)", q)
        if launch_match:
            app_name = launch_match.group(1).strip()
            return {
                "intent": "launch_app",
                "param": app_name,
                "speak": f"Launching {app_name}."
            }

        # 5. Website Navigation Commands
        # Match: "open youtube" or "go to github"
        web_match = re.match(r"(?:open|go to|navigate to)\s+(youtube|github|gmail|google)", q)
        if web_match:
            web_name = web_match.group(1).strip()
            return {
                "intent": "open_url",
                "param": web_name,
                "speak": f"Opening {web_name} in browser."
            }

        # 6. System Status Commands
        if any(stat in q for stat in ["system status", "pc performance", "cpu and ram"]):
            return {
                "intent": "system_status",
                "param": "",
                "speak": "Accessing hardware telemetry."
            }

        # No match found, forward to LLM
        return None
