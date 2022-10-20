import os
from os import path, system
from re import ASCII
import threading
from threading import Event

import clr
import System
from System import Text

# Load Bluetooth Framework assemblies
LibPath = path.dirname(__file__) + "\\..\\_Lib\\"
clr.AddReference(LibPath + "wclCommon.dll")
clr.AddReference(LibPath + "wclCommunication.dll")
clr.AddReference(LibPath + "wclBluetoothFramework.dll")


# Import assemblies namespaces
import wclCommon
from wclCommon import wclErrors
import wclCommunication
import wclBluetooth
from wclBluetooth import wclBluetoothDiscoverKind

# === Discovering events ===

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
    if (len(Devices) == 0) :
        print("  No classic Bluetooth devices found")
        OperEvent.set()
    else :
        while (True) :
            print()
            print("Found devices")
            # Show found devices.
            i = 1
            for Address in Devices :
                Res, Name = Radio.GetRemoteName(Address)
                # Set Name as empty string in case of name reading error
                if (Res != wclErrors.WCL_E_SUCCESS) :
                    Name = ""
                print("  %d - %0.12X [%s]" % (i, Address, Name))
                i += 1

            print("  e - Exit")
            Opt = input("Enter device number or 'e' to exit: ")
            if (Opt == "e" or Opt == "E") :
                OperEvent.set()
                return

            if (not Opt.isnumeric()) :
                print("Invalid input")
                continue

            Ndx = int(Opt) - 1
            if (Ndx < 0 or Ndx > len(Devices) - 1) :
                print("Invalid device number")
                continue

            ConnectToDevice(Radio, Devices[Ndx])
            break

# === RFCOMM client events ===

# The method handles wclRfCommClient.OnDisconnect event.
# The event called when remote device disconnects
def Disconnect(sender, Reason) :
    print("Client disconnected. Reason: 0x%0.8X" % Reason)
    OperEvent.set()


# The method handles wclRfCommClient.OnConnect event.
# The event called when remote device connects
def Connect(sender, Error) :
    print("Connection completed with result: 0x%0.8X" % Error)
    if (Error != wclErrors.WCL_E_SUCCESS) :
        OperEvent.set()


# The method handles wclRfCommClient.OnData event.
# The event called when data from connected device recevied.
def Data(sender, Data) :
    Str = Text.Encoding.ASCII.GetString(Data)
    print(Str)


# =======================================================

# Connects to specific device
def ConnectToDevice(Radio, Address) :
    print()
    print("Start connecting to the device %0.12X" % Address)

    # Set connection parameters
    Client.Address = Address
    Client.Authentication = True
    Client.Encryption = False
    Client.Channel = 0
    Client.Service = wclBluetooth.wclUUIDs.SerialPortServiceClass_UUID

    # Start connecting to device.
    Res = Client.Connect(Radio)
    if (Res != wclErrors.WCL_E_SUCCESS) :
        print("  Connect failed: 0x%0.8X" % Res)
    OperEvent.set()


# The main function
def main() :
    # Change synchronization method to be able to use it in console
    wclCommon.wclMessageBroadcaster.SetSyncMethod(wclCommon.wclMessageSynchronizationKind.skThread)

    print("This simple demo shows how to connect to Classic Bluetooth device")
    print("using RFCOMM protocol.")
    print("By default the demo connects to Serial Port Profile (SPP) service.")
    print("To make it simple the demo only receives data. For testing Gps2Blue Android")
    print("application used on the cell as server.")
    print("NOTE: The demo does not pair with device. If device requires pairing do it before")
    print("running the demo.")
    print()

    # Create and initialize operation completion event
    global OperEvent
    OperEvent = Event()

    # Found devices array
    global Devices
    Devices = []

    # Create Bluetooth Manager object
    global Manager
    Manager = wclBluetooth.wclBluetoothManager()
    Manager.OnDiscoveringStarted += DiscoveringStarted
    Manager.OnDeviceFound += DeviceFound
    Manager.OnDiscoveringCompleted += DiscoveringCompleted

    global Client
    Client = wclBluetooth.wclRfCommClient()
    Client.OnDisconnect += Disconnect
    Client.OnConnect += Connect
    Client.OnData += Data

    print("Try to open Bluetooth Manager")
    Res = Manager.Open()
    if (Res != wclErrors.WCL_E_SUCCESS) :
        print("  Open Bluetooth Manager failed: 0x%0.8X" % Res)
    else :
        print("Try to get first available Bluetooth Radio that supports Bluetooth Classic communication")
        Res, Radio = Manager.GetClassicRadio()
        if (Res != wclErrors.WCL_E_SUCCESS) :
            print("  Get working radio failed: 0x%0.8X" % Res)
        else :
            print("  Radio found: " + Radio.ApiName)
            
            print("Try to start discovering")
            Res = Radio.Discover(10, wclBluetoothDiscoverKind.dkClassic)
            if (Res != wclErrors.WCL_E_SUCCESS) :
                print("  Start discovering failed: 0x%0.8X" % Res)
            else :
                print("  Waiting for connection completion...")
                OperEvent.wait()
                os.system("PAUSE")
                
        # It also disconnects all connected clients
        print("Closing Bluetooth Manager")
        Res = Manager.Close()
        if (Res != wclErrors.WCL_E_SUCCESS) :
            print("  Bluetooth Manager close failed: 0x%0.8X" % Res)

    os.system("PAUSE")


if __name__ == '__main__' :
    main()