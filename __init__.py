from mycroft import MycroftSkill, intent_file_handler
from mycroft_bus_client import MessageBusClient, Message

from .lib.pixels import Pixels

class ReSpeakerPixelFeedback(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        self.add_events()
        self.use_settings()

        self.pixels = Pixels(pattern=self.pixel_pattern, num_pixels=self.device_num_pixels)

    def use_settings(self):
        self.device_type = self.settings.get('device_type')
        self.device_num_pixels = self.settings.get('device_num_pixels')
        self.pixel_pattern = self.settings.get('pixel_pattern')

    def on_settings_changed(self):
        self.use_settings()

    def add_events(self):
        # add events for basic recognition
        self.add_event('recognizer_loop:wakeword', self.handle_wakeup)
        self.add_event('recognizer_loop:record_begin', self.handle_output)
        self.add_event('recognizer_loop:record_end', self.handle_stop)
        self.add_event('recognizer_loop:audio_output_start', self.handle_output)
        self.add_event('recognizer_loop:audio_output_end', self.handle_stop)
        # add events for question skill
        self.add_event('question.query', self.handle_processing)
        self.add_event('question.query.response', self.handle_output)
        # add events for audio
        self.add_event('mycroft.audio.service.play', self.handle_output)
        self.add_event('mycroft.audio.service.stop', self.handle_stop)
        self.add_event('mycroft.audio.service.pause', self.handle_stop)
        self.add_event('mycroft.audio.service.resume', self.handle_output)
        # add events for skill handlers
        self.add_event('mycroft.skill.handler.start', self.handle_processing)
        self.add_event('mycroft.skill.handler.complete', self.handle_stop)
        # other events
        self.add_event('complete_intent_failure', self.handle_stop)

    def handle_listen(self, message):
        self.pixels.listen()

    def handle_wakeup(self, message):
        self.pixels.wakeup()

    def handle_processing(self, message):
        self.pixels.think()

    def handle_output(self, message):
        self.pixels.speak()

    def handle_stop(self, message):
        self.pixels.off()

    @intent_file_handler('pixel.get.pattern.intent')
    def handle_pixel_get_pattern(self, message):
        self.speak_dialog('pixel.get.pattern', {pattern: self.pixel_pattern})
        pass

    @intent_file_handler('pixel.set.pattern.intent')
    def handle_pixel_set_pattern(self, message):
        pattern = message.data.get('pattern')
        if pattern is not None:
            # check patterns
            if pattern in ['alexa', 'google']:
                self.pixel_pattern = pattern
                self.speak_dialog('pixel.set.pattern', {pattern: self.pixel_pattern})
            else:
                self.speak_dialog('pixel.set.pattern.fail', {pattern: pattern})
        else:
            self.speak.dialog('pixel.set.pattern.fail.unknown')

    @intent_file_handler('pixel.show.intent')
    def handle_pixel_show(self, message):
        kind = message.data.get('kind')
        if kind is not None:
            # todo: translate kind
            if kind in ['wakeup', 'listen', 'think', 'process', 'speak']:
                if kind == 'wakeup':
                    self.pixel.wakeup()
                    time.sleep(3)
                    self.pixel.stop()

                elif kind == 'listen':
                    self.pixel.listen()
                    time.sleep(3)
                    self.pixel.stop()

                elif kind == 'think' or kind == 'process':
                    self.pixel.think()
                    time.sleep(3)
                    self.pixel.stop()

                elif kind == 'speak' or kind == 'output':
                    self.pixel.speak()
                    time.sleep(3)
                    self.pixel.stop()

                else:
                    self.speak_dialog('pixel.show.fail', {kind: kind})
            else:
                self.speak_dialog('pixel.show.fail', {kind: kind})
        else:
            self.speak_dialog('pixel.show.fail.unknown')

    @intent_file_handler('pixel.stop.intent')
    def pixel_stop_handler(self, message):
        self.handle_stop()

def create_skill():
    return ReSpeakerPixelFeedback()

