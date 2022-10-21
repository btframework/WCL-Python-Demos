import os
from os import path
import threading
from threading import Event

import clr

# Load Bluetooth Framework assemblies
LibPath = path.dirname(__file__) + "\\..\\_Lib\\"
clr.AddReference(LibPath + "wclCommon.dll")
clr.AddReference(LibPath + "wclCommunication.dll")
clr.AddReference(LibPath + "wclBluetoothFramework.dll")

# Import assemblies namespaces
import wclCommon
from wclCommon import wclErrors
import wclBluetooth
from wclBluetooth import wclBluetoothDiscoverKind

# === Helper methods ===

# Prints error message
def PrintError(Message, Error) :
    print(Message + " : 0x%0.8X" % Error)

# === Bluetooth Manager event handlers ===

# +++ Common events +++

# This method handles wclBluetoothManager.AfterOpen event.
# The event called after Bluetooth Manager opened
def AfterOpen(sender, args) :
    # It is good idea to start working with local Radio objects here.
    # In this sample code I just show how to get working LE and Classic
    # Radios    
    print()
    print("Bluetooth Manager opened")

    print("Try to get working Bluetooth Classic radio")    
    # The working classic radio can be used for Classic Bluetooth communication
    Res, Radio = Manager.GetClassicRadio()
    if (Res != wclErrors.WCL_E_SUCCESS) :
        PrintError("  Get working classic radio failed", Res)
    else :
        print("  Found Bluetooth Classic Radio with driver", Radio.ApiName)
    
    print("Try to get working Bluetooth LE radio")
    # The working LE radio can be used for Bluetooth LE communication
    Res, Radio = Manager.GetLeRadio()
    if (Res != wclErrors.WCL_E_SUCCESS) :
        PrintError("  Get working LE radio failed", Res)
    else :
        print("  Found Bluetoth LE radio with driver", Radio.ApiName)


# The method handles wclBluetoothManager.BeforeClose event.
# The event called before Bluetooth Manager will be closed
def BeforeClose(sender, args) :
    # In real code you should do all finalizing and Bluetooth
    # communication resource releasing in this method
    print()
    print("Bluetooth Manager is about to close")


# The method handles wclBluetoothManager.OnClosed event.
# The event called after Bluetooth Manager is closed
def Closed(sender, args) :
    print()
    print("Bluetooth Manager closed")


# The method handles wclBluetoothManager.OnStatusChanged event.
# The event called when the local Radio status changed: the radio
# removed, turned off, plugged, etc
def StatusChanged(sender, Radio) :
    print()
    print(Radio.ApiName + " radio status changed. New status:")
    print("  Available : ", Radio.Available)
    print("  Plugged   : ", Radio.Plugged)

# +++ Discovering events +++

# The method handles wclBluetoothManager.OnDiscoveringStarted event.
# The event called when Bluetooth discoverign has been started with
# susccess
def DiscoveringStarted(sender, Radio) :
    print("  Discovering started")
    # Clear the global devices list
    Devices.clear()


# The method handles wclBluetoothManager.OnDeviceFound event.
# The event called when new Bluetooth device found.
def DeviceFound(sender, Radio, Address) :
    print("  Device found: %0.12X" % Address)
    # Add just found device into the found devices list
    Devices.append(Address)


# The method handles wclBluetoothManager.OnDiscoveringCompleted event.
# The event called when discovering has been completed with or without
# success.
def DiscoveringCompleted(sender, Radio, Error) :
    print("  Discovering completed with result : 0x%0.8X" % Error)
    # Set discovering completed event
    OperEvent.set()

# +++ Authentication events +++

# The method handles wclBluetoothManager.OnAuthenticationCompleted event.
# The event called when authentication (pairing) completed
def AuthenticationCompleted(sender, Radio, Address, Error) :
    print("  Pairing with device %0.12X completed with result %0.8X" % (Address, Error))
    # Set pairing completed event
    OperEvent.set()


# The method handles wclBluetoothManager.OnNumericComparison event.
# Teh event called when remote device requires Numeric Comparison pairing.
def NumericComparison(sender, Radio, Address, Number, Confirm) :
    print("  Device %0.12X requires numeric comparison: %d" % (Address, Number))
    return (input("  Type 'y' to confirm pairing: ") == "y")


# The method handles wclBluetoothManager.OnPasskeyNotification event.
# The event called when device requires entering the passkey.
def PasskeyNotification(sender, Radio, Address, Passkey) :
    print("  Device %0.12X requires passkey entering" % Address)
    print("  Type the passkey on device: %d" % (Passkey))


# The method handles wclBluetoothManager.OnPasskeyRequest event.
# The event called when remote device requires Passkey.
def PasskeyRequest(sender, Radio, Address, Passkey) :
    print("  Device %0.12X requires passkey" % Address)
    Pass = input("  Type the passkey: ")
    return int(Pass)


# The method handles wclBluetoothManager.OnPinRequest event.
# The event called when reqmote device needs PIN pairing.
def PinRequest(sender, Radio, Address, Pin) :
    print("  Device %0.12X requires PIN" % Address)
    return input("  Input PIN: ")


# The method handles wclBluetoothManager.OnConfirm event.
# The event called for Just-Works pairing
def Confirm(sender, Radio, Address, Conf) :
    print("  Just-works pairing for device %0.12X" % Address)
    return True

# === Radio menu functions ===

# Gets the local radio information
def GetRadioInfo(Radio) :
    print()
    print("Reading local radio information")
    
    print("  API             : %s" % Radio.ApiName)
    print("  Available       : " + str(Radio.Available))
    print("  Plugged         : " + str(Radio.Plugged))
    # Ignore any error and simple skip information that could not be read
    Res, Address = Radio.GetAddress()
    if (Res == wclErrors.WCL_E_SUCCESS) :
        print("  Address         : %0.12X" % Address)
    Res, Connectable = Radio.GetConnectable()
    if (Res == wclErrors.WCL_E_SUCCESS) :
        print("  Connectabled    : " + str(Connectable))
    Res, Discoverable = Radio.GetDiscoverable()
    if (Res == wclErrors.WCL_E_SUCCESS) :
        print("  Discoverable    : " + str(Discoverable))
    Res, Version, SubVersion = Radio.GetHciVersion()
    if (Res == wclErrors.WCL_E_SUCCESS) :
        print("  HCI version     : %d.%d" % (Version, SubVersion))
    Res, Version, SubVersion = Radio.GetLmpVersion()
    if (Res == wclErrors.WCL_E_SUCCESS) :
        print("  LMP version     : %d.%d" % (Version, SubVersion))
    Res, Manufacturer = Radio.GetManufacturer()
    if (Res == wclErrors.WCL_E_SUCCESS) :
        print("  Manufacturer    : %d" % Manufacturer)
    Res, Name = Radio.GetName()
    if (Res == wclErrors.WCL_E_SUCCESS) :
        print("  Name            : %s" % Name)
    Res, Cod = Radio.GetCod()
    if (Res == wclErrors.WCL_E_SUCCESS) :
        print("  Class of Device : %0.8X" % Cod)
    
    os.system("PAUSE")


# Turns the specified radio OFF
def TurnRadioOff(Radio) :
    print("Turning the radio OFF")
    Res = Radio.TurnOff()
    if (Res != wclErrors.WCL_E_SUCCESS) :
        PrintError("  Turn radio OFF failed", Res)
    else :
        print("  Radio rutned OFF")
    os.system("PAUSE")


# Turns the specified radio ON
def TurnRadioOn(Radio) :
    print("Turning the radio ON")
    Res = Radio.TurnOn()
    if (Res != wclErrors.WCL_E_SUCCESS) :
        PrintError("  Turn radio ON failed", Res)
    else :
        print("  Radio turned ON")
    os.system("PAUSE")


# Start classic discovering
def DiscoverClassic(Radio) :
    print()
    print("Start classic discovering")

    OperEvent.clear()
    Res = Radio.Discover(10, wclBluetoothDiscoverKind.dkClassic)
    if (Res != wclErrors.WCL_E_SUCCESS) :
        PrintError("  Start classic discovering failed", Res)
    else :
        # Wait for discovering completion
        OperEvent.wait()
        ShowDevicesMenu(Radio)
    os.system("PAUSE")


# Start LE discovering
def DiscoverLe(Radio) :
    print()
    print("Start LE discovering")

    OperEvent.clear()
    Res = Radio.Discover(10, wclBluetoothDiscoverKind.dkBle)
    if (Res != wclErrors.WCL_E_SUCCESS) :
        PrintError("  Start LE discovering failed", Res)
    else :
        # Wait for discovering completion
        OperEvent.wait()
        ShowDevicesMenu(Radio)
    os.system("PAUSE")


# Enumerate paired devices
def EnumPaired(Radio) :
    print()
    print("Enumerate paired devices")

    Devices.clear()
    Res, Enumerated = Radio.EnumPairedDevices()
    Res = 0
    if (Res != wclErrors.WCL_E_SUCCESS) :
        PrintError("  Enumerate failed", Res)
    else :
        # Copy enumerated devices to the global devices list
        if (Enumerated is not None and len(Enumerated) > 0) :
            for Address in Enumerated :
                Devices.append(Address)
        ShowDevicesMenu(Radio)
    os.system("PAUSE")


# Enumerate connected devices
def EnumConnected(Radio) :
    print()
    print("Enumerate connected devices")
    
    Res, Enumerated = Radio.EnumConnectedDevices()
    if (Res != wclErrors.WCL_E_SUCCESS) :
        PrintError("  Enumerate failed", Res)
    else :
        # Copy enumerated devices to the global devices list
        if (Enumerated is not None and len(Enumerated) > 0) :
            for Address in Enumerated :
                Devices.append(Address)
        ShowDevicesMenu(Radio)
    os.system("PAUSE")


# Shows remote device paired status
def ShowPairingState(Radio, Address) :
    print()
    print("Remote device %0.12X paired state" % Address)
    Res, Paired = Radio.GetRemotePaired(Address)
    if (Res != wclErrors.WCL_E_SUCCESS) :
        PrintError("  Get paired state failed", Res)
    else :
        print("  Paired status: ", Paired)
    os.system("PAUSE")


# Shows remote device connected status
def ShowConnectedState(Radio, Address) :
    print()
    print("Remote device %0.12X connected state" % Address)
    Res, Connected = Radio.GetRemoteConnectedStatus(Address)
    if (Res != wclErrors.WCL_E_SUCCESS) :
        PrintError("  Get connected state failed", Res)
    else :
        print("  Conenctedg status: ", Connected)
    os.system("PAUSE")


# Pairs with remote device
def Pair(Radio, Address) :
    OperEvent.clear()
    print()
    print("Start pairing")
    Res = Radio.RemotePair(Address)
    if (Res != wclErrors.WCL_E_SUCCESS) :
        print("  Start pairing failed: 0x%0.8X" % Res)
    else :
        print("  Pairing started. Wait for completion")
        OperEvent.wait()
    os.system("PAUSE")


# Unpairs remote device
def Unpair(Radio, Address) :
    print()
    print("Unpair remote device %0.12X" % Address)
    Res = Radio.RemoteUnpair(Address)
    if (Res != wclErrors.WCL_E_SUCCESS) :
        PrintError("  Unpair failed", Res)
    else :
        print("  Device unpaired")
    os.system("PAUSE")


# Disconencts remote device
def Disconnect(Radio, Address) :
    print()
    print("Disconnect remote device %0.12X" % Address)
    Res = Radio.RemoteDisconnect(Address)
    if (Res != wclErrors.WCL_E_SUCCESS) :
        PrintError("  Disconnect failed", Res)
    else :
        print("  Device disconnected")
    os.system("PAUSE")


# Enumerates classic device services
def EnumServices(Radio, Address) :
    print()
    print("Enumerating %0.12X device services" % Address)
    
    Res, Services = Radio.EnumRemoteServices(Address, System.Guid.Empty)
    if (Res != wclErrors.WCL_E_SUCCESS) :
        PrintError("  Enumerate services failed", Res)
    else :
        if (Services is None or len(Services) == 0) :
            print("  No services found")
        else :
            print("  Found %d services" % len(Services))
            for Service in Services :
                print("  Service ", Service.Uuid)
                print("    Channel ", Service.Channel)
                print("    Name ", Service.Name)
                print("    Comment ", Service.Comment)
    os.system("PAUSE")

# === Menu functions ===

# Shows the selected device menu
def ShowDeviceMenu(Radio, Address) :
    while (True) :
        print()
        print("Device %0.12X" % Address)
        print("  1 - show pairing state")
        print("  2 - show connected state")
        print("  3 - pair")
        print("  4 - unpair")
        print("  5 - disconnect")
        print("  6 - enumerate service (for classic devices only)")
        print("  e - exit")
        Opt = input("Select option or type 'e' to exit: ")
        if (Opt == "e" or Opt == "E") :
            break

        if (Opt == "1") :
            ShowPairingState(Radio, Address)
        elif (Opt == "2") :
            ShowConnectedState(Radio, Address)
        elif (Opt == "3") :
            Pair(Radio, Address)
        elif (Opt == "4") :
            Unpair(Radio, Address)
        elif (Opt == "5") :
            Disconnect(Radio, Address)
        elif (Opt == "6") :
            EnumServices(Radio, Address)


# Shows the found devices menu
def ShowDevicesMenu(Radio) :
    while (True) :
        print()
        print("Found: %d devices" % len(Devices))
        if (len(Devices) > 0) :
            i = 1
            for Address in Devices :
                # Try to get devices name
                Res, Name = Radio.GetRemoteName(Address)
                if (Res != wclErrors.WCL_E_SUCCESS) :
                    Name = ""
                # Print device information
                print("  %d - %0.12X (%s)" % (i, Address, Name))
                i += 1
        print("  e - exit")
        Opt = input("Select option or type 'e' to exit: ")
        if (Opt == "e" or Opt == "E") :
            break

        if (not Opt.isnumeric()) :
            print("Invalid choose. Please enter the options number or 'e' to exit")
            continue

        Ndx = int(Opt) - 1
        if (Ndx < 0 or Ndx > len(Devices) - 1) :
            print("Invalid device number")
            continue

        ShowDeviceMenu(Radio, Devices[Ndx])


# Shows the radio functions menu
def ShowRadioMenu(Ndx) :
    Radio = Manager[Ndx]
    while (True) :
        print()
        print(Radio.ApiName + " Radio Menu:")
        print("  1 - get Radio information")
        print("  2 - discover classic Bluetooth devices")
        print("  3 - discover Bluetooth LE devices")
        print("  4 - enumerate paired Bluetooth devices")
        print("  5 - enumerate connected Bluetooth devices")
        print("  6 - turn radio off")
        print("  7 - trun radio on")
        print("  e - exit")
        Opt = input("Select option or type 'e' to exit: ")
        if (Opt == "e" or Opt == "E") :
            break
        
        if (not Opt.isnumeric()) :
            print("Invalid choose. Please enter the options number or 'e' to exit")
        elif (Opt == "1") :
            GetRadioInfo(Radio)
        elif (Opt == "2") :
            DiscoverClassic(Radio)
        elif (Opt == "3") :
            DiscoverLe(Radio)
        elif (Opt == "4") :
            EnumPaired(Radio)
        elif (Opt == "5") :
            EnumConnected(Radio)
        elif (Opt == "6") :
            TurnRadioOff(Radio)
        elif (Opt == "7") :
            TurnRadioOn(Radio)
        else :
            print("Invalid choose. Please enter the options number or 'e' to exit")


# Shows the main menu that gives a way to select working radio
def ShowMainMenu() :
    while (True) :
        print()
        print("Main Menu:")
        if (Manager.Count == 0) :
            print("  No Bluetooth Radio available")
        else :
            i = 0
            while (i < Manager.Count) :
                Radio = Manager[i]
                print("  " + str(i + 1) + " - " + Radio.ApiName)
                i += 1

        print("  e - exit")
        Opt = input("Select radio or type 'e' to exit: ")
        if (Opt == "e" or Opt == "E") :
            break

        if (not Opt.isnumeric()) :
            print("Invalid choose. Please enter the radio number or 'e' to exit")
            continue
        
        Ndx = int(Opt) - 1
        if (Ndx < 0 or Ndx >= Manager.Count) :
            print("Invalid radio number.")
            continue
        
        ShowRadioMenu(Ndx)

# =======================================================

# The main function
def main() :
    # Change synchronization method to be able to use it in console
    wclCommon.wclMessageBroadcaster.SetSyncMethod(wclCommon.wclMessageSynchronizationKind.skThread)

    print("This very simple demo shows how to use Bluetooth Manager features:")
    print("  - enumerate available local Radio modules")
    print("  - get local Radio information")
    print("  - discover classic Bluetooth devices")
    print("  - discover Bluetooth LE devices")
    print("  - enumerate paired Bluetooth devices")
    print("  - pair with selected Bluetooth device")
    print("  - unpair paired Bluetooth device")
    print("  - enumerate connected Bluetooth devices")
    print("  - disconnect connected Bluetooth device")
    print("  - read classic Bluetooth device services")
    print("Refer to BluetoothManager demo from Bluetooth Framework package")
    print("to find more details about wclBluetoothManager usage and features")
    print()

    # Create and initialize discovering event objects
    global OperEvent
    OperEvent = Event()

    # Found devices array
    global Devices
    Devices = []

    # Create Bluetooth Manager object
    global Manager
    Manager = wclBluetooth.wclBluetoothManager()
    Manager.AfterOpen += AfterOpen
    Manager.BeforeClose += BeforeClose
    Manager.OnClosed += Closed
    Manager.OnStatusChanged += StatusChanged
    Manager.OnDiscoveringStarted += DiscoveringStarted
    Manager.OnDeviceFound += DeviceFound
    Manager.OnDiscoveringCompleted += DiscoveringCompleted
    Manager.OnAuthenticationCompleted += AuthenticationCompleted
    Manager.OnNumericComparison += NumericComparison
    Manager.OnPasskeyNotification += PasskeyNotification
    Manager.OnPasskeyRequest += PasskeyRequest
    Manager.OnPinRequest += PinRequest
    
    print("Try to open Bluetooth Manager")
    Res = Manager.Open()
    if (Res != wclErrors.WCL_E_SUCCESS) :
        PrintError("  Open Bluetooth Manager failed", Res)
    else :
        ShowMainMenu()

        print("Closing Bluetooth Manager")
        Res = Manager.Close()
        if (Res != wclErrors.WCL_E_SUCCESS) :
            PrintError("  Bluetooth Manager close failed", Res)
    
    os.system("PAUSE")


if __name__ == '__main__' :
    main()