from __future__ import annotations

import home
from soco_plugin.message import Trigger as Parent, Description


class Trigger(Parent):

    ACTION = "ramp_to_volume"

    Msg = {
        "type": Parent.PROTOCOL,
        "name": ACTION,
        "fields": {"volume": 10, "ramp_type": "SLEEP_TIMER_RAMP_TYPE"},
        "addresses": [],
    }

    def make_new_state_from(
        self,
        another_description: Description,
        old_state: home.appliance.State,
    ):
        """
        >>> import soco_plugin
        >>> import home
        >>> old_state = home.appliance.sound.player.state.off.State()
        >>> old_state = old_state.next(home.event.presence.Event.On)
        >>> old_state = old_state.next(home.event.sleepiness.Event.Asleep)
        >>> trigger = soco_plugin.trigger.volume.ramp.Trigger.make(
        ...     ["Bath"], events=[home.event.sleepiness.Event.Awake]
        ... )
        >>> msg = trigger.Msg.copy()
        >>> msg["addresses"] = ["Bath"]
        >>> msg["fields"] = {"volume": 40, "ramp_type": "SLEEP_TIMER_RAMP_TYPE"}
        >>> d = soco_plugin.Description(msg)
        >>> new_state = trigger.make_new_state_from(d, old_state)
        >>> new_state.is_fading
        True
        >>> new_state.volume
        40
        """
        if not self.is_triggered(another_description):
            return old_state

        new_state = super(Trigger, self).make_new_state_from(
            another_description, old_state
        )
        try:
            if (
                hasattr(new_state, "volume")
                and "volume" in another_description.msg["fields"]
            ):
                new_state.volume = int(
                    another_description.msg["fields"]["volume"]
                )
        except AttributeError as e:
            raise e
        return new_state
