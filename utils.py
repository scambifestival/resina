# Questo modulo contiene tutte le funzioni che non competono agli altri moduli. Leggere 'struttura.txt' per più info
from telegram import *
from telegram.ext import *
import variables

# Costanti globali
d = ""
CHAT_ID = ""
TOKEN = ""
user = variables.UserInfos


async def _reply(update: Update, context: CallbackContext, text: str, reply_markup: InlineKeyboardMarkup,
                 parse_mode='MARKDOWN'):
    if d == "":
        user_infos_saver(context.user_data)

    if not hasattr(update.callback_query, "inline_message_id"):
        if "{}" in text:
            message = await update.message.reply_text(text.format(user.first_name), parse_mode=parse_mode,
                                                      reply_markup=reply_markup)
        else:
            message = await update.message.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
        variables.ids.last_user_message_id = message.message_id

    else:
        query = update.callback_query
        await query.answer()
        if "{}" in text:
            message = await query.message.reply_text(text.format(user.first_name), parse_mode=parse_mode,
                                                     reply_markup=reply_markup)
        else:
            message = await query.message.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
        variables.ids.last_user_message_id = message.message_id


def constant_set():
    global d
    global CHAT_ID
    global TOKEN
    d = variables.data_key
    CHAT_ID = variables.CHAT_ID
    TOKEN = variables.TOKEN


# Ho bisogno di questa funzione per salvare le informazioni dell'utente che sta richiedendo di essere iscritto
# Ogni volta che una terza persona interagisce col bot, l'utente di riferimento viene sostituito; nel mio caso,
# invece, deve restare lo stesso
def user_infos_saver(user_dict: CallbackContext.user_data):
    global user
    constant_set()
    user.first_name = user_dict[d].first_name
    user.last_name = user_dict[d].last_name
    # Claudio mi ha aiutato a scoprire l'errore del cognome.
    # if user.last_name is not None:
    user.full_name = user.first_name + " " + user.last_name
    user.id = user_dict[d].id
    user.username = user_dict[d].username
    user.link = "https://t.me/" + user.username
    user.name = "@" + user.username
    return user


async def data_gatherer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    if hasattr(update.callback_query, "data"):
        if update.callback_query.data == "full_name_correct":
            if variables.fullname != "":
                name_dict = variables.fullname.split()
                context.user_data[variables.data_key].first_name = name_dict[0]
                context.user_data[variables.data_key].last_name = name_dict[1]
            variables.done = True
        elif update.callback_query.data == "full_name_not_correct":
            await bot.editMessageText(text="Ok, no problem! Please tell me your correct full name.",
                                      chat_id=context.user_data[variables.data_key].id,
                                      message_id=variables.ids.last_user_message_id)

    elif update.message.text == "/start":
        if context.user_data[variables.data_key].last_name is not None:
            # L'utente ha scritto qualcosa nel campo 'Cognome' sul suo profilo Telegram. Chiedo se è corretto.
            full_name = context.user_data[variables.data_key].first_name + " " +\
                        context.user_data[variables.data_key].last_name
            keyboard = [
                [
                    InlineKeyboardButton("Yes!", callback_data="full_name_correct"),
                    InlineKeyboardButton("No!", callback_data="full_name_not_correct")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            message = await update.message.reply_text(text="Hi! I'm _Resina_, the Scambi digital helper.\n"
                                                           "Before we can proceed, I need to know if I got your correct"
                                                           " full name.\n\n Is *" + full_name +
                                                           "* your actual full name?",
                                                      parse_mode='MARKDOWN', reply_markup=reply_markup)
            variables.ids.last_user_message_id = message.message_id
        else:
            message = await update.message.reply_text(text="Hi! I'm _Resina_, the Scambi digital helper.\n\n"
                                                           "Before we can proceed, I need to know if I got your correct"
                                                           " full name.\n\nCan you just write it down? 😊",
                                                      parse_mode='MARKDOWN')
            variables.ids.last_user_message_id = message.message_id
    else:
        # L'utente ha indicato il suo nome, chiedo se è corretto
        variables.fullname = update.message.text
        keyboard = [
            [
                InlineKeyboardButton("Yes!", callback_data="full_name_correct"),
                InlineKeyboardButton("No!", callback_data="full_name_not_correct")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await update.message.reply_text(text="`Is \"" + variables.fullname + "\" your actual name?`",
                                                  parse_mode='MARKDOWN', reply_markup=reply_markup)
        variables.ids.last_user_message_id = message.message_id

    return
