# SPDX-License-Identifier: GPL-3.0-only
#
# automate home devices
#
# Copyright (C) 2021  Maja Massarini

import unittest
import unittest.mock

import home
import soco_plugin


def _on():
    state = home.appliance.sound.player.state.off.State()
    return state.next(home.appliance.sound.player.event.forced.Event.On)


class TestGroupCommands(unittest.TestCase):
    def test_join_is_sent_on_every_execution(self):
        cmd = soco_plugin.command.group.join.Command.make(
            ["Camera Alja"], {"coordinator": "Bagno"}
        )
        state = home.appliance.sound.player.state.off.State()

        for old_state, new_state in ((state, _on()), (_on(), _on())):
            msgs = cmd.make_msgs_from(old_state, new_state)
            self.assertEqual(len(msgs), 1)
            self.assertEqual(msgs[0]["name"], "join")
            self.assertEqual(msgs[0]["fields"], {"coordinator": "Bagno"})
            self.assertEqual(msgs[0]["addresses"], ["Camera Alja"])

    def test_leave_is_sent_on_every_execution(self):
        cmd = soco_plugin.command.group.leave.Command.make(["Camera Alja"])
        state = home.appliance.sound.player.state.off.State()

        for old_state, new_state in ((_on(), state), (state, state)):
            msgs = cmd.make_msgs_from(old_state, new_state)
            self.assertEqual(len(msgs), 1)
            self.assertEqual(msgs[0]["name"], "leave")
            self.assertEqual(msgs[0]["addresses"], ["Camera Alja"])


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
            ["Camera Alja"], {"coordinator": "Bagno"}
        ).make_msgs_from(home.appliance.sound.player.state.off.State(), _on())
        soco_plugin.Gateway.get_action(self.player, join[0])()
        self.player.join.assert_called_once_with(self.bagno)

        leave = soco_plugin.command.group.leave.Command.make(
            ["Camera Alja"]
        ).make_msgs_from(_on(), home.appliance.sound.player.state.off.State())
        soco_plugin.Gateway.get_action(self.player, leave[0])()
        self.player.unjoin.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
