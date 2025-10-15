# properties found in the registry root
kIOKitBuildVersionKey = b"IOKitBuildVersion"
kIOKitDiagnosticsKey = b"IOKitDiagnostics"
# a dictionary keyed by plane name
kIORegistryPlanesKey = b"IORegistryPlanes"
kIOCatalogueKey = b"IOCatalogue"

# registry plane names
kIOServicePlane = b"IOService"
kIOPowerPlane = b"IOPower"
kIODeviceTreePlane = b"IODeviceTree"
kIOAudioPlane = b"IOAudio"
kIOFireWirePlane = b"IOFireWire"
kIOUSBPlane = b"IOUSB"

# registry ID number
kIORegistryEntryIDKey = b"IORegistryEntryID"
# property name to get array of property names
kIORegistryEntryPropertyKeysKey = b"IORegistryEntryPropertyKeys"
# property name to allow only the given keys present in an OSDictionary from a user space call to IORegistryEntry::setProperties (OSArray)
kIORegistryEntryAllowableSetPropertiesKey = b"IORegistryEntryAllowableSetProperties"
# property name to single thread a user space call to IORegistryEntry::setProperties (OSBoolean)
kIORegistryEntryDefaultLockingSetPropertiesKey = (
    b"IORegistryEntryDefaultLockingSetProperties"
)

# IOService class name
kIOServiceClass = b"IOService"

# IOResources class name
kIOResourcesClass = b"IOResources"

# IOService driver probing property names
kIOClassKey = b"IOClass"
kIOProbeScoreKey = b"IOProbeScore"
kIOKitDebugKey = b"IOKitDebug"

# DriverKit class keys
kIOUserClassKey = b"IOUserClass"
kIOUserClassesKey = b"IOUserClasses"

# Properties to be supported as API
kIOSupportedPropertiesKey = b"IOSupportedProperties"
# Properties writable by dexts
kIOUserServicePropertiesKey = b"IOUserServiceProperties"

# IOService matching property names
kIOProviderClassKey = b"IOProviderClass"
kIONameMatchKey = b"IONameMatch"
kIOPropertyMatchKey = b"IOPropertyMatch"
kIOPropertyExistsMatchKey = b"IOPropertyExistsMatch"
kIOPathMatchKey = b"IOPathMatch"
kIOLocationMatchKey = b"IOLocationMatch"
kIOParentMatchKey = b"IOParentMatch"
kIOResourceMatchKey = b"IOResourceMatch"
kIOResourceMatchedKey = b"IOResourceMatched"
kIOMatchedServiceCountKey = b"IOMatchedServiceCountMatch"

kIONameMatchedKey = b"IONameMatched"

kIOMatchCategoryKey = b"IOMatchCategory"
kIODefaultMatchCategoryKey = b"IODefaultMatchCategory"

kIOMatchedPersonalityKey = b"IOMatchedPersonality"
kIORematchPersonalityKey = b"IORematchPersonality"
kIORematchCountKey = b"IORematchCount"
kIODEXTMatchCountKey = b"IODEXTMatchCount"

# Property specifying the entitlement to check against an IOUserClient's opening process
# kOSBooleanFalse - Allow access (no entitlements required)
# string - If the opening process has the named entitlement with value == boolean true, allow access
kIOUserClientEntitlementsKey = b"IOUserClientEntitlements"

# Entitlements to check against dext process
# Property is an array, one or more of which may match, of:
#   an array of entitlement strings, all must be present
# Any array can be a single string.
kIOServiceDEXTEntitlementsKey = b"IOServiceDEXTEntitlements"

# Entitlement required to open dext connection
kIODriverKitEntitlementKey = b"com.apple.developer.driverkit"

# Entitlements required to open dext IOUserClient
# Property is an array of strings containing CFBundleIdentifiers of service being opened
kIODriverKitUserClientEntitlementsKey = (
    b"com.apple.developer.driverkit.userclient-access"
)

# Allows the entitled process to open a user client connection to any dext that has specific entitlements
# Property is an array of strings containing entitlements, one of which needs to be present
# in the dext providing the user client being opened
kIODriverKitRequiredEntitlementsKey = b"com.apple.private.driverkit.driver-access"

# Specifies that this driver is used for internal tests. This opts the driver out of our policy to
# reboot the device if a driver crashes too often.
kIODriverKitTestDriverEntitlementKey = b"com.apple.private.driverkit.test-driver"

# Entitlement of a dext that allows any task to open one of its IOUserClients
kIODriverKitUserClientEntitlementAllowAnyKey = (
    b"com.apple.developer.driverkit.allow-any-userclient-access"
)

kIODriverKitUserClientEntitlementAdministratorKey = (
    b"com.apple.developer.driverkit.administrator"
)

# Entitlements for third party drivers on iOS
kIODriverKitUserClientEntitlementCommunicatesWithDriversKey = (
    b"com.apple.developer.driverkit.communicates-with-drivers"
)
kIODriverKitUserClientEntitlementAllowThirdPartyUserClientsKey = (
    b"com.apple.developer.driverkit.allow-third-party-userclients"
)

# Other DriverKit entitlements
kIODriverKitUSBTransportEntitlementKey = b"com.apple.developer.driverkit.transport.usb"
kIODriverKitHIDTransportEntitlementKey = b"com.apple.developer.driverkit.transport.hid"
kIODriverKitHIDFamilyDeviceEntitlementKey = (
    b"com.apple.developer.driverkit.family.hid.device"
)
kIODriverKitHIDFamilyEventServiceEntitlementKey = (
    b"com.apple.developer.driverkit.family.hid.eventservice"
)
kIODriverKitTransportBuiltinEntitlementKey = b"com.apple.developer.driverkit.builtin"

# Entitlement required to read nvram root-only properties as non-root user
kIONVRAMReadAccessKey = b"com.apple.private.iokit.nvram-read-access"
# Entitlement required to write nvram properties as non-root user
kIONVRAMWriteAccessKey = b"com.apple.private.iokit.nvram-write-access"
# Entitlement required to set properties on the IOResources object as non-root user
kIOResourcesSetPropertyKey = b"com.apple.private.iokit.ioresources.setproperty"
# Entitlement required to read/write to the system nvram region
kIONVRAMSystemAllowKey = b"com.apple.private.iokit.system-nvram-allow"

# When possible, defer matching of this driver until kextd has started.
kIOMatchDeferKey = b"IOMatchDefer"

# Published after processor_start() has been called on all CPUs at boot time.
kIOAllCPUInitializedKey = b"IOAllCPUInitialized"

# IOService default user client class, for loadable user clients
kIOUserClientClassKey = b"IOUserClientClass"

# key to find IOMappers
kIOMapperIDKey = b"IOMapperID"

kIOUserClientCrossEndianKey = b"IOUserClientCrossEndian"
kIOUserClientCrossEndianCompatibleKey = b"IOUserClientCrossEndianCompatible"
kIOUserClientSharedInstanceKey = b"IOUserClientSharedInstance"

kIOUserClientDefaultLockingKey = b"IOUserClientDefaultLocking"
kIOUserClientDefaultLockingSetPropertiesKey = b"IOUserClientDefaultLockingSetProperties"
kIOUserClientDefaultLockingSingleThreadExternalMethodKey = (
    b"IOUserClientDefaultLockingSingleThreadExternalMethod"
)

# diagnostic string describing the creating task
kIOUserClientCreatorKey = b"IOUserClientCreator"
# the expected cdhash value of the userspace driver executable
kIOUserServerCDHashKey = b"IOUserServerCDHash"

kIOUserUserClientKey = b"IOUserUserClient"

kIOUserServerOneProcessKey = b"IOUserServerOneProcess"
kIOUserServerPreserveUserspaceRebootKey = b"IOUserServerPreserveUserspaceReboot"

# IOService notification types
kIOPublishNotification = b"IOServicePublish"
kIOFirstPublishNotification = b"IOServiceFirstPublish"
kIOMatchedNotification = b"IOServiceMatched"
kIOFirstMatchNotification = b"IOServiceFirstMatch"
kIOTerminatedNotification = b"IOServiceTerminate"
kIOWillTerminateNotification = b"IOServiceWillTerminate"

# IOService interest notification types
kIOGeneralInterest = b"IOGeneralInterest"
kIOBusyInterest = b"IOBusyInterest"
kIOAppPowerStateInterest = b"IOAppPowerStateInterest"
kIOPriorityPowerStateInterest = b"IOPriorityPowerStateInterest"

kIOPlatformDeviceMessageKey = b"IOPlatformDeviceMessage"

# IOService interest notification types
kIOCFPlugInTypesKey = b"IOCFPlugInTypes"

kIOCompatibilityMatchKey = b"IOCompatibilityMatch"
kIOCompatibilityPropertiesKey = b"IOCompatibilityProperties"
kIOPathKey = b"IOPath"

# properties found in services that implement command pooling
kIOCommandPoolSizeKey = b"IOCommandPoolSize"  # (OSNumber)

# properties found in services that implement priority
kIOMaximumPriorityCountKey = b"IOMaximumPriorityCount"  # (OSNumber)

# properties found in services that have transfer constraints
kIOMaximumBlockCountReadKey = b"IOMaximumBlockCountRead"  # (OSNumber)
kIOMaximumBlockCountWriteKey = b"IOMaximumBlockCountWrite"  # (OSNumber)
kIOMaximumByteCountReadKey = b"IOMaximumByteCountRead"  # (OSNumber)
kIOMaximumByteCountWriteKey = b"IOMaximumByteCountWrite"  # (OSNumber)
kIOMaximumSegmentCountReadKey = b"IOMaximumSegmentCountRead"  # (OSNumber)
kIOMaximumSegmentCountWriteKey = b"IOMaximumSegmentCountWrite"  # (OSNumber)
kIOMaximumSegmentByteCountReadKey = b"IOMaximumSegmentByteCountRead"  # (OSNumber)
kIOMaximumSegmentByteCountWriteKey = b"IOMaximumSegmentByteCountWrite"  # (OSNumber)
kIOMinimumSegmentAlignmentByteCountKey = (
    b"IOMinimumSegmentAlignmentByteCount"  # (OSNumber)
)
kIOMaximumSegmentAddressableBitCountKey = (
    b"IOMaximumSegmentAddressableBitCount"  # (OSNumber)
)
kIOMinimumSaturationByteCountKey = b"IOMinimumSaturationByteCount"  # (OSNumber)
kIOMaximumSwapWriteKey = b"IOMaximumSwapWrite"  # (OSNumber)

# properties found in services that wish to describe an icon
#
# IOIcon = {
#     CFBundleIdentifier   = "com.example.driver.example";
#     IOBundleResourceFile = "example.icns";
# };
#
# where IOBundleResourceFile is the filename of the resource

kIOIconKey = b"IOIcon"  # (OSDictionary)
kIOBundleResourceFileKey = b"IOBundleResourceFile"  # (OSString)

kIOBusBadgeKey = b"IOBusBadge"  # (OSDictionary)
kIODeviceIconKey = b"IODeviceIcon"  # (OSDictionary)

# property of root that describes the machine's serial number as a string
kIOPlatformSerialNumberKey = b"IOPlatformSerialNumber"  # (OSString)

# property of root that describes the machine's UUID as a string
kIOPlatformUUIDKey = b"IOPlatformUUID"  # (OSString)

# IODTNVRAM property keys
kIONVRAMBootArgsKey = b"boot-args"
kIONVRAMDeletePropertyKey = b"IONVRAM-DELETE-PROPERTY"
kIONVRAMSyncNowPropertyKey = b"IONVRAM-SYNCNOW-PROPERTY"
kIONVRAMActivateCSRConfigPropertyKey = b"IONVRAM-ARMCSR-PROPERTY"
kIODTNVRAMPanicInfoKey = b"aapl,panic-info"
kIONVRAMDeletePropertyKeyWRet = b"IONVRAM-DELETEWRET-PROPERTY"

# keys for complex boot information
kIOBootDeviceKey = b"IOBootDevice"  # dict | array of dicts
kIOBootDevicePathKey = b"IOBootDevicePath"  # arch-neutral OSString
kIOBootDeviceSizeKey = b"IOBootDeviceSize"  # OSNumber of bytes

# keys for OS Version information
kOSBuildVersionKey = b"OS Build Version"

kIOStateNotificationItemCreateKey = b"com.apple.iokit.statenotification.create"
kIOStateNotificationItemSetKey = b"com.apple.iokit.statenotification.set"
kIOStateNotificationItemCopyKey = b"com.apple.iokit.statenotification.copy"

kIOStateNotificationNameKey = b"com.apple.iokit.statenotification.name"
kIOStateNotificationEntitlementSetKey = (
    b"com.apple.iokit.statenotification.entitlement-set"
)
kIOStateNotificationEntitlementGetKey = (
    b"com.apple.iokit.statenotification.entitlement-get"
)

kIOSystemStateClamshellKey = b"com.apple.iokit.pm.clamshell"

kIOSystemStateSleepDescriptionKey = b"com.apple.iokit.pm.sleepdescription"
kIOSystemStateSleepDescriptionReasonKey = b"com.apple.iokit.pm.sleepreason"
kIOSystemStateSleepDescriptionHibernateStateKey = b"com.apple.iokit.pm.hibernatestate"

# Must match IOHibernatePrivate.h!
kIOSystemStateSleepDescriptionHibernateStateInactive = 0
kIOSystemStateSleepDescriptionHibernateStateHibernating = 1  # writing image
kIOSystemStateSleepDescriptionHibernateStateWakingFromHibernate = (
    2  # booted and restored image
)

kIOSystemStateWakeDescriptionKey = b"com.apple.iokit.pm.wakedescription"
kIOSystemStateWakeDescriptionWakeReasonKey = b"com.apple.iokit.pm.wakereason"
kIOSystemStateWakeDescriptionContinuousTimeOffsetKey = (
    b"com.apple.iokit.pm.wakedescription.continuous-time-offset"
)

kIOSystemStateHaltDescriptionKey = b"com.apple.iokit.pm.haltdescription"
kIOSystemStateHaltDescriptionHaltStateKey = b"com.apple.iokit.pm.haltstate"

kIOSystemStatePowerSourceDescriptionKey = b"com.apple.iokit.pm.powersourcedescription"
kIOSystemStatePowerSourceDescriptionACAttachedKey = b"com.apple.iokit.pm.acattached"
