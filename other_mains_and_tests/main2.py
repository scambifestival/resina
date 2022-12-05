import requests
from telegram import *
from telegram.ext import *

TOKEN = "5601080393:AAGR0WcTSIoikFTxGi1gcm0c3semtfv398M"
allowedUsernames = ["Pino"]
user, psw = "", ""

CHECK, CHECK_EMAIL, CHECK_PASSWORD, MENU, ERR_HANDLER = range(5)


async def hello_world(update: Update, context=ContextTypes.DEFAULT_TYPE) -> int:

    """Check if the user is allowed to use this bot."""
    if update.effective_chat.username not in allowedUsernames:
        reply_keyboard = [["Yes, I think I should."], ["No, you're right."]]
        await update.message.reply_text("Sorry, you are not allowed to use Pino!\nDo you think you should?",
                                        reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                         resize_keyboard=True,
                                                                         one_time_keyboard=True,
                                                                         input_field_placeholder="yes_no"
                                                                         ))
        return CHECK

    operation_keyboard = [["Update"], ["Delete"], ["Add"]]
    await update.message.reply_text("Hi! I'm Pino, the official Scambi Staff member who'll help you using our DB.")


async def check_user(update: Update, context=ContextTypes.DEFAULT_TYPE) -> int:

    """If the user thinks he should be able to use the bot, then ask for a login"""
    await update.message.reply_text("OK! I'm sorry for that. I need to add you to my list before we can proceed.\n"
                                    "Can you please tell me the email you use to access Pino?")
    return CHECK_EMAIL


async def email_getter(update: Update, context=ContextTypes.DEFAULT_TYPE) -> int:

    """Saving the email and asking for the password"""
    global user
    user = update.message.text
    await update.message.reply_text("Perfect! We are almost there, now I only need your Pino password. Make sure to"
                                    " spell it correctly.\n\nIf the email you told me was not correct, you can"
                                    " restart me by typing /retry.")
    return CHECK_PASSWORD


async def psw_getter(update: Update, context=ContextTypes.DEFAULT_TYPE):
    global psw
    bot = context.bot
    await bot.send_message(update.message.chat_id, text="Alright, let me try to login to Pino! Give me some seconds...")
    psw = update.message.text
    session = await login(user, psw, update, context)
    if session == 1:
        allowedUsernames.append(update.message.from_user.username)
        print("THE USER "+update.message.from_user.username+" HAS BEEN ADDED TO THE ALLOWED USERS!!!\n")
        await bot.send_message(update.message.chat_id, text="You were right: now you are in my list! Let me restart.")
        await hello_world(update, context)


async def login(email, password, update: Update, context=ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["/retry"], ["/quit"]]
    bot = context.bot
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
        return 0
    elif res.status_code != 201:
        await bot.send_message(update.message.chat_id, text="Is seems something went wrong! Type "
                                                            "/retry to let me try again, or type /quit to abort"
                                                            " the operation. Sorry about that :(",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                resize_keyboard=True,
                                                                one_time_keyboard=True,
                                                                input_field_placeholder="retry_or_not"))
        return 0
    return 1


async def abort(update: Update, context=ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Operation aborted from the user. Type /start to restart the bot."
    )
    return ConversationHandler.END


async def err_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == "/retry":
        await check_user(update, context)
    elif update.message.text == "/start":
        await hello_world(update, context)
        return CHECK
    elif update.message.text == "/quit":
        return await abort(update, context)


def main() -> None:
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", hello_world)],
        states={
            MENU: [],
            CHECK: [MessageHandler(filters.Regex("(?:^|\\W)Yes(?:$|\\W)"), callback=check_user)],
            CHECK_EMAIL: [MessageHandler(filters.Regex("\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b"),
                                         callback=email_getter)],
            CHECK_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, callback=psw_getter)]
        },
        fallbacks=[CommandHandler("quit", abort), CommandHandler("retry", hello_world),
                   MessageHandler(filters.Regex("(?:^|\\W)No(?:$|\\W)"), callback=abort)]
    )

    application.add_handler(conv_handler)
    application.run_polling()


main()
