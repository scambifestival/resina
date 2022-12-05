import sqlite3
from utils import *
from dataclasses import dataclass

from utils import _reply


@dataclass
class Connection:
    session: sqlite3.Connection
    cursor: sqlite3.dbapi2.Cursor


def connect():
    con = Connection
    con.session = sqlite3.connect("database/usernames.db")
    con.cursor = con.session.cursor()
    return con


def user_in_db(update: Update, context: CallbackContext):
    conn = sqlite3.connect("database/usernames.db")
    conn.cursor()
    keyboard = [
        [InlineKeyboardButton("⬅ Back to main menu", callback_data="start_over")],
        [InlineKeyboardButton("❌ Stop the bot", callback_data="stop")]
    ]
    try:
        res = conn.execute(
            "SELECT USERNAME FROM USER_RECORD WHERE USERNAME = '" + update.callback_query.from_user.username + "'")
    except sqlite3.OperationalError:
        _reply(update, context, text="Something went wrong while doing the necessary checks with the DB.\n"
                                     "Please contact the staff about this.",
               reply_markup=InlineKeyboardMarkup(keyboard))

    return res
