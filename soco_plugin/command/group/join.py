import logging

import soco
from soco_plugin.message import Command as Parent
from soco_plugin.command import Mixin


class Command(Parent):
    """Join the player to the group of another player.

    The ``coordinator`` field names the player playing the music for the
    group, e.g. ``fields: {"coordinator": "Bagno"}``. The command is sent
    every time it is executed. A player already in that group is left as it
    is. Setting a playlist on a grouped player takes it out of the group, so
    join after the playlist and play commands.

    >>> import home
    >>> import soco_plugin

    >>> cmd = soco_plugin.command.group.join.Command.make(["Camera"], {"coordinator": "Bagno"})
    >>> old_state = home.appliance.sound.player.state.off.State()
    >>> new_state = old_state.next(home.appliance.sound.player.event.volume.Event(50))
    >>> msg = cmd.make_msgs_from(old_state, new_state)
    >>> msg[0]["name"]
    'join'
    >>> msg[0]["fields"]["coordinator"]
    'Bagno'
    """

    ACTION = "join"

    Msg = {
        "type": "soco",
        "name": ACTION,
        "fields": {"coordinator": "Unknown"},
        "addresses": [],
    }

    def make_msgs_from(self, old_state: Mixin, new_state: Mixin):
        return self.execute()


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
