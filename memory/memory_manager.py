import sqlite3
import os
import config
from utils import logger
from datetime import datetime
from enum import Enum

class MemoryCategory(Enum):
    PERSONAL = "personal"
    PROJECT = "project"
    PREFERENCE = "preference"
    GOAL = "goal"
    TASK = "task"
    GENERAL = "general"

class MemoryManager:
    def __init__(self):
        self.db_path = config.DB_PATH
        self.initialize_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_db(self):
        """Creates database schema if it doesn't already exist."""
        logger.info(f"Initializing SQLite Memory Database at {self.db_path}")
        conn = self.get_connection()
        cursor = conn.cursor()

        # Conversation Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT,
                message TEXT
            )
        """)

        # User Profile Table (Key-Value Preferences)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profile (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Long-Term Facts Database
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact_text TEXT UNIQUE,
                category TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Seed default profile preferences if empty
        cursor.execute("SELECT COUNT(*) FROM profile")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO profile (key, value) VALUES (?, ?)", ("username", config.USER_NAME))
            cursor.execute("INSERT INTO profile (key, value) VALUES (?, ?)", ("preferred_editor", "VS Code"))
            cursor.execute("INSERT INTO profile (key, value) VALUES (?, ?)", ("theme", "dark_hud"))
            conn.commit()

        conn.commit()
        conn.close()
        logger.info("Memory DB initialization complete.")

    # ==================== CONVERSATION LOGS ====================
    def add_conversation_message(self, role, message):
        """Saves a conversation message (user or FRIDAY) to the logs."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO conversations (role, message) VALUES (?, ?)",
                (role, message)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to save message to memory: {e}")

    def get_conversation_history(self, limit=50):
        """Fetches recent conversation messages."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, message, timestamp FROM conversations ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            conn.close()
            # Return in chronological order
            return [{"role": r["role"], "message": r["message"], "timestamp": r["timestamp"]} for r in reversed(rows)]
        except Exception as e:
            logger.error(f"Failed to fetch conversation history: {e}")
            return []

    # ==================== USER PROFILE / PREFERENCES ====================
    def get_profile_value(self, key, default=None):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM profile WHERE key = ?", (key,))
            row = cursor.fetchone()
            conn.close()
            return row["value"] if row else default
        except Exception as e:
            logger.error(f"Failed to read profile key {key}: {e}")
            return default

    def set_profile_value(self, key, value):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO profile (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP",
                (key, str(value))
            )
            conn.commit()
            conn.close()
            logger.info(f"Memory update: {key} -> {value}")
        except Exception as e:
            logger.error(f"Failed to write profile key {key}: {e}")

    def get_all_profile_settings(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM profile")
            rows = cursor.fetchall()
            conn.close()
            return {r["key"]: r["value"] for r in rows}
        except Exception as e:
            logger.error(f"Failed to load profile settings: {e}")
            return {}

    # ==================== LONG-TERM FACTS ====================
    def add_fact(self, fact_text, category=None):
        """Saves a learned fact about the user or preferences with a category."""
        if not category:
            text_lower = fact_text.lower()
            if any(word in text_lower for word in ["project", "build", "code"]):
                category = MemoryCategory.PROJECT.value
            elif any(word in text_lower for word in ["want", "like", "prefer", "don't like"]):
                category = MemoryCategory.PREFERENCE.value
            elif any(word in text_lower for word in ["goal", "aim", "target"]):
                category = MemoryCategory.GOAL.value
            elif any(word in text_lower for word in ["todo", "task", "assignment"]):
                category = MemoryCategory.TASK.value
            else:
                category = MemoryCategory.GENERAL.value

        try:
            # Validate category
            if category not in [c.value for c in MemoryCategory]:
                logger.warning(f"Invalid memory category '{category}'. Falling back to 'general'.")
                category = MemoryCategory.GENERAL.value
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO facts (fact_text, category) VALUES (?, ?)",
                (fact_text.strip(), category)
            )
            conn.commit()
            conn.close()
            logger.info(f"Learned new fact: '{fact_text}' under '{category}'")
        except Exception as e:
            logger.error(f"Failed to learn fact: {e}")

    def get_all_facts(self):
        """Return all facts across categories (used by legacy UI)."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT fact_text, category, created_at FROM facts ORDER BY created_at DESC")
            rows = cursor.fetchall()
            conn.close()
            return [{"fact": r["fact_text"], "category": r["category"], "date": r["created_at"]} for r in rows]
        except Exception as e:
            logger.error(f"Failed to load facts: {e}")
            return []

    def get_facts_by_category(self, category):
        """Return facts for a specific category."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT fact_text, category, created_at FROM facts WHERE category = ? ORDER BY created_at DESC",
                (category,)
            )
            rows = cursor.fetchall()
            conn.close()
            return [{"fact": r["fact_text"], "category": r["category"], "date": r["created_at"]} for r in rows]
        except Exception as e:
            logger.error(f"Failed to load facts for category {category}: {e}")
            return []

    def search_facts(self, keyword):
        """Search facts containing the keyword across all categories."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            pattern = f"%{keyword}%"
            cursor.execute(
                "SELECT fact_text, category, created_at FROM facts WHERE fact_text LIKE ? ORDER BY created_at DESC",
                (pattern,)
            )
            rows = cursor.fetchall()
            conn.close()
            return [{"fact": r["fact_text"], "category": r["category"], "date": r["created_at"]} for r in rows]
        except Exception as e:
            logger.error(f"Failed to search facts with keyword {keyword}: {e}")
            return []

    def delete_fact(self, fact_text):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM facts WHERE fact_text = ?", (fact_text,))
            conn.commit()
            conn.close()
            logger.info(f"Forgotten fact: '{fact_text}'")
        except Exception as e:
            logger.error(f"Failed to delete fact: {e}")

    def clear_all_memory(self):
        """Purges tables completely."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations")
            cursor.execute("DELETE FROM facts")
            cursor.execute("DELETE FROM profile WHERE key != 'username'")
            conn.commit()
            conn.close()
            logger.warn("Memory database has been purged by user.")
        except Exception as e:
            logger.error(f"Failed to purge memory: {e}")
