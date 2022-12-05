# Questo modulo contiene tutte le funzioni che non competono agli altri moduli. Leggere 'struttura.txt' per più info
from telegram import *
from telegram.ext import *
import variables

# Costanti globali
d = ""
CHAT_ID = ""
TOKEN = ""
user = variables.UserInfos
data_key = ""


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
    user.full_name = user.first_name + " " + user.last_name
    user.id = user_dict[d].id
    user.username = user_dict[d].username
    user.link = "https://t.me/" + user.username
    user.name = "@" + user.username
    return user
