import logging
import enum

import soco
from soco_plugin.message import Command as Parent
from soco_plugin.command import Mixin


class Command(Parent):
    """
    >>> import home
    >>> import soco_plugin

    >>> cmd = soco_plugin.command.volume.ramp.Command.make(["Bath"])
    >>> old_state = home.appliance.sound.player.state.off.State()
    >>> old_state = old_state.next(home.event.presence.Event.On)
    >>> old_state = old_state.next(home.event.sleepiness.Event.Asleep)
    >>> new_state = old_state.next(home.event.sleepiness.Event.Awake)
    >>> msg = cmd.make_msgs_from(old_state, new_state)
    >>> msg[0]["fields"]["volume"]
    30
    >>> msg[0]["fields"]["ramp_type"]
    'SLEEP_TIMER_RAMP_TYPE'
    """

    class RampType(enum.Enum):
        SLEEP_TIMER_RAMP_TYPE = "SLEEP_TIMER_RAMP_TYPE"
        ALARM_RAMP_TYPE = "ALARM_RAMP_TYPE"
        AUTOPLAY_RAMP_TYPE = "AUTOPLAY_RAMP_TYPE"

    ACTION = "ramp_to_volume"

    Msg = {
        "type": "soco",
        "name": ACTION,
        "fields": {"volume": 10, "ramp_type": "SLEEP_TIMER_RAMP_TYPE"},
        "addresses": [],
    }

    def make_msgs_from(self, old_state: Mixin, new_state: Mixin):
        result = []
        if new_state.is_fading:
            self.msg["fields"]["volume"] = new_state.volume
            result = self.execute()
        return result


def action(player: soco.SoCo, volume: int, ramp_type):
    try:
        logging.getLogger(__name__).debug("Ramp %s" % player.player_name)
        player.ramp_to_volume(volume, ramp_type)
    except Exception as e:
        logging.getLogger(__name__).error(e)
