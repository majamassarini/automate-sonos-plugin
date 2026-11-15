import logging
import enum

import soco
from soco_plugin.message import Command as Parent
from soco_plugin.command import Mixin


class Command(Parent):
    """Set the play mode (repeat, shuffle) of the player from its state.

    The mode is the ``play_mode`` property of the new state. It is sent when
    the player is on and it has just been turned on, has changed state, or
    its play mode has changed.

    >>> import home
    >>> import soco_plugin

    >>> cmd = soco_plugin.command.mode.Command.make(["Bath"])
    >>> off = home.appliance.sound.player.state.off.State()
    >>> on = off.next(home.appliance.sound.player.event.forced.Event.On)
    >>> msg = cmd.make_msgs_from(off, on)
    >>> msg[0]["fields"]["mode"]
    'REPEAT_ALL'
    >>> cmd.make_msgs_from(on, on)
    []
    >>> shuffle = on.next(home.appliance.sound.player.event.sleepy_play_mode.Event.Shuffle)
    >>> cmd.make_msgs_from(on, shuffle)[0]["fields"]["mode"]
    'SHUFFLE'
    >>> cmd.make_msgs_from(on, off)
    []
    """

    class Mode(enum.Enum):
        NORMAL = "NORMAL"
        REPEAT_ALL = "REPEAT_ALL"
        SHUFFLE = "SHUFFLE"
        SHUFFLE_NOREPEAT = "SHUFFLE_NOREPEAT"
        REPEAT_ONE = "REPEAT_ONE"
        SHUFFLE_REPEAT_ONE = "SHUFFLE_REPEAT_ONE"

    MODES = {
        "Normal": Mode.NORMAL,
        "RepeatAll": Mode.REPEAT_ALL,
        "RepeatOne": Mode.REPEAT_ONE,
        "Shuffle": Mode.SHUFFLE,
        "ShuffleNoRepeat": Mode.SHUFFLE_NOREPEAT,
        "ShuffleRepeatOne": Mode.SHUFFLE_REPEAT_ONE,
    }

    ACTION = "play_mode"

    Msg = {
        "type": "soco",
        "name": ACTION,
        "fields": {"mode": "NORMAL"},
        "addresses": [],
    }

    def make_msgs_from(self, old_state: Mixin, new_state: Mixin):
        result = []
        if new_state.is_on and (
            not old_state.is_on
            or type(old_state) is not type(new_state)
            or old_state.play_mode != new_state.play_mode
        ):
            self.msg["fields"]["mode"] = self.MODES[new_state.play_mode].value
            result = self.execute()
        return result


def action(player: soco.SoCo, mode):
    try:
        logging.getLogger(__name__).debug(
            "Changing mode %s" % player.player_name
        )
        player.play_mode = mode
    except Exception as e:
        logging.getLogger(__name__).error(e)
