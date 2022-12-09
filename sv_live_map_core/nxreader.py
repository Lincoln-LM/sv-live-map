"""Simplified class to read information from sys-botbase
   https://github.com/Lincoln-LM/PyNXReader"""
import socket
import binascii
from time import sleep

class NXReader:
    """Simplified class to read information from sys-botbase"""
    def __init__(self, ip_address: str, port: int = 6000) -> None:
        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(1)
        self.socket.connect((ip_address, port))
        print('Connected')
        self.ls_lastx: int = 0
        self.ls_lasty: int = 0
        self.rs_lastx: int = 0
        self.rs_lasty: int = 0
        self._configure()

    def _send_command(self, content: str) -> None:
        """Send a command to sys-botbase on the switch"""
        content += '\r\n' # important for the parser on the switch side
        self.socket.sendall(content.encode())

    def _configure(self) -> None:
        self._send_command('configure echoCommands 0')

    def detach(self) -> None:
        """Detach controller from switch"""
        self._send_command('detachController')

    def _recv(self, size: int) -> bytes:
        """Receive response from sys-botbase"""
        return binascii.unhexlify(self.socket.recv(2 * size + 1)[:-1])

    def close(self) -> None:
        """Close connection to switch"""
        print("Exiting...")
        self.detach()
        self.pause(0.5)
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        print('Disconnected')

    # TODO: button enum
    def click(self, button: str) -> None:
        """Press and release button"""
        self._send_command(f'click {button}')

    def press(self, button: str) -> None:
        """Press and hold button"""
        self._send_command(f'press {button}')

    def release(self, button: str) -> None:
        """Release held button"""
        self._send_command(f'release {button}')

    def manual_click(self, button: str, delay: float = 0.1, init_count = 1):
        """Manually press and release button"""
        for _ in range(init_count):
            self.press(button)
        self.pause(delay)
        self.release(button)

    def touch_hold(self, x_val: int, y_val: int, delay_ms: int) -> None:
        """Hold the touch screen at (x, y) for delay ms"""
        self._send_command(f"touchHold {x_val} {y_val} {delay_ms}")

    def move_stick(self, stick: str, x_val: int, y_val: int) -> None:
        """Move stick to position"""
        self._send_command(f"setStick {stick} 0x{x_val:X} 0x{y_val:X}")

    def move_left_stick(self, x_val: int = None, y_val: int = None) -> None:
        """Move the left stick to position"""
        if x_val is not None:
            self.ls_lastx = x_val
        if y_val is not None:
            self.ls_lasty = y_val
        self.move_stick('LEFT', self.ls_lastx, self.ls_lasty)

    def move_right_stick(self, x_val: int = None, y_val: int = None) -> None:
        """Move the right stick to position"""
        if x_val is not None:
            self.rs_lastx = x_val
        if y_val is not None:
            self.rs_lasty = y_val
        self.move_stick('RIGHT', self.rs_lastx, self.rs_lasty)

    def read(self, address: int, size: int) -> bytes:
        """Read bytes from heap"""
        self._send_command(f'peek 0x{address:X} 0x{size:X}')
        sleep(size / 0x8000)
        return self._recv(size)

    def read_int(self, address: int, size: int) -> int:
        """Read integer from heap"""
        return int.from_bytes(self.read(address, size), 'little')

    def read_absolute(self, address: int, size: int) -> bytes:
        """Read bytes from absolute address"""
        self._send_command(f'peekAbsolute 0x{address:X} 0x{size:X}')
        sleep(size / 0x8000)
        return self._recv(size)

    def read_absolute_int(self, address: int, size: int) -> int:
        """Read integer from absolute address"""
        return int.from_bytes(self.read_absolute(address, size), 'little')

    def write(self, address: int, data: str) -> None:
        """Write data to heap"""
        self._send_command(f'poke 0x{address:X} 0x{data}')

    def read_main(self, address: int, size: int) -> bytes:
        """Read bytes from main"""
        self._send_command(f'peekMain 0x{address:X} 0x{size:X}')
        sleep(size / 0x8000)
        return self._recv(size)

    def read_main_int(self, address: int, size: int) -> int:
        """Read integer from main"""
        return int.from_bytes(self.read_main(address, size), 'little')

    def write_main(self, address, data) -> None:
        """Write data to main"""
        self._send_command(f'pokeMain 0x{address:X} 0x{data}')

    def read_pointer(self, pointer: str, size: int) -> bytes:
        """Read bytes from pointer"""
        jumps = pointer.replace('[', '').replace('main', '').split(']')
        command = f'pointerPeek 0x{size:X} 0x{" 0x".join(jump.replace("+", "") for jump in jumps)}'
        self._send_command(command)
        sleep(size / 0x4000)
        return self._recv(size)

    def read_pointer_int(self, pointer: str, size: int) -> int:
        """Read integer from pointer"""
        return int.from_bytes(self.read_pointer(pointer, size), 'little')

    def write_pointer(self, pointer: str, data: str) -> None:
        """Write data to pointer"""
        jumps = pointer.replace('[', '').replace('main', '').split(']')
        command = f'pointerPoke 0x{data} 0x{" 0x".join(jump.replace("+", "") for jump in jumps)}'
        self._send_command(command)

    @staticmethod
    def pause(duration: float):
        """Pause connection to switch"""
        sleep(duration)
