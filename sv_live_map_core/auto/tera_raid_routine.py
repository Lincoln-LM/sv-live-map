"""Routine for automating dateskipping of tera raids"""

from __future__ import annotations
from threading import Thread
from typing import TYPE_CHECKING
import os
import contextlib
import time
import struct
import binascii
import tkinter
import io
import customtkinter
import discord_webhook
from PIL import Image, ImageTk
from .base_routine import BaseRoutine
from .inputseq import InputSeq
from ..widget.raid_info_widget import RaidInfoWidget
from ..save.raid_block import RaidBlock, TeraRaid
from ..util.raid_filter import RaidFilter
from ..util.path_handler import get_path
from ..enums import Button

if TYPE_CHECKING:
    from ..window.application import Application


# TODO: exceptions.py
class NotConnectedException(Exception):
    """Exception for when not connected to switch"""


class TeraRaidRoutine(BaseRoutine):
    """Routine for automating dateskipping of tera raids"""

    def __init__(self) -> None:
        super().__init__()
        self.filters: list[RaidFilter] = []
        self.settings: dict = {}
        self.thread_alive = False
        self.parent_application: Application = None
        self.date_skip_routine = InputSeq()
        self.date_skip_routine = (
            self.date_skip_routine
            # (hopefully) fixes the issue of HOME not working as first input
            .dummy_click()
            .click(Button.HOME)
            .wait(600)
            .touch_hold(845, 545, 50)
            .touch_hold(845, 545, 50)
            .hold(Button.DPAD_DOWN, 2300)
            .touch_hold(1150, 670, 50)
            .hold(Button.DPAD_DOWN, 760)
            .touch_hold(1150, 670, 50)
            .wait(150)
            .touch_hold(1006, 386, 50)
            .wait(150)
            .touch_hold(151, 470, 50)
            .wait(150)
            .touch_hold(1102, 470, 50)
            .wait(150)
            .click(Button.HOME)
            .wait(800)
            .click(Button.HOME)
            .wait(3000)
        )

    def start_routine(self) -> None:
        """Start dateskip automation routine"""
        if self.reader is None:
            raise NotConnectedException("Not connected to switch")
        self.send_webhook_log("Tera Raid Routine Starting...")
        self.thread_alive = True
        Thread(target=self.routine_work).start()

    def stop_routine(self) -> None:
        """Manually stop dateskip automation routine"""
        self.thread_alive = False
        self.send_webhook_log("Tera Raid Routine Stopping...")

    def routine_work(self) -> None:
        """Work to be run within the routine's thread"""
        total_raid_count = 0
        total_reset_count = 0
        last_seed = None
        while self.thread_alive:
            try:
                total_raid_count, total_reset_count, last_seed, raid_block = \
                    self.read_raids(total_raid_count, total_reset_count, last_seed)

                target_found = False

                for raid in raid_block.raids:
                    matches_filters = False

                    if not raid.is_enabled:
                        continue

                    for raid_filter in self.filters:
                        if not raid_filter.is_enabled:
                            continue
                        matches_filters |= raid_filter.compare(raid)
                        target_found |= matches_filters

                    if matches_filters:
                        if self.settings.get('Popup', False):
                            self.open_raid_popup(raid)
                        for webhook in self.webhooks:
                            self.send_raid_webhook(raid, webhook)
                if target_found:
                    # render map if target found
                    self.parent_application.read_all_raids(True)
                    # wait until rendering is done
                    while self.parent_application.render_thread is not None:
                        self.reader.pause(0.2)
                    self.thread_alive = False
                    break

                self.date_skip_routine.execute(self.reader)
            except (TimeoutError, struct.error, binascii.Error) as error:
                self.send_webhook_log(str(error), True)
                raise error
        self.send_webhook_log("Tera Raid Routine Ended.")

    def check_on_routine(self) -> bool:
        """Check on routine to see if it is still running"""
        return self.thread_alive

    def advance_date(self) -> None:
        """Advance date once"""
        if self.reader is None:
            raise NotConnectedException("Not connected to switch")
        self.send_webhook_log("Skipping Date...")
        Thread(target=lambda: self.date_skip_routine.execute(self.reader)).start()

    def read_raids(
        self,
        total_raid_count: int,
        total_reset_count: int,
        last_seed: int
    ) -> tuple[int, int, int, RaidBlock]:
        """Read and parse raids"""
        raid_block = self.parent_application.read_all_raids(self.settings.get("MapRender", False))
        if raid_block.current_seed != last_seed:
            last_seed = raid_block.current_seed
            total_reset_count += 1
            total_raid_count += 69
        else:
            self.send_webhook_log("Raid seed is a duplicate of the previous day, unsuccessful skip")
        print(
            f"Raid Block Processsed: {total_reset_count=} "
            f"{total_raid_count=} "
            f"{raid_block.current_seed=:X}"
        )
        # wait until rendering is done
        while self.parent_application.render_thread is not None:
            self.reader.pause(0.2)
        return total_raid_count, total_reset_count, last_seed, raid_block

    def open_raid_popup(self, raid: TeraRaid):
        """Open Raid Popup"""
        return self.parent_application.widget_message_window(
            f"Shiny {raid.species} ★"
            if raid.is_shiny else str(raid.species),
            RaidInfoWidget,
            poke_sprite_handler=self.parent_application.sprite_handler,
            raid_data=raid,
            hide_sensitive_info=self.parent_application.hide_info_check.get(),
            fg_color=customtkinter.ThemeManager.theme["color"]["frame_low"],
        )

    def send_raid_webhook(self, raid: TeraRaid, webhook: dict):
        """Send Raid Webhook"""
        if not webhook.get("Active", False):
            return
        if not webhook.get("SendRaids", False):
            return
        if webhook.get("UseEmbedDisplay", False):
            self.send_raid_webhook_embed(webhook, raid)
        else:
            self.send_raid_webhook_widget(raid, webhook)

    def send_raid_webhook_widget(self, raid, webhook):
        """Send Raid Webhook as Widget"""
        popup_window, widget = self.open_raid_popup(raid)
        time.sleep(1)
        widget: RaidInfoWidget
        img = widget.create_image(webhook.get("IncludeRewards", False))
        # unsure why this happens even when window is properly destroyed
        with contextlib.suppress(tkinter.TclError):
            popup_window.destroy()
        if not os.path.exists(get_path("./found_screenshots/")):
            os.mkdir(get_path("./found_screenshots/"))
        img.save(get_path(f"./found_screenshots/{raid.seed}.png"))
        with open(get_path(f"./found_screenshots/{raid.seed}.png"), "rb") as img:
            webhook_message = discord_webhook.webhook.DiscordWebhook(
                url=webhook.get("WebhookURL", ""),
                content=f"<@{webhook.get('IDToPing', '')}>"
            )
            webhook_message.add_file(img.read(), "img.png")
            webhook_message.execute()

    def send_raid_webhook_embed(self, webhook, raid):
        """Send Raid Webhook as embed"""
        webhook_message = discord_webhook.webhook.DiscordWebhook(
            url=webhook.get("WebhookURL", ""),
            content=f"<@{webhook.get('IDToPing', '')}>"
        )
        embed = discord_webhook.webhook.DiscordEmbed(
            title=f"Shiny {raid.species} ★"
            if raid.is_shiny else str(raid.species),
            color=0xF8C8DC
        )
        embed.set_image("attachment://poke.png")
        embed.set_author(
            f"{raid.tera_type} Tera Type",
            icon_url="attachment://tera.png"
        )
        dummy_widget = RaidInfoWidget(
            poke_sprite_handler=self.parent_application.sprite_handler,
            raid_data=raid,
            hide_sensitive_info=self.parent_application.hide_info_check.get(),
        )

        poke_sprite_img: Image = ImageTk.getimage(dummy_widget.poke_sprite)
        with io.BytesIO() as poke_sprite_bytes:
            poke_sprite_img.save(poke_sprite_bytes, format="PNG")
            webhook_message.add_file(
                poke_sprite_bytes.getvalue(),
                "poke.png"
            )

        tera_sprite_img: Image = ImageTk.getimage(dummy_widget.tera_sprite)
        with io.BytesIO() as tera_sprite_bytes:
            tera_sprite_img.save(tera_sprite_bytes, format="PNG")
            webhook_message.add_file(
                tera_sprite_bytes.getvalue(),
                "tera.png"
            )
        embed.add_embed_field("Info", str(dummy_widget.info_display.text))
        if webhook.get("IncludeRewards", False):
            item_embed = discord_webhook.webhook.DiscordEmbed(
                title=f"{raid.species} Items",
                color=0xF8C8DC
            )
            item_embed.add_embed_field(
                "Items",
                "\n".join(
                    f"{reward[1]}x {reward[0]}" for reward in raid.rewards
                )
            )

        webhook_message.add_embed(embed)
        if webhook.get("IncludeRewards", False):
            webhook_message.add_embed(item_embed)
        webhook_message.execute()
