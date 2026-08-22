from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv
import sqlite3, os

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))


conn = sqlite3.connect("pyq.db", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, exam TEXT)")
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("SSC", callback_data="cat_SSC")],
        [InlineKeyboardButton("Banking", callback_data="cat_Banking")],
        [InlineKeyboardButton("Railway", callback_data="cat_Railway")],
    ]
    await update.message.reply_text("🇮🇳 Welcome! Select Exam Category:", reply_markup=InlineKeyboardMarkup(keyboard))

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "cat_SSC":
        keyboard = [[InlineKeyboardButton("SSC CGL", callback_data="exam_SSC CGL")],[InlineKeyboardButton("SSC CHSL", callback_data="exam_SSC CHSL")]]
        await q.edit_message_text("Select SSC Exam:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif q.data.startswith("exam_"):
        exam = q.data.replace("exam_", "")
        cur.execute("INSERT OR REPLACE INTO users VALUES (?,?)", (q.from_user.id, exam))
        conn.commit()
        await q.edit_message_text(f"✅ You selected: {exam}\n\nBot is working! Next we will add PYQs.")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
print("Bot is running... Go to Telegram and type /start")
app.run_polling()