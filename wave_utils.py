# -*- coding: utf-8 -*-
# don't name file name as module name, otherwise wave.open will fail
import wave
from pyaudio import PyAudio,paInt16
import struct


file_buf_name ='02.wav'
framerate=16000
chunk=2014
NUM_SAMPLES=chunk
channels=1
sampwidth=2
TIME=20


def get_wave_header(frame_rate,stream=True):
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
    # user 0 length for audio stream
    if stream :
        data += struct.pack('<L', 0)
    else:
        data += struct.pack('<L', 1900000)
        
    data += b'WAVE'
    data += b'fmt '
    data += struct.pack('<L', 16)
    data += struct.pack('<H', 0x0001)
    data += struct.pack('<H', nchannels)
    data += struct.pack('<L', frame_rate)
    data += struct.pack('<L', frame_rate * nchannels * bytes_per_sample)
    data += struct.pack('<H', nchannels * bytes_per_sample)
    data += struct.pack('<H', bytes_per_sample * 8)
    #wrong format
    #data += struct.pack('<H', 0)
    data += b'data'
    if stream :
        data += struct.pack('<L', 0)
    else:
        data += struct.pack('<L', 1900000-36)
        

    return data

def  recordAsStream(filename):
    '''
    test function. hand made wave header 
    '''
    pa=PyAudio()
    print("Say something:")
    stream=pa.open(format = paInt16,channels=1,
                   rate=framerate,input=True,
                   frames_per_buffer=chunk)
    my_buf=[]
    count=0
    with  open(filename,'wb') as fp:
        waveheader = get_wave_header(framerate,stream=False)
        fp.write(waveheader)

        while count<TIME:#控制录音时间
            string_audio_data = stream.read(chunk)
            my_buf.append(string_audio_data)
            count+=1
            print('.',end = ' ')
        print("\nRecord end.")
        fp.write(b''.join(my_buf))
    stream.close()



def save_wave_file(filename,data):
    '''save the date to the wavfile'''
    wf=wave.open(filename,'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(sampwidth)
    wf.setframerate(framerate)
    wf.writeframes(b"".join(data))
    wf.close()

def my_record(filename):
    ''' record microphone audio  to file, use wave module'''
    pa=PyAudio()
    print("Say something:")
    stream=pa.open(format = paInt16,channels=1,
                   rate=framerate,input=True,
                   frames_per_buffer=NUM_SAMPLES)
    my_buf=[]
    count=0
    while count<TIME:#控制录音时间
        string_audio_data = stream.read(NUM_SAMPLES)
        my_buf.append(string_audio_data)
        count+=1
        print('.',end = ' ')
    print("\nRecord end.")
    save_wave_file(filename,my_buf)
    stream.close()


def play(filename):
    wf=wave.open(filename,'rb')
    p=PyAudio()
    stream=p.open(format=p.get_format_from_width(wf.getsampwidth()),channels=
    wf.getnchannels(),rate=wf.getframerate(),output=True)
    while True:
        data=wf.readframes(chunk)
        # use bytes"" as end of chunk
        if data==b"":break
        stream.write(data)
    stream.close()
    p.terminate()

if __name__ == '__main__':
    #my_record()
    recordAsStream(file_buf_name)
    print('Over!') 
    play(file_buf_name)
