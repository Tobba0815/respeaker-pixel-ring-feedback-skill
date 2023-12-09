import time
import threading
from gpiozero import LED
try:
    import queue as Queue
except ImportError:
    import Queue as Queue

from .apa102 import APA102
from .pattern.alexa_led_pattern import AlexaLedPattern
from .pattern.google_home_led_pattern import GoogleHomeLedPattern

class Pixels:
    num_pixels = None
    controller = None
    patterns = {
        'google': GoogleHomeLedPattern,
        'alexa': AlexaLedPattern
    }
    def __init__(self, pattern="google", num_pixels=12):

        self.set_num_pixels(num_pixels)
        if self.set_pattern(pattern) == False:
            raise RuntimeError('pattern "{}" is not defined'.format(pattern))

        self.power = LED(5)
        self.power.on()

        self.queue = Queue.Queue()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

        self.last_direction = None

    def set_pattern(self, pattern_name):
        if pattern_name in self.patterns:
            pattern = self.patterns.get(pattern_name)
            self.pattern = pattern(show=self.show)
            return True
        else:
            return False

    def set_num_pixels(self, num_pixels):
        if self.controller is not None:
            self.controller.cleanup()

        self.num_pixels = num_pixels
        self.controller = APA102(num_led=num_pixels)

    ### generic feedback functions
    def info(self):
        #todo: show pixel feedback in lightblue
        pass

    def success(self):
        #todo: show pixel feedback in green
        pass

    def warning(self):
        #todo: show pixel feedback in yellow/orange
        pass

    def error(self):
        #todo: show pixel feedback in red
        pass

    ### pattern feedback functions
    def wakeup(self, direction=0):
        self.last_direction = direction
        def f():
            self.pattern.wakeup(direction)

        self.put(f)

    def listen(self):
        if self.last_direction:
            def f():
                self.pattern.wakeup(self.last_direction)
            self.put(f)
        else:
            self.put(self.pattern.listen)

    def think(self):
        self.put(self.pattern.think)

    def speak(self):
        self.put(self.pattern.speak)

    def off(self):
        self.put(self.pattern.off)

    def put(self, func):
        self.pattern.stop = True
        self.queue.put(func)

    def _run(self):
        while True:
            func = self.queue.get()
            self.pattern.stop = False
            func()

    def show(self, data):
        for i in range(self.num_pixels):
            self.controller.set_pixel(i, int(data[4*i + 1]), int(data[4*i + 2]), int(data[4*i + 3]))

        self.controller.show()
