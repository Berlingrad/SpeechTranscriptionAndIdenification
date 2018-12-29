import tkinter as tk                # python 3
from tkinter import font  as tkfont # python 3
import pyaudio, wave, CreateProfile, json, EnrollProfile

#import Tkinter as tk     # python 2
#import tkFont as tkfont  # python 2

speakerProfiles = {'7f459648-ee2e-4903-91b4-0145a1bafb88':'grace'}

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

Audio = pyaudio.PyAudio()
Frames = []
stream = None

SUB_KEY = '583b8f19ffa24b27b6868f4c2e4b1611'


class TIApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("Transcription and Identification")
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
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Welcome", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Add a New Speaker Profile",
                            command=lambda: controller.show_frame("AddProfile"),
                            width = 70)
        button2 = tk.Button(self, text="Process an Audio",
                            command=lambda: controller.show_frame("Identify"),
                            width = 70)
        button1.pack()
        button2.pack()


class AddProfile(tk.Frame):

    def __init__(self, parent, controller):

        def _createProfile():
            name = nameEntry.get()
            nameEntry.delete(0, 'end')
            id = CreateProfile.create_profile(SUB_KEY, 'zh-CN')
            print(type(id))
            
            with open('SpeakerProfiles.json') as jf:
                jDecoded = json.load(jf)
            jDecoded.update({id:name})
            with open('SpeakerProfiles.json', 'w') as jf:
                json.dump(jDecoded, jf)
                
            EnrollProfile.enroll_profile(SUB_KEY, id, WAVE_OUTPUT_FILENAME, 'true')


        def _startRecord():
            stream = Audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK)
            data = stream.read(CHUNK)

            Frames.append(data)
        def _stopRecord():
            stream.stop_stream()
            stream.close()
            Audio.terminate()

            waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(Audio.get_sample_size(FORMAT))
            waveFile.setframerate(RATE)
            waveFile.writeframes(b''.join(Frames))
            waveFile.close()





        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Add a new speaker profile", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        nameLabel =tk.Label(self, text="Name:")
        nameLabel.pack(side='top')

        nameEntry = tk.Entry(self)
        nameEntry.pack(side='top')


        recordButton = tk.Button(self, text="Record", width=50,
                                 command=_startRecord)
        recordButton.pack(side='left')

        stopButton = tk.Button(self, text="Stop", width=50,
                               command=_stopRecord)
        stopButton.pack(side='right')

        createButton = tk.Button(self, text="Create Profile", width=50,
                                 command=_createProfile)
        createButton.pack(side='bottom')

        button = tk.Button(self, text="Go Back to Main Menu", width=50,
                           command=lambda: controller.show_frame("StartPage"))
        button.pack(side='bottom')




class Identify(tk.Frame):

    def __init__(self, parent, controller):
        def _importFile():


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



        importButton = tk.Button(self, text="Import a Audio file", width=20)
        importButton.pack(side='top', fill ='y', pady = 10)

        processButton = tk.Button(self, text="Process", width=20)
        processButton.pack(side='top', fill='y', pady=10)

if __name__ == "__main__":
    app = TIApp()
    app.mainloop()
