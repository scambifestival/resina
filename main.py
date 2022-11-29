import os
from telegram.ext import *
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup
from telegram import __version__ as TG_VER
from uuid import uuid4
import logging

from dispatcher import _dispatcher, _reply


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

# GLOBAL VARIABLES
TOKEN = os.environ.get('BOT_TOKEN')

# Stati - Differenzio le funzioni
ISCRIZIONE, DBEDITING, UPDATE = range(3)

data_key = ""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Salvo le informazioni sull'utente
    global data_key

    if len(context.chat_data) == 0:
        data_key = str(uuid4())
        user = update.message.from_user
        context.user_data[str(data_key)] = user
        context.chat_data[data_key] = update.message.id

    keyboard = [
        [
            InlineKeyboardButton("Sign me up!", callback_data=str(ISCRIZIONE)),
            InlineKeyboardButton("I need to edit Pino.", callback_data=str(DBEDITING)),
        ],
        [InlineKeyboardButton("I need an update on a group current tasks.", callback_data=str(UPDATE))],
    ]

    await _reply(update, text="Hi, {}!\nMy name is Resina and I'm a digital Scambi staff member. I can do several"
                              " things; please choose from the keyboard below. 😊".format(user.first_name),
                 reply_markup=InlineKeyboardMarkup(keyboard))

    # reply_markup = InlineKeyboardMarkup(keyboard)
    #
    # await update.message.reply_text("Hi, {}!\nMy name is Resina and I'm a digital Scambi staff member. I can do several"
    #                                 " things; please choose from the keyboard below. 😊".format(user.first_name),
    #                                 reply_markup=reply_markup)


# async def _reply(update: Update, text: str, reply_markup: InlineKeyboardMarkup, parse_mode='MARKDOWN'):
#     if not hasattr(update.callback_query, "inline_message_id"):
#         await update.message.reply_text(
#             text, reply_markup=reply_markup, parse_mode=parse_mode)
#     else:
#         query = update.callback_query
#         await query.answer()
#         await query.message.reply_text(
#             text, reply_markup=reply_markup, parse_mode=parse_mode)


async def user_signin_up(update: Update, context: CallbackContext):
    await update.callback_query.message.delete()
    await _dispatcher(update, context, update.callback_query, ISCRIZIONE, data_key)


def main():
    app = Application.builder().token(TOKEN).build()

    # Definizione degli handler

    # Handler che lancia la funzione iniziale
    app.add_handler(CommandHandler("start", start))

    # Handler che direziona verso la funzione di iscrizione e gestisce gli stati
    # inscription_feature_handler = ConversationHandler(
    #     entry_points=[CallbackQueryHandler(user_signin_up, pattern="^" + str(ISCRIZIONE) + "$")],
    #     states={
    #         # Ogni stato corrisponde ad un'informazione ricevuta in input dall'utente
    #         # Sarà la funzione "user_signin_up" a richiedere se l'utente ha già pagato l'iscrizione
    #         PAYMENT_REQUEST: [
    #             CallbackQueryHandler(user_signin_up, pattern="user_payment_confirmed"),
    #             CallbackQueryHandler(user_signin_up, pattern="user_payment_not_confirmed")
    #         ]
    #     },
    #     fallbacks=[CallbackQueryHandler(start, pattern="^" + str(START_OVER) + "$")]
    # )
    #
    # app.add_handler(inscription_feature_handler)

    # Handlers che gestiscono la feature d'iscrizione. Ad ogni handler corrisponde uno stato.
    # Gli stati consentono alla procedura di proseguire.
    app.add_handler(CallbackQueryHandler(user_signin_up, pattern="^" + str(ISCRIZIONE) + "$"))
    app.add_handler(CallbackQueryHandler(user_signin_up, pattern="user_payment_confirmed"))
    app.add_handler(CallbackQueryHandler(user_signin_up, pattern="user_payment_not_confirmed"))
    app.add_handler(CallbackQueryHandler(start, pattern="start_over"))
    app.run_polling()


if __name__ == "__main__":
    main()
