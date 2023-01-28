"""Xoroshiro128+ Implementation"""

import numpy as np


class Xoroshiro128Plus:
    """Xoroshiro128+ Implementation"""
    _XORO_CONST: np.uint64 = np.uint64(0x82A2B175229D6A5B)
    _ULONG_SIZE: np.uint64 = np.uint64(64)
    _ROT_24: np.uint64 = np.uint64(24)
    _ROT_37: np.uint64 = np.uint64(37)
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
        rand = self.seed0 + self.seed1
        self.seed1 ^= self.seed0
        self.seed0 = \
            self._rotl(self.seed0, self._ROT_24) ^ self.seed1 ^ (self.seed1 << self._SHIFT_16)
        self.seed1 = self._rotl(self.seed1, self._ROT_37)
        # integer overflow
        return rand

    @staticmethod
    def get_mask(maximum: np.uint64) -> np.uint64:
        """Generate a bitmask for rand generation"""
        mask = maximum - Xoroshiro128Plus._ONE
        for i in range(6):
            mask |= mask >> (Xoroshiro128Plus._ONE << np.uint64(i))
        return mask

    def rand(self, maximum: np.uint64 = 0xFFFFFFFF) -> int:
        """Generate a pseudorandom number in range [0, maximum)"""
        assert maximum != self._ZERO
        # ensure integer inputs are casted to numpy ints
        maximum = np.uint64(maximum)
        mask = self.get_mask(maximum)
        # ensure loop is at least run once
        # sourcery skip: use-assigned-variable
        result = maximum
        while result >= maximum:
            result = self.next() & mask
        return int(result)
