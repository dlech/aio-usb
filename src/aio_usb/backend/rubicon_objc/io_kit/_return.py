# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from typing import TypeAlias

from ._driver_kit import kern_return_t

IOReturn: TypeAlias = kern_return_t


def _err_system(x: int) -> int:
    return (x & 0x3F) << 26


def _err_sub(x: int) -> int:
    return (x & 0x3F) << 22


_sys_iokit = _err_system(0x38)
_sub_iokit_common = _err_sub(0)
_sub_iokit_usb = _err_sub(1)
_sub_iokit_firewire = _err_sub(2)
_sub_iokit_block_storage = _err_sub(4)
_sub_iokit_graphics = _err_sub(5)
_sub_iokit_networking = _err_sub(6)
_sub_iokit_bluetooth = _err_sub(8)
_sub_iokit_pmu = _err_sub(9)
_sub_iokit_acpi = _err_sub(10)
_sub_iokit_smbus = _err_sub(11)
_sub_iokit_ahci = _err_sub(12)
_sub_iokit_powermanagement = _err_sub(13)
_sub_iokit_hidsystem = _err_sub(14)
_sub_iokit_scsi = _err_sub(16)
_sub_iokit_usbaudio = _err_sub(17)
_sub_iokit_wirelesscharging = _err_sub(18)
_sub_iokit_thunderbolt = _err_sub(29)
_sub_iokit_graphics_acceleration = _err_sub(30)
_sub_iokit_keystore = _err_sub(31)
_sub_iokit_platform = _err_sub(0x2A)
_sub_iokit_audio_video = _err_sub(0x45)
_sub_iokit_cec = _err_sub(0x46)
_sub_iokit_baseband = _err_sub(0x80)
_sub_iokit_HDA = _err_sub(0xFE)
_sub_iokit_hsic = _err_sub(0x147)
_sub_iokit_sdio = _err_sub(0x174)
_sub_iokit_wlan = _err_sub(0x208)
_sub_iokit_appleembeddedsleepwakehandler = _err_sub(0x209)
_sub_iokit_appleppm = _err_sub(0x20A)

_sub_iokit_vendor_specific = _err_sub(-2)
_sub_iokit_reserved = _err_sub(-1)


def iokit_common_err(ret: int) -> int:
    # Errors are signed 32-bit values, so can be negative.
    return ctypes.c_int(_sys_iokit | _sub_iokit_common | ret).value


# define	iokit_family_err(sub,return)      (_sys_iokit|sub|return)
# define iokit_vendor_specific_err(return) (_sys_iokit|_sub_iokit_vendor_specific|return)

kIOReturnSuccess = 0  # OK
kIOReturnError = iokit_common_err(0x2BC)  # general error
kIOReturnNoMemory = iokit_common_err(0x2BD)  # can't allocate memory
kIOReturnNoResources = iokit_common_err(0x2BE)  # resource shortage
kIOReturnIPCError = iokit_common_err(0x2BF)  # error during IPC
kIOReturnNoDevice = iokit_common_err(0x2C0)  # no such device
kIOReturnNotPrivileged = iokit_common_err(0x2C1)  # privilege violation
kIOReturnBadArgument = iokit_common_err(0x2C2)  # invalid argument
kIOReturnLockedRead = iokit_common_err(0x2C3)  # device read locked
kIOReturnLockedWrite = iokit_common_err(0x2C4)  # device write locked
kIOReturnExclusiveAccess = iokit_common_err(
    0x2C5
)  # exclusive access and device already open
kIOReturnBadMessageID = iokit_common_err(
    0x2C6
)  # sent/received messages had different msg_id
kIOReturnUnsupported = iokit_common_err(0x2C7)  # unsupported function
kIOReturnVMError = iokit_common_err(0x2C8)  # misc. VM failure
kIOReturnInternalError = iokit_common_err(0x2C9)  # internal error
kIOReturnIOError = iokit_common_err(0x2CA)  # General I/O error
##define kIOReturn???Error      iokit_common_err(0x2cb) # ???
kIOReturnCannotLock = iokit_common_err(0x2CC)  # can't acquire lock
kIOReturnNotOpen = iokit_common_err(0x2CD)  # device not open
kIOReturnNotReadable = iokit_common_err(0x2CE)  # read not supported
kIOReturnNotWritable = iokit_common_err(0x2CF)  # write not supported
kIOReturnNotAligned = iokit_common_err(0x2D0)  # alignment error
kIOReturnBadMedia = iokit_common_err(0x2D1)  # Media Error
kIOReturnStillOpen = iokit_common_err(0x2D2)  # device(s) still open
kIOReturnRLDError = iokit_common_err(0x2D3)  # rld failure
kIOReturnDMAError = iokit_common_err(0x2D4)  # DMA failure
kIOReturnBusy = iokit_common_err(0x2D5)  # Device Busy
kIOReturnTimeout = iokit_common_err(0x2D6)  # I/O Timeout
kIOReturnOffline = iokit_common_err(0x2D7)  # device offline
kIOReturnNotReady = iokit_common_err(0x2D8)  # not ready
kIOReturnNotAttached = iokit_common_err(0x2D9)  # device not attached
kIOReturnNoChannels = iokit_common_err(0x2DA)  # no DMA channels left
kIOReturnNoSpace = iokit_common_err(0x2DB)  # no space for data
##define kIOReturn???Error      iokit_common_err(0x2dc) # ???
kIOReturnPortExists = iokit_common_err(0x2DD)  # port already exists
kIOReturnCannotWire = iokit_common_err(0x2DE)  # can't wire down physical memory
kIOReturnNoInterrupt = iokit_common_err(0x2DF)  # no interrupt attached
kIOReturnNoFrames = iokit_common_err(0x2E0)  # no DMA frames enqueued
kIOReturnMessageTooLarge = iokit_common_err(
    0x2E1
)  # oversized msg received on interrupt port
kIOReturnNotPermitted = iokit_common_err(0x2E2)  # not permitted
kIOReturnNoPower = iokit_common_err(0x2E3)  # no power to device
kIOReturnNoMedia = iokit_common_err(0x2E4)  # media not present
kIOReturnUnformattedMedia = iokit_common_err(0x2E5)  # media not formatted
kIOReturnUnsupportedMode = iokit_common_err(0x2E6)  # no such mode
kIOReturnUnderrun = iokit_common_err(0x2E7)  # data underrun
kIOReturnOverrun = iokit_common_err(0x2E8)  # data overrun
kIOReturnDeviceError = iokit_common_err(0x2E9)  # the device is not working properly!
kIOReturnNoCompletion = iokit_common_err(0x2EA)  # a completion routine is required
kIOReturnAborted = iokit_common_err(0x2EB)  # operation aborted
kIOReturnNoBandwidth = iokit_common_err(0x2EC)  # bus bandwidth would be exceeded
kIOReturnNotResponding = iokit_common_err(0x2ED)  # device not responding
kIOReturnIsoTooOld = iokit_common_err(
    0x2EE
)  # isochronous I/O request for distant past!
kIOReturnIsoTooNew = iokit_common_err(
    0x2EF
)  # isochronous I/O request for distant future
kIOReturnNotFound = iokit_common_err(0x2F0)  # data was not found
kIOReturnInvalid = iokit_common_err(0x1)  # should never be seen
