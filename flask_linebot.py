# import flask related
from flask import Flask, request, abort, send_from_directory
# import linebot related
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, AudioSendMessage, VideoSendMessage
)
from AzureProject_HelpBlinder_Final import *
import os
import wave
import contextlib
# create flask server
app = Flask(__name__)
# your linebot message API - Channel access token (from LINE Developer)
line_bot_api = LineBotApi('AoLCtbL0Q7oa5JVHfbSLCYvkMOagroiZPOI2Us4lMJcpN8t1YhHQgmz6km+mmLb0DLYB6/t9X+FgCgqF5V1bbqUWmQqY/zBILTP5N9rth4QuB8i6r024uCCQnmF96ilho3816oxySR+eLYos65+BBgdB04t89/1O/w1cDnyilFU=')
# your linebot message API - Channel secret
handler = WebhookHandler('9abe71bd007f6791fc06e3e977eba873')
# Linebot webhook URL (only survive 2 hours)
NGROK_URL = 'https://eb372f3fe052.ngrok.io'

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

# handle text msg
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # get user info & message
    user_id = event.source.user_id
    msg = event.message.text
    user_name = line_bot_api.get_profile(user_id).display_name
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = '請傳送照片使用幫幫盲服務！'))
# handle image msg
@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    # get user & message id
    user_id = event.source.user_id
    message_id = event.message.id
    # get image content
    message_content = line_bot_api.get_message_content(message_id)
    # write image file
    if not os.path.exists('./img/'):
        os.mkdir('./img/')
    with open('./img/%s_%s.jpg'%(user_id,message_id), 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
    # read local image file
    image_data = open('./img/%s_%s.jpg'%(user_id,message_id), "rb").read()
    # Using the functions implementing Azure API
    # image to text
    reply_text = image_to_text(img_data = image_data)
    # text to speech
    text_to_speech(reply_text,message_id)
    with contextlib.closing(wave.open('./static/audio/%s.wav'%(message_id),'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
    # search youtube video
    vids = text_to_ytsearch(reply_text)
    # reply messages
    SendMessages = list()
    SendMessages.append(TextSendMessage(text = reply_text))
    SendMessages.append(AudioSendMessage(original_content_url='%s/static/audio/%s.wav'%(NGROK_URL,message_id), duration=duration))
    if len(vids)>0 :
        for obj in vids:
            if len(SendMessages)==5:
                break
            SendMessages.append(TextSendMessage(text=obj['video_url']))
    line_bot_api.reply_message(event.reply_token,SendMessages)
    
# run app
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=12345)