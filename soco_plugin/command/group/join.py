import logging

import soco
from soco_plugin.message import Command as Parent
from soco_plugin.command import Mixin


class Command(Parent):
    """Join the player to the group of another player.

    The player to join (the coordinator, playing the music for the group)
    is the ``group`` property of the new state. The command is sent when
    that property changes to a non-empty name. A player already in that
    group is left as it is. Setting a playlist on a grouped player takes it
    out of the group, so set the group after the playlist has been sent.

    >>> import home
    >>> import soco_plugin

    >>> cmd = soco_plugin.command.group.join.Command.make(["Camera"])
    >>> alone = home.appliance.sound.player.state.off.State()
    >>> grouped = alone.next(home.appliance.sound.player.event.group.Event("Bagno"))
    >>> msg = cmd.make_msgs_from(alone, grouped)
    >>> msg[0]["name"]
    'join'
    >>> msg[0]["fields"]["coordinator"]
    'Bagno'
    >>> cmd.make_msgs_from(grouped, grouped)
    []
    >>> cmd.make_msgs_from(grouped, alone)
    []
    """

    ACTION = "join"

    Msg = {
        "type": "soco",
        "name": ACTION,
        "fields": {"coordinator": "Unknown"},
        "addresses": [],
    }

    def make_msgs_from(self, old_state: Mixin, new_state: Mixin):
        result = []
        if new_state.group and old_state.group != new_state.group:
            self.msg["fields"]["coordinator"] = new_state.group
            result = self.execute()
        return result


def action(player: soco.SoCo, coordinator: str):
    try:
        zone = next(
            (z for z in player.all_zones if z.player_name == coordinator),
            None,
        )
        if zone is None:
            logging.getLogger(__name__).error(
                "Cannot join %s to %s: no such player"
                % (player.player_name, coordinator)
            )
        elif player.group is not None and player.group.coordinator == zone:
            logging.getLogger(__name__).debug(
                "%s already in the group of %s"
                % (player.player_name, coordinator)
            )
        else:
            logging.getLogger(__name__).debug(
                "Joining %s to %s" % (player.player_name, coordinator)
            )
            player.join(zone)
    except Exception as e:
        logging.getLogger(__name__).error(e)
