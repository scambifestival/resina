import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram import __version__ as TG_VER
from telegram.ext import *

import db_functions
import utils
import variables
from dispatcher import dispatcher
from utils import _reply
from variables import _set

TOKEN = variables.TOKEN

# noinspection DuplicatedCode
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

    actual_user = utils.get_user(update)

    if actual_user.username not in variables.users_dict:
        # Salvo le information sull'utente
        _set(actual_user, update.message)
        await utils.data_gatherer(update, context, variables.users_dict[actual_user.username])
    # (ELE) lo prendo in culo, dio bon
    else:
        if variables.users_dict[actual_user.username].checks.fullname_check is not True:
            await utils.data_gatherer(update, context, variables.users_dict[actual_user.username])
        if variables.users_dict[actual_user.username].checks.fullname_check is True:
            keyboard = [
                [
                    InlineKeyboardButton("Sign me up!", callback_data=str(ISCRIZIONE)),
                    InlineKeyboardButton("I need to edit Pino.", callback_data=str(DBEDITING)),
                ],
                [InlineKeyboardButton("I need an update on a group current tasks.", callback_data=str(UPDATE))],
            ]

            await _reply(actual_user, context, text="Hi, {}!\nMy name is Resina and I'm a digital Scambi staff"
                                                    " member. I can do several things; please choose from"
                                                    " the keyboard below. 😊",
                         reply_markup=InlineKeyboardMarkup(keyboard))


async def user_signin_up(update: Update, context: CallbackContext):
    for_who = update.callback_query.data.split()
    if for_who.__len__() == 1:
        actual_user = variables.users_dict[update.callback_query.from_user.username]
    else:
        actual_user = variables.users_dict[for_who[1]]

    res = db_functions.user_in_db(context, actual_user)
    if res is not None and res.fetchall().__len__() == 0:
        await db_functions.add_user(context, actual_user)
    elif update.callback_query.data != str(ISCRIZIONE):
        await db_functions.update_subscription_user_status(for_who[0], context, actual_user)

    await dispatcher(actual_user, update, context, ISCRIZIONE)
    return


def main():
    app = Application.builder().token(variables.TOKEN).build()

    # Definizione degli handler

    # Handler che lancia la funzione iniziale
    app.add_handler(CommandHandler("start", start))

    # Handlers per la raccolta delle informazioni sull'utente
    app.add_handler(CallbackQueryHandler(start, pattern="full_name_correct"))
    app.add_handler(CallbackQueryHandler(start, pattern="full_name_not_correct"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))

    # Handlers che gestiscono la feature d'iscrizione. A ogni handler corrisponde uno stato.
    # Gli stati consentono alla procedura di proseguire.
    app.add_handler(CallbackQueryHandler(user_signin_up, pattern="^" + str(ISCRIZIONE) + "$"))
    app.add_handler(CallbackQueryHandler(user_signin_up, pattern="user_payment_not_confirmed"))
    app.add_handler(CallbackQueryHandler(user_signin_up, pattern="^user_payment_confirmed"))
    app.add_handler(CallbackQueryHandler(user_signin_up, pattern="^admin_payment_confirmed"))
    app.add_handler(CallbackQueryHandler(user_signin_up, pattern="^admin_payment_not_confirmed"))
    app.add_handler(CallbackQueryHandler(user_signin_up, pattern="^payment_not_confirmed"))
    app.add_handler(CallbackQueryHandler(user_signin_up, pattern="^payment_confirmed"))
    app.add_handler(CallbackQueryHandler(start, pattern="start_over"))

    # inscription_handler = ConversationHandler(
    #     entry_points=[CallbackQueryHandler(user_signin_up, pattern="^" + str(ISCRIZIONE) + "$")],
    #     states={
    #         ISCRIZIONE: [
    #             CallbackQueryHandler(user_signin_up, pattern="user_payment_confirmed"),
    #             CallbackQueryHandler(user_signin_up, pattern="user_payment_not_confirmed"),
    #             CallbackQueryHandler(user_signin_up, pattern="admin_payment_confirmed"),
    #             CallbackQueryHandler(user_signin_up, pattern="admin_payment_not_confirmed"),
    #             CallbackQueryHandler(user_signin_up, pattern="payment_not_confirmed")
    #         ]
    #     },
    #     fallbacks=[CallbackQueryHandler(start, pattern="start_over")]
    # )
    # app.add_handler(inscription_handler)
    app.run_polling()


if __name__ == "__main__":
    main()
