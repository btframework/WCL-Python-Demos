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

# =======================================================        

# The main function
def main() :
    # Change synchronization method to be able to use it in console
    wclCommon.wclMessageBroadcaster.SetSyncMethod(wclCommon.wclMessageSynchronizationKind.skThread)

    print("WiFi Client Demo")
    print("This demo enumerates WiFi interfaces, networks and BBS")
    
    Client = wclWiFi.wclWiFiClient()
    Res = Client.Open()
    if (Res != wclErrors.WCL_E_SUCCESS) :
        print("Failed to open WiFi client: 0x%0.8X" % Res)
    else :
        Res, Ifaces = Client.EnumInterfaces()
        if (Res != wclErrors.WCL_E_SUCCESS) :
            print("Failed to enumerate WiFi interfaces: 0x%0.8X" % Res)
        elif (Ifaces is None) :
            print("No WiFi Interfaces found")
        else :
            for IfaceData in Ifaces :
                Id = IfaceData.Id
                
                print("Interface ", Id, " found")
                print("  Description :", IfaceData.Description)
                
                print("Try to enumerate available networks")
                Res, Networks = Client.EnumAvailableNetworks(Id, wclWiFi.wclWiFiAvailableNetworkFilter(0))
                if (Res != wclErrors.WCL_E_SUCCESS) :
                    print("      Failed to enumerate available networks: 0x%0.8X" % Res)
                else :
                    for Network in Networks :
                        # Ignore networks that has profile.
                        if (Network.ProfileName == "" and Network.Ssid != "") :
                            print("      SSID: ", Network.Ssid)
                            Res, BssList = Client.EnumBss(Id, Network.Ssid, wclWiFi.wclWiFiBssType.bssInfrastructure, True)
                            if (Res != wclErrors.WCL_E_SUCCESS) :
                                print("        Failed to enumerate BSS: 0x%0.8X" % Res)
                            elif (BssList is not None and len(BssList) > 0) :
                                for Bss in BssList :
                                    print("        BSS :", Bss.Ssid)
                                    print("          Frequency :", Bss.ChCenterFrequency, "; MAC: ", Bss.Mac , "; RSSI: " , Bss.Rssi)
        
        Client.Close();
    os.system("PAUSE")


if __name__ == '__main__' :
    main()
