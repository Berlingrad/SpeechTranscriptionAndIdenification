# -*- coding: utf-8 -*-

# To install this package, run:
#   pip install websocket-client
# Support unify speech services
import websocket
import wave
from pyaudio import PyAudio,paInt16
import threading
import time
import json
import argparse
import requests
import utils
import numpy as np 
import struct
import sys

import platform


startTime = time.time()
endTime = startTime
sendTime = startTime

FILE_NAME = None

# **********************************************
# *** Update or verify the following values. ***
# **********************************************

# Replace the subscriptionKey string value with your valid subscription key.
BING_KEY = '4f93f1d69c5b4d28bf26128930916cf1'
pay_key = '2ed2a4769d5c41fd9fdd771d74721f9e'
api_key = 'df3d3d0c608548e6872c3d6ec96dcf5a'
api_key_asia = 'a584b4af890b4614a651b3fee9f83019'

# Token请求地址
AUTH_URL = 'https://westus.api.cognitive.microsoft.com/sts/v1.0/issueToken'
ASIA_AUTH_URL = 'https://eastasia.api.cognitive.microsoft.com/sts/v1.0/issuetoken'
BING_AUTH_URL = 'https://api.cognitive.microsoft.com/sts/v1.0/issueToken'

#end point
#host = 'wss://speech.platform.bing.com'
api_host = 'wss://westus.stt.speech.microsoft.com'
bing_host = 'wss://speech.platform.bing.com'
asia_host = 'wss://eastasia.stt.speech.microsoft.com'
rest_host = 'https://westus.stt.speech.microsoft.com'
#conversation 适合做交互回话
#interactive 适合实现Rest API，单次应答
path = '/speech/recognition/conversation/cognitiveservices/v1'
params = '?language=zh-CN'

#west URL
url = api_host+path+params
key = api_key
auth_url = AUTH_URL
'''
#bing URL
url = bing_host+path+params
key = BING_KEY
auth_url = BING_AUTH_URL

'''
'''
#asia URL
url = asia_host+path+params
key = api_key_asia
auth_url = ASIA_AUTH_URL
'''
#uri = host + path + params

# UUID
connection_id = utils.generate_id()
request_id = utils.generate_id()

TIME= 20  #控制录音时间
#chunk_size=8192
chunk_size=2048

framerate=16000         #取样频率
NUM_SAMPLES = chunk_size      #pyaudio内置缓冲大小
LEVEL = 100         #声音保存的阈值

channels=1
sampwidth=2
INPUT_DEVICE_INDEX = 1

f = None

def tts_log(text,filename='output.txt'):
    global f
    if f == None :
        f = open(filename,'w',encoding='utf-8')
    f.write(text)

debug = False
def log(str):
    if debug :
        print(str)

def send_speech_config_msg(client):
    # assemble the payload for the speech.config message
    context = {
        'system': {
            'version': '5.4'
        },
        'os': {
            'platform': platform.system(),
            'name': platform.system() + ' ' + platform.version(),
            'version': platform.version()
        },
        'device': {
            'manufacturer': 'SpeechSample',
            'model': 'SpeechSample',
            'version': '1.0.00000'
        }
    }
    payload = {'context': context}

    # assemble the header for the speech.config message
    msg = 'Path: speech.config\r\n'
    msg += 'Content-Type: application/json; charset=utf-8\r\n'
    msg += 'X-Timestamp: ' + utils.generate_timestamp() + '\r\n'
    # append the body of the message
    msg += '\r\n' + json.dumps(payload, indent=2)

    # DEBUG PRINT
    # print('>>', msg)

    client.send(msg,websocket.ABNF.OPCODE_TEXT)

def build_chunk(audio_chunk):
    # assemble the header for the binary audio message
    msg = b'Path: audio\r\n'
    msg += b'Content-Type: audio/x-wav\r\n'
    msg += b'X-RequestId: ' + bytearray(request_id, 'ascii') + b'\r\n'
    msg += b'X-Timestamp: ' + bytearray(utils.generate_timestamp(), 'ascii') + b'\r\n'
    # prepend the length of the header in 2-byte big-endian format
    msg = len(msg).to_bytes(2, byteorder='big') + msg
    # append the body of the message
    msg += b'\r\n' + audio_chunk
    return msg

def send_audio_stream(client,buf):
    msg = build_chunk(buf)
    client.send(msg,websocket.ABNF.OPCODE_BINARY)

def send_audio_msg(client,audio_file_path):
    # open the binary audio file
    with open(audio_file_path, 'rb') as f_audio:
        num_chunks = 0
        while True:
            # read the audio file in small consecutive chunks
            audio_chunk = f_audio.read(chunk_size)
            #audio_chunk = f_audio.read()
            if not audio_chunk:
                break
            num_chunks += 1

            # assemble the header for the binary audio message
            msg = build_chunk(audio_chunk)

            client.send(msg,websocket.ABNF.OPCODE_BINARY)
            #print(num_chunks,end = ' ')
            #slow down send speed, 模拟实时音频 sleep 0.02
            time.sleep(0.02)



def get_wave_header(frame_rate):
    """
    Generate WAV header that precedes actual audio data sent to the speech translation service.
    :param frame_rate: Sampling frequency (8000 for 8kHz or 16000 for 16kHz).
    :return: binary string
    """

    if frame_rate not in [8000, 16000]:

        raise ValueError("Sampling frequency, frame_rate, should be 8000 or 16000.")

    nchannels = channels
    bytes_per_sample = sampwidth

    data = b'RIFF'
    data += struct.pack('<L', 0)
    data += b'WAVE'
    data += b'fmt '
    data += struct.pack('<L', 16)
    data += struct.pack('<H', 0x0001)
    data += struct.pack('<H', nchannels)
    data += struct.pack('<L', frame_rate)
    data += struct.pack('<L', frame_rate * nchannels * bytes_per_sample)
    data += struct.pack('<H', nchannels * bytes_per_sample)
    data += struct.pack('<H', bytes_per_sample * 8)
    #data += struct.pack('<H', 0)
    data += b'data'
    data += struct.pack('<L', 0)

    return data


def on_open (client):
    global startTime
    global sendTime
    endTime = time.time()
    print ("Connected. time",endTime - startTime)
    send_speech_config_msg(client)
    endTime = time.time()
    print ("Config msg sended. time",endTime - startTime)

    # send audio thread
    startTime = time.time()


    def sendThread():

        #stream audio file to speech services
        send_audio_msg(client, FILE_NAME)
        sendTime = time.time()
        client.close()
        print('Audio file sended. Send Time:',sendTime-startTime)

    t = threading.Thread(target=sendThread)
    t.setDaemon(True)
    t.start()

def on_data (client, message, message_type, is_last):
    global endTime
    endTime = time.time()
    #print ("Received text data. ",message)
    #print("Receive time = ", endTime - startTime)
    if (websocket.ABNF.OPCODE_TEXT == message_type):
        #print ("Received text. time = {0:0.2f} Real Time ={1:0.2f}".format(endTime - startTime, endTime -sendTime))
        #log (message)
        # decode response, is not a json file
        
        response_path = utils.parse_header_value(message, 'Path')
        if response_path is None:
            print('Error: invalid response header.')
            return


        parsed = utils.parse_body_json(message)
        Duration = parsed["Duration"]

        # Finally result use DisplayText as result
        # partial result use Text as result
        if response_path == 'speech.phrase':
            text = parsed["DisplayText"]
            offset = parsed["Offset"]
            #print ("Received Result. time = {0:.2f} Real Time = {1:.2f}".format( endTime - startTime,endTime -sendTime))
            print("Path:{2}\t Offset:{3} Duration:{1} STT Result:{0}".format(text,Duration/10000000,response_path,offset/10000000) )
            #print(parsed)
            #tts_log("Offset:{2} Duration:{1} Text:{0}\n".format(text,Duration/10000000,offset/10000000) )
            p = json.dumps(parsed)
            tts_log(p+'\n')
            #k = json.loads(p)
            #print(k)


        else:
            #parsed = json.loads(message)
            text = parsed["Text"]
            #print(text)
 
        if text == '结束会话。':
            client.close()
    else:
        print ("Received data of type: " + str (message_type))

def on_error (client, error):
    print ("Connection error: " + str (error))
    f.close()
    #client.close()

def on_close (client):
    print ("Connection closed.")
    f.close()





if __name__ == '__main__':
    '''
    # Parse input arguments
    parser = argparse.ArgumentParser(description='Speech Translator Demo script. use language.py to list support language')
    parser.add_argument("--source","-s", default = "zh-CN", help="recognition speech language.default is zh_CN")
    parser.add_argument("--to","-t", default = "en", help="translate language. default is en")
    parser.add_argument("--voice","-v", default = "en-US-BenjaminRUS", help="translate language. default is en-US-BenjaminRUS")


    parser.add_argument("--debug","-d", action="store_true", default =False,help="debug True/Flase")
    
    args = parser.parse_args()
    debug = args.debug
    ##debug = True
    #params = '?api-version=1.0&from={0}&to={1}&features=texttospeech,TimingInfo&voice={2}'.format(args.source,args.to,args.voice)
    #log(params)
    #url = host + path + params
    '''
    FILE_NAME = sys.argv[1]
    log(url)

    startTime = time.time()
    authToken = utils.obtain_auth_token(key,auth_url)
    endTime = time.time()
    print("Auth time:",endTime - startTime)
    print('X-ConnectionId: ' + connection_id)


    #authToken = str(auth_token,encoding = "utf-8")

    # recalcuate startTime, sentTime
    startTime = time.time()
    sendTime = startTime
    client = websocket.WebSocketApp(
        url,
        header=[
            'X-ConnectionId: ' + connection_id,
            'Authorization: ' +'Bearer '+authToken
        ],
        on_open=on_open,
        on_data=on_data,
        on_error=on_error,
        on_close=on_close
    )

    print ("Connecting...")
    client.run_forever()