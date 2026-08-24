import os, sqlite3, threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Keep Render alive
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "Bot Live"
threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=10000)).start()

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
DB = "pyq.db"

def seed():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS pyqs (id INTEGER PRIMARY KEY, exam TEXT, question TEXT, options TEXT, answer TEXT)")
    if c.execute("SELECT COUNT(*) FROM pyqs WHERE exam='OPSC'").fetchone()[0] == 0:
        print("SEEDING 1000 OPSC...")
        for i in range(1000):
            c.execute("INSERT INTO pyqs (exam,question,options,answer) VALUES (?,?,?,?)",
                      ("OPSC", f"[OPSC] Q{i+1}: Sample PYQ {i+1} for OPSC?", "A) One | B) Two | C) Three | D) Four", "A"))
            c.execute("INSERT INTO pyqs (exam,question,options,answer) VALUES (?,?,?,?)",
                      ("Odisha Police", f"[Odisha Police] Q{i+1}: Sample PYQ?", "A) One | B) Two | C) Three | D) Four", "A"))
        conn.commit()
    conn.close()
seed()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("OPSC", callback_data="OPSC")],[InlineKeyboardButton("Odisha Police", callback_data="Odisha Police")],[InlineKeyboardButton("Railway", callback_data="Railway")],[InlineKeyboardButton("UPSC", callback_data="UPSC")]]
    await update.message.reply_text("Select Exam:", reply_markup=InlineKeyboardMarkup(kb))

async def btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    exam = q.data if q.data!= "NEXT" else context.user_data.get("exam")
    idx = context.user_data.get("idx",0)
    if q.data!= "NEXT":
        idx=0
        context.user_data["exam"]=exam
        await q.message.reply_text(f"✅ Exam set: {exam}")
    else:
        idx+=1
    context.user_data["idx"]=idx
    conn = sqlite3.connect(DB)
    row = conn.execute("SELECT question, options FROM pyqs WHERE exam=? LIMIT 1 OFFSET?", (exam, idx)).fetchone()
    conn.close()
    if not row:
        await q.message.reply_text(f"No more Qs for {exam}")
    else:
        await q.message.reply_text(f"{row[0]}\n{row[1]}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➡️ Next PYQ", callback_data="NEXT")]]))

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(btn))
app.run_polling()
