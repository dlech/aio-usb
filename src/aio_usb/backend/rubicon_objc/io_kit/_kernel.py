# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes


class boolean_t(ctypes.c_int):
    """
    https://developer.apple.com/documentation/kernel/boolean_t?language=objc
    """


io_name_t = ctypes.c_char * 128
"""
https://developer.apple.com/documentation/kernel/io_name_t?language=objc
"""
