"""Class for building sysbot-base clickseq commands"""

from typing import Self
from ..nxreader.nxreader import NXReader
from ..enums import Button, InputSeqEvent, Stick


class ClickSeq:
    """Class for building sysbot-base clickseq commands"""

    def __init__(self) -> None:
        self.actions: list[
            tuple[InputSeqEvent, Button | int] | tuple[InputSeqEvent, int, int]
        ] = []
        self.command_modified = True
        self._built_command: str = ""
        self._assumed_time: float = 0

    def click(self, button: Button) -> Self:
        """Add a click event to the sequence"""
        self.actions.append((InputSeqEvent.CLICK, button))
        self.command_modified = True
        return self

    def press(self, button: Button) -> Self:
        """Add a press event to the sequence"""
        self.actions.append((InputSeqEvent.PRESS, button))
        self.command_modified = True
        return self

    def release(self, button: Button) -> Self:
        """Add a press event to the sequence"""
        self.actions.append((InputSeqEvent.RELEASE, button))
        self.command_modified = True
        return self

    def wait(self, ms_duration: int) -> Self:
        """Add a wait event to the sequence"""
        self.actions.append((InputSeqEvent.WAIT, ms_duration))
        self.command_modified = True
        return self

    def dummy_click(self) -> Self:
        """Add a click event for POKEBALL_PLUS, doing nothing but allowing HOME to work"""
        return self.click(Button.POKEBALL_PLUS)

    def _move_left_stick(self, x_value: int, y_value: int) -> Self:
        """Add a move left stick event to the sequence"""
        self.actions.append((InputSeqEvent.MOVE_LEFT_STICK, x_value, y_value))
        self.command_modified = True
        return self

    def _move_right_stick(self, x_value: int, y_value: int) -> Self:
        """Add a move right stick event to the sequence"""
        self.actions.append((InputSeqEvent.MOVE_RIGHT_STICK, x_value, y_value))
        self.command_modified = True
        return self

    def hold(self, button: Button, ms_duration: int) -> Self:
        """Add a press, wait, then release event to hold a button"""
        return self.press(button).wait(ms_duration).release(button)

    def move_stick(self, stick: Stick, x_value: int, y_value: int) -> Self:
        """Add a move right or left stick event depending on stick input"""
        return (
            self._move_left_stick(x_value, y_value)
            if stick == Stick.LEFT
            else self._move_right_stick(x_value, y_value)
        )

    def release_stick(self, stick: Stick) -> Self:
        """Reset stick to (0, 0)"""
        return self.move_stick(stick, 0, 0)

    def hold_stick(
        self, stick: Stick, x_value: int, y_value: int, ms_duration: int
    ) -> Self:
        """Add move right or left stick event, wait event, normalizing right/left stick event"""
        return (
            self.move_stick(stick, x_value, y_value)
            .wait(ms_duration)
            .release_stick(stick)
        )

    def build(self) -> str:
        """Build click seq command, update built_command and return"""
        assumed_time, built_command = self.build_click_seq(self.actions)
        self._assumed_time = assumed_time
        self._built_command = built_command
        self.command_modified = False
        return built_command

    @staticmethod
    def build_click_seq(actions: list):
        """Build clickSeq command"""
        assumed_time = 0
        built_command = "clickSeq "
        for event_type, *arguments in actions:
            match event_type:
                case InputSeqEvent.CLICK:
                    button: Button = arguments[0]
                    built_command += f"{button.value},"
                case InputSeqEvent.PRESS:
                    button: Button = arguments[0]
                    built_command += f"+{button.value},"
                case InputSeqEvent.RELEASE:
                    button: Button = arguments[0]
                    built_command += f"-{button.value},"
                case InputSeqEvent.WAIT:
                    ms_duration: int = arguments[0]
                    built_command += f"W{ms_duration},"
                    assumed_time += ms_duration / 1000
                case InputSeqEvent.MOVE_LEFT_STICK:
                    x_value: int = arguments[0]
                    y_value: int = arguments[1]
                    built_command += f"%{x_value},{y_value},"
                case InputSeqEvent.MOVE_RIGHT_STICK:
                    x_value: int = arguments[0]
                    y_value: int = arguments[1]
                    built_command += f"&{x_value},{y_value},"
        if built_command.endswith(","):
            built_command = built_command[:-1]
        return assumed_time, built_command

    def execute(self, reader: NXReader) -> Self:
        """Send clickseq command to a NXReader object"""
        reader.send_command(str(self))
        reader.wait_until_clickseq_done(self._assumed_time * 1.5 + 1)
        return self

    def __str__(self) -> str:
        return self.build() if self.command_modified else self._built_command
