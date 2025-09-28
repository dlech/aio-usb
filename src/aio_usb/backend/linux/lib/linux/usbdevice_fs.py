import ctypes

from .ioctl import _IO, _IOC, _IOC_READ, _IOR, _IOW, _IOWR

"""
Comes from include/uapi/linux/usbdevice_fs.h.
"""

# usbdevfs ioctl codes


class usbdevfs_ctrltransfer(ctypes.Structure):
    _fields_ = [
        ("bRequestType", ctypes.c_uint8),
        ("bRequest", ctypes.c_uint8),
        ("wValue", ctypes.c_uint16),
        ("wIndex", ctypes.c_uint16),
        ("wLength", ctypes.c_uint16),
        ("timeout", ctypes.c_uint32),  # in milliseconds
        ("data", ctypes.c_void_p),
    ]


class usbdevfs_bulktransfer(ctypes.Structure):
    _fields_ = [
        ("ep", ctypes.c_uint32),
        ("len", ctypes.c_uint32),
        ("timeout", ctypes.c_uint32),  # in milliseconds
        ("data", ctypes.c_void_p),
    ]


class usbdevfs_setinterface(ctypes.Structure):
    _fields_ = [
        ("interface", ctypes.c_uint32),
        ("altsetting", ctypes.c_uint32),
    ]


class usbdevfs_disconnectsignal(ctypes.Structure):
    _fields_ = [
        ("signr", ctypes.c_uint32),
        ("context", ctypes.c_void_p),
    ]


USBDEVFS_MAXDRIVERNAME = 255


class usbdevfs_getdriver(ctypes.Structure):
    _fields_ = [
        ("interface", ctypes.c_uint32),
        ("driver", ctypes.c_char * (USBDEVFS_MAXDRIVERNAME + 1)),
    ]


class usbdevfs_connectinfo(ctypes.Structure):
    _fields_ = [
        ("devnum", ctypes.c_uint32),
        ("slow", ctypes.c_uint8),
    ]


class usbdevfs_conninfo_ex(ctypes.Structure):
    size: int
    """
    Size of the structure from the kernel's point of view. Can be used by userspace
    to determine how much data can be used/trusted.
    """
    busnum: int
    """
    USB bus number, as enumerated by the kernel, the device is connected to.
    """
    devnum: int
    """
    Device address on the bus.
    """
    speed: int
    """
    USB_SPEED_* constants from ch9.h
    """
    num_ports: int
    """
    Number of ports the device is connected to on the way to the root hub. It may
    be bigger than size of 'ports' array so userspace can detect overflows.
    """
    ports: list[int]
    """
    List of ports on the way from the root hub to the device. Current limit in
    USB specification is 7 tiers (root hub, 5 intermediate hubs, device), which
    gives at most 6 port entries.
    """
    _fields_ = [
        ("size", ctypes.c_uint32),
        ("busnum", ctypes.c_uint32),
        ("devnum", ctypes.c_uint32),
        ("speed", ctypes.c_uint32),
        ("num_ports", ctypes.c_uint8),
        ("ports", ctypes.c_uint8 * 7),
    ]


USBDEVFS_URB_SHORT_NOT_OK = 0x01
USBDEVFS_URB_ISO_ASAP = 0x02
USBDEVFS_URB_BULK_CONTINUATION = 0x04
USBDEVFS_URB_NO_FSBR = 0x20  # Not used
USBDEVFS_URB_ZERO_PACKET = 0x40
USBDEVFS_URB_NO_INTERRUPT = 0x80

USBDEVFS_URB_TYPE_ISO = 0
USBDEVFS_URB_TYPE_INTERRUPT = 1
USBDEVFS_URB_TYPE_CONTROL = 2
USBDEVFS_URB_TYPE_BULK = 3


class usbdevfs_iso_packet_desc(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_uint32),
        ("actual_length", ctypes.c_uint32),
        ("status", ctypes.c_uint32),
    ]


def usbdevfs_urb(num_iso_frame_desc: int) -> type[ctypes.Structure]:
    class _usbdevfs_urb(ctypes.Structure):
        _fields_ = [
            ("type", ctypes.c_uint8),
            ("endpoint", ctypes.c_uint8),
            ("status", ctypes.c_int32),
            ("flags", ctypes.c_uint32),
            ("buffer", ctypes.c_void_p),
            ("buffer_length", ctypes.c_int32),
            ("actual_length", ctypes.c_int32),
            ("start_frame", ctypes.c_int32),
            # union
            ("number_of_packets", ctypes.c_int32)
            if num_iso_frame_desc > 0
            else ("stream_id", ctypes.c_uint32),
            # signal to be sent on completion, or 0 if none should be sent.
            ("error_count", ctypes.c_int32),
            ("signr", ctypes.c_uint32),
            ("usercontext", ctypes.c_void_p),
            ("iso_frame_desc", usbdevfs_iso_packet_desc * num_iso_frame_desc),
        ]

    return _usbdevfs_urb


# ioctls for talking directly to drivers


class usbdevfs_ioctl(ctypes.Structure):
    _fields_ = [
        # interface 0..N ; negative numbers reserved
        ("ifno", ctypes.c_int32),
        # MUST encode size + direction of data so the
        # macros in <asm/ioctl.h> give correct values
        ("ioctl_code", ctypes.c_int32),
        # param buffer (in, or out)
        ("data", ctypes.c_void_p),
    ]


# You can do most things with hubs just through control messages,
# except find out what device connects to what port.


class usbdevfs_hub_portinfo(ctypes.Structure):
    _fields_ = [
        ("nports", ctypes.c_uint8),  # number of downstream ports in this hub
        ("port", ctypes.c_uint8 * 127),  # e.g. port 3 connects to device 27
    ]


# System and bus capability flags

USBDEVFS_CAP_ZERO_PACKET = 0x01
USBDEVFS_CAP_BULK_CONTINUATION = 0x02
USBDEVFS_CAP_NO_PACKET_SIZE_LIM = 0x04
USBDEVFS_CAP_BULK_SCATTER_GATHER = 0x08
USBDEVFS_CAP_REAP_AFTER_DISCONNECT = 0x10
USBDEVFS_CAP_MMAP = 0x20
USBDEVFS_CAP_DROP_PRIVILEGES = 0x40
USBDEVFS_CAP_CONNINFO_EX = 0x80
USBDEVFS_CAP_SUSPEND = 0x100


# USBDEVFS_DISCONNECT_CLAIM flags & struct

# disconnect-and-claim if the driver matches the driver field
USBDEVFS_DISCONNECT_CLAIM_IF_DRIVER = 0x01
# disconnect-and-claim except when the driver matches the driver field
USBDEVFS_DISCONNECT_CLAIM_EXCEPT_DRIVER = 0x02


class usbdevfs_disconnect_claim(ctypes.Structure):
    _fields_ = [
        ("interface", ctypes.c_uint32),
        ("flags", ctypes.c_uint32),
        ("driver", ctypes.c_char * (USBDEVFS_MAXDRIVERNAME + 1)),
    ]


def usbdevfs_streams(num_eps: int) -> type[ctypes.Structure]:
    class _usbdevfs_streams(ctypes.Structure):
        _fields_ = [
            ("num_streams", ctypes.c_uint32),  # Not used by USBDEVFS_FREE_STREAMS
            ("num_eps", ctypes.c_uint32),
            ("eps", ctypes.c_uint8 * num_eps),
        ]

    return _usbdevfs_streams


#  USB_SPEED_* values returned by USBDEVFS_GET_SPEED are defined in linux/usb/ch9.h

USBDEVFS_CONTROL = _IOWR(ord("U"), 0, usbdevfs_ctrltransfer)
# USBDEVFS_CONTROL32 = _IOWR(ord("U"), 0, usbdevfs_ctrltransfer32)
USBDEVFS_BULK = _IOWR(ord("U"), 2, usbdevfs_bulktransfer)
# USBDEVFS_BULK32 = _IOWR(ord("U"), 2, usbdevfs_bulktransfer32)
USBDEVFS_RESETEP = _IOR(ord("U"), 3, ctypes.c_uint32)
USBDEVFS_SETINTERFACE = _IOR(ord("U"), 4, usbdevfs_setinterface)
USBDEVFS_SETCONFIGURATION = _IOR(ord("U"), 5, ctypes.c_uint32)
USBDEVFS_GETDRIVER = _IOR(ord("U"), 8, usbdevfs_getdriver)
USBDEVFS_SUBMITURB = _IOR(ord("U"), 10, usbdevfs_urb(0))
# USBDEVFS_SUBMITURB32 = _IOR(ord("U"), 10, usbdevfs_urb32(0))
USBDEVFS_DISCARDURB = _IO(ord("U"), 11)
USBDEVFS_REAPURB = _IOW(ord("U"), 12, ctypes.c_void_p)
USBDEVFS_REAPURB32 = _IOW(ord("U"), 12, ctypes.c_uint32)
USBDEVFS_REAPURBNDELAY = _IOW(ord("U"), 13, ctypes.c_void_p)
USBDEVFS_REAPURBNDELAY32 = _IOW(ord("U"), 13, ctypes.c_uint32)
USBDEVFS_DISCSIGNAL = _IOR(ord("U"), 14, usbdevfs_disconnectsignal)
# USBDEVFS_DISCSIGNAL32 = _IOR(ord("U"), 14, usbdevfs_disconnectsignal32)
USBDEVFS_CLAIMINTERFACE = _IOR(ord("U"), 15, ctypes.c_uint32)
USBDEVFS_RELEASEINTERFACE = _IOR(ord("U"), 16, ctypes.c_uint32)
USBDEVFS_CONNECTINFO = _IOW(ord("U"), 17, usbdevfs_connectinfo)
USBDEVFS_IOCTL = _IOWR(ord("U"), 18, usbdevfs_ioctl)
# USBDEVFS_IOCTL32 = _IOWR(ord("U"), 18, usbdevfs_ioctl32)
USBDEVFS_HUB_PORTINFO = _IOR(ord("U"), 19, usbdevfs_hub_portinfo)
USBDEVFS_RESET = _IO(ord("U"), 20)
USBDEVFS_CLEAR_HALT = _IOR(ord("U"), 21, ctypes.c_uint32)
USBDEVFS_DISCONNECT = _IO(ord("U"), 22)
USBDEVFS_CONNECT = _IO(ord("U"), 23)
USBDEVFS_CLAIM_PORT = _IOR(ord("U"), 24, ctypes.c_uint32)
USBDEVFS_RELEASE_PORT = _IOR(ord("U"), 25, ctypes.c_uint32)
USBDEVFS_GET_CAPABILITIES = _IOR(ord("U"), 26, ctypes.c_uint32)
USBDEVFS_DISCONNECT_CLAIM = _IOR(ord("U"), 27, usbdevfs_disconnect_claim)
USBDEVFS_ALLOC_STREAMS = _IOR(ord("U"), 28, usbdevfs_streams(0))
USBDEVFS_FREE_STREAMS = _IOR(ord("U"), 29, usbdevfs_streams(0))
USBDEVFS_DROP_PRIVILEGES = _IOW(ord("U"), 30, ctypes.c_uint32)
USBDEVFS_GET_SPEED = _IO(ord("U"), 31)


# Returns struct usbdevfs_conninfo_ex; length is variable to allow
# extending size of the data returned.
def USBDEVFS_CONNINFO_EX(len: int) -> int:
    return _IOC(_IOC_READ, ord("U"), 32, len)


USBDEVFS_FORBID_SUSPEND = _IO(ord("U"), 33)
USBDEVFS_ALLOW_SUSPEND = _IO(ord("U"), 34)
USBDEVFS_WAIT_FOR_RESUME = _IO(ord("U"), 35)
