from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Main Categories - you can edit these names
# Main Categories
MAIN_CATS = ["SSC", "Banking", "Railway", "UPSC", "State Exams"]
SUB_CATS = {
    "SSC": ["CGL", "CHSL", "MTS", "GD", "CPO"],
    "Banking": ["PO", "Clerk", "SO"],
    "Railway": ["Group D", "NTPC", "ALP"],
    "UPSC": ["Prelims", "Mains"],
    "State Exams": ["UP Police", "UPPSC", "BPSC", "MPPSC", "Rajasthan", "Haryana", "Bihar Police", "UPSSSC"]
}

def main_menu():
    buttons = [[InlineKeyboardButton(cat, callback_data=f"cat_{cat}")] for cat in MAIN_CATS]
    return InlineKeyboardMarkup(buttons)

def sub_menu(category):
    subs = SUB_CATS.get(category, [])
    buttons = [[InlineKeyboardButton(sub, callback_data=f"sub_{category}_{sub}")] for sub in subs]
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)

def year_menu(category, sub_category):
    # We will show 2024 to 2018 by default
    years = ["2024", "2023", "2022", "2021", "2020", "2019"]
    buttons = [[InlineKeyboardButton(y, callback_data=f"year_{category}_{sub_category}_{y}")] for y in years]
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data=f"cat_{category}")])
    return InlineKeyboardMarkup(buttons)