import logging

import home
import soco
from soco_plugin.message import Command as Parent
from soco_plugin.command import Mixin


class Command(Parent):
    """Take the player out of its group when it stops fading in.

    It undoes :class:`soco_plugin.command.group.join.Command`. A player that
    plays for a group (a coordinator) or plays alone is left as it is. List
    this command before the pause command: a grouped player can't be paused
    on its own.

    >>> import home
    >>> import soco_plugin

    >>> cmd = soco_plugin.command.group.leave.Command.make(["Camera Alja"])
    >>> old_state = home.appliance.sound.player.state.off.State()
    >>> old_state = old_state.next(home.event.presence.Event.On)
    >>> old_state = old_state.next(home.event.sleepiness.Event.Awake)
    >>> old_state.VALUE
    'Fade In'
    >>> new_state = old_state.next(home.event.elapsed.Event.On)
    >>> msg = cmd.make_msgs_from(old_state, new_state)
    >>> msg[0]["name"]
    'leave'

    It also leaves when fading in is interrupted:

    >>> msg = cmd.make_msgs_from(old_state, old_state.next(home.appliance.sound.player.event.forced.Event.Off))
    >>> msg[0]["name"]
    'leave'

    It does nothing when the player was not fading in:

    >>> on = home.appliance.sound.player.state.off.State().next(home.appliance.sound.player.event.forced.Event.On)
    >>> cmd.make_msgs_from(on, on.next(home.appliance.sound.player.event.forced.Event.Off))
    []
    """

    ACTION = "leave"

    Msg = {"type": "soco", "name": ACTION, "fields": {}, "addresses": []}

    def make_msgs_from(self, old_state: Mixin, new_state: Mixin):
        fade_in = home.appliance.sound.player.state.fade_in.State
        result = []
        if isinstance(old_state, fade_in) and not isinstance(
            new_state, fade_in
        ):
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
