import os
from os import path

import clr

# Load Bluetooth Framework assemblies
LibPath = path.dirname(__file__) + "\\..\\_Lib\\"
clr.AddReference(LibPath + "wclCommon.dll")
clr.AddReference(LibPath + "wclCommunication.dll")
clr.AddReference(LibPath + "wclSerialFramework.dll")

# Import assemblies namespaces
import wclCommon
from wclCommon import wclErrors
import wclSerial

# ==== Serial Monitor event handler ====

# The method hanles wclSerialMonitor.OnInserver event.
def Inserted(sender, Device) :
    print("Device INSERTED:")
    print("  Friendly name :", Device.FriendlyName)
    print("  Is modem      :", Device.IsModem)
    print("  Name          :", Device.DeviceName)


# The method handles wclSerialMonitor.OnRemoved event.
def Removed(Sender, Device) :
    print("Device REMOVED:")
    print("  Friendly name :", Device.FriendlyName)
    print("  Is modem      :", Device.IsModem)
    print("  Name          :", Device.DeviceName)

# ==== Helper functions ====

# Enumerating olugged serial devices
def EnumDevices() :
    print()
    print("Enumerate installed devices.")
    Res, Devices = Monitor.EnumDevices()
    if (Res != wclErrors.WCL_E_SUCCESS) :
        print("  Enumerate serial devices failed: 0x%0.8X" % Res)
    else :
        if (Devices is None or len(Devices) == 0) :
            print("  No serial devices found")
        else :
            i = 1
            for Device in Devices :
                print("  Device %d" % i)
                print("    Friendly name : ", Device.FriendlyName)
                print("    Is modem      : ", Device.IsModem)
                print("    Name          : ", Device.DeviceName)
                i += 1


def StartMonitoring() :
    print()
    print("Start monitoring serial devices")
    Res = Monitor.Start()
    if (Res != wclErrors.WCL_E_SUCCESS) :
        print("  Start monitoring failed 0x%0.4X" % Res)
    else :
        print("  Monitoring started")


# Stop monitoring serial devices
def StopMonitoring() :
    print()
    print("Stop monitoring serial devices")
    if (not Monitor.Monitoring) :
        print("  Monitoring is not active")
    else :
        Res = Monitor.Stop()
        if (Res != wclErrors.WCL_E_SUCCESS) :
            print("  Stop monitoring failed 0x%0.4X" % Res)
        else :
            print("  Monitoring stopped")

# =======================================================

# The main function
def main() :
    # Change synchronization method to be able to use it in console
    wclCommon.wclMessageBroadcaster.SetSyncMethod(wclCommon.wclMessageSynchronizationKind.skThread)

    print("This very simple demo shows how to enumerate and monitor serial devices:")
    
    global Monitor
    Monitor = wclSerial.wclSerialMonitor()
    Monitor.OnInserted += Inserted
    Monitor.OnRemoved += Removed

    EnumDevices()
    StartMonitoring()
    os.system("PAUSE")
    StopMonitoring()


if __name__ == '__main__' :
    main()