from mycroft import MycroftSkill, intent_file_handler


class RespeakerPixelRingFeedback(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('feedback.ring.pixel.respeaker.intent')
    def handle_feedback_ring_pixel_respeaker(self, message):
        self.speak_dialog('feedback.ring.pixel.respeaker')


def create_skill():
    return RespeakerPixelRingFeedback()

