import logging

import soco
from soco_plugin.message import Command as Parent
from soco_plugin.command import Mixin


class Command(Parent):
    """Take the player out of its group when the appliance exits a given
    state.

    It undoes :class:`soco_plugin.command.group.join.Command`; the field
    names the same state, e.g. ``fields: {"state": "Forced Circadian Rhythm"}``. A player
    that plays for a group (a coordinator) or plays alone is left as it is.
    List this command before the pause command: a grouped player can't be
    paused on its own.

    >>> import home
    >>> import soco_plugin

    >>> cmd = soco_plugin.command.group.leave.Command.make(
    ...     ["Camera"], {"state": "Forced Circadian Rhythm"})
    >>> old_state = home.appliance.sound.player.state.off.State()
    >>> old_state = old_state.next(home.appliance.sound.player.event.forced.Event.CircadianRhythm)
    >>> old_state.VALUE
    'Forced Circadian Rhythm'
    >>> new_state = old_state.next(home.appliance.sound.player.event.forced.Event.Off)
    >>> msg = cmd.make_msgs_from(old_state, new_state)
    >>> msg[0]["name"]
    'leave'

    It does nothing while the appliance stays in that state, or when it
    exits another one:

    >>> cmd.make_msgs_from(old_state, old_state.next(home.appliance.sound.player.event.volume.Event(50)))
    []
    >>> other = home.appliance.sound.player.state.off.State().next(
    ...     home.appliance.sound.player.event.forced.Event.On)
    >>> cmd.make_msgs_from(other, other.next(home.appliance.sound.player.event.forced.Event.Off))
    []
    """

    ACTION = "leave"

    Msg = {
        "type": "soco",
        "name": ACTION,
        "fields": {"state": "Unknown"},
        "addresses": [],
    }

    def make_msgs_from(self, old_state: Mixin, new_state: Mixin):
        state = self.msg["fields"]["state"]
        result = []
        if old_state.VALUE == state and new_state.VALUE != state:
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
