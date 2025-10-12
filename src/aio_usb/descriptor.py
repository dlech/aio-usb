# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import struct

# Language ID for English (United States)

LANGID_EN_US = 0x0409


class StringLangIdDescriptor:
    def __init__(self, data: bytes) -> None:
        self.length = data[0]
        self.descriptor_type = data[1]
        self.langids: list[int] = list(
            struct.unpack_from(f"<{(self.length - 2) // 2}H", data, 2)
        )

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__qualname__} "
            f"length={self.length} "
            f"descriptor_type={self.descriptor_type:02x} "
            f"langids=[{', '.join([f'0x{langid:04x}' for langid in self.langids])}]>"
        )


class StringDescriptor:
    def __init__(self, data: bytes) -> None:
        self.length = data[0]
        self.descriptor_type = data[1]
        self.string = data[2 : self.length].decode("utf-16le")

    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__qualname__} "
            f"length={self.length} "
            f"descriptor_type={self.descriptor_type:02x} "
            f"string={self.string!r}>"
        )
