import json
import logging
import os
import sqlite3
import threading
from pathlib import Path
from typing import Dict, List, Any

from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# =========================
# CONFIG
# =========================
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "pyq.db"
SEED_JSON_PATH = BASE_DIR / "pyq_seed.json"

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", "10000"))

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables.")

# =========================
# EXAM MASTER
# IMPORTANT:
# - Callback keys are short and stable
# - DB exam names come ONLY from this mapping
# =========================
EXAMS = {
    "banking": "Banking",
    "railway": "Railway",
    "upsc": "UPSC",
    "uppsc_ro_aro": "UPPSC RO/ARO",
    "ahc_ro_aro": "AHC RO/ARO",
    "upsssc": "UPSSSC",
    "opsc": "OPSC",
    "odisha_police": "Odisha Police",
}

MAIN_EXAM_KEYS = [
    "banking",
    "railway",
    "upsc",
    "uppsc_ro_aro",
    "ahc_ro_aro",
    "upsssc",
]

STATE_EXAM_KEYS = [
    "opsc",
    "odisha_police",
]

# =========================
# DEFAULT IN-FILE SEED DATA
# Replace these samples with your real PYQs
# OR better: create pyq_seed.json in the repo root
# =========================
SEED_DATA: Dict[str, List[Dict[str, Any]]] = {
    "Banking": [],
    "Railway": [],
    "UPSC": [],
    "UPPSC RO/ARO": [],
    "AHC RO/ARO": [],
    "UPSSSC": [],
    "OPSC": [
        {
            "question": "Sample OPSC PYQ 1 - Replace this with a real question.",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "A",
        }
    ],
    "Odisha Police": [
        {
            "question": "Sample Odisha Police PYQ 1 - Replace this with a real question.",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "A",
        }
    ],
}

# =========================
# FLASK KEEP-ALIVE FOR RENDER
# =========================
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Sarkari PYQ Bot is running.", 200

def run_flask():
    flask_app.run(host="0.0.0.0", port=PORT)

# =========================
# DATABASE HELPERS
# =========================
def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS pyqs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam TEXT NOT NULL,
                question TEXT NOT NULL,
                options TEXT NOT NULL,
                answer TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_pyqs_exam
            ON pyqs (exam)
        """)
        conn.commit()

def normalize_options(raw_options):
    if isinstance(raw_options, list):
        return [str(x).strip() for x in raw_options]

    if isinstance(raw_options, str):
        # support old pipe format: A|B|C|D
        if "|" in raw_options:
            return [x.strip() for x in raw_options.split("|")]
        # support JSON string list if present
        try:
            parsed = json.loads(raw_options)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed]
        except Exception:
            pass

    return []

def load_seed_data() -> Dict[str, List[Dict[str, Any]]]:
    """
    Priority:
    1) pyq_seed.json (recommended for real data)
    2) SEED_DATA in this file
    """
    data = {v: [] for v in EXAMS.values()}

    if SEED_JSON_PATH.exists():
        logger.info("Loading seed data from pyq_seed.json")
        with open(SEED_JSON_PATH, "r", encoding="utf-8") as f:
            file_data = json.load(f)

        if not isinstance(file_data, dict):
            raise ValueError("pyq_seed.json must be a dict: {exam_name: [questions...]}")

        for exam_name, items in file_data.items():
            if exam_name in data and isinstance(items, list):
                data[exam_name] = items
    else:
        logger.info("pyq_seed.json not found, using SEED_DATA inside bot.py")
        for exam_name, items in SEED_DATA.items():
            if exam_name in data and isinstance(items, list):
                data[exam_name] = items

    return data

def validate_and_prepare_questions(exam_name: str, items: List[Dict[str, Any]]):
    prepared = []

    for item in items:
        if not isinstance(item, dict):
            continue

        question = str(item.get("question", "")).strip()
        answer = str(item.get("answer", "")).strip()
        options = normalize_options(item.get("options", []))

        if not question or not options or not answer:
            continue

        prepared.append(
            (
                exam_name,
                question,
                json.dumps(options, ensure_ascii=False),
                answer,
            )
        )

    return prepared

def seed_database():
    """
    Self-healing seed:
    - compares DB count vs source count exam-wise
    - if mismatch, deletes that exam's rows and re-inserts fresh
    """
    source_data = load_seed_data()

    with get_conn() as conn:
        cur = conn.cursor()

        for exam_name, items in source_data.items():
            prepared = validate_and_prepare_questions(exam_name, items)
            desired_count = len(prepared)

            cur.execute("SELECT COUNT(*) FROM pyqs WHERE exam = ?", (exam_name,))
            current_count = cur.fetchone()[0]

            if desired_count == 0:
                logger.info("No seed data for %s, skipping.", exam_name)
                continue

            if current_count != desired_count:
                logger.info(
                    "Refreshing %s | current=%s desired=%s",
                    exam_name, current_count, desired_count
                )
                cur.execute("DELETE FROM pyqs WHERE exam = ?", (exam_name,))
                cur.executemany(
                    "INSERT INTO pyqs (exam, question, options, answer) VALUES (?, ?, ?, ?)",
                    prepared,
                )

        conn.commit()

def get_total_questions(exam_name: str) -> int:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM pyqs WHERE exam = ?", (exam_name,))
        return cur.fetchone()[0]

def get_question_by_offset(exam_name: str, offset: int):
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT question, options, answer
            FROM pyqs
            WHERE exam = ?
            ORDER BY id
            LIMIT 1 OFFSET ?
        """, (exam_name, offset))
        return cur.fetchone()

# =========================
# UI HELPERS
# =========================
def main_menu_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Banking", callback_data="exam|banking"),
            InlineKeyboardButton("Railway", callback_data="exam|railway"),
        ],
        [
            InlineKeyboardButton("UPSC", callback_data="exam|upsc"),
            InlineKeyboardButton("UPPSC RO/ARO", callback_data="exam|uppsc_ro_aro"),
        ],
        [
            InlineKeyboardButton("AHC RO/ARO", callback_data="exam|ahc_ro_aro"),
            InlineKeyboardButton("UPSSSC", callback_data="exam|upsssc"),
        ],
        [
            InlineKeyboardButton("State Exams", callback_data="menu|state"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def state_menu_markup() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("OPSC", callback_data="exam|opsc"),
            InlineKeyboardButton("Odisha Police", callback_data="exam|odisha_police"),
        ],
        [
            InlineKeyboardButton("⬅ Back", callback_data="menu|main"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def question_markup(exam_key: str, index: int, total: int) -> InlineKeyboardMarkup:
    buttons = []

    if index + 1 < total:
        buttons.append(
            [InlineKeyboardButton("Next ➡", callback_data=f"next|{exam_key}|{index + 1}")]
        )

    if exam_key in STATE_EXAM_KEYS:
        buttons.append([InlineKeyboardButton("⬅ State Exams", callback_data="menu|state")])
    else:
        buttons.append([InlineKeyboardButton("⬅ Main Menu", callback_data="menu|main")])

    return InlineKeyboardMarkup(buttons)

def format_question_text(exam_name: str, index: int, total: int, row) -> str:
    question, options_raw, answer = row

    try:
        options = json.loads(options_raw)
        if not isinstance(options, list):
            options = normalize_options(options_raw)
    except Exception:
        options = normalize_options(options_raw)

    option_lines = []
    for i, opt in enumerate(options):
        label = chr(65 + i) if i < 26 else f"Opt{i+1}"
        option_lines.append(f"{label}. {opt}")

    options_text = "\n".join(option_lines) if option_lines else "No options available"

    return (
        f"📘 {exam_name}\n"
        f"🧾 Question {index + 1} of {total}\n\n"
        f"{question}\n\n"
        f"{options_text}\n\n"
        f"✅ Answer: {answer}"
    )

async def send_exam_question(query, exam_key: str, index: int):
    exam_name = EXAMS[exam_key]
    total = get_total_questions(exam_name)

    if total == 0:
        text = f"⚠ No PYQs available yet for {exam_name}."
        markup = state_menu_markup() if exam_key in STATE_EXAM_KEYS else main_menu_markup()
        await query.edit_message_text(text=text, reply_markup=markup)
        return

    if index < 0:
        index = 0
    if index >= total:
        index = total - 1

    row = get_question_by_offset(exam_name, index)
    if not row:
        text = f"⚠ Could not load question for {exam_name}."
        markup = state_menu_markup() if exam_key in STATE_EXAM_KEYS else main_menu_markup()
        await query.edit_message_text(text=text, reply_markup=markup)
        return

    text = format_question_text(exam_name, index, total, row)
    await query.edit_message_text(
        text=text,
        reply_markup=question_markup(exam_key, index, total),
    )

# =========================
# TELEGRAM HANDLERS
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Sarkari PYQ Helper.\n\nChoose an exam:",
        reply_markup=main_menu_markup(),
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data or ""
    parts = data.split("|")

    try:
        action = parts[0]

        if action == "menu":
            target = parts[1]

            if target == "main":
                await query.edit_message_text(
                    text="Choose an exam:",
                    reply_markup=main_menu_markup(),
                )
                return

            if target == "state":
                await query.edit_message_text(
                    text="Choose a state exam:",
                    reply_markup=state_menu_markup(),
                )
                return

        elif action == "exam":
            exam_key = parts[1]
            if exam_key not in EXAMS:
                await query.edit_message_text("Invalid exam selected.")
                return
            await send_exam_question(query, exam_key, 0)
            return

        elif action == "next":
            exam_key = parts[1]
            index = int(parts[2])

            if exam_key not in EXAMS:
                await query.edit_message_text("Invalid exam selected.")
                return

            await send_exam_question(query, exam_key, index)
            return

        await query.edit_message_text("Unknown action.")
    except Exception as e:
        logger.exception("Callback error: %s", e)
        await query.edit_message_text("Something went wrong. Please type /start again.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.exception("Unhandled exception: %s", context.error)

# =========================
# MAIN
# =========================
def main():
    init_db()
    seed_database()

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_error_handler(error_handler)

    logger.info("Bot is starting...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

