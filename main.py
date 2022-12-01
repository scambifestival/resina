from telegram.ext import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram import __version__ as TG_VER
from uuid import uuid4
import logging

import variables
from dispatcher import _dispatcher, _reply

d = variables.data_key
CHAT_ID = variables.CHAT_ID
TOKEN = variables.TOKEN

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Stati - Differenzio le funzioni
ISCRIZIONE, DBEDITING, UPDATE = range(3)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if hasattr(update.callback_query, "data"):
        await update.callback_query.message.delete()

    if len(context.chat_data) == 0:
        # Salvo le informazioni sull'utente
        global d
        d = variables.data_key = str(uuid4())
        user = update.message.from_user
        context.user_data[str(d)] = user
        context.chat_data[d] = update.message.id

    keyboard = [
        [
            InlineKeyboardButton("Sign me up!", callback_data=str(ISCRIZIONE)),
            InlineKeyboardButton("I need to edit Pino.", callback_data=str(DBEDITING)),
        ],
        [InlineKeyboardButton("I need an update on a group current tasks.", callback_data=str(UPDATE))],
    ]

    await _reply(update, context, text="Hi, {}!\nMy name is Resina and I'm a digital Scambi staff member. "
                                       "I can do several things; please choose from the keyboard below. 😊",
                 reply_markup=InlineKeyboardMarkup(keyboard))


async def user_signin_up(update: Update, context: CallbackContext):
    await update.callback_query.message.delete()
    await _dispatcher(update, context, update.callback_query, ISCRIZIONE)
    return


def main():
    app = Application.builder().token(TOKEN).build()

    # Definizione degli handler

    # Handler che lancia la funzione iniziale
    app.add_handler(CommandHandler("start", start))

    # Handlers che gestiscono la feature d'iscrizione. A ogni handler corrisponde uno stato.
    # Gli stati consentono alla procedura di proseguire.
    app.add_handler(CallbackQueryHandler(user_signin_up, pattern="^" + str(ISCRIZIONE) + "$"))
    app.add_handler(CallbackQueryHandler(user_signin_up, pattern="user_payment_confirmed"))
    app.add_handler(CallbackQueryHandler(user_signin_up, pattern="user_payment_not_confirmed"))
    app.add_handler(CallbackQueryHandler(user_signin_up, pattern="admin_payment_confirmed"))
    app.add_handler(CallbackQueryHandler(start, pattern="start_over"))
    app.run_polling()


if __name__ == "__main__":
    main()
