from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Poll
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
import sqlite3, os, threading

app_web = Flask(__name__)
@app_web.route('/')
def home(): return "SarkariBot 5 Category Live!"
threading.Thread(target=lambda: app_web.run(host="0.0.0.0", port=10000)).start()

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

conn = sqlite3.connect("pyq.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, exam TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS pyqs (id INTEGER PRIMARY KEY AUTOINCREMENT, exam TEXT, question TEXT, opt1 TEXT, opt2 TEXT, opt3 TEXT, opt4 TEXT, correct INTEGER, explanation TEXT)")
conn.commit()

# MAIN CATEGORIES - 5 BUTTONS
MAIN_CATS = {
    "SSC": ["SSC CGL", "SSC CHSL", "SSC MTS", "SSC GD"],
    "Banking": ["IBPS PO", "IBPS Clerk", "SBI PO", "SBI Clerk"],
    "Railway": ["RRB NTPC", "RRB Group D", "RRB JE"],
    "UPSC": ["UPSC CSE", "UPSC CDS", "UPSC NDA", "UPSC CAPF"],
    "State Exams": ["UPPSC", "BPSC", "MPSC", "RPSC", "MPPSC"]
}

def main_keyboard():
    kb = [[InlineKeyboardButton(cat, callback_data=f"cat_{cat}")] for cat in MAIN_CATS.keys()]
    return InlineKeyboardMarkup(kb)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🇮🇳 Welcome! Select Exam Category:", reply_markup=main_keyboard())

async def send_random_pyq(chat_id, exam, app):
    cur.execute("SELECT * FROM pyqs WHERE exam=? ORDER BY RANDOM() LIMIT 1", (exam,))
    row = cur.fetchone()
    if not row:
        await app.bot.send_message(chat_id=chat_id, text=f"No PYQs yet for {exam}. Admin add via /add")
        return
    _, _, q, o1, o2, o3, o4, correct, exp = row
    await app.bot.send_poll(
        chat_id=chat_id,
        question=f"[{exam}] {q}"[:300],
        options=[o1, o2, o3, o4],
        type=Poll.QUIZ,
        correct_option_id=correct,
        explanation=exp[:200] if exp else None,
        is_anonymous=False
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data == "back_main":
        await q.edit_message_text("🇮🇳 Welcome! Select Exam Category:", reply_markup=main_keyboard())
        return

    if q.data.startswith("cat_"):
        cat = q.data.replace("cat_", "")
        exams = MAIN_CATS.get(cat, [])
        keyboard = [[InlineKeyboardButton(e, callback_data=f"exam_{e}")] for e in exams]
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back_main")])
        await q.edit_message_text(f"Select {cat} Exam:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if q.data.startswith("exam_"):
        exam = q.data.replace("exam_", "")
        cur.execute("INSERT OR REPLACE INTO users VALUES (?,?)", (q.from_user.id, exam))
        conn.commit()
        await q.edit_message_text(f"✅ Exam set: {exam}\nSending your first PYQ...")
        await send_random_pyq(q.from_user.id, exam, context.application)
        # Add Next button after
        await context.application.bot.send_message(chat_id=q.from_user.id, text="Click /next for next question", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➡️ Next PYQ", callback_data="next")]]))

    if q.data == "next":
        cur.execute("SELECT exam FROM users WHERE user_id=?", (q.from_user.id,))
        r = cur.fetchone()
        if r:
            await send_random_pyq(q.from_user.id, r[0], context.application)
        else:
            await q.edit_message_text("First do /start")

async def add_pyq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        await update.message.reply_text("❌ You are not Admin!")
        return
    try:
        text = update.message.text.replace("/add ", "")
        parts = [p.strip() for p in text.split("|")]
        exam, ques, o1, o2, o3, o4, correct, exp = parts
        cur.execute("INSERT INTO pyqs (exam, question, opt1, opt2, opt3, opt4, correct, explanation) VALUES (?,?,?,?,?,?,?,?)",
                    (exam, ques, o1, o2, o3, o4, int(correct), exp))
        conn.commit()
        await update.message.reply_text(f"✅ Added to {exam}: {ques}")
    except Exception as e:
        await update.message.reply_text(f"❌ Format:\n/add Exam | Question | Opt1 | Opt2 | Opt3 | Opt4 | Correct(0-3) | Explanation\nError: {e}")

async def next_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cur.execute("SELECT exam FROM users WHERE user_id=?", (update.effective_user.id,))
    r = cur.fetchone()
    if r:
        await send_random_pyq(update.effective_user.id, r[0], context.application)
    else:
        await update.message.reply_text("First do /start and select exam")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add_pyq))
app.add_handler(CommandHandler("next", next_q))
app.add_handler(CallbackQueryHandler(buttons))
print("5-CATEGORY FORWARD BOT RUNNING...")
app.run_polling()