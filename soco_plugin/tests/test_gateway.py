# SPDX-License-Identifier: GPL-3.0-only
#
# automate home devices
#
# Copyright (C) 2021  Maja Massarini

import asyncio
import unittest
import unittest.mock

import soco_plugin


class TestGateway(unittest.TestCase):
    def test_stopped(tc):
        events = []

        class Test(unittest.IsolatedAsyncioTestCase):

            STATE_CHANGED = "stopped"
            MAX_LOOP = 10

            async def a_task(self, msgs):
                events.append(self.STATE_CHANGED)

            async def postpone_gw_running(self):
                await asyncio.sleep(0.1)
                await self._gw.run([self.a_task])

            async def asyncSetUp(self):
                self._gw = soco_plugin.Gateway()
                self._loop = asyncio.get_event_loop()
                self._loop.create_task(
                    self._gw.associate_triggers(
                        [
                            soco_plugin.Description(
                                {
                                    "type": "soco",
                                    "name": "volume",
                                    "fields": {"delta": 100},
                                    "addresses": ["Bagno"],
                                }
                            )
                        ]
                    )
                )
                self._loop.create_task(self.postpone_gw_running())

            async def test_stopped(self):
                i = 0
                while self.STATE_CHANGED not in events and i < self.MAX_LOOP:
                    await asyncio.sleep(1)
                    i += 1

        test = Test("test_stopped")
        mock = unittest.mock.Mock()
        event_mock = unittest.mock.Mock()
        event_mock.variables = {"transport_state": "STOPPED"}
        av_mock = unittest.mock.Mock()
        av_mock.events.get.return_value = event_mock
        mock.avTransport.subscribe.return_value = av_mock
        with unittest.mock.patch("soco.discovery.by_name") as new_mock:
            new_mock.return_value = mock
            test.run()
        tc.assertIn(Test.STATE_CHANGED, events)

    def test_stopped_answer_after_play_command(tc):
        events = []

        class Test(unittest.IsolatedAsyncioTestCase):
            STATE_CHANGED = "stopped"
            MAX_LOOP = 10

            async def a_task(self, msgs):
                events.append(self.STATE_CHANGED)

            async def postpone_writer_running(self, msgs):
                await asyncio.sleep(0.1)
                await self._gw.writer(msgs)

            async def postpone_gw_running(self):
                await asyncio.sleep(0.2)
                await self._gw.run([self.a_task])

            async def asyncSetUp(self):
                self._gw = soco_plugin.Gateway()
                self._loop = asyncio.get_event_loop()
                self._loop.create_task(
                    self._gw.associate_triggers(
                        [
                            soco_plugin.Description(
                                {
                                    "type": "soco",
                                    "name": "volume",
                                    "fields": {"delta": 100},
                                    "addresses": ["Bagno"],
                                }
                            )
                        ]
                    )
                )
                self._loop.create_task(
                    self.postpone_writer_running(
                        soco_plugin.command.play.Command.make(
                            [
                                "Bagno",
                            ]
                        ).execute()
                    )
                )
                self._loop.create_task(self.postpone_gw_running())

            async def test_stopped(self):
                i = 0
                while self.STATE_CHANGED not in events and i < self.MAX_LOOP:
                    await asyncio.sleep(1)
                    i += 1

        test = Test("test_stopped")
        mock = unittest.mock.Mock()
        event_mock = unittest.mock.Mock()
        event_mock.variables = {"transport_state": "STOPPED"}
        av_mock = unittest.mock.Mock()
        av_mock.events.get.return_value = event_mock
        mock.avTransport.subscribe.return_value = av_mock
        with unittest.mock.patch("soco.discovery.by_name") as new_mock:
            new_mock.return_value = mock
            test.run()
        tc.assertIn(Test.STATE_CHANGED, events)
