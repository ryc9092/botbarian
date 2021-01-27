import os
import yaml


"""
Config
"""


def load_config(config_path='./resources/app.yml'):
    with open(config_path) as f:
        return yaml.load(f)

CONFIG = load_config()


"""
Reply
"""


SECTION_REPLY = "reply"

REPLY_STICKER_MESSAGE = CONFIG[SECTION_REPLY]['sticker_message']


"""
Tide
"""


SECTION_TIDE = "tide"

TIDE_URL = CONFIG[SECTION_TIDE]['url']
REPLY_TITLE = CONFIG[SECTION_TIDE]['reply_title']
ALERT_THRESHOLD = CONFIG[SECTION_TIDE]['alert_threshold']
