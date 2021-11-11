import home
from typing import TypeVar

Mixin = TypeVar(
    "Mixin",
    home.appliance.sound.player.state.off.State,
    home.appliance.sound.player.state.fade_in.State,
    home.appliance.sound.player.state.fade_out.State,
    home.appliance.sound.player.state.forced.on.State,
    home.appliance.sound.player.state.forced.circadian_rhythm.State,
    home.appliance.sound.player.state.forced.off.State,
)


from soco_plugin.command import volume, playlist, play, pause, stop, mode
