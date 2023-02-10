"""Class for building sysbot-base input sequences"""

from typing import Self
from .clickseq import ClickSeq
from ..nxreader.nxreader import NXReader
from ..enums import Button, InputSeqEvent


class InputSeq(ClickSeq):
    """Class for building sysbot-base input sequences"""

    def __init__(self) -> None:
        self.actions: list[tuple[InputSeqEvent, Button | int] | tuple[InputSeqEvent, int, int]] = []
        self.command_modified = True
        self._built_commands: list[str] = []
        self._assumed_time: float = 0

    def touch(self, x_value: int, y_value: int) -> Self:
        """Add a touch event"""
        self.actions.append((InputSeqEvent.TOUCH, x_value, y_value))
        self.command_modified = True
        return self

    def touch_hold(self, x_value: int, y_value: int, ms_duration) -> Self:
        """Add a touch hold event"""
        self.actions.append((InputSeqEvent.TOUCH_HOLD, x_value, y_value, ms_duration))
        self.command_modified = True
        return self

    def build(self) -> str:
        """Build input seq command, update built_command and return"""
        total_assumed_time = 0
        current_actions = []
        for (event_type, *arguments) in self.actions:
            if event_type >= InputSeqEvent.TOUCH:
                # touch event, clickseq must be split
                if len(current_actions) > 0:
                    current_assumed_time, current_action = self.build_click_seq(current_actions)
                    total_assumed_time += current_assumed_time
                    current_actions = []
                    self._built_commands.append(
                        (InputSeqEvent.CLICK, current_assumed_time, current_action)
                    )
                if event_type == InputSeqEvent.TOUCH:
                    x_value: int = arguments[0]
                    y_value: int = arguments[1]
                    self._built_commands.append(
                        (InputSeqEvent.TOUCH, 0, f"touch {x_value} {y_value}")
                    )
                elif event_type == InputSeqEvent.TOUCH_HOLD:
                    x_value: int = arguments[0]
                    y_value: int = arguments[1]
                    ms_duration: int = arguments[2]
                    total_assumed_time += ms_duration / 1000
                    self._built_commands.append(
                        (
                            InputSeqEvent.TOUCH_HOLD,
                            ms_duration / 1000,
                            f"touchHold {x_value} {y_value} {ms_duration}"
                        )
                    )
            else:
                current_actions.append((event_type, *arguments))
        # touch event, clickseq must be split
        if len(current_actions) > 0:
            current_assumed_time, current_action = self.build_click_seq(current_actions)
            total_assumed_time += current_assumed_time
            current_actions = []
            self._built_commands.append(
                (InputSeqEvent.CLICK, current_assumed_time, current_action)
            )
        self._assumed_time = total_assumed_time
        self.command_modified = False
        return self._built_commands

    def execute(self, reader: NXReader) -> Self:
        """Send clickseq command to a NXReader object"""
        if self.command_modified:
            self.build()
        for (command_type, assumed_time, command) in self._built_commands:
            reader.send_command(command)
            if command_type < InputSeqEvent.TOUCH:
                reader.wait_until_clickseq_done(assumed_time * 1.5 + 1)
        return self

    def __str__(self) -> str:
        if self.command_modified:
            self.build()
        return '\n'.join(x[2] for x in self._built_commands)
