import logging

import soco
from soco_plugin.message import Command as Parent
from soco_plugin.command import Mixin


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

    ACTION = "playlist"

    Msg = {
        "type": "soco",
        "name": ACTION,
        "fields": {"title": "Unknown"},
        "addresses": [],
    }

    def make_msgs_from(self, old_state: Mixin, new_state: Mixin):
        result = []
        if new_state.is_on and (
            (old_state.is_on != new_state.is_on)
            or (old_state.playlist != new_state.playlist)
        ):
            self.msg["fields"]["title"] = new_state.playlist
            result = self.execute()
        return result


def action(player: soco.SoCo, title: str):
    try:
        _playlist = player.get_sonos_playlist_by_attr("title", title)
        player.clear_queue()
        player.add_uri_to_queue(uri=_playlist.resources[0].uri)
        player.play_from_queue(index=0)
    except Exception as e:
        logging.getLogger(__name__).error(e)
