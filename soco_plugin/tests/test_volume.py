# SPDX-License-Identifier: GPL-3.0-only
#
# automate home devices
#
# Copyright (C) 2021  Maja Massarini

import unittest
import unittest.mock

import home
import soco_plugin


class TestVolumeCommands(unittest.TestCase):
    def setUp(self):
        self.mock_player = unittest.mock.Mock()
        self.mock_player.player_name = "LivingRoom"
        self.mock_player.volume = 20

    def test_absolute_volume_command_make_msgs(self):
        cmd = soco_plugin.command.volume.absolute.Command.make(["LivingRoom"])
        old_state = home.appliance.sound.player.state.off.State()
        new_state = old_state.next(
            home.appliance.sound.player.event.forced.Event.On
        )
        new_state = new_state.next(home.event.presence.Event.On)
        new_state = new_state.next(
            home.appliance.sound.player.event.volume.Event(45)
        )
        new_state = new_state.next(home.event.sleepiness.Event.Awake)

        msgs = cmd.make_msgs_from(old_state, new_state)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["name"], "absolute_volume")
        self.assertEqual(msgs[0]["fields"]["value"], 45)
        self.assertEqual(msgs[0]["addresses"], ["LivingRoom"])

    def test_absolute_volume_command_off_state(self):
        cmd = soco_plugin.command.volume.absolute.Command.make(["LivingRoom"])
        old_state = home.appliance.sound.player.state.off.State()
        new_state = home.appliance.sound.player.state.off.State()

        msgs = cmd.make_msgs_from(old_state, new_state)
        self.assertEqual(msgs, [])

    def test_absolute_volume_action(self):
        soco_plugin.command.volume.absolute.action(self.mock_player, value=50)
        self.assertEqual(self.mock_player.volume, 50)

    def test_absolute_volume_action_handles_exception(self):
        error_player = unittest.mock.Mock()
        type(error_player).volume = unittest.mock.PropertyMock(
            side_effect=Exception("Volume error")
        )
        # Should not raise exception
        soco_plugin.command.volume.absolute.action(error_player, value=50)

    def test_relative_volume_command_make_msgs(self):
        cmd = soco_plugin.command.volume.relative.Command.make(
            ["LivingRoom"], fields={"delta": 15}
        )
        old_state = home.appliance.sound.player.state.off.State()
        new_state = old_state.next(
            home.appliance.sound.player.event.forced.Event.On
        )

        msgs = cmd.make_msgs_from(old_state, new_state)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["name"], "relative_volume")
        self.assertEqual(msgs[0]["fields"]["delta"], 15)
        self.assertEqual(msgs[0]["addresses"], ["LivingRoom"])

    def test_relative_volume_command_off_state(self):
        cmd = soco_plugin.command.volume.relative.Command.make(["LivingRoom"])
        old_state = home.appliance.sound.player.state.off.State()
        new_state = home.appliance.sound.player.state.off.State()

        msgs = cmd.make_msgs_from(old_state, new_state)
        self.assertEqual(msgs, [])

    def test_relative_volume_action_positive_delta(self):
        soco_plugin.command.volume.relative.action(self.mock_player, delta=10)
        self.mock_player.set_relative_volume.assert_called_once_with(10)

    def test_relative_volume_action_negative_delta(self):
        soco_plugin.command.volume.relative.action(self.mock_player, delta=-5)
        self.mock_player.set_relative_volume.assert_called_once_with(-5)

    def test_relative_volume_action_handles_exception(self):
        error_player = unittest.mock.Mock()
        error_player.set_relative_volume.side_effect = Exception(
            "Volume error"
        )
        # Should not raise exception
        soco_plugin.command.volume.relative.action(error_player, delta=5)

    def test_ramp_volume_command_make_msgs(self):
        cmd = soco_plugin.command.volume.ramp.Command.make(["LivingRoom"])
        old_state = home.appliance.sound.player.state.off.State()
        old_state = old_state.next(home.event.presence.Event.On)
        old_state = old_state.next(home.event.sleepiness.Event.Asleep)
        new_state = old_state.next(home.event.sleepiness.Event.Awake)

        msgs = cmd.make_msgs_from(old_state, new_state)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["name"], "ramp_to_volume")
        self.assertEqual(msgs[0]["fields"]["volume"], 30)
        self.assertEqual(
            msgs[0]["fields"]["ramp_type"], "SLEEP_TIMER_RAMP_TYPE"
        )

    def test_ramp_volume_action(self):
        soco_plugin.command.volume.ramp.action(
            self.mock_player, volume=35, ramp_type="ALARM_RAMP_TYPE"
        )
        self.mock_player.ramp_to_volume.assert_called_once_with(
            35, "ALARM_RAMP_TYPE"
        )

    def test_ramp_volume_action_handles_exception(self):
        error_player = unittest.mock.Mock()
        error_player.ramp_to_volume.side_effect = Exception("Ramp error")
        # Should not raise exception
        soco_plugin.command.volume.ramp.action(
            error_player, volume=35, ramp_type="ALARM_RAMP_TYPE"
        )


class TestVolumeTriggers(unittest.TestCase):
    def test_volume_trigger_is_triggered(self):
        trigger = soco_plugin.trigger.volume.Trigger.make(["LivingRoom"])
        matching_desc = soco_plugin.Description(
            {
                "type": "soco",
                "name": "volume",
                "fields": {"volume": 40},
                "addresses": ["LivingRoom"],
            }
        )
        wrong_addr_desc = soco_plugin.Description(
            {
                "type": "soco",
                "name": "volume",
                "fields": {"volume": 40},
                "addresses": ["Kitchen"],
            }
        )
        wrong_name_desc = soco_plugin.Description(
            {
                "type": "soco",
                "name": "play",
                "fields": {},
                "addresses": ["LivingRoom"],
            }
        )

        self.assertTrue(trigger.is_triggered(matching_desc))
        self.assertFalse(trigger.is_triggered(wrong_addr_desc))
        self.assertFalse(trigger.is_triggered(wrong_name_desc))

    def test_volume_trigger_make_new_state(self):
        trigger = soco_plugin.trigger.volume.Trigger.make(["LivingRoom"])
        state = (
            home.appliance.sound.player.state.forced.circadian_rhythm.state.State()
        )
        desc = soco_plugin.Description(
            {
                "type": "soco",
                "name": "volume",
                "fields": {"volume": 55},
                "addresses": ["LivingRoom"],
            }
        )
        new_state = trigger.make_new_state_from(desc, state)
        self.assertEqual(new_state.volume, 55)

    def test_volume_trigger_skips_when_fading(self):
        trigger = soco_plugin.trigger.volume.Trigger.make(["LivingRoom"])
        off_state = home.appliance.sound.player.state.off.State()
        off_state = off_state.next(home.event.presence.Event.On)
        off_state = off_state.next(home.event.sleepiness.Event.Asleep)
        fading_state = off_state.next(home.event.sleepiness.Event.Awake)
        self.assertTrue(fading_state.is_fading)
        initial_vol = fading_state.volume

        desc = soco_plugin.Description(
            {
                "type": "soco",
                "name": "volume",
                "fields": {"volume": 99},
                "addresses": ["LivingRoom"],
            }
        )
        new_state = trigger.make_new_state_from(desc, fading_state)
        self.assertEqual(new_state.volume, initial_vol)


class TestGatewayActions(unittest.TestCase):
    def setUp(self):
        self.mock_player = unittest.mock.Mock()
        self.mock_player.player_name = "LivingRoom"
        self.mock_player.volume = 20

    def test_gateway_relative_volume_action(self):
        msg = soco_plugin.Msg(
            {
                "type": "soco",
                "name": "relative_volume",
                "fields": {"delta": 5},
                "addresses": ["LivingRoom"],
            }
        )
        action = soco_plugin.Gateway.get_action(self.mock_player, msg)
        self.assertIsNotNone(action)
        action()
        self.mock_player.set_relative_volume.assert_called_once_with(5)

    def test_gateway_absolute_volume_action(self):
        msg = soco_plugin.Msg(
            {
                "type": "soco",
                "name": "absolute_volume",
                "fields": {"value": 50},
                "addresses": ["LivingRoom"],
            }
        )
        action = soco_plugin.Gateway.get_action(self.mock_player, msg)
        self.assertIsNotNone(action)
        action()
        self.assertEqual(self.mock_player.volume, 50)

    def test_gateway_ramp_volume_action(self):
        msg = soco_plugin.Msg(
            {
                "type": "soco",
                "name": "ramp_to_volume",
                "fields": {
                    "volume": 35,
                    "ramp_type": "AUTOPLAY_RAMP_TYPE",
                },
                "addresses": ["LivingRoom"],
            }
        )
        action = soco_plugin.Gateway.get_action(self.mock_player, msg)
        self.assertIsNotNone(action)
        action()
        self.mock_player.ramp_to_volume.assert_called_once_with(
            35, "AUTOPLAY_RAMP_TYPE"
        )

    def test_gateway_volume_trigger_msg_is_not_a_command(self):
        msg = soco_plugin.Msg(
            {
                "type": "soco",
                "name": "volume",
                "fields": {"volume": 42},
                "addresses": ["LivingRoom"],
            }
        )
        self.assertIsNone(
            soco_plugin.Gateway.get_action(self.mock_player, msg)
        )


class TestGatewayBuildMsgsFromBus(unittest.TestCase):
    def setUp(self):
        self.gateway = soco_plugin.Gateway.__new__(soco_plugin.Gateway)
        self.player = unittest.mock.Mock()
        self.player.player_name = "LivingRoom"

    def test_volume_event_with_master(self):
        event = unittest.mock.Mock()
        # soco 0.24 renderingControl LastChange event shape
        event.variables = {
            "volume": {"Master": "36", "LF": "100", "RF": "100"}
        }
        msgs = self.gateway.build_msgs_from_bus(self.player, event)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["name"], "volume")
        self.assertEqual(msgs[0]["fields"], {"volume": "36"})

    def test_volume_event_without_master_is_ignored(self):
        event = unittest.mock.Mock()
        event.variables = {"volume": {"LF": "100", "RF": "100"}}
        self.assertEqual(
            self.gateway.build_msgs_from_bus(self.player, event), []
        )


if __name__ == "__main__":
    unittest.main()
