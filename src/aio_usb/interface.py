# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

from contextlib import AbstractAsyncContextManager
from typing import final

from aio_usb.backend.interface import UsbBackendInterface
from aio_usb.pipe import UsbInPipe, UsbOutPipe


@final
class UsbInterface:
    """
    A USB interface that has been opened for communication.
    """

    def __init__(self, backend: UsbBackendInterface) -> None:
        self._backend = backend

    @property
    def interface_number(self) -> int:
        """
        The interface number (bInterfaceNumber).
        """
        return self._backend.interface_number

    @property
    def alternate_setting(self) -> int:
        """
        The alternate setting number (bAlternateSetting).
        """
        return self._backend.alternate_setting

    @property
    def interface_class(self) -> int:
        """
        The interface class (bInterfaceClass).
        """
        return self._backend.interface_class

    @property
    def interface_subclass(self) -> int:
        """
        The interface subclass (bInterfaceSubClass).
        """
        return self._backend.interface_subclass

    @property
    def interface_protocol(self) -> int:
        """
        The interface protocol (bInterfaceProtocol).
        """
        return self._backend.interface_protocol

    @property
    def description(self) -> str | None:
        """
        A human-readable description of the interface, if available.
        """
        return self._backend.description

    def open_in_pipe(self) -> AbstractAsyncContextManager[UsbInPipe]:
        """
        Open an IN pipe (bulk or interrupt endpoint) for communication.
        """
        return self._backend.open_in_pipe()

    def open_out_pipe(self) -> AbstractAsyncContextManager[UsbOutPipe]:
        """
        Open an OUT pipe (bulk or interrupt endpoint) for communication.
        """
        return self._backend.open_out_pipe()
