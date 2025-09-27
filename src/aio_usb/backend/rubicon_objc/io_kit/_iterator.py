# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from collections.abc import Iterator
from typing import Protocol, TypeAlias

from ._kernel import boolean_t
from ._object import IOObject, io_object_t
from ._runtime import IOKitLib


class IOIterator(IOObject):
    """
    https://developer.apple.com/documentation/iokit/io_iterator_t?language=objc
    """

    def __iter__(self) -> Iterator[IOObject]:
        return self

    def __next__(self) -> IOObject:
        if not IOIteratorIsValid(self):
            raise RuntimeError("Iterator is not valid")

        next = IOIteratorNext(self)
        if next:
            return next

        raise StopIteration

    def reset(self) -> None:
        """
        Resets the iterator back to the beginning.
        """
        IOIteratorReset(self)


# Type alias to match the C type name for use in function signatures to match
# the Apple documentation.
io_iterator_t: TypeAlias = IOIterator


class _IOIteratorIsValid(Protocol):
    def __call__(self, iterator: IOIterator) -> bool:
        """
        Checks an iterator is still valid.

        Args:
            iterator: An IOKit iterator handle.

        Returns:
            True if the iterator handle is valid, otherwise false is returned.

        Some iterators will be made invalid if changes are made to the structure
        they are iterating over. This function checks the iterator is still
        valid and should be called when IOIteratorNext returns zero. An invalid
        iterator can be reset and the iteration restarted.

        https://developer.apple.com/documentation/iokit/1514556-ioiteratorisvalid?language=objc
        """
        ...


IOIteratorIsValid: _IOIteratorIsValid = ctypes.CFUNCTYPE(boolean_t, io_iterator_t)(
    ("IOIteratorIsValid", IOKitLib), ((1, "iterator"),)
)


def _errcheck_IOIteratorIsValid(
    result: boolean_t, func: _IOIteratorIsValid, args: tuple[io_iterator_t]
) -> bool:
    return bool(result)


IOIteratorIsValid.errcheck = _errcheck_IOIteratorIsValid  # type: ignore


class _IOIteratorNext(Protocol):
    def __call__(self, iterator: IOIterator) -> IOObject | None:
        """
        Returns the next object in an iteration.

        Args:
            iterator: An IOKit iterator handle.

        Returns:
            If the iterator handle is valid, the next element in the iteration
            is returned, otherwise zero is returned. The element should be
            released by the caller when it is finished.

        This function returns the next object in an iteration, or zero if no
        more remain or the iterator is invalid.

        https://developer.apple.com/documentation/iokit/1514741-ioiteratornext?language=objc
        """
        ...


IOIteratorNext: _IOIteratorNext = ctypes.CFUNCTYPE(io_object_t, io_iterator_t)(
    ("IOIteratorNext", IOKitLib), ((1, "iterator"),)
)


def _errcheck_IOIteratorNext(
    result: io_object_t, func: _IOIteratorNext, args: tuple[io_iterator_t]
) -> io_object_t | None:
    if result.value == 0:
        return None

    return result


IOIteratorNext.errcheck = _errcheck_IOIteratorNext  # type: ignore


class _IOIteratorReset(Protocol):
    def __call__(self, iterator: IOIterator) -> None:
        """
        Resets an iteration back to the beginning.

        Args:
            iterator: An IOKit iterator handle.

        If an iterator is invalid, or if the caller wants to start over,
        IOIteratorReset will set the iteration back to the beginning.

        https://developer.apple.com/documentation/iokit/1514379-ioiteratorreset?language=objc
        """
        ...


IOIteratorReset: _IOIteratorReset = ctypes.CFUNCTYPE(None, io_iterator_t)(
    ("IOIteratorReset", IOKitLib), ((1, "iterator"),)
)
