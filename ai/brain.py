import json
import re
from PyQt5.QtCore import QObject, pyqtSignal
from utils import logger
import config
from memory.memory_manager import MemoryManager
from ai.llm_client import LLMClient
from ai.intent_analyzer import IntentAnalyzer
from automation import app_launcher, browser_controller
from automation.workflow_engine import WorkflowEngine
import psutil
from ai.ollama_provider import ask_friday
from ai.prompts import SYSTEM_INSTRUCTIONS

class FRIDAYBrain(QObject):
    """Orchestrates query parsing, DB logging, tool calls, and LLM text generation."""
    memory_updated = pyqtSignal()  # Signal emitted after memory updates
    speak_requested = pyqtSignal(str)              # FRIDAY speaks this
    response_completed = pyqtSignal(str, str)     # Emits (user_msg, friday_msg) to Chat UI
    workflow_trigger = pyqtSignal(str)            # Triggers workflow execution
    system_exit_triggered = pyqtSignal()          # Triggers system close

    def __init__(self, parent=None):
        super().__init__(parent)
        self.memory = MemoryManager()
        self.llm = LLMClient(self.memory)
        self.intent_analyzer = IntentAnalyzer()
        self.workflow_engine = WorkflowEngine()
        self._current_model = "Ollama (qwen2.5-coder:latest)"
        self._current_voice = getattr(config, "VOICE_DEFAULT", "en-US-JennyNeural")
        self._current_workflow = "None"
        # Authentication and session management removed

    def process_query(self, user_query):
        """Processes the query, checks local commands, calls LLM, and triggers tools.
        All commands are now available without authentication checks."""
        if not user_query.strip():
            return
        # No session active check needed
        logger.info(f"Brain: Processing query: '{user_query}'")
        self.memory.add_conversation_message("user", user_query)
        local_intent = self.intent_analyzer.analyze(user_query)
        if local_intent:
            intent_type = local_intent["intent"]
            param = local_intent["param"]
            speak_text = local_intent["speak"]
            logger.info(f"Brain: Local command match found: {intent_type}")
            if intent_type == "exit_app":
                self.speak_requested.emit(speak_text)
                self.system_exit_triggered.emit()
                self.memory.add_conversation_message("friday", speak_text)
                self.response_completed.emit(user_query, speak_text)
                return
            elif intent_type == "launch_app":
                success, msg = app_launcher.launch_application(param)
                response_str = f"{speak_text} {msg}"
                self.speak_requested.emit(response_str)
                self.memory.add_conversation_message("friday", response_str)
                self.response_completed.emit(user_query, response_str)
                return
            elif intent_type == "open_url":
                success, msg = browser_controller.open_url(param)
                response_str = f"{speak_text} {msg}"
                self.speak_requested.emit(response_str)
                self.memory.add_conversation_message("friday", response_str)
                self.response_completed.emit(user_query, response_str)
                return
            elif intent_type == "execute_workflow":
                self.speak_requested.emit(speak_text)
                self.workflow_trigger.emit(param)
                self.memory.add_conversation_message("friday", speak_text)
                self.response_completed.emit(user_query, speak_text)
                return
            elif intent_type == "learn_fact":
                self.memory.add_fact(param)
                self.memory_updated.emit()
                self.speak_requested.emit(speak_text)
                self.memory.add_conversation_message("friday", speak_text)
                self.response_completed.emit(user_query, speak_text)
                return
            elif intent_type == "learn_fact_category":
                category = local_intent.get("category", "general")
                self.memory.add_fact(param, category)
                self.memory_updated.emit()
                self.speak_requested.emit(speak_text)
                self.memory.add_conversation_message("friday", speak_text)
                self.response_completed.emit(user_query, speak_text)
                return
            elif intent_type == "show_facts_category":
                facts = self.memory.get_facts_by_category(param)
                if facts:
                    fact_list = ", ".join([f["fact"] for f in facts])
                    response_str = f"Here are your {param} items: {fact_list}."
                else:
                    response_str = f"You have no stored {param} items, Chief."
                self.speak_requested.emit(response_str)
                self.memory.add_conversation_message("friday", response_str)
                self.response_completed.emit(user_query, response_str)
                return
            elif intent_type == "forget_fact":
                self.memory.delete_fact(param)
                self.speak_requested.emit(speak_text)
                self.memory.add_conversation_message("friday", speak_text)
                self.response_completed.emit(user_query, speak_text)
                return
            elif intent_type == "get_profile":
                facts = self.memory.get_all_facts()
                if facts:
                    fact_list = ", ".join([f["fact"] for f in facts])
                    response_str = f"Here is what I have archived: {fact_list}."
                else:
                    response_str = "No profile matrices logged yet, Chief."
                self.speak_requested.emit(response_str)
                self.memory.add_conversation_message("friday", response_str)
                self.response_completed.emit(user_query, response_str)
                return
            elif intent_type == "clear_memory":
                self.memory.clear_all_memory()
                self.speak_requested.emit(speak_text)
                self.memory.add_conversation_message("friday", speak_text)
                self.response_completed.emit(user_query, speak_text)
                return
            elif intent_type == "system_status":
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                status_msg = f"Systems are nominal, Chief. CPU is at {cpu} percent. Memory is at {ram} percent."
                self.speak_requested.emit(status_msg)
                self.memory.add_conversation_message("friday", status_msg)
                self.response_completed.emit(user_query, status_msg)
                return
        # No local command match. Use Ollama first, Gemini fallback
        logger.info("Brain: Forwarding query to AI engine...")
        friday_response = None

        # 1. Retrieve conversation history
        chat_history = self.memory.get_conversation_history(limit=10)

        # 2. Inject memory facts into system instructions
        context = SYSTEM_INSTRUCTIONS
        facts = self.memory.get_all_facts()
        if facts:
            facts_str = "\n".join([f"- {f['fact']} (Category: {f['category']})" for f in facts[:10]])
            context += f"\n\nKnown Facts about the Chief/User:\n{facts_str}"

        try:
            logger.info("Brain: Using Ollama provider")
            friday_response = ask_friday(user_query, system_prompt=context, chat_history=chat_history)
            self._current_model = "Ollama (qwen2.5-coder:latest)"
        except Exception as ollama_error:
            logger.warning(f"Brain: Ollama unavailable. Falling back to Gemini. Error: {ollama_error}")
            if self.llm.api_key:
                self._current_model = f"Gemini ({self.llm.model})"
            else:
                self._current_model = "Offline Rule-Based"
            try:
                friday_response = self.llm.generate_response(user_query, chat_history)
            except Exception as gemini_error:
                logger.error(f"Brain: Gemini also failed. Error: {gemini_error}")
                self._current_model = "Offline Rule-Based"
                friday_response = ("Chief, I am unable to connect to either the local AI model or the cloud AI service.")
        # Parse embedded tool blocks
        try:
            self.parse_and_execute_tools(friday_response)
        except Exception as tool_error:
            logger.error(f"Brain Tool Engine Error: {tool_error}")
        # Save response
        self.memory.add_conversation_message("friday", friday_response)
        # Speak response
        clean_speech = self.clean_json_from_response(friday_response)
        self.speak_requested.emit(clean_speech)
        # Update UI
        self.response_completed.emit(user_query, friday_response)

    def parse_and_execute_tools(self, response_text):
        """Searches for json markdown blocks and runs corresponding launcher commands."""
        json_blocks = re.findall(r"```json\s*(.*?)\s*```", response_text, re.DOTALL)
        for block in json_blocks:
            try:
                action_data = json.loads(block.strip())
                action = action_data.get("action", "").lower().strip()
                param = action_data.get("param", "")
                logger.info(f"Brain Tool Engine: Executing tool call: {action} with param: {param}")
                if action == "launch_app":
                    app_launcher.launch_application(param)
                elif action == "open_url":
                    browser_controller.open_url(param)
                elif action == "execute_workflow":
                    self.workflow_trigger.emit(param)
            except Exception as e:
                logger.error(f"Brain Tool Engine: Failed to parse action block: {block}. Error: {e}")

    def clean_json_from_response(self, text):
        """Removes the JSON block and internal log tags from text so TTS reads clean sentences."""
        text = re.sub(r"```json\s*.*?\s*```", "", text, flags=re.DOTALL)
        text = re.sub(r"\[.*?\]", "", text)
        text = text.strip()
        if not text.lower().startswith("chief"):
            text = f"Chief, {text[0].lower() + text[1:] if text else ''}"
        return text

    def get_active_model(self) -> str:
        """Return the name of the currently active AI model for HUD display."""
        return getattr(self, "_current_model", "N/A")

    def get_active_voice(self) -> str:
        """Return the name of the currently active voice engine for HUD display."""
        return getattr(self, "_current_voice", "N/A")

    def get_active_workflow(self) -> str:
        """Return the name of the running workflow for HUD display."""
        return getattr(self, "_current_workflow", "N/A")
