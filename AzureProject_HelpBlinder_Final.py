import http.client, urllib.request, urllib.parse, urllib.error, base64
import requests, uuid, json
import time
import re
from random import sample
import azure.cognitiveservices.speech as speechsdk
from apiclient.discovery import build

import os



def image_to_text(img_data):
    #connect API: Computer Vision(detect text on the picture)
    #local img file: 'Content-Type': 'application/octet-stream'
    #img URL:'Content-Type': 'application/json'
    headers_cv = {
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': '79787c2cba6640c688aa28214ca84cdb',
    }

    params_cv = urllib.parse.urlencode({
        'language': 'unk', #AutoDetect自動偵測語言
        'detectOrientation ': 'true',
    })

    conn = http.client.HTTPSConnection('southcentralus.api.cognitive.microsoft.com')
    
    #Code:圖片偵測「文字」與「語言」
    # photo = "{'url':'%s'}"%(image_url)
    photo = img_data
    conn.request("POST", "/vision/v1.0/ocr?%s" % params_cv, photo, headers_cv)
    response = conn.getresponse()
    data = response.read()
    parsed = json.loads(data)
    lang=parsed['language'] #英文en/繁中zh-Hant/簡中zh-Hans
    
    #connect API: Translate(translate English to Chinese)
    subscription_key = "7dc4a96f371d44b5abc3a79fb8dd1275"
    endpoint = "https://api.cognitive.microsofttranslator.com/"
    location = "global"
    path = '/translate'
    constructed_url = endpoint + path
    params = {
        'api-version': '3.0',
        'from': 'en',
        'to': 'zh-Hant'
    }
    constructed_url = endpoint + path
    headers = {
        'Ocp-Apim-Subscription-Key': subscription_key,
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    # Code:翻譯-英翻中
    # 寫判斷句：若為英文→英翻中；若為簡中與繁中→使用圖片偵測出來的文字；其他→無此服務        
    if lang == 'en':
        ocr_text=" "
        for sentence in parsed['regions'][0]['lines']:
            for words in sentence['words']: 
                ocr_text+=words['text']+" "
        body = [{'text': ocr_text}] 
        request = requests.post(constructed_url, params=params, headers=headers, json=body)
        response = request.json()
        ocr_text=response[0]['translations'][0]['text']
        print(ocr_text)

    elif lang == 'zh-Hant' or 'zh-Hans':
        ocr_text=" "
        for sentence in parsed['regions'][0]['lines']:
            for words in sentence['words']: 
                ocr_text+=words['text']
        print(ocr_text)
                
    else:
        print('很抱歉，此服務僅提供中文與英文查詢')

    conn.close()    
    
    #回傳值
    return ocr_text

def text_to_speech(ocr_text,filename):    
    #connect API: Text-to-Speech
    speech_key, service_region = "492b3d4205594a4fb05920a6281c9b4e", "southcentralus"
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region,speech_recognition_language='zh-TW')
    speech_config.speech_synthesis_language = 'zh-TW' #set language of speech
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    
    #Code: Text-to-Speech(save as wave file)
    if not os.path.exists('./static/audio/'):
        os.makedirs('./static/audio/')
    audio_filename = "./static/audio/%s.wav"%(filename)
    audio_output = speechsdk.audio.AudioOutputConfig(filename=audio_filename)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)
    audio_result = speech_synthesizer.speak_text_async(ocr_text).get()#create an audio file
    
def text_to_ytsearch(ocr_text):    
    #connect API: Youtube Data API v3
    api_key='AIzaSyAFOER3IwBh6IvTWGAhvW2ay7vFlvNBq58'
    youtube=build('youtube','v3',developerKey=api_key)
                      
    #Code: Connect Youtube Search Engine (每日搜尋上限為10,000筆結果)
    req=youtube.search().list(q=ocr_text,part='snippet',type='video',maxResults=5) 
    res=req.execute()
    results = list()
    for item in res['items']:
        vid_obj = dict()
        vid_obj['video_thumbnails']=item['snippet']['thumbnails']['medium']['url']  
        vid_obj['video_url']='https://www.youtube.com/watch?v='+item['id']['videoId']
        results.append(vid_obj)
    return results
        
        
        