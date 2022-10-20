# Bluetooth Framework for Python
 Bluetooth Framework .NET Edition can be used with Python on Windows platforms.
 
 To be able to use Bluetooth Framework with Python the [Python .NET](https://github.com/pythonnet/pythonnet) package is required.
 
 This repository contains simple demos that show how to use call Bluetooth Framework from Python scripts.
 
 ## BluetoothManager.py
 
 This very simple demo shows how to use Bluetooth Manager features:
 - enumerate available local Radio modules
 - get local Radio information
 - discover classic Bluetooth devices
 - discover Bluetooth LE devices
 - enumerate paired Bluetooth devices
 - pair with selected Bluetooth device
 - unpair paired Bluetooth device
 - enumerate connected Bluetooth devices
 - disconnect connected Bluetooth device
 - read classic Bluetooth device services
 
 Refer to **BluetoothManager demo** from Bluetooth Framework package to find more details about wclBluetoothManager usage and features.
 
 ## GattClient.py
 
 This simple demo shows how to use GATT Client to connect to GATT enabled Bluetooth LE devices. The demo shows how to:
 - search for Bluetooth LE GATT enabled devices
 - connect to found device
 - read GATT services
 - read GATT characteristics
 - read GATT characteristic values (if readable characteristics found)
 - subscribes for characteristic changes notification
 
 Refer to **GattClient demo** from Bluetooth Framework package to find more details about using Bluetooth Framework for Bluetooth LE GATT communication.
 
 ## RfCommClient.py
 
 This simple demo shows how to connect to Classic Bluetooth device using Bluetooth classic RFCOMM protocol.
 By default the demo connects to Serial Port Profile (SPP) service. To make it simple the demo only receives data. For testing **Gps2Blue** Android application used on the cell as server.
 **NOTE**: The demo does not pair with device. If device requires pairing do it before running the demo.
 
 ## Support
 
 Should you have any questions about using Bluetooth Framework with Python please do not hesitate to contact us support@btframework.com
