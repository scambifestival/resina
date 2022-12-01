import os
from dataclasses import dataclass
from telegram.ext import CallbackContext


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


user = UserInfos
# Bot token
TOKEN = os.environ.get('BOT_TOKEN')
# Executive chat ID
CHAT_ID = os.environ.get("CHANNEL_ID")
# dictionary kay to stored data
data_key = ""


def user_infos_saver(user_dict: CallbackContext.user_data):
    global user
    user.first_name = user_dict[data_key].first_name
    user.last_name = user_dict[data_key].last_name
    user.full_name = user.first_name + " " + user.last_name
    user.id = user_dict[data_key].id
    user.username = user_dict[data_key].username
    user.link = "https://t.me/" + user.username
    user.name = "@" + user.username
    return user
