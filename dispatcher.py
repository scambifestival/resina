import utils
from utils import *
from utils import _reply
import db_functions

# Costanti globali
d = ""
CHAT_ID = ""
TOKEN = ""
user = variables.UserInfos
check = bool

# Features
ISCRIZIONE, DBEDITING, UPDATE = range(3)


# Gestisce il valore di query.data, lanciando l'opportuna funzione
async def _dispatcher(update: Update, context: CallbackContext, query: CallbackQuery, feature: range):
    # Ogni feature va trattata a se. A seconda della feature scelta, seguo il ramo adeguato.
    # NOTA: potrei gestire insieme tutti gli stati senza distinguere i tre rami, ma lo faccio per questioni di ordine.
    if feature == int(ISCRIZIONE):
        # L'utente ha scelto d'iscriversi

        if query.data == str(ISCRIZIONE):
            # Devo controllare che la richiesta non sia già stata fatta
            if db_functions.user_in_db(update, context).fetchall().__len__() > 0:
                keyboard = [
                    [InlineKeyboardButton("⬅ Back to main menu", callback_data="start_over")],
                    [InlineKeyboardButton("❌ Stop the bot", callback_data="stop")]
                ]
                await _reply(update, context, text="Sorry, you already asked to be signed up to Scambi staff.",
                             reply_markup=InlineKeyboardMarkup(keyboard))
            # Devo richiedere conferma del pagamento
            global check
            check = False
            await update.callback_query.message.delete()
            await user_payment_confirmation_request(update, context)

        elif query.data == "user_payment_confirmed" or query.data == "admin_payment_confirmed":
            # Devo richiedere la conferma sul gruppo del direttivo
            await admin_payment_confirmation_request(update, context)

        elif query.data == "user_payment_not_confirmed":
            # Avviso l'utente che non è possibile procedere se aver pagato l'iscrizione.
            await context.bot.delete_message(chat_id=user.id, message_id=variables.ids.last_user_message_id)
            keyboard = [
                [InlineKeyboardButton("⬅ Back to main menu", callback_data="start_over")],
                [InlineKeyboardButton("❌ Stop the bot", callback_data="stop")]
            ]
            await _reply(update, context, "Sorry, I can't sign you up without the payment confirmation... 😣",
                         reply_markup=InlineKeyboardMarkup(keyboard))

        elif query.data == "admin_payment_not_confirmed":
            # Il direttivo ha selezionato "no"; chiedo conferma inequivocabile
            await admin_payment_confirmation_request(update, context)

        elif query.data == "payment_not_confirmed":
            # Il direttivo non ha confermato il pagamento; avviso l'utente e gli do le opzioni
            bot = context.bot
            await bot.delete_message(chat_id=variables.user.id, message_id=variables.ids.last_user_message_id)
            keyboard = [
                [InlineKeyboardButton("⬅ Back to main menu", callback_data="start_over")],
                [InlineKeyboardButton("❌ Stop the bot", callback_data="stop")]
            ]
            await bot.send_message(user.id, "Sorry, the executive staff didn't confirm your fee payment..."
                                            "\n\nIf you think there is a problem you can contact the Scambi staff "
                                            "directly.",
                                            reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='MARKDOWN')

        return

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
    global check
    if update.callback_query.data == "user_payment_confirmed":
        # Avviso l'utente che sto chiedendo conferma al direttivo
        # noinspection PyTypeChecker
        if not check:
            await bot.delete_message(chat_id=variables.user.id, message_id=variables.ids.last_user_message_id)
            message = await bot.send_message(user.id, text="Got it! Before we can proceed, I need a confirmation from "
                                                           "the executive staff.\n\n"
                                                           "📩  `Confirmation request sent. Awaiting the answer..`\n\n"
                                                           "⏳ Please note that this can take a while depending on when "
                                                           "a staff member will answer to the Telegram confirmation "
                                                           "message.\n\n💡 Meanwhile you can contact someone from the "
                                                           "Scambi team to be confirmed sooner.", reply_markup=None,
                                             parse_mode='MARKDOWN')
            variables.ids.last_user_message_id = message.message_id
            check = True

        # Chiedo la prima conferma al direttivo
        if variables.ids.last_group_message_id != 0:
            await bot.delete_message(chat_id=variables.CHAT_ID, message_id=variables.ids.last_group_message_id)
        keyboard = [
            [
                InlineKeyboardButton("✅ Fee verified", callback_data="admin_payment_confirmed"),
                InlineKeyboardButton("❌ Fee not verified", callback_data="admin_payment_not_confirmed")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await bot.send_message(utils.CHAT_ID, text="⚠️ *PAY CONFIRMATION REQUEST* ⚠️\n\n"
                                                             "The following user asked to be signed up to Scambi staff."
                                                             "\n\n_Full name_: " + user.full_name + "\n"
                                                             "_Username_: " + user.name + "\n\n➡️ Did this user"
                                                             " already pay the fee?",
                                         reply_markup=reply_markup, parse_mode='MARKDOWN')
        variables.ids.last_group_message_id = message.message_id
        
    elif update.callback_query.data == "admin_payment_confirmed":
        # Chiedo la conferma della conferma (non si sa mai)
        await context.bot.delete_message(chat_id=variables.CHAT_ID, message_id=variables.ids.last_group_message_id)
        keyboard = [
            [
                InlineKeyboardButton("Yes.", callback_data="payment_confirmed"),
                InlineKeyboardButton("No, go back.", callback_data="user_payment_confirmed")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await bot.send_message(utils.CHAT_ID,
                                         text="✅️ *PAY CONFIRMATION REQUEST* ✅️\n\nYou just confirmed"
                                              " the payment from " + user.full_name + " (" + user.name + ").\n\n"
                                              "*Are you sure?*\nPlease note that this operation cannot"
                                              " be cancelled.", reply_markup=reply_markup, parse_mode='MARKDOWN')
        variables.ids.last_group_message_id = message.message_id

    elif update.callback_query.data == "admin_payment_not_confirmed":
        # Chiedo la conferma della conferma (non si sa mai)
        await context.bot.delete_message(chat_id=variables.CHAT_ID, message_id=variables.ids.last_group_message_id)
        keyboard = [
            [
                InlineKeyboardButton("Yes.", callback_data="payment_not_confirmed"),
                InlineKeyboardButton("No, go back.", callback_data="user_payment_confirmed")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        message = await bot.send_message(utils.CHAT_ID,
                                         text="❌️ *PAY CONFIRMATION REQUEST* ❌️\n\nYou *didn't confirm*"
                                              " the payout from " + user.full_name + " (" + user.name + ").\n\n"
                                              "*Are you sure?*\nPlease note that  this operation cannot be"
                                              " cancelled.",
                                         reply_markup=reply_markup, parse_mode='MARKDOWN')
        variables.ids.last_group_message_id = message.message_id
