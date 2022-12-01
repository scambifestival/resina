import variables

from telegram.ext import *
from telegram import *

# Costanti globali
d = ""
CHAT_ID = ""
TOKEN = ""
user = variables.UserInfos
right_user_data = CallbackContext.user_data

# Features
ISCRIZIONE, DBEDITING, UPDATE = range(3)


# Gestisce il valore di query.data, lanciando l'opportuna funzione
async def _dispatcher(update: Update, context: CallbackContext, query: CallbackQuery, feature: range):
    await constant_set()
    # Ogni feature va trattata a se. A seconda della feature scelta, seguo il ramo adeguato.
    # NOTA: potrei gestire insieme tutti gli stati senza distinguere i tre rami, ma lo faccio per questioni di ordine.
    if feature == int(ISCRIZIONE):
        # L'utente ha scelto d'iscriversi

        if query.data == str(ISCRIZIONE):
            # Devo richiedere conferma del pagamento
            await user_payment_confirmation_request(update, context)
            return

        elif query.data == "user_payment_confirmed" or query.data == "admin_payment_confirmed":
            # Devo richiedere la conferma sul gruppo del direttivo
            await admin_payment_confirmation_request(update, context)
            return

        elif query.data == "user_payment_not_confirmed":
            # Avviso l'utente che non è possibile procedere se aver pagato l'iscrizione.
            keyboard = [
                [InlineKeyboardButton("⬅ Back to main menu", callback_data="start_over")],
                [InlineKeyboardButton("❌ Stop the bot", callback_data="stop")]
            ]
            await _reply(update, context, "Sorry, I can't sign you up without the payment confirmation... 😣",
                         reply_markup=InlineKeyboardMarkup(keyboard))

    elif feature == int(DBEDITING):
        print("hai scelto dbediting")

    else:
        print("hai scelto update")


# Funzione per chiedere all'utente se ha pagato l'iscrizione
async def user_payment_confirmation_request(update: Update, context: CallbackContext):
    payment_request_keyboard = [
            [
                InlineKeyboardButton("Yes!", callback_data="user_payment_confirmed"),
                InlineKeyboardButton("No, I haven't yet.", callback_data="user_payment_not_confirmed")
            ],
            [InlineKeyboardButton("⬅ Back to main menu", callback_data="start_over")]
    ]
    reply_markup = InlineKeyboardMarkup(payment_request_keyboard)

    # Filosofia di MozItaBot: per rendere possibile l'accesso alla funzione anche tramite comando, sfruttiamo
    # una funzione in grado di gestire la risposta sia di una callbackquery sia di un messaggio di update
    await _reply(update, context, "🖋 *Scambi staff subscription*\n\nOk! I guess we are gonna have a new member. 😎\n"
                                  "\nHave you paid the membership fee yet?", reply_markup)


# Funzione per chiedere al direttivo se effettivamente l'utente ha già pagato l'iscrizione
async def admin_payment_confirmation_request(update: Update, context: CallbackContext):
    bot = context.bot
    global user
    if update.callback_query.data == "user_payment_confirmed":
        if not(hasattr(user, "first_name")):
            global right_user_data
            right_user_data = context.user_data
            user = variables.user_infos_saver(right_user_data)

        # Chiedo la prima conferma al direttivo
        keyboard = [
            [
                InlineKeyboardButton("✅ Fee verified", callback_data="admin_payment_confirmed"),
                InlineKeyboardButton("❌ Fee not verified", callback_data="admin_payment_not_confirmed")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(CHAT_ID, text="⚠️ *PAY CONFIRMATION REQUEST* ⚠️\n\n"
                                             "The following user asked to be signed up to Scambi staff.\n\n"
                                             "_Full name_: " + user.full_name + "\n"
                                             "_Username_: " + user.name + "\n\n➡️ Did this user"
                                             " already pay the fee?",
                               reply_markup=reply_markup, parse_mode='MARKDOWN')
        
    elif update.callback_query.data == "admin_payment_confirmed":
        # Chiedo la conferma della conferma (non si sa mai)
        keyboard = [
            [
                InlineKeyboardButton("Yes", callback_data="payment_confirmed"),
                InlineKeyboardButton("No, go back.", callback_data="user_payment_confirmed")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await bot.send_message(CHAT_ID, text="✅️ *PAY CONFIRMATION REQUEST* ✅️\n\nYou just confirmed"
                                             " the payment from " + user.full_name + " (" +
                                             user.name + ").\n\n*Are you sure?*\nPlease note that"
                                             " this operation cannot be cancelled.",
                               reply_markup=reply_markup, parse_mode='MARKDOWN')


async def _reply(update: Update, context: CallbackContext, text: str, reply_markup: InlineKeyboardMarkup,
                 parse_mode='MARKDOWN'):
    if len(d) == 0:
        await constant_set()

    if not hasattr(update.callback_query, "inline_message_id"):
        if "{}" in text:
            await update.message.reply_text(text.format(context.user_data[d].first_name), reply_markup=reply_markup,
                                            parse_mode=parse_mode)
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)

    else:
        query = update.callback_query
        await query.answer()
        if "{}" in text:
            await query.message.reply_text(text.format(context.user_data[d].first_name), reply_markup=reply_markup,
                                           parse_mode=parse_mode)

        else:
            await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)


async def constant_set():
    global d
    global CHAT_ID
    global TOKEN
    d = variables.data_key
    CHAT_ID = variables.CHAT_ID
    TOKEN = variables.TOKEN
