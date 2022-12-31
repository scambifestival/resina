import os
from dataclasses import dataclass

import telegram


@dataclass
class MessagesIds:
    last_user_message_id: int
    last_group_message_id: int


@dataclass
class Checks:
    # for user's fullname checking at the start
    fullname_check: bool
    # for checking if the payment request has been proposed to the executive group
    signin_up_note_check: bool


# user infos class
@dataclass
class UserInfos:
    link: str
    name: str
    id: int
    username: str
    lm_ids: MessagesIds
    checks: Checks
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    full_name_temp: str = ""


# variabile contenente gli id degli ultimi messaggi inviati nelle chat
ids = MessagesIds
# Bot token
TOKEN = os.environ.get('BOT_TOKEN')
# Executive chat ID
CHAT_ID = os.environ.get('EXECUTIVE_CHAT_ID')
# dictionary kay to stored data
data_key = ""
# fullname if inserted manually
fullname = ""
# users dictionary - per l'uso contemporaneo
users_dict = {}


def _set(starting_infos: telegram.User):
    users_dict[starting_infos.username] = UserInfos(
        username=starting_infos.username,
        id=starting_infos.id,
        link="https://t.me/" + starting_infos.username,
        name=starting_infos.name,
        lm_ids=MessagesIds(
            last_user_message_id=0,
            last_group_message_id=0
        ),
        checks=Checks(
            fullname_check=False,
            signin_up_note_check=False
        )
    )
    if starting_infos.last_name is not None:
        users_dict[starting_infos.username].first_name = starting_infos.first_name
        users_dict[starting_infos.username].last_name = starting_infos.last_name
        users_dict[starting_infos.username].full_name = \
            users_dict[starting_infos.username].first_name + " " + users_dict[starting_infos.username].last_name
