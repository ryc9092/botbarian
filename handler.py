import requests

from bs4 import BeautifulSoup
from linebot.models import *

import config
from db import db_api
from parser import tide


def help_command():
    """
Web:
  https://botbarian.herokuapp.com/
Command:
  -help: List usage of this chatbot.
  -tide: List 7 days tide info.
  -switch: Switch sticker reply setting.
    """
    return TextSendMessage(help_command.__doc__)


def get_tide_info(days=7):
    r = requests.get(config.TIDE_URL)
    r.encoding = r.apparent_encoding

    soup = BeautifulSoup(r.text, "lxml")
    daily_tide_list = tide.tide_parser(soup)
    tide_data_list = tide.get_several_days_tide_data(daily_tide_list, days)
    title = f"{config.REPLY_TITLE}\n"
    formatted_tide_data = title + tide.format_tide_data(tide_data_list)

    return TextSendMessage(formatted_tide_data)


def switch_sticker_reply():
    switch = True
    current_setting = db_api.get_sticker_reply_setting()
    if current_setting is None:
        db_api.set_sticker_reply_setting(True)
    else:
        switch = not current_setting
        db_api.update_sticker_reply_setting(switch)

    reply = f"Switch sticker reply setting to {switch}"
    print(reply)
    return TextSendMessage(reply)


# The map of commands and methods.
COMMAND_METHOD_MAP = {
    "-help": help_command,
    "-tide": get_tide_info,
    "-switch": switch_sticker_reply,
}


def split_text(text):
    """
    Split text to command and parameter.

    Returns:
        tuple:
            [0] Is command in text is valid?
            [1] Command.
            [2] Parameter.
    """
    command = parameter = None
    splitted_text = text.split()

    is_valid_command = splitted_text[0] in COMMAND_METHOD_MAP.keys()
    is_correct_length = True if len(splitted_text) <=2 else False
    is_valid = is_valid_command and is_correct_length

    if is_valid:
        command = splitted_text[0]
        parameter = splitted_text[1] if len(splitted_text) is 2 else None

    return is_valid, command, parameter


def make_reply(text):
    """
    Params:
        text (str): Text from line app.

    Returns:
        linebot.models object: Message which replied to line app.
    """
    is_valid, command, parameter = split_text(text)

    if not is_valid:
        return

    reply = COMMAND_METHOD_MAP[command]()

    return reply


def get_tide_info_need_to_alert(alert_tidal_range):
    """
    This method return the latest tide info if tidal range is lower than <alert_tidal_range>.
    """
    r = requests.get(config.TIDE_URL)
    r.encoding = r.apparent_encoding

    soup = BeautifulSoup(r.text, "lxml")
    daily_tide_list = tide.tide_parser(soup)
    tide_data = tide.get_latest_tide_data(daily_tide_list)

    need_to_alert = False
    for tide_info in tide_data.tide_info_list:
        if int(tide_info["tidal_range"]) < alert_tidal_range:
            need_to_alert = True
            break

    formatted_tide_data = tide.format_tide_data([tide_data], emoji="") if need_to_alert else ""
    return formatted_tide_data


def get_alert_tide_data(alert_tidal_range=-100):
    """
    Push tide data to client if tidal range is lower than <low_tidal_range>.
    """
    print(f"Schedular start...")
    tide_data = get_tide_info_need_to_alert(alert_tidal_range)

    if tide_data:
        return TextSendMessage(tide_data)

    return None
