"""Xorshift32 Implementation for saveblock decryption"""

import numpy as np

class SCXorshift32:
    """Xorshift32 Implementation for saveblock decryption"""
    _SHIFT2: np.uint32 = np.uint32(2)
    _SHIFT15: np.uint32 = np.uint32(15)
    _SHIFT13: np.uint32 = np.uint32(13)
    _SHIFT8: np.uint32 = np.uint32(8)
    _SHIFT16: np.uint32 = np.uint32(16)
    _SHIFT24: np.uint32 = np.uint32(24)

    def __init__(self, key: np.uint32) -> None:
        # ensure integer inputs are casted to numpy ints
        self.seed: np.uint32 = np.uint32(key)
        for _ in range(self.pop_count(self.seed)):
            self.advance()
        self.counter: np.uint32 = 0

    def advance(self) -> None:
        """Advance RNG"""
        self.seed ^= self.seed << self._SHIFT2
        self.seed ^= self.seed >> self._SHIFT15
        self.seed ^= self.seed << self._SHIFT13

    def next(self) -> np.uint32:
        """Generate next pseudorandom byte"""
        result: np.uint32 = (self.seed >> (self.counter << 3)) & 0xFF
        if self.counter == 3:
            self.advance()
            self.counter = 0
        else:
            self.counter += 1
        return result

    def next_32(self) -> np.uint32:
        """Generate next pseudorandom uint"""
        return (
            self.next()
            | (self.next() << self._SHIFT8)
            | (self.next() << self._SHIFT16)
            | (self.next() << self._SHIFT24)
        )

    @staticmethod
    def pop_count(val: np.uint32) -> np.uint32:
        """Count of bits set in value"""
        val -= ((val >> 1) & 0x55555555)
        val = (val & 0x33333333) + ((val >> 2) & 0x33333333)
        val = (val + (val >> 4)) & 0x0F0F0F0F
        val += (val >> SCXorshift32._SHIFT8)
        val += (val >> SCXorshift32._SHIFT16)
        return val & 0x3F
