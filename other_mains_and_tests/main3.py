import telegram
from telegram.ext import *
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
import logging


import requests
import json

Email, Psw, Login, LogErr = range(4)

TOKEN = "5601080393:AAGR0WcTSIoikFTxGi1gcm0c3semtfv398M"
email_adr, psw = "", ""

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["/login"]]
    await update.message.reply_text('Hi! This is a bot created to help Scambi Staff using Pino DB!\n'
                                    'Please login first.',
                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,
                                                                     one_time_keyboard=True,
                                                                     input_field_placeholder="login")
                                    )

    return Email


async def email_getter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "First, enter your email.\nType /quit to stop."
    )
    return Psw


async def psw_getter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global email_adr
    email_adr = update.message.text
    print(email_adr)
    await update.message.reply_text(
        "Now tell me your password. Make sure to spell it correctly!\n"
        "If you spelled your email wrongly, type /quit to stop."
    )
    return Login


async def abort(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Operation aborted from the user. If your wanna retry to login, type /start."
    )
    return LogErr


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global psw
    psw = update.message.text
    print(email_adr)
    print(psw)
    await update.message.reply_text(
        "OK! I'm trying to login to your Baserow account, just wait some seconds..."
    )
    session = await baserow_login(update, context, email_adr, psw)
    return session


async def baserow_login(update: Update, context: ContextTypes.DEFAULT_TYPE, email, password) -> int:
    reply_keyboard = [["/retry"], ["/quit"]]
    bot = telegram.Bot(TOKEN)
    s = requests.Session()
    payload = {
        'username': email,
        'password': password
    }
    res = s.post('https://pino.scambi.org/api/user/token-auth/', json=payload)
    if res.status_code == 400:
        await bot.send_message(update.message.chat_id, text="Is seems your credentials were not correct! Type "
                                                            "/retry to let me try again, or type /quit to abort"
                                                            " the operation.",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                resize_keyboard=True,
                                                                one_time_keyboard=True,
                                                                input_field_placeholder="retry_or_not"))
        return LogErr
    elif res.status_code == 500:
        await bot.send_message(update.message.chat_id, text="Something unknown went wrong... Type /retry to try again"
                                                            "or type /quit to abort the operation. Sorry about that :(",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                resize_keyboard=True,
                                                                one_time_keyboard=True,
                                                                input_field_placeholder="retry_or_not"))
        return LogErr
    elif res.status_code == 502:
        await bot.send_message(update.message.chat_id, text="Baserow seems to be updating right now. I recommend to"
                                                            " retry within some hours. Type /retry to try again"
                                                            "or type /quit to abort the operation.",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                resize_keyboard=True,
                                                                one_time_keyboard=True,
                                                                input_field_placeholder="retry_or_not")
                               )
        return LogErr
    elif res.status_code == 503:
        await bot.send_message(update.message.chat_id, text="Baserow has a problem so it could not process your"
                                                            " request in time. Type /retry to try again or type /quit"
                                                            " to abort the operation.",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                resize_keyboard=True,
                                                                one_time_keyboard=True,
                                                                input_field_placeholder="retry_or_not")
                               )
        return LogErr
    print(res.content)
    s.headers.update({'token': json.loads(res.content)['token']})
    '''The loggin as done successfully. Now I handle all operations in Baserow.'''
    await operations_handler(update)
    return ConversationHandler.END


async def operations_handler(update: Update):
    bot = telegram.Bot(TOKEN)
    await bot.send_message(update.message.chat_id, text="You logged in successefully, now you can choose the operation"
                                                        " to perform.")


async def err_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "/retry":
        await login(update, context)
    elif update.message.text == "/start":
        await start(update, context)
        return Email
    elif update.message.text == "/quit":
        await abort(update, context)
        return ConversationHandler.END


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            Email: [MessageHandler(filters.COMMAND, callback=email_getter)],
            Psw: [MessageHandler(filters.Regex("\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"),
                                 callback=psw_getter)],
            Login: [MessageHandler(filters.Regex("^[\\w]"), callback=login)],
            LogErr: [MessageHandler(filters.COMMAND, callback=err_handler)]
        },
        fallbacks=[CommandHandler("quit", abort)]
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()
