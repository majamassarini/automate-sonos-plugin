import logging

import soco
from soco_plugin.message import Command as Parent
from soco_plugin.command import Mixin


class Command(Parent):
    """
    >>> import home
    >>> import soco_plugin

    >>> cmd = soco_plugin.command.volume.relative.Command.make(["Bath"])
    >>> old_state = home.appliance.sound.player.state.off.State()
    >>> new_state = old_state.next(home.appliance.sound.player.event.forced.Event.On)
    >>> new_state = new_state.next(home.appliance.sound.player.event.volume.Event(66))
    >>> new_state = new_state.next(home.appliance.sound.player.event.sleepy_volume.Event(33))
    >>> new_state = new_state.next(home.event.sleepiness.Event.Awake)
    >>> msg = cmd.make_msgs_from(old_state, new_state)
    >>> msg[0]["fields"]["delta"]
    10
    >>> new_state = new_state.next(home.event.sleepiness.Event.Sleepy)
    >>> msg = cmd.make_msgs_from(old_state, new_state)
    >>> msg[0]["fields"]["delta"]
    10
    """

    ACTION = "relative_volume"

    Msg = {"type": "soco", "name": ACTION, "fields": {"delta": 10}, "addresses": []}

    def make_msgs_from(self, old_state: Mixin, new_state: Mixin):
        result = []
        if new_state.is_on and (
            (old_state.is_on != new_state.is_on)
            or (old_state.volume != new_state.volume)
        ):
            result = self.execute()
        return result


def action(player: soco.SoCo, delta: int):
    try:
        player.volume += delta
    except Exception as e:
        logging.getLogger(__name__).error(e)
