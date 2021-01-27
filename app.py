import os

from flask import Flask, request, abort
from flask_cors import CORS
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

from db import db_api
from handler import make_reply


app = Flask(__name__)
CORS(app)

# Channel Access Token
line_bot_api = LineBotApi(os.environ.get('line_channel_access_token'))
# Channel Secret
handler = WebhookHandler(os.environ.get('line_channel_secret'))


@app.route('/')
def index():
    return "Hello, World!"


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    reply = make_reply(text)
    if reply:
        line_bot_api.reply_message(event.reply_token, reply)


@handler.add(MessageEvent, message=StickerMessage)
def handle_message(event):
    reply = StickerSendMessage(package_id=event.message.package_id, sticker_id=event.message.sticker_id)
    try:
        reply_sticker = db_api.get_sticker_reply_setting()
        if reply_sticker:
            line_bot_api.reply_message(event.reply_token, reply)

    except LineBotApiError as e:
        print(f"Reply sticker message error: {e}")


def start_server():
    # Start server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
