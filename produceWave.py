import json
import wave
import sys
cacheFile = 'output.txt'
audioFile = 'grace.wav'
indexFile = 'index.txt'

if __name__ == '__main__':
    i =1
    indexFp = open(indexFile,'w',encoding='utf-8')
    with open(cacheFile,'r',encoding='utf-8') as load_f:
        j = load_f.readline()
        while j != '' :
            parsed = json.loads(j)
            text = parsed['DisplayText']
            startTime = parsed['Offset']/10000000
            length= parsed['Duration']/10000000
            print("ffmpeg -ss {2} -t {3} -i  {0} -y -nostdin -f wav -ar 16000 -ac 1 -acodec pcm_s16le {1:05d}.wav ".format(audioFile,i, startTime,length))
            indexFp.write("{0:09d}\t{1}\n".format(i,parsed['DisplayText']))
            i += 1
            j = load_f.readline()

    indexFp.close()