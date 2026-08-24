from telegram import InlineKeyboardButton, InlineKeyboardMarkup

MAIN_CATS = ["SSC", "Banking", "Railway", "UPSC", "UPPSC RO/ARO", "AHC RO/ARO", "UPSSSC", "State Exams"]

STATES = ["Uttar Pradesh", "Madhya Pradesh", "Bihar", "Rajasthan", "Delhi", "Haryana", "Maharashtra", "Gujarat", "West Bengal", "Uttarakhand", "Punjab", "Jharkhand", "Chhattisgarh", "Odisha", "Kerala", "Karnataka", "Tamil Nadu", "Andhra Pradesh", "Telangana", "Assam", "Himachal Pradesh"]

STATE_EXAMS = {
    "Uttar Pradesh": ["UPPSC RO/ARO", "UPPSC PCS Pre", "UPSSSC PET", "UPSSSC VDO", "Lekhpal", "UP Police", "AHC RO/ARO"],
    "Madhya Pradesh": ["MPPSC", "MP Police", "MP Patwari", "MP Vyapam"],
    "Bihar": ["BPSC", "Bihar Police", "Bihar SSC"],
    "Rajasthan": ["RPSC RAS", "Rajasthan Police", "Rajasthan Patwari", "REET"],
    "Delhi": ["DSSSB", "Delhi Police"],
    "Haryana": ["HPSC", "Haryana Police", "HSSC CET"],
    "Maharashtra": ["MPSC", "Maharashtra Police"],
    "Gujarat": ["GPSC", "Gujarat Police"],
    "West Bengal": ["WBPSC", "West Bengal Police"],
    "Uttarakhand": ["UKPSC", "Uttarakhand Police"],
    "Punjab": ["PPSC", "Punjab Police"],
    "Jharkhand": ["JPSC", "Jharkhand Police"],
    "Chhattisgarh": ["CGPSC", "CG Police"],
    "Odisha": ["OPSC", "Odisha Police"],
    "Kerala": ["KPSC", "Kerala Police"],
    "Karnataka": ["KPSC", "Karnataka Police"],
    "Tamil Nadu": ["TNPSC", "TN Police"],
    "Andhra Pradesh": ["APPSC", "AP Police"],
    "Telangana": ["TSPSC", "Telangana Police"],
    "Assam": ["APSC", "Assam Police"],
    "Himachal Pradesh": ["HPPSC", "HP Police"]
}

SUB_CATS = {
    "SSC": ["SSC CGL", "SSC CHSL", "SSC MTS", "SSC GD", "SSC CPO", "SSC Stenographer"],
    "Banking": ["IBPS PO", "IBPS Clerk", "SBI PO", "SBI Clerk", "RBI Grade B", "IBPS RRB"],
    "Railway": ["RRB NTPC", "RRB Group D", "RRB JE", "RRB ALP", "RPF SI"],
    "UPSC": ["UPSC Prelims", "UPSC Mains", "UPSC Optional"],
    "UPPSC RO/ARO": ["1990-2006 Papers", "2007-2023 Papers", "Full Mock Test", "8300 Qs Chapter-wise"],
    "AHC RO/ARO": ["8300 Chapter-wise Qs", "Full Mock Test", "Previous Year Papers"],
    "UPSSSC": ["UPSSSC PET", "VDO", "Lekhpal", "Junior Assistant", "Forest Guard"]
}

YEARS = ["2024", "2023", "2022", "2021", "2020", "2019"]

def main_menu():
    buttons = [[InlineKeyboardButton(cat, callback_data=f"cat_{cat}")] for cat in MAIN_CATS]
    return InlineKeyboardMarkup(buttons)

def states_menu():
    buttons = [[InlineKeyboardButton(state, callback_data=f"state_{state}")] for state in STATES]
    buttons.append([InlineKeyboardButton("⬅️ Back to Main", callback_data="back_main")])
    return InlineKeyboardMarkup(buttons)

def state_exam_menu(state):
    exams = STATE_EXAMS.get(state, [])
    buttons = [[InlineKeyboardButton(exam, callback_data=f"sexam_{state}_{exam}")] for exam in exams]
    buttons.append([InlineKeyboardButton("⬅️ Back to States", callback_data="cat_State Exams")])
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
