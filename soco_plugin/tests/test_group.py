# SPDX-License-Identifier: GPL-3.0-only
#
# automate home devices
#
# Copyright (C) 2021  Maja Massarini

import unittest
import unittest.mock

import home
import soco_plugin


def _fade_in():
    state = home.appliance.sound.player.state.off.State()
    state = state.next(home.event.presence.Event.On)
    return state.next(home.event.sleepiness.Event.Awake)


class TestGroupCommands(unittest.TestCase):
    def setUp(self):
        self.join = soco_plugin.command.group.join.Command.make(
            ["Camera Alja"], {"coordinator": "Bagno", "state": "Fade In"}
        )
        self.leave = soco_plugin.command.group.leave.Command.make(
            ["Camera Alja"], {"state": "Fade In"}
        )

    def test_join_when_entering_the_state(self):
        old_state = home.appliance.sound.player.state.off.State().next(
            home.event.presence.Event.On
        )

        msgs = self.join.make_msgs_from(old_state, _fade_in())

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["name"], "join")
        self.assertEqual(msgs[0]["fields"]["coordinator"], "Bagno")
        self.assertEqual(msgs[0]["addresses"], ["Camera Alja"])

    def test_no_join_when_entering_another_state(self):
        old_state = home.appliance.sound.player.state.off.State()
        new_state = old_state.next(
            home.appliance.sound.player.event.forced.Event.On
        )

        self.assertEqual(self.join.make_msgs_from(old_state, new_state), [])

    def test_no_join_while_staying_in_the_state(self):
        old_state = _fade_in()
        new_state = old_state.next(
            home.appliance.sound.player.event.fade_in.volume_scale.Event(50)
        )

        self.assertEqual(self.join.make_msgs_from(old_state, new_state), [])

    def test_leave_when_exiting_the_state(self):
        old_state = _fade_in()
        new_state = old_state.next(home.event.elapsed.Event.On)

        msgs = self.leave.make_msgs_from(old_state, new_state)

        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["name"], "leave")
        self.assertEqual(msgs[0]["addresses"], ["Camera Alja"])

    def test_no_leave_while_staying_in_the_state(self):
        old_state = _fade_in()
        new_state = old_state.next(
            home.appliance.sound.player.event.fade_in.volume_scale.Event(50)
        )

        self.assertEqual(self.leave.make_msgs_from(old_state, new_state), [])

    def test_no_leave_when_exiting_another_state(self):
        old_state = home.appliance.sound.player.state.off.State().next(
            home.appliance.sound.player.event.forced.Event.On
        )
        new_state = old_state.next(
            home.appliance.sound.player.event.forced.Event.Off
        )

        self.assertEqual(self.leave.make_msgs_from(old_state, new_state), [])


class TestGroupActions(unittest.TestCase):
    def setUp(self):
        self.bagno = unittest.mock.Mock(player_name="Bagno")
        self.player = unittest.mock.Mock(player_name="Camera Alja")
        self.player.all_zones = {self.bagno, self.player}
        self.player.group.coordinator = self.player

    def test_join_action_joins_the_coordinator(self):
        soco_plugin.command.group.join.action(self.player, coordinator="Bagno")
        self.player.join.assert_called_once_with(self.bagno)

    def test_join_action_skips_when_already_grouped(self):
        self.player.group.coordinator = self.bagno
        soco_plugin.command.group.join.action(self.player, coordinator="Bagno")
        self.player.join.assert_not_called()

    def test_join_action_unknown_coordinator(self):
        soco_plugin.command.group.join.action(self.player, coordinator="Nope")
        self.player.join.assert_not_called()

    def test_join_action_handles_exception(self):
        self.player.join.side_effect = Exception("UPnP error")
        # Should not raise exception
        soco_plugin.command.group.join.action(self.player, coordinator="Bagno")

    def test_leave_action_unjoins_a_member(self):
        self.player.is_coordinator = False
        soco_plugin.command.group.leave.action(self.player)
        self.player.unjoin.assert_called_once_with()

    def test_leave_action_keeps_a_coordinator(self):
        self.player.is_coordinator = True
        soco_plugin.command.group.leave.action(self.player)
        self.player.unjoin.assert_not_called()

    def test_gateway_dispatches_group_commands(self):
        self.player.is_coordinator = False
        join = soco_plugin.command.group.join.Command.make(
            ["Camera Alja"], {"coordinator": "Bagno", "state": "Fade In"}
        ).make_msgs_from(
            home.appliance.sound.player.state.off.State(), _fade_in()
        )
        soco_plugin.Gateway.get_action(self.player, join[0])()
        self.player.join.assert_called_once_with(self.bagno)

        leave = soco_plugin.command.group.leave.Command.make(
            ["Camera Alja"], {"state": "Fade In"}
        ).make_msgs_from(
            _fade_in(), home.appliance.sound.player.state.off.State()
        )
        soco_plugin.Gateway.get_action(self.player, leave[0])()
        self.player.unjoin.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
