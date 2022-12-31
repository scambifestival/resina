import os
from dataclasses import dataclass

import telegram


@dataclass
class LastMessages:
    last_user_message: telegram.Message
    last_group_message: telegram.Message
    first_user_message: telegram.Message
    first_group_message: telegram.Message


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
    last_mess: LastMessages
    checks: Checks
    first_name: str = ""
    last_name: str = ""
    full_name: str = ""
    full_name_temp: str = ""


# Bot token
TOKEN = os.environ.get('BOT_TOKEN')
# Executive chat ID
CHAT_ID = os.environ.get('EXECUTIVE_CHAT_ID')
# users dictionary - per l'uso contemporaneo
users_dict = {}


def _set(starting_infos: telegram.User, starting_message: telegram.Message):
    users_dict[starting_infos.username] = UserInfos(
        username=starting_infos.username,
        id=starting_infos.id,
        link="https://t.me/" + starting_infos.username,
        name=starting_infos.name,
        last_mess=LastMessages(
            last_user_message=starting_message,
            last_group_message=starting_message,
            first_user_message=starting_message,
            first_group_message=starting_message
        ),
        checks=Checks(
            fullname_check=False,
            signin_up_note_check=False,
        )
    )
    if starting_infos.last_name is not None:
        users_dict[starting_infos.username].first_name = starting_infos.first_name
        users_dict[starting_infos.username].last_name = starting_infos.last_name
        users_dict[starting_infos.username].full_name = \
            users_dict[starting_infos.username].first_name + " " + users_dict[starting_infos.username].last_name
