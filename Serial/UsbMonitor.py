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

# ==== USB Monitor events ====

# Handles wclUsbMonitor.OnRemoved event.
def Removed(sender, Device) :
    print("Device REMOVED")
    print("  Friendly name :", Device.FriendlyName)
    print("  Hardware ID   :", Device.HardwareId)
    print("  Instance      :", Device.Instance)
    print("  Manufacturer  : ", Device.Manufacturer)
    

# Handles wclUsbMonitor.OnInserted event.
def Inserted(sender, Device) :
    print("Device INSERTED:")
    print("  Friendly name :", Device.FriendlyName)
    print("  Hardware ID   :", Device.HardwareId)
    print("  Instance      :", Device.Instance)
    print("  Manufacturer: " + Device.Manufacturer)

# ==== Helper functions ====

# Enumerates USB devices
def EnumDevices() :
    print("Enumerate installed USB devices")
    Res, Devices = Monitor.EnumDevices()
    if (Res != wclErrors.WCL_E_SUCCESS) :
        print("  Enumerate USB devices failed: 0x%0.8X" % Res)
    else :
        if (Devices is None or len(Devices) == 0) :
            print(" No USB devices found")
        else :
            i = 1
            for Device in Devices :
                print("Device %d" % i)
                print("  Friendly name :", Device.FriendlyName)
                print("  Hardware ID   :", Device.HardwareId)
                print("  Instance      :", Device.Instance)
                print("  Manufacturer  :", Device.Manufacturer)
                i += 1


def StartMonitoring() :
    print("Try to start monitoring USB device.")
    Res = Monitor.Start()
    if (Res != wclErrors.WCL_E_SUCCESS) :
        print("  Start monitoring USB devices failed 0x%0.8X" % Res)
    else :
        print("  Monitoring started")


def StopMonitoring() :
    if (Monitor.Monitoring) :
        print("Try to stop monitoring")
        Res = Monitor.Stop()
        if (Res != wclErrors.WCL_E_SUCCESS) :
            print("  Stop monitoring USB devices failed 0x%0.8X" % Res)
        else :
            print("  Monitoring stopped")

# =======================================================        

# The main function
def main() :
    # Change synchronization method to be able to use it in console
    wclCommon.wclMessageBroadcaster.SetSyncMethod(wclCommon.wclMessageSynchronizationKind.skThread)

    print("This very simple demo shows how to enumerate and monitor USB devices:")
    
    global Monitor
    Monitor = wclSerial.wclUsbMonitor()
    Monitor.OnInserted += Inserted
    Monitor.OnRemoved += Removed

    EnumDevices()
    StartMonitoring()
    os.system("PAUSE")
    StopMonitoring()


if __name__ == '__main__' :
    main()
