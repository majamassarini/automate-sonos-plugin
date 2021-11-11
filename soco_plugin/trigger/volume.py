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
        new_state = super(Trigger, self).make_new_state_from(
            another_description, old_state
        )
        new_state.volume = self.Msg["fields"]["volume"]
        return new_state
