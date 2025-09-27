# SPDX-License-Identifier: MIT
# Copyright (c) 2025 David Lechner <david@pybricks.com>

import ctypes
from typing import ClassVar, Self, TypeAlias

from rubicon.objc import NSArray, NSDictionary, NSObject, NSUInteger, objc_id
from rubicon.objc.api import NSData

class NSString(NSObject):
    string: ClassVar[str]
    def init(self) -> Self: ...
    def initWithBytes(
        self,
        bytes: bytes,
        /,
        *,
        length: NSUInteger,
        encoding: NSStringEncoding,
    ) -> Self: ...

NSStringEncoding: TypeAlias = NSUInteger

NSErrorDomain: TypeAlias = NSString
"""
https://developer.apple.com/documentation/foundation/nserrordomain?language=objc
"""

class NSError(NSObject):
    @classmethod
    def errorWithDomain(
        cls,
        domain: NSErrorDomain,
        /,
        *,
        code: int,
        userInfo: NSDictionary[NSString, objc_id] | None,
    ) -> Self: ...
    @property
    def code(self) -> int: ...
    @property
    def domain(self) -> NSErrorDomain: ...
    @property
    def userInfo(self) -> NSDictionary[NSString, objc_id]: ...
    @property
    def localizedDescription(self) -> NSString: ...
    @property
    def localizedRecoveryOptions(self) -> NSArray[NSString] | None: ...
    @property
    def localizedRecoverySuggestion(self) -> NSString | None: ...
    @property
    def localizedFailureReason(self) -> NSString | None: ...
    @property
    def recoveryAttempter(self) -> objc_id | None: ...
    @property
    def helpAnchor(self) -> NSString | None: ...

class NSMutableData(NSData):
    @classmethod
    def dataWithCapacity(cls, aNumItems: int, /) -> Self: ...
    @classmethod
    def dataWithLength(cls, length: int, /) -> Self: ...
    def initWithCapacity(self, capacity: int, /) -> Self: ...
    def initWithLength(self, length: int, /) -> Self: ...
    @property
    def mutableBytes(self) -> ctypes.c_void_p: ...
    @property
    def length(self) -> int: ...
    @length.setter
    def length(self, value: int) -> None: ...
