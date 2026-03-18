from __future__ import annotations

import asyncio
import logging
import requests
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import home
import soco
from soco_plugin.message import Command, Description, Trigger, Msg
from soco_plugin import command, trigger


class Gateway(home.protocol.Gateway):

    PROTOCOL = Description.PROTOCOL

    def __init__(self):
        self._players = {}
        self.executor = ThreadPoolExecutor(max_workers=100)
        self.logger = logging.getLogger(__name__)

    async def disconnect(self) -> None:
        for player, sub_rendering, sub_avtransport in self._players.values():
            player.renderingControl.unsubscribe()
            player.avTransport.unsubscribe()
        self.executor.shutdown(wait=True)

    async def _associate(self, descriptions: Iterable[Description]) -> None:
        loop = asyncio.get_running_loop()
        for description in descriptions:
            for name in description.msg["addresses"]:
                if name not in self._players:
                    try:
                        player = await loop.run_in_executor(
                            self.executor,
                            lambda: soco.discovery.scan_network_get_by_name(
                                name
                            ),
                        )
                    except TypeError as e:
                        self.logger.error(e)
                        player = None
                    except ConnectionError as e:
                        self.logger.error(e)
                        player = None
                    except requests.exceptions.ReadTimeout as e:
                        self.logger.error(e)
                        player = None
                    self.logger.info("Player %s: %s" % (name, str(player)))
                    if player:
                        # Subscribe calls are blocking and must run in executor
                        sub_rendering = await loop.run_in_executor(
                            self.executor,
                            lambda: player.renderingControl.subscribe(),
                        )
                        sub_avtransport = await loop.run_in_executor(
                            self.executor,
                            lambda: player.avTransport.subscribe(),
                        )
                        self._players[name] = (
                            player,
                            sub_rendering,
                            sub_avtransport,
                        )

    async def associate_commands(
        self, descriptions: Iterable[Command]
    ) -> None:
        await self._associate(descriptions)

    async def associate_triggers(
        self, descriptions: Iterable[Trigger]
    ) -> None:
        await self._associate(descriptions)

    def build_msg(
        self,
        address: str,
        action: Optional[str],
        fields: Optional[dict] = None,
    ) -> Msg:
        msg = Msg()
        msg["type"] = Description.PROTOCOL
        msg["name"] = action
        msg["addresses"] = [address]
        msg["fields"] = fields if fields else {}
        return msg

    def build_msgs_from_bus(self, player: soco.SoCo, event) -> list[Msg]:
        msgs = list()
        if "transport_state" in event.variables:
            transport_state = event.variables["transport_state"]
            # if "PAUSED_PLAYBACK" in transport_state:
            #    msgs.append(self.build_msg(player.player_name,
            #                               trigger.pause.Trigger.ACTION))
            if "PLAYING" in transport_state:
                msgs.append(
                    self.build_msg(
                        player.player_name, trigger.play.Trigger.ACTION
                    )
                )
            elif "PAUSED" in transport_state:
                msgs.append(
                    self.build_msg(
                        player.player_name, trigger.pause.Trigger.ACTION
                    )
                )
            elif "STOPPED" in transport_state:
                msgs.append(
                    self.build_msg(
                        player.player_name, trigger.stop.Trigger.ACTION
                    )
                )
        elif "volume" in event.variables:
            msgs.append(
                self.build_msg(
                    player.player_name,
                    trigger.volume.Trigger.ACTION,
                    {"volume": event.variables["volume"]["Master"]},
                )
            )
        return msgs

    async def _wait_for_event(self, player: soco.SoCo, channel, tasks) -> None:
        loop = asyncio.get_running_loop()
        self.logger.info(
            "Waiting for events from player {}".format(player.player_name)
        )
        while True:
            await asyncio.sleep(0.01)  # avoid potential starvation
            try:
                event = await loop.run_in_executor(
                    self.executor,
                    lambda: channel.events.get(block=True),
                )
                self.logger.debug(
                    "Sonos event from %s: %s"
                    % (player.player_name, str(event))
                )
                msgs = self.build_msgs_from_bus(player, event)
                for task in tasks:
                    for msg in msgs:
                        self.logger.debug(
                            "Processing Sonos event: {}".format(msg)
                        )
                        loop.create_task(task(msg))
            except Exception as e:
                self.logger.error(e)

    @staticmethod
    def get_action(player: soco.SoCo, msg: Command) -> Optional[Callable]:
        """
        >>> import home
        >>> import soco_plugin
        >>> class Player:
        ...     player_name = "TestPlayer"
        ...     def play(self):
        ...         print("play")
        ...     def pause(self):
        ...         print("pause")
        ...     def stop(self):
        ...         print("stop")
        ...     @property
        ...     def volume(self):
        ...         return 1
        ...     @property
        ...     def play_mode(self):
        ...         return "booo"
        ...     @volume.setter
        ...     def volume(self, value):
        ...         print("volume is {}".format(value))
        ...     @play_mode.setter
        ...     def play_mode(self, mode):
        ...         print("play mode is {}".format(mode))
        ...     def get_sonos_playlist_by_attr(self, attr, title):
        ...         print ("playlist title is {}".format(title))
        ...         class Playlist:
        ...             def __init__(self):
        ...                 class Resource:
        ...                     uri = "a uri"
        ...                 self.resources = [Resource()]
        ...         return Playlist()
        ...     def clear_queue(self):
        ...         pass
        ...     def add_uri_to_queue(self, uri):
        ...         pass
        ...     def play_from_queue(self, index):
        ...         pass
        ...     def ramp_to_volume(self, volume, ramp_type):
        ...         print("ramp to {} {}".format(volume, ramp_type))

        >>> old_state = home.appliance.sound.player.state.off.State()
        >>> new_state = old_state.next(home.appliance.sound.player.event.forced.Event.On)
        >>> new_state = new_state.next(home.event.sleepiness.Event.Awake)
        >>> msgs = soco_plugin.command.play.Command.make(["Bath"]).make_msgs_from(old_state, new_state)
        >>> action = soco_plugin.Gateway.get_action(Player(), msgs[0])
        >>> action()
        play
        >>> msgs = soco_plugin.command.volume.absolute.Command.make(["Bath"]).make_msgs_from(old_state, new_state)
        >>> action = soco_plugin.Gateway.get_action(Player(), msgs[0])
        >>> action()
        volume is 20
        >>> msgs = soco_plugin.command.volume.relative.Command.make(["Bath"]).make_msgs_from(old_state, new_state)
        >>> action = soco_plugin.Gateway.get_action(Player(), msgs[0])
        >>> action()
        volume is 11
        >>> msgs = soco_plugin.command.playlist.Command.make(["Bath"]).make_msgs_from(old_state, new_state)
        >>> action = soco_plugin.Gateway.get_action(Player(), msgs[0])
        >>> action()
        playlist title is Common
        >>> old_state = home.appliance.sound.player.state.off.State()
        >>> old_state = old_state.next(home.event.presence.Event.On)
        >>> old_state = old_state.next(home.event.sleepiness.Event.Asleep)
        >>> new_state = old_state.next(home.event.sleepiness.Event.Awake)
        >>> msgs = soco_plugin.command.volume.ramp.Command.make(["Bath"]).make_msgs_from(old_state, new_state)
        >>> action = soco_plugin.Gateway.get_action(Player(), msgs[0])
        >>> action()
        ramp to 30 SLEEP_TIMER_RAMP_TYPE
        >>> msgs = soco_plugin.command.mode.Command.make(["Bath"]).make_msgs_from(old_state, new_state)
        >>> action = soco_plugin.Gateway.get_action(Player(), msgs[0])
        >>> action()
        play mode is SHUFFLE

        :param msg: a command message to be executed
        :param player: a player where the command will be applied
        :return: a callable to execute
        """
        name = msg["name"]
        fields = msg["fields"]
        action = None
        if name == command.play.Command.ACTION:
            action = lambda: command.play.action(player)  # noqa
        elif name == command.stop.Command.ACTION:
            action = lambda: command.stop.action(player)  # noqa
        elif name == command.pause.Command.ACTION:
            action = lambda: command.pause.action(player)  # noqa
        elif name == command.volume.relative.Command.ACTION:
            action = lambda: command.volume.relative.action(  # noqa: E731
                player, **fields
            )
        elif name == command.volume.absolute.Command.ACTION:
            action = lambda: command.volume.absolute.action(  # noqa: E731
                player, **fields
            )
        elif name == command.volume.ramp.Command.ACTION:
            action = lambda: command.volume.ramp.action(  # noqa: E731
                player, **fields
            )
        elif name == command.playlist.Command.ACTION:
            action = lambda: command.playlist.action(player, **fields)  # noqa
        elif name == command.mode.Command.ACTION:
            action = lambda: command.mode.action(player, **fields)  # noqa
        return action

    async def send_msg(self, msg: Command, player: soco.SoCo) -> None:
        self.logger.info(
            "Executing Sonos action {} on player {}".format(
                msg["name"], player.player_name
            )
        )
        if msg:
            action = self.get_action(player, msg)
            if action is not None:
                self.logger.info("Action found: {}".format(action))
                try:
                    await asyncio.get_running_loop().run_in_executor(
                        self.executor, action
                    )
                    self.logger.info("Action executed successfully")
                except soco.exceptions.SoCoUPnPException as e:
                    self.logger.error("SoCo UPnP exception: {}".format(e))
                except Exception as e:
                    self.logger.error(
                        "Exception executing action: {}".format(e)
                    )
            else:
                self.logger.warning(
                    "No action found for message: {}".format(msg)
                )

    async def writer(self, msgs: Iterable[Command], *args) -> None:
        self.logger.debug("Writer called")
        msg_count = 0
        for msg in msgs:
            msg_count += 1
            self.logger.info(
                "Processing message {}: {} (type: {})".format(
                    msg_count, msg, type(msg)
                )
            )
            if isinstance(msg, Msg):
                for address in msg["addresses"]:
                    self.logger.info(
                        "Checking address: {} in players: {}".format(
                            address, list(self._players.keys())
                        )
                    )
                    if address in self._players:
                        (player, _, _) = self._players[address]
                        self.logger.info(
                            "Sending Sonos command {} to {}".format(
                                msg, address
                            )
                        )
                        await self.send_msg(msg, player)
                    else:
                        self.logger.warning(
                            "Address {} not found in players {}".format(
                                address, list(self._players.keys())
                            )
                        )
            else:
                self.logger.warning(
                    "Message is not a Msg instance: {} (type: {})".format(
                        msg, type(msg)
                    )
                )
        if msg_count == 0:
            self.logger.debug("Writer called with 0 messages")

    @staticmethod
    def make_trigger(msg: Description) -> Trigger:
        t = Trigger.make_from(msg)
        return t

    async def run(self, other_tasks: Iterable[Callable]) -> None:
        loop = asyncio.get_running_loop()
        wrapped_tasks = self._wrap_tasks(other_tasks)
        for player, sub_rendering, sub_avtransport in self._players.values():
            loop.create_task(
                self._wait_for_event(player, sub_avtransport, wrapped_tasks),
                name="Soco wait for event (avtransport) for {}".format(
                    player.player_name
                ),
            )
            loop.create_task(
                self._wait_for_event(player, sub_rendering, wrapped_tasks),
                name="Soco wait for event (rendering) for {}".format(
                    player.player_name
                ),
            )
