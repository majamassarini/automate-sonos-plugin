# automate-sonos-plugin
[![Build Status](https://app.travis-ci.com/majamassarini/automate-sonos-plugin.svg?branch=main)](https://app.travis-ci.com/majamassarini/automate-sonos-plugin)
[![codecov](https://codecov.io/gh/majamassarini/automate-sonos-plugin/branch/main/graph/badge.svg?token=pOvjwMbn6E)](https://codecov.io/gh/majamassarini/automate-sonos-plugin)
[![Documentation Status](https://readthedocs.org/projects/automate-sonos-plugin/badge/?version=latest)](https://automate-sonos-plugin.readthedocs.io/en/latest/?badge=latest)

The **Sonos** plugin for the [automate-home project](https://github.com/majamassarini/automate-home).

## Yaml examples of usage

Trigger and command for a [sound player model](https://automate-home.readthedocs.io/en/latest/appliances.html#sound-player-appliance).
```yaml
- !Performer
  name: "forced on/off triggers"
  for appliance: "a sound player"
  commands: []
  triggers:
  - !soco_plugin.trigger.play.Trigger
      addresses: ["Bagno"]
      events:
        - !home.appliance.sound.player.event.forced.Event.On
  - !soco_plugin.trigger.stop.Trigger
      addresses: ["Bagno"]
      events:
        - !home.appliance.sound.player.event.forced.Event.Off
  - !soco_plugin.trigger.pause.Trigger
      addresses: ["Bagno"]
      events:
        - !home.appliance.sound.player.event.forced.Event.Off
  - !soco_plugin.trigger.volume.Trigger {addresses: ["Bagno"]}

- !Performer
  name: "sonos commands"
  for appliance: "a sound player"
  commands:
  - !soco_plugin.command.pause.Command {addresses: ["Bagno"]}
  - !soco_plugin.command.playlist.Command {addresses: ["Bagno"]}
  - !soco_plugin.command.volume.absolute.Command {addresses: ["Bagno"]}
  - !soco_plugin.command.mode.Command { addresses: [ "Bagno" ], fields: { "mode": "SHUFFLE" } }
  - !soco_plugin.command.play.Command {addresses: ["Bagno"]}
  triggers: []

- !Performer
  name: "fade in or out command"
  for appliance: "a sound player"
  commands:
    - !soco_plugin.command.volume.ramp.Command { addresses: [ "Bagno" ], fields: { "ramp_type": 'SLEEP_TIMER_RAMP_TYPE' } }
  triggers: [ ]

- !Performer
  name: "sonos relative volume up through knx dimming button"
  for appliance: "a sound player"
  triggers:
  - !knx_plugin.trigger.dpt_control_dimming.step.up.Trigger {addresses: [0x0C09]}
  commands:
    - !soco_plugin.command.volume.relative.Command {addresses: ["Bagno"], fields: {"delta": 10}}

- !Performer
  name: "sonos relative volume down through knx dimming button"
  for appliance: "a sound player"
  triggers:
  - !knx_plugin.trigger.dpt_control_dimming.step.down.Trigger {addresses: [0x0C09]}
  commands:
    - !soco_plugin.command.volume.relative.Command {addresses: ["Bagno"], fields: {"delta": -10}}

- !Performer
  name: "alarm switch on/off player when armed/unarmed alarm system"
  for appliance: "a sound player"
  commands:
    - !soco_plugin.command.play.Command {addresses: ["Bagno"]}
    - !soco_plugin.command.pause.Command {addresses: ["Bagno"]}
  triggers:
    - !knx_plugin.trigger.dpt_switch.On
      addresses: [ 0xA1C, ]
      events:
        - !home.event.presence.Event.Off
    - !knx_plugin.trigger.dpt_switch.Off
      addresses: [ 0xA1C, ]
      events:
        - !home.event.presence.Event.On

- !Performer
  name: "force circadian rhythm through knx scene button"
  for appliance: "a sound player"
  commands:
    - !soco_plugin.command.playlist.Command {addresses: ["Bagno"]}
    - !soco_plugin.command.volume.absolute.Command {addresses: ["Bagno"]}
    - !soco_plugin.command.play.Command {addresses: ["Bagno"]}
  triggers:
    - !knx_plugin.trigger.dpt_scene_control.Activate
      addresses: [ 0x0B0F ]
      number: 15
      events:
        - !home.appliance.sound.player.event.forced.Event.CircadianRhythm

- !Performer
  name: "unforce circadian rhythm through another knx scene button"
  for appliance: "a sound player"
  commands:
    - !soco_plugin.command.pause.Command {addresses: ["Bagno"]}
  triggers:
    - !knx_plugin.trigger.dpt_scene_control.Activate
      addresses: [ 0x0B10 ]
      number: 16
      events:
        - !home.appliance.sound.player.event.forced.Event.Not

- !Performer
  name: "force on/off through knx start/stop button"
  for appliance: "a sound player"
  commands:
    - !soco_plugin.command.pause.Command {addresses: ["Bagno"]}
    - !soco_plugin.command.playlist.Command {addresses: ["Bagno"]}
    - !soco_plugin.command.volume.absolute.Command {addresses: ["Bagno"]}
    - !soco_plugin.command.play.Command {addresses: ["Bagno"]}
  triggers:
    - !knx_plugin.trigger.dpt_start.Start
      addresses: [ 0x0C09, ]
      events:
        - !home.appliance.sound.player.event.forced.Event.On
    - !knx_plugin.trigger.dpt_start.Stop
      addresses: [ 0x0C09, ]
      events:
        - !home.appliance.sound.player.event.forced.Event.Not
```

## Documentation

* [automate-home protocol commands/triggers chapter](https://automate-home.readthedocs.io/en/latest/performer.html)
* [automate-sonos-plugin documentation](https://automate-sonos-plugin.readthedocs.io/en/latest/?badge=latest)

## Contributing

Pull requests are welcome!

## License

The automate-sonos-plugin is licensed under MIT.