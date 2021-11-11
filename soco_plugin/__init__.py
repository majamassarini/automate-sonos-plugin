from typing import NewType

Address = NewType("Address", str)


from soco_plugin.message import Command, Trigger, Description
from soco_plugin import command, trigger
from soco_plugin.gateway import Gateway
