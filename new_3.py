# import flask related
from flask import Flask, request, abort
# import linebot related
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    LocationSendMessage, ImageSendMessage, StickerSendMessage
)

# create flask server
app = Flask(__name__)
# your linebot message API - Channel access token (from LINE Developer)
line_bot_api = LineBotApi('G2mMeGi8PlsUaJ+W0YhKmATu+e83H/stMTc+1QHb63wb0g0ZytRGxpzmpf+PeokolbXCjznPkHwHxkKKgXOvvJgYoTHAxO41Wn5ndqp2S4iTRGDMRHW3ftFLGDXKP5DEPWkIRWSAUooOv9gWno6J0AdB04t89/1O/w1cDnyilFU=')
# your linebot message API - Channel secret
handler = WebhookHandler('38cb8adc5a588518eb547b35dfa285c9')
# Linebot webhook URL (only survive 2 hours)
NGROK_URL = 'https://1fb164f30ad2.ngrok.io'

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        print('receive msg')
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

# handle msg
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # get user info & message
    user_id = event.source.user_id
    msg = event.message.text
    user_name = line_bot_api.get_profile(user_id).display_name
    
    # get msg details
    print('msg from [', user_name, '](', user_id, ') : ', msg)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '不要吵！'))
    line_bot_api.reply_message(event.reply_token, StickerSendMessage(text = '不要吵！'))

# run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=12345)