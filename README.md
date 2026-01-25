# HomeAssistant Diesel Heater BLE

Controlling Chinese diesel parking heaters via Bluetooth Low Energy (BLE), using Custom Components in Home Assistant

## Features

- **BLE Control**: Connect to and control your diesel heater over Bluetooth
- **Real-time Status**: Monitor temperature, voltage, altitude, and operating state
- **Automation-Friendly**: Switch, select, and number entities for easy Home Assistant automations

## BLE Protocol

### Service & Characteristics
- **Service UUID**: `0000FFF0-0000-1000-8000-00805F9B34FB`
- **Write Characteristic**: `0000FFF2-0000-1000-8000-00805F9B34FB`
- **Notify Characteristic**: `0000FFF1-0000-1000-8000-00805F9B34FB`

### Command Format (8 bytes)
```
Byte 0:   0xBA - Header
Byte 1:   0xAB - Header
Byte 2:   0x04 - Length
Byte 3:   Command type (0xCC=Status, 0xBB=Control)
Byte 4:   Command code
Byte 5-6: Parameter (usually 0x0000)
Byte 7:   Checksum (sum of bytes 0-6, mod 256)
```

### Commands
| Command | Bytes | Description |
|---------|-------|-------------|
| Get Status | `BAAB04CC00000035` | Request current status |
| On/Off | `BAAB04BBA10000C5` | Toggle heater on/off |
| Up | `BAAB04BBA20000C6` | Increase level/temp |
| Down | `BAAB04BBA30000C7` | Decrease level/temp |
| Fan | `BAAB04BBA40000C8` | Toggle fan-only mode |
| Plateau | `BAAB04BBA50000C9` | Toggle plateau mode |
| Auto Mode | `BAAB04BBA60000CA` | Toggle auto temperature control |
| Temp °C | `BAAB04BBA70000CB` | Set temperature unit to Celsius |
| Temp °F | `BAAB04BBA80000CC` | Set temperature unit to Fahrenheit |
| Alt Meters | `BAAB04BBA90000CD` | Set altitude unit to meters |
| Alt Feet | `BAAB04BBAA0000CE` | Set altitude unit to feet |
| Level Mode | `BAAB04BBAC0000D0` | Switch to level control mode |
| Temp Mode | `BAAB04BBAD0000D1` | Switch to temperature control mode |

### Response Format (21 bytes)
```
Bytes 0-3:   AB.BA.11.CC - Header
Byte 4:      Operating mode (0x00=Idle, 0x01=Heating, 0x02=Cooling, 0x04=Fan Only)
Byte 5:      Control mode (0x00=Level, 0x01=Temperature, 0xFF=Error)
Byte 6:      Level (1-6) or target temp or error code
Byte 7:      Running state (0x00=Idle, 0x01=Cooling, 0x03=Glowplug, 0x05=Heating, 0x07=Preheating)
Byte 8:      Auto mode (0x00=Manual, 0x01=Auto)
Byte 9:      Supply voltage (whole volts)
Byte 10:     Temperature unit (0x00=Celsius, 0x01=Fahrenheit)
Byte 11:     Environment temp (raw, subtract 30 for °C)
Bytes 12-13: Combustion temperature (little-endian, °C)
Byte 14:     Altitude unit (0x00=meters, 0x01=feet)
Byte 15:     High altitude mode (0x00=Off, 0x01=On)
Bytes 16-17: Altitude (little-endian)
Bytes 18-19: Reserved
Byte 20:     Checksum (sum of bytes 0-19, mod 256)
```

## License

MIT
