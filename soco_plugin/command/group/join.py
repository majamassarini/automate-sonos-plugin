import logging

import soco
from soco_plugin.message import Command as Parent
from soco_plugin.command import Mixin


class Command(Parent):
    """Join the player to the group of another player when the appliance
    enters a given state.

    The fields name the player playing the music for the group (the
    coordinator) and the appliance state that starts the grouping, e.g.
    ``fields: {"coordinator": "Bagno", "state": "Forced Circadian Rhythm"}``. List this
    command after the playlist and play commands: setting a playlist on a
    grouped player takes it out of the group.

    >>> import home
    >>> import soco_plugin

    >>> cmd = soco_plugin.command.group.join.Command.make(
    ...     ["Camera"], {"coordinator": "Bagno", "state": "Forced Circadian Rhythm"})
    >>> old_state = home.appliance.sound.player.state.off.State()
    >>> new_state = old_state.next(home.appliance.sound.player.event.forced.Event.CircadianRhythm)
    >>> new_state.VALUE
    'Forced Circadian Rhythm'
    >>> msg = cmd.make_msgs_from(old_state, new_state)
    >>> msg[0]["name"]
    'join'
    >>> msg[0]["fields"]["coordinator"]
    'Bagno'

    It does nothing while the appliance stays in that state, or when it
    enters another one:

    >>> cmd.make_msgs_from(new_state, new_state.next(home.appliance.sound.player.event.volume.Event(50)))
    []
    >>> cmd.make_msgs_from(old_state, old_state.next(home.appliance.sound.player.event.forced.Event.On))
    []
    """

    ACTION = "join"

    Msg = {
        "type": "soco",
        "name": ACTION,
        "fields": {"coordinator": "Unknown", "state": "Unknown"},
        "addresses": [],
    }

    def make_msgs_from(self, old_state: Mixin, new_state: Mixin):
        state = self.msg["fields"]["state"]
        result = []
        if new_state.VALUE == state and old_state.VALUE != state:
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
