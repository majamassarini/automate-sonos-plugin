import copy
import logging

from typing import List, Any, Type

import home

from soco_plugin import Address


class Msg(dict):
    pass


class Description(home.protocol.Description):
    """
    >>> description1 = {"type": "soco",
    ...                "name": "volume",
    ...                "fields": {"delta": 100},
    ...                "addresses": ["Bagno"]}
    >>> description2 = {"type": "soco",
    ...                "name": "volume",
    ...                "fields": {"delta": 50},
    ...                "addresses": ["Bagno"]}
    >>> d1 = Description(description1)
    >>> d2 = Description(description2)
    >>> d1 == d2
    True
    >>> str(d1.msg["name"])
    'volume'
    """

    PROTOCOL = "soco"

    Msg = {"type": PROTOCOL, "name": "Fake", "fields": {}, "addresses": []}

    def __init__(self, data):
        super(Description, self).__init__(data)
        self._msg = data
        self._addresses = [address for address in data["addresses"]]
        self._label = str(self._msg)
        self._logging = logging.getLogger(__name__)

    def __hash__(self):
        return hash("class: " + self.msg["name"] + str(self.addresses))

    def __eq__(self, other):
        if self.PROTOCOL == other.PROTOCOL:
            if self.msg["name"] == other.msg["name"] and set(self.addresses) == set(
                other.addresses
            ):
                return True
        return False

    @property
    def msg(self):
        return self._msg

    @property
    def addresses(self) -> List[Address]:
        return self._addresses

    @classmethod
    def make(
        cls, addresses: List[Address], fields: Any = None
    ) -> "soco_plugin.Description":
        description = copy.deepcopy(cls.Msg)
        description["addresses"] += addresses
        if fields:
            description["fields"] = fields
        return cls(description)

    @classmethod
    def make_from_yaml(
        cls, addresses: List[Address], fields: Any = None
    ) -> "soco_plugin.Description":
        return cls.make(addresses, fields)

    @classmethod
    def make_from(cls, msg: Msg) -> "soco_plugin.Description":
        description = cls(msg)
        return description

    def __str__(self, *args, **kwargs):
        s = "%s" % str(self.msg)
        return s


class Trigger(home.protocol.Trigger, Description):
    """Build a Trigger from a python dictionary

    @param trigger_data: a python dictionary with the trigger data

    >>> import io
    >>> import json
    >>> import home
    >>> import soco_plugin
    >>> json_trigger = '''
    ...                {
    ...                    "name": "play",
    ...                    "fields": {},
    ...                    "addresses": ["Bagno"]
    ...                }
    ... '''
    >>> class Triggerr(soco_plugin.trigger.play.Trigger):
    ...     pass
    >>> fd = io.StringIO(json_trigger)
    >>> trigger_data = json.load(fd)
    >>> d = Description(trigger_data)
    >>> trigger1 = Triggerr(trigger_data, [home.appliance.sound.player.event.forced.Event.On])
    >>> trigger1.is_triggered(d)
    True
    >>> trigger1.events
    [<Event.On: 'On'>]
    """

    ACTION = None

    def is_triggered(self, another_description: Description) -> bool:
        triggered = False
        if super(Trigger, self).is_triggered(another_description):
            if (
                set(another_description.addresses) & set(self.addresses)
                and another_description.msg["name"] == self.msg["name"]
            ):
                triggered = another_description.msg["fields"] == self.msg["fields"]
        if triggered:
            self._logging.info(
                "Triggered {} for {}".format(self.ACTION, self.addresses)
            )
            return triggered
        else:
            return triggered

    @classmethod
    def make(
        cls,
        addresses: List[Address],
        events: List[home.Event] = None,
        fields: Any = None,
    ) -> Type["soco_plugin.Trigger"]:
        description = copy.deepcopy(cls.Msg)
        description["addresses"] += addresses
        if fields:
            description["fields"] = fields
        return cls(description, events)

    @classmethod
    def make_from_yaml(
        cls,
        addresses: List[Address],
        events: List[home.Event] = None,
        fields: Any = None,
    ) -> Type["soco_plugin.Trigger"]:
        return cls.make(addresses, events, fields)


class Command(Description, home.protocol.Command):
    def execute(self) -> List[Msg]:
        msgs = []
        msg = Msg(copy.deepcopy(self.msg))
        msg["addresses"] = self.addresses
        msgs.append(msg)
        return msgs

    def make_msgs_from(
        self, old_state: home.appliance.State, new_state: home.appliance.State
    ) -> List[Msg]:
        return []
