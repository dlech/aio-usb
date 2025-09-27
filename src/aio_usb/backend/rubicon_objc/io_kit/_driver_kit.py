# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes


class kern_return_t(ctypes.c_int):
    """
    https://developer.apple.com/documentation/driverkit/kern_return_t?language=objc
    """


class natural_t(ctypes.c_uint):
    """
    https://developer.apple.com/documentation/driverkit/natural_t?language=objc
    """


class mach_port_t(natural_t):
    """
    https://developer.apple.com/documentation/driverkit/mach_port_t?language=objc
    """


class IOOptionBits(ctypes.c_uint32):
    """
    https://developer.apple.com/documentation/driverkit/iooptionbits?language=objc
    """
