import logging

import soco
from soco_plugin.message import Command as Parent
from soco_plugin.command import Mixin


class Command(Parent):
    """
    >>> import home
    >>> import soco_plugin

    >>> cmd = soco_plugin.command.stop.Command.make(["Bath"])
    >>> old_state = home.appliance.sound.player.state.off.State()
    >>> old_state = old_state.next(home.appliance.sound.player.event.forced.Event.On)
    >>> new_state = old_state.next(home.appliance.sound.player.event.forced.Event.Off)
    >>> msg = cmd.make_msgs_from(old_state, new_state)
    >>> msg[0]["name"]
    'stop'
    """

    ACTION = "stop"

    Msg = {"type": "soco", "name": ACTION, "fields": {}, "addresses": []}

    def make_msgs_from(self, old_state: Mixin, new_state: Mixin):
        result = []
        if (old_state.is_on != new_state.is_on) and not new_state.is_on:
            result = self.execute()
        return result


def action(player: soco.SoCo):
    try:
        player.stop()
    except Exception as e:
        logging.getLogger(__name__).error(e)
