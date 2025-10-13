# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

from enum import IntEnum

from rubicon.objc.api import ObjCClass, objc_const
from rubicon.objc.runtime import load_library

IOUSBHost = load_library("IOUSBHost")


IOUSBHostObject = ObjCClass("IOUSBHostObject")
IOUSBHostDevice = ObjCClass("IOUSBHostDevice")

IOUSBHostErrorDomain = objc_const(IOUSBHost, "IOUSBHostErrorDomain")


class IOUSBHostAbortOption(IntEnum):
    Synchronous = 0
    Asynchronous = 1
