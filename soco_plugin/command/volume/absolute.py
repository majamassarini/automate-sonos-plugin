import logging

import soco
from soco_plugin.message import Command as Parent
from soco_plugin.command import Mixin


class Command(Parent):
    """
    >>> import home
    >>> import soco_plugin

    >>> cmd = soco_plugin.command.volume.absolute.Command.make(["Bath"])
    >>> old_state = home.appliance.sound.player.state.off.State()
    >>> new_state = old_state.next(home.appliance.sound.player.event.forced.Event.On)
    >>> new_state = new_state.next(home.appliance.sound.player.event.volume.Event(66))
    >>> new_state = new_state.next(home.appliance.sound.player.event.sleepy_volume.Event(33))
    >>> new_state = new_state.next(home.event.sleepiness.Event.Awake)
    >>> msg = cmd.make_msgs_from(old_state, new_state)
    >>> msg[0]["fields"]["value"]
    66
    >>> new_state = new_state.next(home.event.sleepiness.Event.Sleepy)
    >>> msg = cmd.make_msgs_from(old_state, new_state)
    >>> msg[0]["fields"]["value"]
    33
    """

    ACTION = "absolute_volume"

    Msg = {"type": "soco", "name": ACTION, "fields": {"value": 10}, "addresses": []}

    def make_msgs_from(self, old_state: Mixin, new_state: Mixin):
        result = []
        if new_state.is_on:
            self.msg["fields"]["value"] = new_state.volume
            result = self.execute()
        return result


def action(player: soco.SoCo, value: int):
    try:
        logging.getLogger(__name__).debug("Setting absolute volume %s" % player.player_name)
        player.volume = value
    except Exception as e:
        logging.getLogger(__name__).error(e)
