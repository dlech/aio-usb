# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from typing import Protocol, TypeAlias, TypeVar

from ..runtime import mach_error_string
from ._driver_kit import kern_return_t, mach_port_t
from ._kernel import boolean_t, io_name_t
from ._runtime import IOKitLib

_TIOObject = TypeVar("_TIOObject", bound="IOObject")


class IOObject(mach_port_t):
    """
    https://developer.apple.com/documentation/iokit/io_object_t?language=objc
    """

    @property
    def class_name(self) -> str:
        """
        Gets the OSMetaClass name of the object.
        """
        assert self.value != 0, "IOObject is NULL"
        name = IOObjectGetClass(self)
        return name.decode("utf-8")

    @property
    def user_retain_count(self) -> int:
        """
        Gets the user retain count of the object.
        """
        assert self.value != 0, "IOObject is NULL"
        return IOObjectGetUserRetainCount(self)

    def conforms_to(self, class_name: str) -> bool:
        """
        Checks if this object conforms to the given class name.
        """
        assert self.value != 0, "IOObject is NULL"
        return bool(IOObjectConformsTo(self, class_name.encode("utf-8")).value)

    def as_(self, cls: type[_TIOObject]) -> _TIOObject:
        """
        Casts this object to a subclass of IOObject.
        """
        if not self.conforms_to(cls.__name__):
            raise TypeError(f"Object does not conform to {cls.__name__}")

        if not issubclass(cls, IOObject):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f"{cls.__name__} is not a subclass of IOObject")

        self.retain()
        return cls(self.value)

    def retain(self) -> None:
        assert self.value != 0, "IOObject is NULL"
        IOObjectRetain(self)

    def release(self):
        if self.value != 0:
            IOObjectRelease(self)
            self.value = 0

    def __del__(self):
        self.release()

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, IOObject):
            return NotImplemented

        assert self.value != 0, "IOObject is NULL"
        assert value.value != 0, "value IOObject is NULL"
        return bool(IOObjectIsEqualTo(self, value).value)


# Type alias to match the C type name for use in function signatures to match
# the Apple documentation.
io_object_t: TypeAlias = IOObject


class _IOObjectGetClass(Protocol):
    def __call__(self, object: IOObject) -> bytes:
        """
        Return the class name of an IOKit object.

        Args:
            object: The IOKit object.

        Returns:
            The class name of the object.

        Raises:
            OSError: A kern_return_t error code.

        This function uses the OSMetaClass system in the kernel to derive the
        name of the class the object is an instance of.
        """
        ...


IOObjectGetClass: _IOObjectGetClass = ctypes.CFUNCTYPE(
    kern_return_t, io_object_t, io_name_t
)(("IOObjectGetClass", IOKitLib), ((1, "object"), (2, "className")))


def _errcheck_IOObjectGetClass(
    result: kern_return_t,
    func: _IOObjectGetClass,
    args: tuple[io_object_t, ctypes.Array[ctypes.c_char]],
) -> bytes:
    if result.value != 0:
        raise OSError(result.value, mach_error_string(result.value))

    return args[1].raw.split(b"\0", 1)[0]


IOObjectGetClass.errcheck = _errcheck_IOObjectGetClass  # type: ignore


class _IOObjectRelease(Protocol):
    def __call__(self, object: IOObject) -> None:
        """
        Releases an object handle previously returned by IOKitLib.

        Args:
            object: The IOKit object to release.

        Raises:
            OSError: A kern_return_t error code.

        All objects returned by IOKitLib should be released with this function
        when access to them is no longer needed. Using the object after it has
        been released may or may not return an error, depending on how many
        references the task has to the same object in the kernel.

        https://developer.apple.com/documentation/iokit/1514627-ioobjectrelease?language=objc
        """
        ...


IOObjectRelease: _IOObjectRelease = ctypes.CFUNCTYPE(kern_return_t, io_object_t)(
    ("IOObjectRelease", IOKitLib), ((1, "object"),)
)


def _errcheck_IOObjectRelease(
    result: kern_return_t, func: _IOObjectRelease, args: tuple[io_object_t]
) -> None:
    if result.value != 0:
        raise OSError(result.value, mach_error_string(result.value))


IOObjectRelease.errcheck = _errcheck_IOObjectRelease  # type: ignore


class _IOObjectRetain(Protocol):
    def __call__(self, object: IOObject) -> None:
        """
        Retains an object handle previously returned by IOKitLib.

        Args:
            object: The IOKit object to retain.

        Raises:
            OSError: A kern_return_t error code.

        Gives the caller an additional reference to an existing object handle
        previously returned by IOKitLib.

        https://developer.apple.com/documentation/iokit/1514769-ioobjectretain?language=objc
        """
        ...


IOObjectRetain: _IOObjectRetain = ctypes.CFUNCTYPE(kern_return_t, io_object_t)(
    ("IOObjectRetain", IOKitLib), ((1, "object"),)
)


def _errcheck_IOObjectRetain(
    result: kern_return_t, func: _IOObjectRetain, args: tuple[io_object_t]
) -> None:
    if result.value != 0:
        raise OSError(result.value, mach_error_string(result.value))


IOObjectRetain.errcheck = _errcheck_IOObjectRetain  # type: ignore


class _IOObjectGetUserRetainCount(Protocol):
    def __call__(self, object: IOObject) -> int: ...


IOObjectGetUserRetainCount: _IOObjectGetUserRetainCount = ctypes.CFUNCTYPE(
    ctypes.c_uint32, io_object_t
)(("IOObjectGetUserRetainCount", IOKitLib), ((1, "object"),))


class _IOObjectIsEqualTo(Protocol):
    def __call__(self, object: IOObject, anObject: IOObject) -> boolean_t:
        """
        Checks two object handles to see if they represent the same kernel object.

        Args:
            object: An IOKit object.
            anObject: Another IOKit object.

        Returns:
            If both object handles are valid, and represent the same object in
            the kernel true is returned, otherwise false.

        If two object handles are returned by IOKitLib functions, this function
        will compare them to see if they represent the same kernel object.

        https://developer.apple.com/documentation/iokit/1514563-ioobjectisequalto?language=objc
        """
        ...


IOObjectIsEqualTo: _IOObjectIsEqualTo = ctypes.CFUNCTYPE(
    boolean_t, io_object_t, io_object_t
)(("IOObjectIsEqualTo", IOKitLib), ((1, "object"), (1, "anObject")))


class _IOObjectConformsTo(Protocol):
    def __call__(self, object: IOObject, className: bytes) -> boolean_t:
        """
        Performs an OSDynamicCast operation on an IOKit object.

        Args:
            object: An IOKit object.
            className: The name of the class, as a C-string.

        Returns:
            If the object handle is valid, and represents an object in the
            kernel that dynamic casts to the class true is returned, otherwise
            false.

        This function uses the OSMetaClass system in the kernel to determine if
        the object will dynamic cast to a class, specified as a C-string. In
        other words, if the object is of that class or a subclass.

        https://developer.apple.com/documentation/iokit/1514505-ioobjectconformsto?language=objc
        """
        ...


IOObjectConformsTo: _IOObjectConformsTo = ctypes.CFUNCTYPE(
    boolean_t, io_object_t, ctypes.c_char_p
)(("IOObjectConformsTo", IOKitLib), ((1, "object"), (1, "className")))
