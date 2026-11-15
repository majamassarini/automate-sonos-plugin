import logging

import home
import soco
from soco_plugin.message import Command as Parent
from soco_plugin.command import Mixin


class Command(Parent):
    """Join the player to the group of another player when it starts fading in.

    The player playing the music for the group (the coordinator) is named in
    the ``coordinator`` field, e.g. ``fields: {"coordinator": "Bagno"}``.
    List this command after the play command: setting a playlist on a
    grouped player makes it leave the group.

    >>> import home
    >>> import soco_plugin

    >>> cmd = soco_plugin.command.group.join.Command.make(["Camera Alja"], {"coordinator": "Bagno"})
    >>> old_state = home.appliance.sound.player.state.off.State()
    >>> old_state = old_state.next(home.event.presence.Event.On)
    >>> new_state = old_state.next(home.event.sleepiness.Event.Awake)
    >>> new_state.VALUE
    'Fade In'
    >>> msg = cmd.make_msgs_from(old_state, new_state)
    >>> msg[0]["name"]
    'join'
    >>> msg[0]["fields"]["coordinator"]
    'Bagno'

    It does nothing while the player keeps fading in, or when it turns on
    in any other way:

    >>> cmd.make_msgs_from(new_state, new_state.next(home.appliance.sound.player.event.fade_in.volume_scale.Event(50)))
    []
    >>> cmd.make_msgs_from(old_state, old_state.next(home.appliance.sound.player.event.forced.Event.On))
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
        fade_in = home.appliance.sound.player.state.fade_in.State
        result = []
        if isinstance(new_state, fade_in) and not isinstance(
            old_state, fade_in
        ):
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
