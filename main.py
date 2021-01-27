import os

from apscheduler.schedulers.background import BackgroundScheduler 
from linebot import LineBotApi, WebhookHandler

import app
import config
from db import db_api
from handler import make_reply, get_alert_tide_data


def alert_tide_info():
    """
    This method push tide info to group/users.
    """
    text = get_alert_tide_data(alert_tidal_range=config.ALERT_THRESHOLD)
    if text:
        for target in db_api.get_push_msg_setting():
            app.line_bot_api.push_message(target, text)


if __name__ == "__main__":
    # Initialize database schema
    db_api.init_db(os.environ.get('DATABASE_URL'))

    # Start schedular
    scheduler = BackgroundScheduler()
    scheduler.add_job(alert_tide_info, 'cron', day='*',
                      misfire_grace_time=86400, coalesce=True)
    scheduler.start()

    # Start server
    app.start_server()
