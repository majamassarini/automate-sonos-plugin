import logging

import soco
from soco_plugin.message import Command as Parent
from soco_plugin.command import Mixin


class Command(Parent):
    """Take the player out of its group.

    It undoes :class:`soco_plugin.command.group.join.Command`. The command
    is sent when the ``group`` property of the state changes to an empty
    name. A player that plays for a group (a coordinator) or plays alone is
    left as it is.

    >>> import home
    >>> import soco_plugin

    >>> cmd = soco_plugin.command.group.leave.Command.make(["Camera"])
    >>> alone = home.appliance.sound.player.state.off.State()
    >>> grouped = alone.next(home.appliance.sound.player.event.group.Event("Bagno"))
    >>> msg = cmd.make_msgs_from(grouped, alone)
    >>> msg[0]["name"]
    'leave'
    >>> cmd.make_msgs_from(alone, alone)
    []
    >>> cmd.make_msgs_from(alone, grouped)
    []
    """

    ACTION = "leave"

    Msg = {"type": "soco", "name": ACTION, "fields": {}, "addresses": []}

    def make_msgs_from(self, old_state: Mixin, new_state: Mixin):
        result = []
        if old_state.group and not new_state.group:
            result = self.execute()
        return result


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
