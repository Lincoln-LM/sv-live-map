"""Simplified class to read information from sys-botbase
   https://github.com/Lincoln-LM/PyNXReader"""

import struct
import socket
import binascii
from time import sleep
import usb.core
import usb.util

class USBError(Exception):
    """Error to be raised for usb connections"""

class NXReader:
    """Simplified class to read information from sys-botbase"""
    def __init__(
        self,
        ip_address: str = None,
        port: int = 6000,
        usb_connection: bool = False
    ) -> None:
        assert usb_connection or ip_address is not None
        self.usb_connection = usb_connection
        if self.usb_connection:
            # nintendo switch vendor and product
            self.global_dev = usb.core.find(idVendor = 0x057E, idProduct = 0x3000)
            if self.global_dev is None:
                raise USBError("Unable to find switch usb connection")
            self.global_dev.set_configuration()
            descriptor = self.global_dev.get_active_configuration()[(0,0)]
            self.global_out = usb.util.find_descriptor(
                descriptor,
                custom_match =
                  lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
            )
            self.global_in = usb.util.find_descriptor(
                descriptor,
                custom_match =
                  lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
            )
        else:
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
        if self.usb_connection:
            self.global_out.write(struct.pack("<I", len(content) + 2))
            self.global_out.write(content)
        else:
            content += '\r\n' # important for the parser on the switch side
            self.socket.sendall(content.encode())

    def _configure(self) -> None:
        self._send_command('configure echoCommands 0')

    def _recv(self, size: int) -> bytes:
        """Receive response from sys-botbase"""
        if not self.usb_connection:
            return binascii.unhexlify(self.socket.recv(2 * size + 1)[:-1])
        size = int(struct.unpack("<L", self.global_in.read(4, timeout = 0).tobytes())[0])
        data = [0 for _ in range(size)]
        if size > 4080:
            i = 0
            while i < size:
                chunk_size = 4080
                if size - i < 4080:
                    chunk_size = size - i
                read_data = self.global_in.read(chunk_size, timeout = 0).tobytes()
                for byte in read_data:
                    data[i] = int(byte)
                    i += 1
        else:
            read_data = self.global_in.read(size, timeout = 0).tobytes()
            for i, byte in enumerate(read_data):
                data[i] = byte
        return bytes(data)

    def close(self) -> None:
        """Close connection to switch"""
        print("Exiting...")
        self.pause(0.5)
        if self.usb_connection:
            self.global_dev.reset()
        else:
            self.socket.shutdown(socket.SHUT_RDWR)
            self.socket.close()
        print('Disconnected')

    def click(self, button: str) -> None:
        """Press and release button"""
        self._send_command(f'click {button}')

    def press(self, button: str) -> None:
        """Press and hold button"""
        self._send_command(f'press {button}')

    def release(self, button: str) -> None:
        """Release held button"""
        self._send_command(f'release {button}')

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
        sleep(size / 0x8000)
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
    def pause(duration):
        """Pause connection to switch"""
        sleep(duration)
