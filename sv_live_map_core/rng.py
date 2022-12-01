"""Pseudorandom number generators used in game"""

import numpy as np

class Xoroshiro128Plus:
    """Xoroshiro128+ Implementation"""
    _XORO_CONST: np.uint64 = np.uint64(0x82A2B175229D6A5B)
    _ULONG_SIZE: np.uint64 = np.uint64(64)
    _ROT_27: np.uint64 = np.uint64(27)
    _ROT_40: np.uint64 = np.uint64(40)
    _SHIFT_16: np.uint64 = np.uint64(16)
    _ONE: np.uint64 = np.uint64(1)
    _ZERO: np.uint64 = np.uint64(0)

    def __init__(self, seed0: np.uint64, seed1: np.uint64 = _XORO_CONST) -> None:
        # disable integer overflow warnings
        np.seterr(over='ignore')
        # ensure integer inputs are casted to numpy ints
        self.seed0: np.uint64 = np.uint64(seed0)
        self.seed1: np.uint64 = np.uint64(seed1)

    @staticmethod
    def _rotl(num: np.uint64, k: np.uint64) -> np.uint64:
        """Rotate num left by k"""
        return ((num << k) | (num >> (Xoroshiro128Plus._ULONG_SIZE - k)))

    def next(self) -> np.uint64:
        """Generate next pseudorandom number"""
        self.seed1 = self._rotl(self.seed1, self._ROT_27)
        self.seed0 = self.seed0 ^ self.seed1 ^ (self.seed1 << self._SHIFT_16)
        self.seed0 = self._rotl(self.seed0, self._ROT_40)
        self.seed1 ^= self.seed0
        # integer overflow
        return self.seed0 + self.seed1

    @staticmethod
    def get_mask(maximum: np.uint64) -> np.uint64:
        """Generate a bitmask for rand generation"""
        mask = maximum - Xoroshiro128Plus._ONE
        for i in range(6):
            mask |= mask >> (Xoroshiro128Plus._ONE << np.uint64(i))
        return mask

    def rand(self, maximum: np.uint64) -> int:
        """Generate a pseudorandom number in range [0, maximum)"""
        assert maximum != self._ZERO
        # ensure integer inputs are casted to numpy ints
        maximum = np.uint64(maximum)
        mask = self.get_mask(maximum)
        # ensure loop is at least run once
        result = maximum
        while result >= maximum:
            result = self.next() & mask
        return int(result)

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
