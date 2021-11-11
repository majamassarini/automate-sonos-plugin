from soco_plugin.message import Trigger as Parent


class Trigger(Parent):

    ACTION = "pause"

    Msg = {"type": Parent.PROTOCOL, "name": ACTION, "fields": {}, "addresses": []}
