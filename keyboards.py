from telegram import InlineKeyboardButton, InlineKeyboardMarkup

MAIN_CATS = ["SSC", "Banking", "Railway", "UPSC", "State Exams"]

SUB_CATS = {
    "SSC": ["SSC CGL", "SSC CHSL", "SSC MTS", "SSC GD"],
    "Banking": ["IBPS PO", "IBPS Clerk", "SBI PO", "SBI Clerk"],
    "Railway": ["RRB NTPC", "RRB Group D", "RRB JE"],
    "UPSC": ["UPSC Prelims", "UPSC Mains"],
    "State Exams": ["UP Police", "UPPSC", "MPPSC", "BPSC"]
}

YEARS = ["2024", "2023", "2022", "2021", "2020"]

def main_menu():
    buttons = [[InlineKeyboardButton(cat, callback_data=f"cat_{cat}")] for cat in MAIN_CATS]
    return InlineKeyboardMarkup(buttons)

def sub_menu(cat):
    subs = SUB_CATS.get(cat, [])
    buttons = [[InlineKeyboardButton(s, callback_data=f"sub_{cat}_{s}")] for s in subs]
    buttons.append([InlineKeyboardButton("⬅️ Back to Main", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)

def year_menu(cat, sub):
    buttons = [[InlineKeyboardButton(y, callback_data=f"year_{cat}_{sub}_{y}")] for y in YEARS]
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f"cat_{cat}")])
    return InlineKeyboardMarkup(buttons)