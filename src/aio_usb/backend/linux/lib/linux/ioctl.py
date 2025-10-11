# IOCTL definitions for asm-generic

# ioctl command encoding: 32 bits total, command in lower 16 bits,
# size of the parameter structure in the lower 14 bits of the
# upper 16 bits.
#
# Encoding the size of the parameter structure in the ioctl request
# is useful for catching programs compiled with old versions
# and to avoid overwriting user space outside the user buffer area.
# The highest 2 bits are reserved for indicating the ``access mode''.
# NOTE: This limits the max parameter size to 16kB -1 !

# The following is for compatibility across the various Linux
# platforms.  The generic ioctl numbering scheme doesn't really enforce
# a type field.  De facto, however, the top 8 bits of the lower 16
# bits are indeed used as a type field, so we might just as well make
# this explicit here.  Please be sure to use the decoding macros
# below from now on.

import ctypes

_IOC_NRBITS = 8
_IOC_TYPEBITS = 8

# Let any architecture override either of the following before
# including this file.

# #ifndef _IOC_SIZEBITS
_IOC_SIZEBITS = 14
# #endif

# #ifndef _IOC_DIRBITS
_IOC_DIRBITS = 2
# #endif

_IOC_NRMASK = (1 << _IOC_NRBITS) - 1
_IOC_TYPEMASK = (1 << _IOC_TYPEBITS) - 1
_IOC_SIZEMASK = (1 << _IOC_SIZEBITS) - 1
_IOC_DIRMASK = (1 << _IOC_DIRBITS) - 1

_IOC_NRSHIFT = 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_DIRSHIFT = _IOC_SIZESHIFT + _IOC_SIZEBITS

# Direction bits, which any architecture can choose to override
# before including this file.
#
# NOTE: _IOC_WRITE means userland is writing and kernel is
# reading. _IOC_READ means userland is reading and kernel is writing.

# #ifndef _IOC_NONE
_IOC_NONE = 0
# #endif

# #ifndef _IOC_WRITE
_IOC_WRITE = 1
# #endif

# #ifndef _IOC_READ
IOC_READ = 2
# #endif


def IOC(dir: int, type: int, nr: int, size: int) -> int:
    return (
        (dir << _IOC_DIRSHIFT)
        | (type << _IOC_TYPESHIFT)
        | (nr << _IOC_NRSHIFT)
        | (size << _IOC_SIZESHIFT)
    )


def _IOC_TYPECHECK(t: type) -> int:
    return ctypes.sizeof(t)


# Used to create numbers.
#
# NOTE: _IOW means userland is writing and kernel is reading. _IOR
# means userland is reading and kernel is writing.


def IO(type: int, nr: int) -> int:
    return IOC(_IOC_NONE, type, nr, 0)


def IOR(type: int, nr: int, size: type) -> int:
    return IOC(IOC_READ, type, nr, _IOC_TYPECHECK(size))


def IOW(type: int, nr: int, size: type) -> int:
    return IOC(_IOC_WRITE, type, nr, _IOC_TYPECHECK(size))


def IOWR(type: int, nr: int, size: type) -> int:
    return IOC(IOC_READ | _IOC_WRITE, type, nr, _IOC_TYPECHECK(size))


def IOR_BAD(type: int, nr: int, size: type) -> int:
    return IOC(IOC_READ, type, nr, ctypes.sizeof(size))


def IOW_BAD(type: int, nr: int, size: type) -> int:
    return IOC(_IOC_WRITE, type, nr, ctypes.sizeof(size))


def IOWR_BAD(type: int, nr: int, size: type) -> int:
    return IOC(IOC_READ | _IOC_WRITE, type, nr, ctypes.sizeof(size))


# used to decode ioctl numbers..


def IOC_DIR(nr: int) -> int:
    return (nr >> _IOC_DIRSHIFT) & _IOC_DIRMASK


def IOC_TYPE(nr: int) -> int:
    return (nr >> _IOC_TYPESHIFT) & _IOC_TYPEMASK


def IOC_NR(nr: int) -> int:
    return (nr >> _IOC_NRSHIFT) & _IOC_NRMASK


def IOC_SIZE(nr: int) -> int:
    return (nr >> _IOC_SIZESHIFT) & _IOC_SIZEMASK


# ...and for the drivers/sound files...

IOC_IN = _IOC_WRITE << _IOC_DIRSHIFT
IOC_OUT = IOC_READ << _IOC_DIRSHIFT
IOC_INOUT = (_IOC_WRITE | IOC_READ) << _IOC_DIRSHIFT
IOCSIZE_MASK = _IOC_SIZEMASK << _IOC_SIZESHIFT
IOCSIZE_SHIFT = _IOC_SIZESHIFT
