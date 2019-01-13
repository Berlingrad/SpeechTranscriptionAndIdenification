import time

class Timer:
    def __init__(self):
        self._start = 0.0
        self.elapsetime = 0.0
        self._running = False
        self.timestr = ""

    def getTime(self):
        self._elapsetime = time.time() - self._start
        self.timestr=time.strftime("%M:%S", time.gmtime(self.elapsetime))
        return self.timestr

    def start(self):
        if not self._running:
            self._start = time.time() - self.elapsetime
            self._running = True

    def stop(self):
        if self._running:
            self._running = False
            return self.getTime()
    def reset(self):
        self._start = 0.0
        self._elapsetime = 0.0
        self._running = False



