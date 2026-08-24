from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Poll
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
import sqlite3, os, threading
import keyboards

app_web = Flask(__name__)
@app_web.route('/')
def home(): return "SarkariBot ALL INDIA LIVE!"
threading.Thread(target=lambda: app_web.run(host="0.0.0.0", port=10000)).start()

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

conn = sqlite3.connect("pyq.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, exam TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS pyqs (id INTEGER PRIMARY KEY AUTOINCREMENT, exam TEXT, question TEXT, opt1 TEXT, opt2 TEXT, opt3 TEXT, opt4 TEXT, correct INTEGER, explanation TEXT)")
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🇮🇳 Welcome! Select Exam Category:", reply_markup=keyboards.main_keyboard())

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
        await q.edit_message_text("🇮🇳 Welcome! Select Exam Category:", reply_markup=keyboards.main_keyboard())
        return

    if q.data == "back_states":
        await q.edit_message_text("📍 Select Your State (21 States):", reply_markup=keyboards.states_menu())
        return

    if q.data.startswith("cat_"):
        cat = q.data.replace("cat_", "")
        if cat == "State Exams":
            await q.edit_message_text("📍 Select Your State (21 States):", reply_markup=keyboards.states_menu())
        else:
            await q.edit_message_text(f"Select {cat} Exam:", reply_markup=keyboards.category_exam_menu(cat))
        return

    if q.data.startswith("state_"):
        state = q.data.replace("state_", "")
        await q.edit_message_text(f"📍 {state} - Select Exam:", reply_markup=keyboards.state_exam_menu(state))
        return

    if q.data.startswith("exam_"):
        exam = q.data.replace("exam_", "")
        cur.execute("INSERT OR REPLACE INTO users VALUES (?,?)", (q.from_user.id, exam))
        conn.commit()
        await q.edit_message_text(f"✅ Exam set: {exam}\nSending your first PYQ...")
        await send_random_pyq(q.from_user.id, exam, context.application)
        await context.application.bot.send_message(chat_id=q.from_user.id, text="Click for next", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➡️ Next PYQ", callback_data="next")]]))
        return

    if q.data == "next":
        cur.execute("SELECT exam FROM users WHERE user_id=?", (q.from_user.id,))
        r = cur.fetchone()
        if r:
            await send_random_pyq(q.from_user.id, r[0], context.application)
        else:
            await q.edit_message_text("First do /start")

async def add_pyq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        await update.message.reply_text("❌ Not Admin!")
        return
    try:
        text = update.message.text.replace("/add ", "")
        parts = [p.strip() for p in text.split("|")]
        exam, ques, o1, o2, o3, o4, correct, exp = parts
        cur.execute("INSERT INTO pyqs (exam, question, opt1, opt2, opt3, opt4, correct, explanation) VALUES (?,?,?,?,?,?,?,?)",
                    (exam, ques, o1, o2, o3, o4, int(correct), exp))
        conn.commit()
        await update.message.reply_text(f"✅ Added to {exam}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def next_q(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cur.execute("SELECT exam FROM users WHERE user_id=?", (update.effective_user.id,))
    r = cur.fetchone()
    if r:
        await send_random_pyq(update.effective_user.id, r[0], context.application)
    else:
        await update.message.reply_text("First do /start")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("add", add_pyq))
app.add_handler(CommandHandler("next", next_q))
app.add_handler(CallbackQueryHandler(buttons))

if __name__ == "__main__":
    app.run_polling()
