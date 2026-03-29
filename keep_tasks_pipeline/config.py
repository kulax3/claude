"""Configuration constants for the Keep/Tasks pipeline."""

import os

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "knowledge_base.db")
CREDENTIALS_PATH = os.path.join(DATA_DIR, "google_credentials.json")
TOKEN_PATH = os.path.join(DATA_DIR, "google_token.json")

# --- Google OAuth scopes ---
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/tasks.readonly",
]

# --- Claude model ---
CLAUDE_MODEL = "claude-haiku-4-5-20251001"   # cheapest; override with env var CLAUDE_MODEL

# --- Pipeline ---
BATCH_SIZE = 10   # items processed per AI batch call

# --- Categories ---
DEFAULT_CATEGORIES = [
    "仕事・業務",
    "学習・勉強",
    "アイデア・企画",
    "買い物・TODO",
    "健康・生活",
    "エンタメ・趣味",
    "読書・記事",
    "技術・IT",
    "その他",
]

os.makedirs(DATA_DIR, exist_ok=True)
