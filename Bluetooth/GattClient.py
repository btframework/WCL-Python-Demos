import os
from os import path, system

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

# The method handles wclGattClient.OnDisconnect event.
# The event called when remote device disconnects
def Disconnect(sender, Reason) :
    print("Client disconnected. Reason: 0x%0.8X" % Reason)
    OperEvent.set()


# The method handles wclGattClient.OnConnect event.
# The event called when remote device connects
def Connect(sender, Error) :
    print("Connection completed with result: 0x%0.8X" % Error)
    if (Error == wclErrors.WCL_E_SUCCESS) :
        ReadServices()
    OperEvent.set()


# The method handles wclGattClient.OnCharacteristicChanged event.
def CharacteristicChanged(sender, Handle, Value) :
    Str = ""
    if (len(Value) > 0) :
        for b in Value :
            Str = Str + hex(b)
        print("Value received: " + Str)

# =======================================================

# Read characteristics from connected device for the given service
def ReadCharacteristics(Service) :
    print("    Read characteristics")
    Res, Characteristics = Client.ReadCharacteristics(Service, wclBluetooth.wclGattOperationFlag.goNone)
    if (Res != wclErrors.WCL_E_SUCCESS) :
        print("      Read services failed: 0x%0.8X" % Res)
    else :
        if (len(Characteristics) == 0) :
            print("      No characteristics found")
        else :
            i = 1
            for Characteristic in Characteristics :
                print("      Characteristic %d" % i)
                print("        Handle %0.4X" % Characteristic.Handle)
                print("        IsShortUUID", Characteristic.Uuid.IsShortUuid)
                if (Service.Uuid.IsShortUuid) :
                    print("        UUID %0.4X" % Characteristic.Uuid.ShortUuid)
                else :
                    print("        UUID", Characteristic.Uuid.LongUuid)
                if (Characteristic.IsReadable) :
                    print("        Try to read characteristic value")
                    Res, Value = Client.ReadCharacteristicValue(Characteristic, wclBluetooth.wclGattOperationFlag.goNone)
                    if (Res != wclErrors.WCL_E_SUCCESS) :
                        print("          Read value failed: %0.8X" % Res)
                    else :
                        print("          Dump value:")
                        Str = ""
                        if (len(Value) > 0) :
                            for b in Value :
                                Str = Str + hex(b)
                        print("            " + Str)
                if (Characteristic.IsIndicatable or Characteristic.IsNotifiable) :
                    print("        Try to subscribe")

                    Chr = Characteristic
                    if (Characteristic.IsIndicatable and Characteristic.IsNotifiable) :
                        Chr.IsIndicatable = False

                    Res = Client.Subscribe(Chr)
                    if (Res != wclErrors.WCL_E_SUCCESS) :
                        print("          Subscribe failed: 0x%0.8X" % Res)
                    else :
                        print("          Subscribed")
                        Res = Client.WriteClientConfiguration(Chr, True, wclBluetooth.wclGattOperationFlag.goNone)
                        if (Res != wclErrors.WCL_E_SUCCESS) :
                            print("          Write configuration failed: 0x%0.8X" % Res)
                            Client.Unsubscribe(Chr)
                i += 1


# Read services from connected device
def ReadServices() :
    print()
    print("Read services")
    Res, Services = Client.ReadServices(wclBluetooth.wclGattOperationFlag.goNone)
    if (Res != wclErrors.WCL_E_SUCCESS) :
        print("  Read services failed: 0x%0.8X" % Res)
    else :
        if (len(Services) == 0) :
            print("  No services found")
        else :
            i = 1
            for Service in Services :
                print("  Services %d" % i)
                print("    Handle %0.4X" % Service.Handle)
                print("    IsShortUUID", Service.Uuid.IsShortUuid)
                if (Service.Uuid.IsShortUuid) :
                    print("    UUID %0.4X" % Service.Uuid.ShortUuid)
                else :
                    print("    UUID", Service.Uuid.LongUuid)
                ReadCharacteristics(Service)
                i += 1


# Connects to specific device
def ConnectToDevice(Radio, Address) :
    print()
    print("Start connecting to the device %0.12X" % Address)

    # Set connection parameters
    Client.Address = Address

    # Start connecting to device.
    Res = Client.Connect(Radio)
    if (Res != wclErrors.WCL_E_SUCCESS) :
        print("  Connect failed: 0x%0.8X" % Res)
    OperEvent.set()


# The main function
def main() :
    # Change synchronization method to be able to use it in console
    wclCommon.wclMessageBroadcaster.SetSyncMethod(wclCommon.wclMessageSynchronizationKind.skThread)

    print("This simple demo shows how to use GATT Client to connect to GATT enabled Bluetooth LE devices.")
    print("The demo:")
    print("  - searches for Bluetooth LE GATT enabled devices")
    print("  - connects to first found device")
    print("  - read services")
    print("  - read characteristics")
    print("  - read characteristic values (if readable characteristics found)")
    print("  - subscribes for notification and/or indications")
    print()

    global Manager
    Manager = wclBluetooth.wclBluetoothManager()
    Manager.OnDiscoveringStarted += DiscoveringStarted
    Manager.OnDeviceFound += DeviceFound
    Manager.OnDiscoveringCompleted += DiscoveringCompleted

    global Client
    Client = wclBluetooth.wclGattClient()
    Client.OnDisconnect += Disconnect
    Client.OnConnect += Connect
    Client.OnCharacteristicChanged += CharacteristicChanged
     
    # Create and initialize operation completion event objects
    global OperEvent
    OperEvent = Event()

    # Found devices array
    global Devices
    Devices = []

    print("Try to open Bluetooth Manager")
    Res = Manager.Open()
    if (Res != wclErrors.WCL_E_SUCCESS) :
        print("  Open Bluetooth Manager failed: 0x%0.8X" % Res)
    else :
        print("Try to get first available Bluetooth Radio that supports Bluetooth LE communication")
        Res, Radio = Manager.GetLeRadio()
        if (Res != wclErrors.WCL_E_SUCCESS) :
            print("  Get working radio failed: 0x%0.8X" % Res)
        else :
            print("  Radio found: " + Radio.ApiName)
            
            print("Try to start discovering")
            Res = Radio.Discover(10, wclBluetoothDiscoverKind.dkBle)
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
