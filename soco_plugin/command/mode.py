import logging
import enum

import home
import soco
from soco_plugin.message import Command as Parent


class Command(Parent):
    """
    >>> import home
    >>> import soco_plugin

    >>> cmd = soco_plugin.command.playlist.Command.make(["Bath"])
    >>> old_state = home.appliance.sound.player.state.off.State()
    >>> old_state = old_state.next(home.appliance.sound.player.event.forced.Event.On)
    >>> new_state = old_state.next(home.appliance.sound.player.event.playlist.Event("A new playlist"))
    >>> msg = cmd.make_msgs_from(old_state, new_state)
    >>> msg[0]["fields"]["title"]
    'A new playlist'
    """

    class Mode(enum.Enum):
        NORMAL = "NORMAL"
        REPEAT_ALL = "REPEAT_ALL"
        SHUFFLE = "SHUFFLE"
        SHUFFLE_NOREPEAT = "SHUFFLE_NOREPEAT"
        REPEAT_ONE = "REPEAT_ONE"
        SHUFFLE_REPEAT_ONE = "SHUFFLE_REPEAT_ONE"

    ACTION = "play_mode"

    Msg = {
        "type": "soco",
        "name": ACTION,
        "fields": {"mode": "SHUFFLE"},
        "addresses": [],
    }

    def make_msgs_from(
        self, old_state: home.appliance.State, new_state: home.appliance.State
    ):
        result = self.execute()
        return result


def action(player: soco.SoCo, mode):
    try:
        player.play_mode = mode
    except Exception as e:
        logging.getLogger(__name__).error(e)
