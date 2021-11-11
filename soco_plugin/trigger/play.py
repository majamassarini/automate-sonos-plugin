from soco_plugin.message import Trigger as Parent


class Trigger(Parent):

    ACTION = "play"

    Msg = {"type": Parent.PROTOCOL, "name": ACTION, "fields": {}, "addresses": []}
