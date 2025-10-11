import ctypes

from .ioctl import IO, IOC, IOC_READ, IOR, IOW, IOWR

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


class _usbdevfs_urb_u(ctypes.Union):
    _fields_ = [
        ("stream_id", ctypes.c_uint32),
        ("error_count", ctypes.c_int32),
    ]


class usbdevfs_urb(ctypes.Structure):
    type: int
    endpoint: int
    status: int
    flags: int
    buffer: int
    buffer_length: int
    actual_length: int
    start_frame: int
    number_of_packets: int
    stream_id: int
    error_count: int
    signr: int
    usercontext: int

    _anonymous_ = ("u",)
    _fields_ = [
        ("type", ctypes.c_uint8),
        ("endpoint", ctypes.c_uint8),
        ("status", ctypes.c_int32),
        ("flags", ctypes.c_uint32),
        ("buffer", ctypes.c_void_p),
        ("buffer_length", ctypes.c_int32),
        ("actual_length", ctypes.c_int32),
        ("start_frame", ctypes.c_int32),
        ("number_of_packets", ctypes.c_int32),
        # union
        ("u", _usbdevfs_urb_u),
        # signal to be sent on completion, or 0 if none should be sent.
        ("signr", ctypes.c_uint32),
        ("usercontext", ctypes.c_void_p),
        ("iso_frame_desc", usbdevfs_iso_packet_desc * 0),
    ]


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


class usbdevfs_streams(ctypes.Structure):
    _fields_ = [
        ("num_streams", ctypes.c_uint32),  # Not used by USBDEVFS_FREE_STREAMS
        ("num_eps", ctypes.c_uint32),
        ("eps", ctypes.c_uint8 * 0),
    ]


#  USB_SPEED_* values returned by USBDEVFS_GET_SPEED are defined in linux/usb/ch9.h

USBDEVFS_CONTROL = IOWR(ord("U"), 0, usbdevfs_ctrltransfer)
# USBDEVFS_CONTROL32 = _IOWR(ord("U"), 0, usbdevfs_ctrltransfer32)
USBDEVFS_BULK = IOWR(ord("U"), 2, usbdevfs_bulktransfer)
# USBDEVFS_BULK32 = _IOWR(ord("U"), 2, usbdevfs_bulktransfer32)
USBDEVFS_RESETEP = IOR(ord("U"), 3, ctypes.c_uint32)
USBDEVFS_SETINTERFACE = IOR(ord("U"), 4, usbdevfs_setinterface)
USBDEVFS_SETCONFIGURATION = IOR(ord("U"), 5, ctypes.c_uint32)
USBDEVFS_GETDRIVER = IOR(ord("U"), 8, usbdevfs_getdriver)
USBDEVFS_SUBMITURB = IOR(ord("U"), 10, usbdevfs_urb)
# USBDEVFS_SUBMITURB32 = _IOR(ord("U"), 10, usbdevfs_urb32)
USBDEVFS_DISCARDURB = IO(ord("U"), 11)
USBDEVFS_REAPURB = IOW(ord("U"), 12, ctypes.c_void_p)
USBDEVFS_REAPURB32 = IOW(ord("U"), 12, ctypes.c_uint32)
USBDEVFS_REAPURBNDELAY = IOW(ord("U"), 13, ctypes.c_void_p)
USBDEVFS_REAPURBNDELAY32 = IOW(ord("U"), 13, ctypes.c_uint32)
USBDEVFS_DISCSIGNAL = IOR(ord("U"), 14, usbdevfs_disconnectsignal)
# USBDEVFS_DISCSIGNAL32 = _IOR(ord("U"), 14, usbdevfs_disconnectsignal32)
USBDEVFS_CLAIMINTERFACE = IOR(ord("U"), 15, ctypes.c_uint32)
USBDEVFS_RELEASEINTERFACE = IOR(ord("U"), 16, ctypes.c_uint32)
USBDEVFS_CONNECTINFO = IOW(ord("U"), 17, usbdevfs_connectinfo)
USBDEVFS_IOCTL = IOWR(ord("U"), 18, usbdevfs_ioctl)
# USBDEVFS_IOCTL32 = _IOWR(ord("U"), 18, usbdevfs_ioctl32)
USBDEVFS_HUB_PORTINFO = IOR(ord("U"), 19, usbdevfs_hub_portinfo)
USBDEVFS_RESET = IO(ord("U"), 20)
USBDEVFS_CLEAR_HALT = IOR(ord("U"), 21, ctypes.c_uint32)
USBDEVFS_DISCONNECT = IO(ord("U"), 22)
USBDEVFS_CONNECT = IO(ord("U"), 23)
USBDEVFS_CLAIM_PORT = IOR(ord("U"), 24, ctypes.c_uint32)
USBDEVFS_RELEASE_PORT = IOR(ord("U"), 25, ctypes.c_uint32)
USBDEVFS_GET_CAPABILITIES = IOR(ord("U"), 26, ctypes.c_uint32)
USBDEVFS_DISCONNECT_CLAIM = IOR(ord("U"), 27, usbdevfs_disconnect_claim)
USBDEVFS_ALLOC_STREAMS = IOR(ord("U"), 28, usbdevfs_streams)
USBDEVFS_FREE_STREAMS = IOR(ord("U"), 29, usbdevfs_streams)
USBDEVFS_DROP_PRIVILEGES = IOW(ord("U"), 30, ctypes.c_uint32)
USBDEVFS_GET_SPEED = IO(ord("U"), 31)


# Returns struct usbdevfs_conninfo_ex; length is variable to allow
# extending size of the data returned.
def USBDEVFS_CONNINFO_EX(len: int) -> int:
    return IOC(IOC_READ, ord("U"), 32, len)


USBDEVFS_FORBID_SUSPEND = IO(ord("U"), 33)
USBDEVFS_ALLOW_SUSPEND = IO(ord("U"), 34)
USBDEVFS_WAIT_FOR_RESUME = IO(ord("U"), 35)
