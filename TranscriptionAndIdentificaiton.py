import tkinter as tk                # python 3
from tkinter import font  as tkfont # python 3
from tkinter import messagebox
import pyaudio, wave, CreateProfile, json, EnrollProfile, utils, websocketSpeech, wave_utils, produceWave, Timer, threading, os, IdentifyFile, PrintAllProfiles

from tkinter.filedialog import askopenfilename

#import Tkinter as tk     # python 2
#import tkFont as tkfont  # python 2

##speakerProfiles = {'7f459648-ee2e-4903-91b4-0145a1bafb88':'grace'}

LANG = 'zh-CN'

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

Audio = pyaudio.PyAudio()
Frames = []
stream = None

IMPORTED_FILE = ''

SUB_KEY = '583b8f19ffa24b27b6868f4c2e4b1611'

# Replace the subscriptionKey string value with your valid subscription key.
pay_key = '2ed2a4769d5c41fd9fdd771d74721f9e'
api_key = 'df3d3d0c608548e6872c3d6ec96dcf5a'
##api_key_asia = 'a584b4af890b4614a651b3fee9f83019'

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
params = '?language='+LANG

#west URL
url = api_host+path+params
key = api_key
auth_url = AUTH_URL


class TIApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Transcription and Speaker Identification")
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.geometry("1024x576")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, AddProfile, Identify):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):


        def change_dropdown(*args):
            LANG = selected_locale.get()
            with open("UserData", 'r') as ud:
                jud = json.load(ud)
                ##jud["locale"] = LANG
            with open("UserData", 'w') as ud:
                jud.update({"locale": LANG})
                json.dump(jud, ud)

            print(LANG)
        def _saveKey():

            SUB_KEY = idEntry.get()
            with open("UserData", 'r') as ud:
                jud = json.load(ud)
            with open("UserData", 'w') as ud:
                jud["ActivationKey"] = SUB_KEY
                json.dump(jud, ud)

        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Welcome", font=controller.title_font)

        label1 = tk.Label(self, text="Select a language locale: ")

        label2 = tk.Label(self, text="Azure Speaker Recognition Sub Key: ")

        idEntry = tk.Entry(self, width=40)


        button1 = tk.Button(self, text="Add a New Speaker Profile",
                            command=lambda: controller.show_frame("AddProfile"),
                            width = 80, height = 5)
        button2 = tk.Button(self, text="Process an Audio File",
                            command=lambda: controller.show_frame("Identify"),
                            width = 80, height = 5)

        saveButton = tk.Button(self, text="Save",
                               command=_saveKey)


        with open("UserData", 'r') as ud:
            userdata = json.load(ud)
            print(userdata)
            if userdata["activationKey"] != 0:
                idEntry.insert('end', userdata["activationKey"])

        ##print(userdata.keyitems())
        locale = userdata["locale"]
        SUB_KEY = userdata["activationKey"] if userdata["activationKey"] != 0 else '583b8f19ffa24b27b6868f4c2e4b1611'

        locales = {'en-US', 'zh-CN', 'es-ES', 'fr-FR'}
        selected_locale= tk.StringVar(parent)

        if locale != "":
            selected_locale.set(locale)
        else:
            selected_locale.set('zh-CN')

        popupMenu = tk.OptionMenu(self, selected_locale, *locales)

        selected_locale.trace('w', change_dropdown)
        ##print(LANG)


        label.place(x=512, y = 30, anchor='center')
        label1.place(x=470, y=80, anchor ='center')
        popupMenu.place(x=600, y=80, anchor ='center')

        label2.place(x=300, y=120, anchor='center')
        idEntry.place(x=600, y=120, anchor='center')
        saveButton.place(x=815, y=120, anchor='center')

        button1.place(x=512, y=200, anchor = 'center')
        button2.place(x=512, y=325, anchor = 'center')


class AddProfile(tk.Frame):

    def __init__(self, parent, controller):

        def _createProfile():
            name = nameEntry.get()
            nameEntry.delete(0, 'end')
            if name=="":
                messagebox.showerror("Invalid Name", "A valid name is required to proceed")

            else:

                id = CreateProfile.create_profile(SUB_KEY, LANG)
                print(type(id))
            
                with open('SpeakerProfiles.json') as jf:
                    jDecoded = json.load(jf)
                jDecoded.update({id:name})
                with open('SpeakerProfiles.json', 'w') as jf:
                    json.dump(jDecoded, jf)
                
                EnrollProfile.enroll_profile(SUB_KEY, id, WAVE_OUTPUT_FILENAME, 'true')

                timeLabel.configure(text="")

                AudioTimer.reset()


        def _startRecord():

            stream = Audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK)
            AudioTimer.start()
            data = stream.read(CHUNK)

            Frames.append(data)
        def _stopRecord():
            try:
                stream.stop_stream()
                stream.close()
                Audio.terminate()
                timeStr = AudioTimer.stop()
                print(timeStr)
                print(AudioTimer.elapsetime)

                waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
                waveFile.setnchannels(CHANNELS)
                waveFile.setsampwidth(Audio.get_sample_size(FORMAT))
                waveFile.setframerate(RATE)
                waveFile.writeframes(b''.join(Frames))
                waveFile.close()

                assert(AudioTimer.elapsetime > 10)
                timeLabel.configure(text="Audio Recorded! Profile Audio Length: "+timeStr+"\n Press Create to upload")
            except AssertionError:
                messagebox.showerror("Incompete Recording", "Profile audio need to be at least 10s. Yours is "+timeStr)
            except:
                messagebox.showerror("Record Fail", "Unable to record an audio")


        AudioTimer = Timer.Timer()


        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Add a new speaker profile", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        nameLabel =tk.Label(self, text="Name:")

        nameEntry = tk.Entry(self)

        timeLabel = tk.Label(self, text="")


        recordButton = tk.Button(self, text="Record", width=30,
                                 command=_startRecord)

        stopButton = tk.Button(self, text="Stop", width=30,
                               command=_stopRecord)
        
        button = tk.Button(self, text="Go Back to Main Menu", width=65,
                           command=lambda: controller.show_frame("StartPage"))


        createButton = tk.Button(self, text="Create Profile", width=65,
                                 command=_createProfile)

        nameLabel.place(x=425, y=70, anchor ='center')
        nameEntry.place(x=535, y=70, anchor ='center')
        recordButton.place(x=375, y=320, anchor='center')
        stopButton.place(x=650, y=320, anchor='center')
        timeLabel.place(x=512, y=200, anchor='center')
        button.pack(side='bottom', pady=10)
        createButton.pack(side='bottom', pady=10)


class Identify(tk.Frame):

    def __init__(self, parent, controller):
        def _importFile():


            IMPORTED_FILE = askopenfilename()
            print("Selected file: ", IMPORTED_FILE)
            ##print(type(IMPORTED_FILE))

        ##def _process():
            display.config(state='normal')
            display.delete(1.0, 'end')
            display.insert('end', "Processing. Please Wait")
            display.config(state='disable')

            print(IMPORTED_FILE)
            webCMD = 'python websocketSpeech.py '+IMPORTED_FILE
            print(webCMD)
            os.system("%s %s %s" % ('python', 'websocketSpeech.py', IMPORTED_FILE))

            indexFile = 'index.txt'
            cacheFile = 'output.txt'
            i = 1
            indexFp = open(indexFile, 'w', encoding='utf-8')
            with open(cacheFile, 'r', encoding='utf-8') as load_f:
               lines = load_f.readlines()
               for j in lines:
                   parsed = json.loads(j)
                   text = parsed['DisplayText']
                   startTime = parsed['Offset'] / 10000000
                   length = parsed['Duration'] / 10000000
                   ##print(
                   cmd = "ffmpeg -ss {2} -t {3} -i  {0} -y -nostdin -f wav -ar 16000 -ac 1 -acodec pcm_s16le AudioSegments/{1:05d}.wav ".format(
                           IMPORTED_FILE, i, startTime, length)
                   ##)
                   os.system(cmd)

                   indexFp.write("{0:09d}\t{1}\n".format(i, parsed['DisplayText']))
                   i += 1

            indexFp.close()

            display.config(state='normal')
            display.delete(1.0, 'end')
            with open(indexFile, 'r') as c:
               content = c.readlines()
               for i, line in enumerate(content):
                   text = line.split('\t')[-1]
                   index = line.split('\t')[0][4:]
                   print(index)
                   ids = PrintAllProfiles.print_all_profiles(SUB_KEY)
                   returned_p_id = IdentifyFile.identify_file(SUB_KEY, 'AudioSegments/%s.wav' % index, 'true', ids)
                   with open('SpeakerProfiles.json') as sp:
                       names = json.load(sp)
                   returned_name = names[returned_p_id]
                   final_text = "{0}: \t".format(returned_name) + text

                   display.insert('end', final_text)



            display.config(state='disabled')




        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Audio Processing", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
       
        sb = tk.Scrollbar(self)
        display = tk.Text(self)
        sb.pack(side='right', fill='y')
        display.pack(side='left', fill= 'x')
        sb.config(command=display.yview)
        display.config(yscrollcommand=sb.set)
        display.insert('end', "Upload a wav file to Start \n (Encoding: \t PCM Sample rate: 16k \t Sample format: 16 bit \t Chanel: Mono) ")
        display.config(state='disabled')
        display.pack(fill = "x", ipady=10)


        button = tk.Button(self, text="Go Back to Main Menu", width = 20,
                          command=lambda: controller.show_frame("StartPage"))
        button.pack(side='bottom', fill = "y", pady = 10)



        importButton = tk.Button(self, text="Import a Audio file", width=20,
                                 command=_importFile)
        importButton.pack(side='top', fill ='y', pady = 10)

        ##processButton = tk.Button(self, text="Process", width=20,
        ##                          command = _importFile)
        ##processButton.pack(side='top', fill='y', pady=10)

if __name__ == "__main__":
    app = TIApp()
    app.mainloop()
