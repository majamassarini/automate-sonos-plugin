from __future__ import annotations

import home
from soco_plugin.message import Trigger as Parent, Description


class Trigger(Parent):

    ACTION = "volume"

    Msg = {
        "type": Parent.PROTOCOL,
        "name": ACTION,
        "fields": {"volume": 1},
        "addresses": [],
    }

    def make_new_state_from(
        self,
        another_description: Description,
        old_state: home.appliance.attribute.mixin.Volume,
    ):
        """
        >>> import soco_plugin
        >>> import home
        >>> trigger = soco_plugin.trigger.volume.absolute.Trigger.make(["an address",])
        >>> old_state = home.appliance.sound.player.state.forced.circadian_rhythm.state.State()
        >>> msg = trigger.Msg.copy()
        >>> msg["addresses"] = ["an address", ]
        >>> d = soco_plugin.Description(msg)
        >>> new_state = trigger.make_new_state_from(d, old_state)
        >>> new_state.volume
        1
        """
        # Skip volume updates when in fading state
        # Volume is constantly changing during fade and incoming values may be stale
        if hasattr(old_state, "is_fading") and old_state.is_fading:
            return old_state

        if not self.is_triggered(another_description):
            return old_state

        new_state = super(Trigger, self).make_new_state_from(
            another_description, old_state
        )
        try:
            if "volume" in another_description.msg["fields"]:
                new_state.volume = int(
                    another_description.msg["fields"]["volume"]
                )
            elif "value" in another_description.msg["fields"]:
                new_state.volume = int(
                    another_description.msg["fields"]["value"]
                )
        except AttributeError as e:
            raise e
        return new_state
