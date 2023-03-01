"""Webhook settings widget"""

import glob
import json
import os
import customtkinter
from PIL import ImageTk, Image
from ..window.text_input_dialouge_window import TextInputDialogueWindow
from ..window.bool_input_dialouge_window import BoolInputDialogueWindow
from ..util.path_handler import get_path


class WebhookSettingsWidget(customtkinter.CTkFrame):
    """Webhook settings widget"""

    EDIT_IMAGE: ImageTk.PhotoImage = None
    NEW_IMAGE: ImageTk.PhotoImage = None
    DELETE_IMAGE: ImageTk.PhotoImage = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_images()
        self.draw_webhook_frame()
        self.select_webhook(self.webhook_combobox.values[0])

    def cache_images(self):
        """Cache GUI images"""
        if WebhookSettingsWidget.EDIT_IMAGE is None:
            WebhookSettingsWidget.EDIT_IMAGE = ImageTk.PhotoImage(
                Image.open(get_path("./resources/icons8/pencil.png"))
            )
        if WebhookSettingsWidget.NEW_IMAGE is None:
            WebhookSettingsWidget.NEW_IMAGE = ImageTk.PhotoImage(
                Image.open(get_path("./resources/icons8/plus.png"))
            )
        if WebhookSettingsWidget.DELETE_IMAGE is None:
            WebhookSettingsWidget.DELETE_IMAGE = ImageTk.PhotoImage(
                Image.open(get_path("./resources/icons8/trash.png"))
            )

    def draw_webhook_frame(self):
        """Draw frame with settings information"""
        self.webhook_combobox_label = customtkinter.CTkLabel(
            self, text="Current Webhook:"
        )
        self.webhook_combobox_label.grid(row=0, column=0)
        self.webhook_combobox = customtkinter.CTkComboBox(
            self, values=self.get_webhooks(), width=220, command=self.select_webhook
        )
        self.webhook_combobox.grid(row=0, column=1, columnspan=4)
        self.webhook_combobox.entry.configure(state="disabled")

        self.new_webhook_button = customtkinter.CTkButton(
            self,
            text="",
            image=self.NEW_IMAGE,
            fg_color=customtkinter.ThemeManager.theme["color"]["frame_low"],
            width=self.NEW_IMAGE.width(),
            height=self.NEW_IMAGE.height(),
            command=self.new_webhook,
        )
        self.new_webhook_button.grid(row=0, column=5)

        self.edit_webhook_button = customtkinter.CTkButton(
            self,
            text="",
            image=self.EDIT_IMAGE,
            fg_color=customtkinter.ThemeManager.theme["color"]["frame_low"],
            width=self.EDIT_IMAGE.width(),
            height=self.EDIT_IMAGE.height(),
            command=self.edit_webhook,
        )
        self.edit_webhook_button.grid(row=0, column=6)
        self.delete_webhook_button = customtkinter.CTkButton(
            self,
            text="",
            image=self.DELETE_IMAGE,
            fg_color=customtkinter.ThemeManager.theme["color"]["frame_low"],
            width=self.DELETE_IMAGE.width(),
            height=self.DELETE_IMAGE.height(),
            command=self.delete_webhook,
        )
        self.delete_webhook_button.grid(row=0, column=7)

        self.webhook_active = customtkinter.CTkCheckBox(
            master=self,
            text="Webhook Active",
        )
        self.webhook_active.grid(row=1, column=0, columnspan=7, padx=10, pady=10)

        self.include_rewards_check = customtkinter.CTkCheckBox(
            master=self,
            text="Include Raid Rewards",
        )
        self.include_rewards_check.grid(row=2, column=0, columnspan=7, padx=10, pady=10)

        self.send_exception_check = customtkinter.CTkCheckBox(
            master=self,
            text="Send Exceptions",
        )
        self.send_exception_check.grid(row=3, column=0, columnspan=7, padx=10, pady=10)

        self.send_logs_check = customtkinter.CTkCheckBox(
            master=self,
            text="Send Logs",
        )
        self.send_logs_check.grid(row=4, column=0, columnspan=7, padx=10, pady=10)

        self.send_raids_check = customtkinter.CTkCheckBox(
            master=self,
            text="Send Filtered Raids",
        )
        self.send_raids_check.grid(row=5, column=0, columnspan=7, padx=10, pady=10)

        self.embed_frame = customtkinter.CTkFrame(
            self,
            fg_color=customtkinter.ThemeManager.theme["color"]["frame_low"],
        )
        self.widget_label = customtkinter.CTkLabel(
            master=self.embed_frame, text="Widget display"
        )
        self.widget_label.grid(row=0, column=0, padx=(10, 0))

        self.embed_select = customtkinter.CTkSwitch(
            master=self.embed_frame,
            # padding
            text="     Embed display",
        )
        self.embed_select.grid(row=0, column=1, padx=(0, 10))
        self.embed_frame.grid(row=6, column=0, columnspan=7, pady=10)

        self.ping_entry_frame = customtkinter.CTkFrame(
            self,
            fg_color=customtkinter.ThemeManager.theme["color"]["frame_low"],
        )
        self.ping_entry_label = customtkinter.CTkLabel(
            master=self.ping_entry_frame, text="ID to Ping:"
        )
        self.ping_entry_label.grid(row=0, column=0)

        self.ping_entry = customtkinter.CTkEntry(
            master=self.ping_entry_frame, width=150
        )
        self.ping_entry.grid(row=0, column=1)
        self.ping_entry_frame.grid(row=7, column=0, columnspan=7, padx=10, pady=10)

        self.webhook_url_entry_frame = customtkinter.CTkFrame(
            self,
            fg_color=customtkinter.ThemeManager.theme["color"]["frame_low"],
        )
        self.webhook_url_entry_label = customtkinter.CTkLabel(
            master=self.webhook_url_entry_frame, text="Webhook URL:"
        )
        self.webhook_url_entry_label.grid(row=0, column=0)

        self.webhook_url_entry = customtkinter.CTkEntry(
            master=self.webhook_url_entry_frame, width=150
        )
        self.webhook_url_entry.grid(row=0, column=1)
        self.webhook_url_entry_frame.grid(
            row=8, column=0, columnspan=7, padx=10, pady=10
        )

    def save_webhook(self):
        """Save currently selected webhook"""
        if name := self.webhook_combobox.get():
            with open(
                get_path(f"./resources/webhook_settings/{name}"), "w+", encoding="utf-8"
            ) as webhook_file:
                json.dump(self.build_webhook_json(), webhook_file, indent=2)

    def build_webhook_json(self):
        """Build webhook json"""
        return {
            "Active": self.webhook_active.get(),
            "IncludeRewards": self.include_rewards_check.get(),
            "SendExceptions": self.send_exception_check.get(),
            "SendLogs": self.send_logs_check.get(),
            "SendRaids": self.send_raids_check.get(),
            "UseEmbedDisplay": self.embed_select.get(),
            "IDToPing": self.ping_entry.get(),
            "WebhookURL": self.webhook_url_entry.get(),
        }

    def select_webhook(self, name: str):
        """To be run when a webhook is selected"""
        if name and name != self.webhook_combobox.get():
            self.save_webhook()
        self.webhook_combobox.entry.configure(state="normal")
        self.webhook_combobox.set(name)
        self.webhook_combobox.entry.configure(state="disabled")

        if name:
            file_path = get_path(f"./resources/webhook_settings/{name}")
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as webhook_file:
                    webhook_json = json.load(webhook_file)
                    self.load_webhook(webhook_json)

    def load_webhook(self, webhook_json: dict[str]):
        """Load webhook settings into gui"""
        self.webhook_active.check_state = bool(webhook_json.get("Active", False))
        self.webhook_active.draw()
        self.include_rewards_check.check_state = bool(
            webhook_json.get("IncludeRewards", False)
        )
        self.include_rewards_check.draw()
        self.send_exception_check.check_state = bool(
            webhook_json.get("SendExceptions", False)
        )
        self.send_exception_check.draw()
        self.send_logs_check.check_state = bool(webhook_json.get("SendLogs", False))
        self.send_logs_check.draw()
        self.send_raids_check.check_state = bool(webhook_json.get("SendRaids", False))
        self.send_raids_check.draw()
        self.embed_select.check_state = bool(webhook_json.get("UseEmbedDisplay", False))
        self.embed_select.draw()
        self.ping_entry.delete(0, "end")
        self.ping_entry.insert(0, webhook_json.get("IDToPing", ""))
        self.webhook_url_entry.delete(0, "end")
        self.webhook_url_entry.insert(0, webhook_json.get("WebhookURL", ""))

    def new_webhook(self):
        """Create a new webhook"""
        TextInputDialogueWindow(
            title="Webhook Creation",
            text="Enter New Webhook Name:",
            command=self.new_webhook_action,
        )

    def new_webhook_action(self, name: str):
        """Create new webhook file"""
        if name is None:
            return
        with open(
            get_path(f"./resources/webhook_settings/{name}.json"),
            "w+",
            encoding="utf-8",
        ) as new_webhook:
            new_webhook.write("{}")
        self.webhook_combobox.configure(values=self.get_webhooks())
        self.select_webhook(f"{name}.json")

    def edit_webhook(self):
        """Edit the name of a webhook"""
        TextInputDialogueWindow(
            title="Webhook Edit",
            text="Enter New Webhook Name:",
            command=self.edit_webhook_action,
        )

    def edit_webhook_action(self, name: str):
        """Rename webhook file"""
        if name is None:
            return
        os.rename(
            get_path(f"./resources/webhook_settings/{self.webhook_combobox.get()}"),
            get_path(f"./resources/webhook_settings/{name}.json"),
        )
        self.webhook_combobox.configure(values=self.get_webhooks())
        self.select_webhook(f"{name}.json")

    def delete_webhook(self):
        """Delete a webhook"""
        BoolInputDialogueWindow(
            title="Delete Webhook",
            text=f"Delete the webhook {self.webhook_combobox.get()}?",
            command=self.delete_webhook_action,
        )

    def delete_webhook_action(self, confirm: bool):
        """Delete webhook file"""
        if confirm:
            os.remove(
                get_path(f"./resources/webhook_settings/{self.webhook_combobox.get()}")
            )
            self.select_webhook("")
            self.webhook_combobox.configure(values=self.get_webhooks())
            # TODO: default case when no webhooks
            self.select_webhook(self.webhook_combobox.values[0])

    def get_webhooks(self) -> list[str]:
        """Get a list of all webhooks in the webhook settings directory"""
        return [
            file.split("/")[-1].split("\\")[-1]
            for file in glob.glob(get_path("./resources/webhook_settings/*.json"))
        ]

    def get_webhook_dicts(self) -> list[dict]:
        """Get a list of all webhooks as dicts"""
        dicts = []
        for filename in glob.glob(get_path("./resources/webhook_settings/*.json")):
            with open(filename, "r", encoding="utf-8") as file:
                dicts.append(json.load(file))
        return dicts
