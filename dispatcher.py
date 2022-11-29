from telegram.ext import *
from telegram import *
import os

# Costanti globali
CHAT_ID = os.environ.get("CHANNEL_ID")

# Features
ISCRIZIONE, DBEDITING, UPDATE = range(3)


# Gestisce il valore di query.data, lanciando l'opportuna funzione
async def _dispatcher(update: Update, context: CallbackContext, query: CallbackQuery, feature: range, data_key: str):
    # Ogni feature va trattata a se. A seconda della feature scelta, seguo il ramo adeguato.
    # NOTA: potrei gestire insieme tutti gli stati senza distinguere i 3 rami, ma lo faccio per questioni di ordine.
    if feature == int(ISCRIZIONE):
        # L'utente ha scelto di iscriversi

        if query.data == str(ISCRIZIONE):
            # Devo richiedere conferma del pagamento

            await user_payment_confirmation_request(update, context)
            return

        elif query.data == "user_payment_confirmed":
            # Devo richiedere la conferma sul gruppo del direttivo

            await admin_payment_confirmation_request(update, context, data_key)
            return

        elif query.data == "user_payment_not_confirmed":
            # Avviso l'utente che non è possibile procedere se aver pagato l'iscrizione.
            keyboard = [
                [
                    InlineKeyboardButton("⬅ Back to main menu", callback_data="start_over"),
                    InlineKeyboardButton("❌ Stop the bot", callback_data="stop")
                ]
            ]
            await _reply(update, "I can't sign you up without the payment confirmation... 😣",
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

    # Filosofia di MozItaBot : per rendere possibile l'accesso alla funzione anche tramite comando, sfruttiamo
    # una funzione in grado di gestire la risposta sia di una callbackquery sia di un messaggio di update
    await _reply(update, "Ok! I guess we are gonna have a new member 😎\n"
                         "Have you paid the membership fee yet?", reply_markup)


# Funzione per chiedere al direttivo se effettivamente l'utente ha già pagato l'iscrizione
async def admin_payment_confirmation_request(update: Update, context: CallbackContext, data_key: str):
    bot = context.bot
    keyboard = [
        [
            InlineKeyboardButton("Payment confirmed.", callback_data="admin_payment_confirmed"),
            InlineKeyboardButton("Payment not confirmed.", callback_data="admin_payment_not_confirmed")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(CHAT_ID, text="⚠️ PAYMENT CONFIRMATION REQUEST ⚠️\n"
                                         "The following user asked to be signed up to Scambi staff.\n\n"
                                         "_Full name_: " + context.user_data[data_key].full_name + "\n"
                                         "_Username_: " +
                                         context.user_data[data_key].name, parse_mode='MARKDOWN')
    await bot.send_message(CHAT_ID, text="Did this user already pay the fee?", reply_markup=reply_markup)


async def _reply(update: Update, text: str, reply_markup: InlineKeyboardMarkup, parse_mode='MARKDOWN'):
    if not hasattr(update.callback_query, "inline_message_id"):
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    else:
        query = update.callback_query
        await query.answer()
        await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)