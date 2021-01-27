from .db_table import ReplySetting, PushMessageSetting
from . import db_util
from . import db_table


def init_db(db_url):
    # Init DB table
    db_util.DATABASE_URL = db_url
    db_connector = db_util.DBConnector(db_url)
    db_table.Base.metadata.create_all(db_connector.engine)

    # Init table values
    if get_sticker_reply_setting() is None:
        set_sticker_reply_setting()


def set_sticker_reply_setting(sticker_reply=False):
    with db_util.session_context() as s:
        reply_setting = ReplySetting(stickerreply=sticker_reply)
        q = s.add(reply_setting)


def update_sticker_reply_setting(sticker_reply):
    with db_util.session_context() as s:
        q = s.query(ReplySetting).update({"stickerreply": sticker_reply})


def get_sticker_reply_setting():
    with db_util.session_context() as s:
        # Return None if no rows present.
        q = s.query(ReplySetting).scalar()
        return getattr(q, 'stickerreply') if q else q


def get_push_msg_setting():
    with db_util.session_context() as s:
        target_list = list()
        q = s.query(PushMessageSetting).filter(PushMessageSetting.push==True)

        for target in q:
            target_list.append(getattr(target, 'targetid'))

        return target_list