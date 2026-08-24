

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

MAIN_CATS = {
    "SSC": ["SSC CGL", "SSC CHSL", "SSC MTS", "SSC GD", "SSC CPO", "SSC Stenographer"],
    "Banking": ["IBPS PO", "IBPS Clerk", "SBI PO", "SBI Clerk", "RBI Grade B", "IBPS RRB"],
    "Railway": ["RRB NTPC", "RRB Group D", "RRB JE", "RRB ALP", "RPF SI"],
    "UPSC": ["UPSC CSE", "UPSC CDS", "UPSC NDA", "UPSC CAPF"],
    "UPPSC RO/ARO": ["UPPSC RO/ARO 2024", "UPPSC RO/ARO 2023", "UPPSC RO/ARO 2021", "8300 Qs Chapter-wise"],
    "AHC RO/ARO": ["AHC RO/ARO 2024", "AHC RO/ARO 2023", "8300 Chapter-wise Qs"],
    "UPSSSC": ["UPSSSC PET", "VDO", "Lekhpal", "Junior Assistant", "Forest Guard"],
    "State Exams": []
}

STATES = ["Uttar Pradesh", "Madhya Pradesh", "Bihar", "Rajasthan", "Delhi", "Haryana", "Maharashtra", "Gujarat", "West Bengal", "Uttarakhand", "Punjab", "Jharkhand", "Chhattisgarh", "Odisha", "Kerala", "Karnataka", "Tamil Nadu", "Andhra Pradesh", "Telangana", "Assam", "Himachal Pradesh"]

STATE_EXAMS = {
    "Uttar Pradesh": ["UPPSC RO/ARO", "UPPSC PCS Pre", "UPSSSC PET", "UP Police", "AHC RO/ARO"],
    "Madhya Pradesh": ["MPPSC", "MP Police", "MP Patwari"],
    "Bihar": ["BPSC", "Bihar Police", "Bihar SSC"],
    "Rajasthan": ["RPSC RAS", "Rajasthan Police", "REET"],
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

def main_keyboard():
    kb = [[InlineKeyboardButton(cat, callback_data=f"cat_{cat}")] for cat in MAIN_CATS.keys()]
    return InlineKeyboardMarkup(kb)

def states_menu():
    kb = [[InlineKeyboardButton(s, callback_data=f"state_{s}")] for s in STATES]
    kb.append([InlineKeyboardButton("⬅️ Back", callback_data="back_main")])
    return InlineKeyboardMarkup(kb)

def state_exam_menu(state):
    exams = STATE_EXAMS.get(state, [])
    kb = [[InlineKeyboardButton(e, callback_data=f"exam_{e}")] for e in exams]
    kb.append([InlineKeyboardButton("⬅️ Back to States", callback_data="back_states")])
    kb.append([InlineKeyboardButton("🏠 Main Menu", callback_data="back_main")])
    return InlineKeyboardMarkup(kb)

def category_exam_menu(cat):
    exams = MAIN_CATS.get(cat, [])
    kb = [[InlineKeyboardButton(e, callback_data=f"exam_{e}")] for e in exams]
    kb.append([InlineKeyboardButton("⬅️ Back", callback_data="back_main")])
    return InlineKeyboardMarkup(kb)
