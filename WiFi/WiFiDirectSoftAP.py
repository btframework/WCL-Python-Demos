import os
from os import path

import clr

# Load WiFi Framework assemblies
LibPath = path.dirname(__file__) + "\\..\\_Lib\\"
clr.AddReference(LibPath + "wclCommon.dll")
clr.AddReference(LibPath + "wclWiFiFramework.dll")

# Import assemblies namespaces
import wclCommon
from wclCommon import wclErrors
import wclWiFi

# ==== Soft AP event handlers ====

def SoftApStopped(sender, e) :
    print("WiFi Direct Soft AP has been stopped")
    

def SoftApDeviceConnected(sender, Device) :
    print("Device has been connected")
    print("  Name               :", Device.Name)
    print("  Local IP addresss  :", Device.LocalAddress)
    print("  Remote IP addresss :", Device.RemoteAddress)


def SoftApDeviceDisconnected(sender, Device) :
    print("Device ", Device.Name, " has been disconnected")


def SoftApStarted(sender, e) :
    print("WiFi Direct Soft AP has been started")
    
    Ap: wclWiFi.wclWiFiSoftAP = sender
    Res, ts = Ap.GetSsid()
    if (Res != wclErrors.WCL_E_SUCCESS) :
        print("  SSID : read error 0x%0.8X" % Res)
    else:
        print("  SSID :", ts)
    
    Res, ts = Ap.GetPassphrase()
    if (Res != wclErrors.WCL_E_SUCCESS) :
        print("  Passphrase : read error 0x%0.8X" % Res)
    else :
        print("  Passphrase :", ts)

# =======================================================        

# The main function
def main() :
    # Change synchronization method to be able to use it in console
    wclCommon.wclMessageBroadcaster.SetSyncMethod(wclCommon.wclMessageSynchronizationKind.skThread)

    Ap = wclWiFi.wclWiFiSoftAP()
    Ap.OnStarted += SoftApStarted
    Ap.OnStopped += SoftApStopped
    Ap.OnDeviceConnected += SoftApDeviceConnected
    Ap.OnDeviceDisconnected += SoftApDeviceDisconnected

    print("WIFI DIRECT SOFT AP DEMO")

    Res = Ap.Start("WiFi_Framework", "12345678")
    if (Res != wclErrors.WCL_E_SUCCESS) :
        print("Failed to start WiFi Direct Soft AP: 0x%0.8X" % Res)
    else :
        os.system("PAUSE")
        
        Res = Ap.Stop()
        if (Res != wclErrors.WCL_E_SUCCESS) :
            print("Failed to stop WiFi Direct Soft AP: 0x%0.8X" % Res)

    os.system("PAUSE")


if __name__ == '__main__' :
    main()