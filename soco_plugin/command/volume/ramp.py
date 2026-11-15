import logging
import enum

import soco
from soco_plugin.message import Command as Parent
from soco_plugin.command import Mixin


class Command(Parent):
    """Ramp the player volume to the ``volume`` property of the new state.

    It is sent when the volume of a fading player changes while it stays in
    the same state. Entering a fade sets its starting volume through
    :class:`soco_plugin.command.volume.absolute.Command`.

    >>> import home
    >>> import soco_plugin

    >>> cmd = soco_plugin.command.volume.ramp.Command.make(["Bath"])
    >>> old_state = home.appliance.sound.player.state.off.State()
    >>> old_state = old_state.next(home.event.presence.Event.On)
    >>> old_state = old_state.next(home.event.sleepiness.Event.Asleep)
    >>> fading = old_state.next(home.event.sleepiness.Event.Awake)
    >>> cmd.make_msgs_from(old_state, fading)
    []
    >>> louder = fading.next(home.appliance.sound.player.event.fade_in.volume.Event(40))
    >>> msg = cmd.make_msgs_from(fading, louder)
    >>> msg[0]["fields"]["volume"]
    40
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
        if (
            new_state.is_fading
            and type(old_state) is type(new_state)
            and old_state.volume != new_state.volume
        ):
            self.msg["fields"]["volume"] = new_state.volume
            result = self.execute()
        return result


def action(player: soco.SoCo, volume: int, ramp_type: str):
    try:
        logging.getLogger(__name__).debug("Ramp %s" % player.player_name)
        player.ramp_to_volume(int(volume), ramp_type)
    except Exception as e:
        logging.getLogger(__name__).error(e)
