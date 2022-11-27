import os
from telegram.ext import *
from telegram import *
import logging
from telegram import __version__ as TG_VER

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
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get('BOT_TOKEN')

# Stages
START_ROUTES, END_ROUTES = range(2)
# Callback data
UNO, DUE, TRE = range(3)


# Questa funzione può essere eseguita ogni volta che l'utente risponde con un messaggio.
# Conseguentemente, non può essere rilanciata in seguito ad una risposta ottenuta da una InlineKeyboard, perché produce
# un oggetto Message nullo, tramite cui non è possibile chiamare nessuna funzione.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user  # Se non c'è risposta tramite messaggio, questa funzione non può essere chiamata
    print(user.first_name + " (user: " + user.username + ") sta usando @r3sinabot")
    keyboard = [
        [
            InlineKeyboardButton("Sign me up!", callback_data=str(UNO)),
            InlineKeyboardButton("I need to edit Pino.", callback_data=str(DUE)),
        ],
        [InlineKeyboardButton("I need an update on a group current tasks.", callback_data=str(TRE))],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Hi, {}!\nMy name is Resina and I'm a digital Scambi staff member. I can do several"
                                    " things; please choose from the keyboard below. 😊".format(user.first_name),
                                    reply_markup=reply_markup)  # Nemmeno questa

    return START_ROUTES


# Questa funzione consente di proseguire nel caso in cui l'utente debba fare più cose senza riavviare il bot.
# Ricorda che non puoi chiamare alcuna funzione attraverso l'oggetto Update, ad eccezione della gestione della query
async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query

    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Sign me up!", callback_data=str(UNO)),
            InlineKeyboardButton("I need to edit Pino.", callback_data=str(DUE)),
        ],
        [InlineKeyboardButton("I need an update on a group current tasks.", callback_data=str(TRE))],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(text="No problem! Choose an option, just like before. 😊", reply_markup=reply_markup)
    return START_ROUTES


async def signin_up(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query

    # Sezione dell'iscrizione

    # Richiedo se posso fare qualcos'altro
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Yes, please!", callback_data=str(UNO)),
            InlineKeyboardButton("No, thank you!", callback_data=str(DUE))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Can I help you with something else?", reply_markup=reply_markup
    )

    return END_ROUTES


async def pino_editing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Yes, please!", callback_data=str(UNO)),
            InlineKeyboardButton("No, thank you!", callback_data=str(DUE))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Can I help you with something else?", reply_markup=reply_markup
    )

    return END_ROUTES


async def updating_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("Yes, please!", callback_data=str(UNO)),
            InlineKeyboardButton("No, thank you!", callback_data=str(DUE))
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Can I help you with something else?", reply_markup=reply_markup
    )

    return END_ROUTES


# Termina la conversazione.
async def quitter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(signin_up, pattern="^" + str(UNO) + "$"),
                CallbackQueryHandler(pino_editing, pattern="^" + str(DUE) + "$"),
                CallbackQueryHandler(updating_tasks, pattern="^" + str(TRE) + "$")
            ],
            END_ROUTES: [
                CallbackQueryHandler(start_over, pattern="^" + str(UNO) + "$"),
                CallbackQueryHandler(quitter, pattern="^" + str(DUE) + "$")
            ]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
