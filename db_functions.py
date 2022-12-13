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


# noinspection PyUnboundLocalVariable
def user_in_db(update: Update, context: CallbackContext):
    conn = connect()
    c = conn.cursor

    try:
        res = c.execute(
            "SELECT username FROM INSCRIPTION_USERS_STATUS WHERE username = '" +
            update.callback_query.from_user.username + "'")
    except sqlite3.OperationalError:
        keyboard = [
            [InlineKeyboardButton("⬅ Back to main menu", callback_data="start_over")],
            [InlineKeyboardButton("❌ Stop the bot", callback_data="stop")]
        ]
        _reply(update, context, text="Something went wrong while doing the necessary checks with the DB.\n"
                                     "Please contact the staff about this.",
               reply_markup=InlineKeyboardMarkup(keyboard))
        return None

    return res


async def add_user(update: Update, context: CallbackContext):
    conn = connect()
    c = conn.cursor
    keyboard = [
        [InlineKeyboardButton("⬅ Back to main menu", callback_data="start_over")],
        [InlineKeyboardButton("❌ Stop the bot", callback_data="stop")]
    ]
    # Lo stato è necessariamente quello iniziale (str(INSCRIPTION) = 0)
    try:
        c.execute(
            "INSERT INTO INSCRIPTION_USERS_STATUS VALUES ('" + update.callback_query.from_user.username + "', '0')"
        )
    except sqlite3.OperationalError:
        await _reply(update, context, text="Something went wrong while doing the necessary checks with the DB.\n"
                                           "Please contact the staff about this.",
                     reply_markup=InlineKeyboardMarkup(keyboard))
    conn.session.commit()
    conn.session.close()


async def update_subscription_user_status(update: Update, context: CallbackContext):
    conn = connect()
    keyboard = [
        [InlineKeyboardButton("⬅ Back to main menu", callback_data="start_over")],
        [InlineKeyboardButton("❌ Stop the bot", callback_data="stop")]
    ]
    try:
        conn.cursor.execute(
            "UPDATE INSCRIPTION_USERS_STATUS SET status = '" + update.callback_query.data +
            "' WHERE username = '" + update.callback_query.from_user.username + "'"
        )
    except sqlite3.OperationalError:
        await _reply(update, context, text="Something went wrong while doing the necessary checks with the DB.\n"
                                           "Please contact the staff about this.",
                     reply_markup=InlineKeyboardMarkup(keyboard))
    conn.session.commit()
    conn.cursor.close()


# noinspection PyUnboundLocalVariable
async def get_subscription_status(update: Update, context: CallbackContext):
    conn = connect()
    keyboard = [
        [InlineKeyboardButton("⬅ Back to main menu", callback_data="start_over")],
        [InlineKeyboardButton("❌ Stop the bot", callback_data="stop")]
    ]
    try:
        res = conn.cursor.execute("SELECT status FROM INSCRIPTION_USERS_STATUS WHERE username = '" +
                                  user.username + "'")
    except sqlite3.OperationalError:
        await _reply(update, context, text="Something went wrong while doing the necessary checks with the DB.\n"
                                           "Please contact the staff about this.",
                     reply_markup=InlineKeyboardMarkup(keyboard))
        res = "err_OperationalError"

    if res != "err_OperationalError":
        res = res.fetchone()[0]

    conn.session.commit()
    conn.session.close()

    return res
