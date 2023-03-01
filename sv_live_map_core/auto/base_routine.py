"""Base Routine for automation"""

from abc import ABC, abstractmethod
import discord_webhook
from ..nxreader.nxreader import NXReader


class BaseRoutine(ABC):
    """Base Routine for automation"""

    def __init__(self) -> None:
        self.webhooks: list[dict] = []
        self.reader: NXReader = None

    @abstractmethod
    def start_routine(self) -> None:
        """All actions neccesary to start the routine"""

    @abstractmethod
    def stop_routine(self) -> None:
        """All actions neccesary to stop the routine"""

    @abstractmethod
    def routine_work(self) -> None:
        """Work to be run in the routine's thread"""

    @abstractmethod
    def check_on_routine(self) -> bool:
        """Check on routine to see if it is still running"""

    def send_webhook_log(self, log_message: str, error: bool = False):
        """Send simple string log to webhooks if applicable"""
        print(f"Sending Webhook: {log_message=}")
        for webhook in self.webhooks:
            if webhook.get("Active", False):
                if error:
                    if webhook.get("SendExceptions"):
                        webhook_message = discord_webhook.webhook.DiscordWebhook(
                            url=webhook.get("WebhookURL", False),
                            content=f"<@{webhook.get('IDToPing', '')}> {log_message}",
                        )
                        webhook_message.execute()
                elif webhook.get("SendLogs"):
                    webhook_message = discord_webhook.webhook.DiscordWebhook(
                        url=webhook.get("WebhookURL", False), content=log_message
                    )
                    webhook_message.execute()
