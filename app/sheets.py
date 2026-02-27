import gspread
from app.config import GOOGLE_CREDS_PATH, SHEET_ID

gc = gspread.service_account(filename=GOOGLE_CREDS_PATH)
sh = gc.open_by_key(SHEET_ID)
ws = sh.worksheet("responses")

def append_row(row):
    ws.append_row(row)

def get_all_rows():
    return ws.get_all_records()