# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>


from abc import ABC, abstractmethod


class UsbBackendInPipe(ABC):
    @abstractmethod
    async def transfer(self, length: int) -> bytes:
        raise NotImplementedError


class UsbBackendOutPipe(ABC):
    @abstractmethod
    async def transfer(self, data: bytes) -> int:
        raise NotImplementedError
