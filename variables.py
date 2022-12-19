import os
from dataclasses import dataclass


# user infos class
@dataclass
class UserInfos:
    full_name: str
    link: str
    name: str
    first_name: str
    id: int
    last_name: str
    username: str


@dataclass
class MessagesIds:
    last_user_message_id: int
    last_group_message_id = 0


# info about the user who is using the bot
user = UserInfos
# variabile contenente gli id degli ultimi messaggi inviati nelle chat
ids = MessagesIds
# Bot token
TOKEN = os.environ.get('BOT_TOKEN')
# Executive chat ID
CHAT_ID = os.environ.get('EXECUTIVE_CHAT_ID')
# dictionary kay to stored data
data_key = ""
# user's full name isterted manually
fullname = ""
# full_name gathered
done = False

