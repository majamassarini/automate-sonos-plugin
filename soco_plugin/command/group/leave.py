import logging

import soco
from soco_plugin.message import Command as Parent
from soco_plugin.command import Mixin


class Command(Parent):
    """Take the player out of its group.

    It undoes :class:`soco_plugin.command.group.join.Command`. The command
    is sent every time it is executed. A player that plays for a group (a
    coordinator) or plays alone is left as it is.

    >>> import home
    >>> import soco_plugin

    >>> cmd = soco_plugin.command.group.leave.Command.make(["Camera"])
    >>> old_state = home.appliance.sound.player.state.off.State()
    >>> new_state = old_state.next(home.appliance.sound.player.event.volume.Event(50))
    >>> msg = cmd.make_msgs_from(old_state, new_state)
    >>> msg[0]["name"]
    'leave'
    """

    ACTION = "leave"

    Msg = {"type": "soco", "name": ACTION, "fields": {}, "addresses": []}

    def make_msgs_from(self, old_state: Mixin, new_state: Mixin):
        return self.execute()


def action(player: soco.SoCo):
    try:
        if player.is_coordinator:
            logging.getLogger(__name__).debug(
                "%s is not a group member, nothing to leave"
                % player.player_name
            )
        else:
            logging.getLogger(__name__).debug(
                "%s leaves its group" % player.player_name
            )
            player.unjoin()
    except Exception as e:
        logging.getLogger(__name__).error(e)
