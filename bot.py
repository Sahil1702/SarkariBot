from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
import sqlite3, os, threading

app_web = Flask(__name__)
@app_web.route('/')
def home(): return "SarkariBot ALL INDIA LIVE!"
threading.Thread(target=lambda: app_web.run(host="0.0.0.0", port=10000)).start()

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DB = "pyq.db"

# --- AUTO CREATE DB IF MISSING - FIX FOR OPSC ---
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS pyqs (id INTEGER PRIMARY KEY, exam TEXT, question TEXT, options TEXT, answer TEXT)")
    count = c.execute("SELECT COUNT(*) FROM pyqs WHERE exam='OPSC'").fetchone()[0]
    if count == 0:
        print("Seeding 8000 Qs...")
        c.execute("DELETE FROM pyqs")
        exams = ["OPSC","Odisha Police","Railway","UPSC","UPPSC RO/ARO","AHC RO/ARO","UPSSSC","Banking","SSC"]
        for exam in exams:
            for i in range(1000):
                c.execute("INSERT INTO pyqs (exam,question,options,answer) VALUES (?,?,?,?)",
                          (exam, f"[{exam}] Q{i+1}: Important PYQ {i+1} for {exam} exam? What is the correct answer?\n", "A) Option A\nB) Option B\nC) Option C\nD) Option D", "A"))
        conn.commit()
        print("Seeding Done!")
    conn.close()
init_db()

# --- BOT LOGIC ---
MAIN_KB = [
    [InlineKeyboardButton("Banking", callback_data="Banking")],
    [InlineKeyboardButton("Railway", callback_data="Railway")],
    [InlineKeyboardButton("UPSC", callback_data="UPSC")],
    [InlineKeyboardButton("UPPSC RO/ARO", callback_data="UPPSC RO/ARO")],
    [InlineKeyboardButton("AHC RO/ARO", callback_data="AHC RO/ARO")],
    [InlineKeyboardButton("UPSSSC", callback_data="UPSSSC")],
    [InlineKeyboardButton("State Exams", callback_data="State Exams")],
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Sarkari PYQ Helper! Select Exam:", reply_markup=InlineKeyboardMarkup(MAIN_KB))

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "State Exams":
        kb = [[InlineKeyboardButton("OPSC", callback_data="OPSC")],
              [InlineKeyboardButton("Odisha Police", callback_data="Odisha Police")]]
        await q.message.reply_text("Select Odisha Exam:", reply_markup=InlineKeyboardMarkup(kb))
        return

    if data == "NEXT":
        exam = context.user_data.get('exam', 'OPSC')
        idx = context.user_data.get('idx', 0) + 1
    else:
        exam = data
        idx = 0
        await q.message.reply_text(f"✅ Exam set: {exam}\nSending your first PYQ...")
        context.user_data['exam'] = exam

    context.user_data['idx'] = idx
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    row = c.execute("SELECT question, options, answer FROM pyqs WHERE exam=? LIMIT 1 OFFSET?", (exam, idx)).fetchone()
    conn.close()

    if not row:
        await q.message.reply_text(f"No more PYQs for {exam}. Restart /start")
        return

    ques, opts, ans = row
    await q.message.reply_text(f"{ques}\n{opts}\n\nAnswer: {ans}")
    await q.message.reply_text("Click for next", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➡️ Next PYQ", callback_data="NEXT")]]))

if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    print("Bot Started...")
    app.run_polling()
