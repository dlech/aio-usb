# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager
from typing import TypedDict

from aio_usb.pipe import UsbInPipe, UsbOutPipe


class UsbInterfaceMatch(TypedDict, total=False):
    """
    A dictionary for matching USB interfaces.
    """

    number: int
    class_: int
    subclass: int
    protocol: int


class UsbBackendInterface(ABC):
    """
    A USB interface that has been opened for communication.
    """

    @property
    @abstractmethod
    def interface_number(self) -> int:
        """
        The interface number (bInterfaceNumber).
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def alternate_setting(self) -> int:
        """
        The alternate setting number (bAlternateSetting).
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def interface_class(self) -> int:
        """
        The interface class (bInterfaceClass).
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def interface_subclass(self) -> int:
        """
        The interface subclass (bInterfaceSubClass).
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def interface_protocol(self) -> int:
        """
        The interface protocol (bInterfaceProtocol).
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self) -> str | None:
        """
        A human-readable description of the interface, if available.
        """
        raise NotImplementedError

    @abstractmethod
    def open_in_pipe(self) -> AbstractAsyncContextManager[UsbInPipe]:
        """
        Open an IN pipe (bulk or interrupt endpoint) for communication.

        Returns:
            An asynchronous context manager that yields a UsbInPipe object.
        """
        raise NotImplementedError

    @abstractmethod
    def open_out_pipe(self) -> AbstractAsyncContextManager[UsbOutPipe]:
        """
        Open an OUT pipe (bulk or interrupt endpoint) for communication.

        Returns:
            An asynchronous context manager that yields a UsbOutPipe object.
        """
        raise NotImplementedError
