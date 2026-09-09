# automate-sonos-plugin
[![Build](https://github.com/majamassarini/automate-sonos-plugin/actions/workflows/build.yml/badge.svg?branch=main)](https://github.com/majamassarini/automate-sonos-plugin/actions/workflows/build.yml)
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

## Known Issues: Command Echo Problem

### Problem Description

The SoCo library (underlying Sonos communication library) does **not** distinguish between:
- Events triggered by commands sent from automate-home
- Events triggered by user actions (Sonos app, physical speaker controls)

This creates a "command echo" problem where your own commands trigger state change events.

### Example Scenario

When pressing a button to enable Forced Circadian Rhythm mode on a Sonos speaker:

1. **Button pressed** → sends `forced.Event.CircadianRhythm` → State becomes **Forced Circadian Rhythm**
2. **Performer executes commands** in sequence:
   - `mode.Command` (set shuffle mode)
   - `playlist.Command` (select playlist)
   - `volume.Command` (set volume)
   - `play.Command` (start playback)
3. **During reconfiguration**: Sonos internally pauses → fires `pause.Trigger` → sends `forced.Event.Off` → State becomes **Off** (unforced!)
4. **After reconfiguration**: Sonos starts playing → fires `play.Trigger` → sends `forced.Event.On` → State becomes **Forced On** (WRONG! Should be Forced Circadian Rhythm)

### Why This Happens

- Sonos speakers send pause events during mode/playlist reconfiguration
- The pause trigger (lines 25-28 in example above) interprets this as user action
- This unforces the state prematurely
- Subsequent play event from Sonos is then interpreted as generic "forced on" instead of maintaining circadian rhythm mode

### Root Cause

The SoCo Event objects contain:
- `sid`: subscription ID
- `seq`: event sequence number
- `service`: subscribed service (avTransport or renderingControl)
- `timestamp`: when event was received
- `variables`: state variables like `transport_state` and `volume`

**They do NOT contain:**
- Command correlation ID
- Source identifier (app vs. external command vs. button)
- Any way to distinguish "echo of your command" from "actual user action"

This is a fundamental limitation of the Sonos UPnP event system and cannot be fully solved without changes to the SoCo library or Sonos firmware.

### Current Mitigation: Appliance-level Event Disabling

The mitigation is implemented at the automate-home appliance state machine level rather
than in this plugin. When a Sonos player enters a playing state (Fade In, Forced On,
Forced Circadian Rhythm), automate-home temporarily disables `forced.Event.Off` in the
appliance state machine so that echo events from Sonos are silently ignored:

1. **On state entry** — a `state.entering.disable_events.Trigger` immediately calls
   `appliance.disable(forced.Event.Off)`. Any `stop`/`pause` echo arriving from Sonos
   is ignored by the state machine.
2. **After 30 seconds** — a `state.entering.delay.enable_events.Trigger` calls
   `appliance.enable(forced.Event.Off)`. Legitimate stop/pause commands from the user
   are processed normally again.

This plugin passes all Sonos events through without any filtering; the suppression
window is configured entirely in the automate-home scheduler trigger YAML.

## Documentation

* [automate-home protocol commands/triggers chapter](https://automate-home.readthedocs.io/en/latest/performer.html)
* [automate-sonos-plugin documentation](https://automate-sonos-plugin.readthedocs.io/en/latest/?badge=latest)

## Contributing

Pull requests are welcome!

## License

The automate-sonos-plugin is licensed under MIT.