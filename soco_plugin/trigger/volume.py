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
    ) -> bool:
        """
        >>> import soco_plugin
        >>> import home
        >>> trigger = soco_plugin.trigger.volume.Trigger.make(["an address",])
        >>> old_state = home.appliance.sound.player.state.forced.circadian_rhythm.state.State()
        >>> msg = trigger.Msg.copy()
        >>> msg["addresses"] = ["an address", ]
        >>> d = soco_plugin.Description(msg)
        >>> new_state = trigger.make_new_state_from(d, old_state)
        """
        new_state = super(Trigger, self).make_new_state_from(
            another_description, old_state
        )
        try:
            new_state.volume = self.msg["fields"]["volume"]
        except AttributeError as e:
            raise e
        return new_state
