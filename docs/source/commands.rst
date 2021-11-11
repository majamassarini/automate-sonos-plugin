Commands
********

Commands are entities **capable of forge** messages for the *Sonos devices* interpreting changes in *Automate Home Appliances* states.

Commands are able to *compare* an *old Appliance state* with a *new one* and create messages to be sent to the Appliance's device(s).

Commands are designed to read *Appliance's attributes*: :meth:`home.appliance.attribute.mixin`

.. autoclass:: soco_plugin.message.Command

Play
----

.. autoclass:: soco_plugin.command.play.Command

Pause
-----

.. autoclass:: soco_plugin.command.pause.Command

Stop
----

.. autoclass:: soco_plugin.command.stop.Command

Playlist
--------

.. autoclass:: soco_plugin.command.playlist.Command

Mode
----

.. autoclass:: soco_plugin.command.mode.Command

Volume Absolute
---------------

.. autoclass:: soco_plugin.command.volume.absolute.Command

Volume Relative
---------------

.. autoclass:: soco_plugin.command.volume.relative.Command

Volume Ramp
-----------

.. autoclass:: soco_plugin.command.volume.ramp.Command
