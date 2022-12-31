from utils import _reply
from db_functions import *

# Costanti globali
d = ""
user = variables.UserInfos

# Features
ISCRIZIONE, DBEDITING, UPDATE = range(3)


# Gestisce il valore di query.data, lanciando l'opportuna funzione
async def dispatcher(actual_user: variables.UserInfos, update: Update, context: CallbackContext, feature: range):
    # Ogni feature va trattata a se. A seconda della feature scelta, seguo il ramo adeguato.
    # NOTA: potrei gestire insieme tutti gli stati senza distinguere i tre rami, ma lo faccio per questioni di ordine.
    if feature == int(ISCRIZIONE):
        # L'utente ha scelto d'iscriversi. Controllo il database per verificare lo stato del processo.
        last_status = await get_subscription_status(context, actual_user)

        if last_status == str(ISCRIZIONE):
            await user_payment_confirmation_request(context, actual_user)

        elif last_status == "user_payment_confirmed" or last_status == "admin_payment_confirmed"\
                or last_status == "admin_payment_not_confirmed":
            await admin_payment_confirmation_request(last_status, context, actual_user)

        elif last_status == "payment_confirmed" or last_status == "payment_not_confirmed":
            if update.callback_query.data != str(ISCRIZIONE):
                await payment_confirmation_answer(last_status, context, actual_user)
            else:
                await payment_already_checked(actual_user, context, last_status)

    elif feature == int(DBEDITING):
        print("hai scelto dbediting")

    else:
        print("hai scelto update")


async def user_payment_confirmation_request(context: CallbackContext, actual_user: variables.UserInfos):
    # await update.callback_query.message.delete()
    payment_request_keyboard = [
            [
                InlineKeyboardButton("Yes!", callback_data="user_payment_confirmed"),
                InlineKeyboardButton("No, I haven't yet.", callback_data="user_payment_not_confirmed")
            ],
            [InlineKeyboardButton("⬅ Back to main menu", callback_data="start_over")]
    ]

    await _reply(actual_user, context, "🖋 *Scambi staff subscription*\n\nOk! I guess we are gonna have a new member. 😎"
                                       "\n\nHave you paid the membership fee yet?",
                 reply_markup=InlineKeyboardMarkup(payment_request_keyboard))


async def admin_payment_confirmation_request(status: str, context: CallbackContext,
                                             actual_user: variables.UserInfos):
    bot = context.bot
    if status == "user_payment_confirmed":
        # Avviso l'utente che sto chiedendo conferma al direttivo
        # noinspection PyTypeChecker
        if not actual_user.checks.signin_up_note_check:
            await bot.delete_message(chat_id=actual_user.id,
                                     message_id=actual_user.last_mess.last_user_message.message_id)
            message = await bot.send_message(actual_user.id,
                                             text="Got it! Before we can proceed, I need a"
                                                  " confirmation from the executive staff.\n\n"
                                                  "📩  `Confirmation request sent. Awaiting the answer..`\n\n"
                                                  "⏳ Please note that this can take a while depending on when "
                                                  "a staff member will answer to the Telegram confirmation "
                                                  "message.\n\n💡 Meanwhile you can contact someone from the "
                                                  "Scambi team to be confirmed sooner.", reply_markup=None,
                                             parse_mode='MARKDOWN')
            actual_user.last_mess.last_user_message.message_id = message.message_id
            actual_user.checks.signin_up_note_check = True

        # Chiedo la conferma al direttivo (se la ho già fatta elimino il messaggio e lo riscrivo)
        keyboard = [
            [
                InlineKeyboardButton("✅ Fee verified", callback_data="admin_payment_confirmed" +
                                                                     " " + actual_user.username),
                InlineKeyboardButton("❌ Fee not verified", callback_data="admin_payment_not_confirmed"
                                                                         + " " + actual_user.username)
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if actual_user.last_mess.last_group_message.message_id != actual_user.last_mess.first_group_message.message_id:
            await bot.editMessageText(chat_id=variables.CHAT_ID,
                                      message_id=actual_user.last_mess.last_group_message.message_id,
                                      text="⚠️ *PAY CONFIRMATION REQUEST* ⚠️\n\n"
                                           "The following user asked to be signed up to Scambi"
                                           " staff.\n\n_Full name_: " + actual_user.full_name +
                                           "\n_Username_: " + actual_user.name + "\n\n"
                                           "➡️ Did this user already pay the fee?",
                                      reply_markup=reply_markup, parse_mode='MARKDOWN')
        else:
            message = await bot.send_message(variables.CHAT_ID, text="⚠️ *PAY CONFIRMATION REQUEST* ⚠️\n\n"
                                                                     "The following user asked to be signed up to Scamb"
                                                                     "i staff.\n\n_Full name_: " + actual_user.full_name
                                                                     + "\n_Username_: " + actual_user.name + "\n\n"
                                                                     "➡️ Did this user already pay the fee?",
                                             reply_markup=reply_markup, parse_mode='MARKDOWN')
            actual_user.last_mess.last_group_message = message

    # Chiedo la conferma della conferma (non si sa mai)
    if status == "admin_payment_confirmed":
        keyboard = [
            [
                InlineKeyboardButton("Yes.", callback_data="payment_confirmed" + " " + actual_user.username),
                InlineKeyboardButton("No, go back.", callback_data="user_payment_confirmed"
                                                                   + " " + actual_user.username)
            ]
        ]
        await bot.editMessageText(chat_id=variables.CHAT_ID,
                                  message_id=actual_user.last_mess.last_group_message.message_id,
                                  text="✅️ *PAY CONFIRMATION REQUEST* ✅️\n\nYou just confirmed"
                                       " the payment from " + actual_user.full_name + " (" + actual_user.name
                                       + ").\n\n*Are you sure?*\nPlease note that this operation cannot be"
                                       " cancelled.",
                                       reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='MARKDOWN')

    elif status == "admin_payment_not_confirmed":
        keyboard = [
            [
                InlineKeyboardButton("Yes.", callback_data="payment_not_confirmed" + " " + actual_user.username),
                InlineKeyboardButton("No, go back.", callback_data="user_payment_confirmed"
                                                                   + " " + actual_user.username)
            ]
        ]
        await bot.editMessageText(chat_id=variables.CHAT_ID,
                                  message_id=actual_user.last_mess.last_group_message.message_id,
                                  text="❌️ *PAY CONFIRMATION REQUEST* ❌️\n\nYou *didn't confirm*"
                                       " the payout from " + actual_user.full_name + " (" + actual_user.name +
                                       ").\n\n*Are you sure?*\nPlease note that this operation cannot be"
                                       " cancelled.",
                                       reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='MARKDOWN')

    variables.users_dict[actual_user.username] = actual_user


async def payment_confirmation_answer(status: str, context: CallbackContext, actual_user: variables.UserInfos):
    bot = context.bot
    await bot.delete_message(chat_id=actual_user.id, message_id=actual_user.last_mess.last_user_message.message_id)
    await bot.delete_message(chat_id=variables.CHAT_ID, message_id=actual_user.last_mess.last_group_message.message_id)

    if status == "payment_confirmed":

        message = await bot.send_message(actual_user.id,
                                         text="✅ *Payment confirmed* ✅\n\nSorry for the wait! The executive"
                                         " group just _confirmed_ your fee payment. Now we can"
                                         " proceed with your subscription. 🤗", parse_mode='MARKDOWN')

        group_message = await bot.send_message(variables.CHAT_ID,
                                               text="✅ The subscription fee payment from " + actual_user.full_name +
                                                    " (" + actual_user.name + ") *has been confirmed*.\nThe user "
                                                    "will be registered to Scambi staff.",
                                               parse_mode='MARKDOWN')

    elif status == "payment_not_confirmed":
        keyboard = [
            [InlineKeyboardButton("⬅ Back to main menu", callback_data="start_over")],
            [InlineKeyboardButton("❌ Stop the bot", callback_data="stop")]
        ]

        message = await bot.send_message(actual_user.id,
                                         text="❌ *Payment not confirmed* ❌\n\nSorry, the executive group did not "
                                              "confirmed you fee payment.\n\nℹ️ If you think there is a problem,"
                                              " feel free to contact the staff to eventually fix that.",
                                         reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='MARKDOWN')

        group_message = await bot.send_message(variables.CHAT_ID,
                                               text="❌ The subscription fee payment from " + actual_user.full_name +
                                                    " (" + actual_user.name + ") *has not been confirmed*.\n"
                                                    "The user will not be able to be enrolled to the staff.\n\n"
                                                    "🆘️ If you made a mistake you can still manually add this user"
                                                    " by yourself or ask @AleLntr to cancel your decision.",
                                               parse_mode='MARKDOWN')

    # noinspection PyUnboundLocalVariable
    variables.users_dict[actual_user.username].last_mess.last_user_message = message
    # noinspection PyUnboundLocalVariable
    variables.users_dict[actual_user.username].last_mess.last_group_message = group_message
    return


async def payment_already_checked(actual_user: variables.UserInfos, context: CallbackContext, status: str):
    if status == "payment_confirmed":
        print()
    else:
        bot = context.bot
        keyboard = [
            [InlineKeyboardButton("⬅ Back to main menu", callback_data="start_over")],
            [InlineKeyboardButton("❌ Stop the bot", callback_data="stop")]
        ]
        await bot.editMessageText(chat_id=actual_user.id, message_id=actual_user.last_mess.last_user_message.message_id,
                                  text="⚠️ Your payment hasn't been confirmed in the past.\n\n🆘️ If "
                                       "you paid the subscription please ask for help to the staff in "
                                       "order to allow me adding you to the shareholders' register now.",
                                  reply_markup=InlineKeyboardMarkup(keyboard))
