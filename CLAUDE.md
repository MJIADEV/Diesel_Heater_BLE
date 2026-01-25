# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Home Assistant custom component for controlling Chinese diesel parking heaters via Bluetooth Low Energy (BLE). The component will provide switch, select, and number entities for automation.

## BLE Protocol Reference

### UUIDs
- Service: `0000FFF0-0000-1000-8000-00805F9B34FB`
- Write Characteristic: `0000FFF2-0000-1000-8000-00805F9B34FB`
- Notify Characteristic: `0000FFF1-0000-1000-8000-00805F9B34FB`

### Command Structure (8 bytes)
- Bytes 0-1: Header `0xBA 0xAB`
- Byte 2: Length `0x04`
- Byte 3: Command type (`0xCC`=Status, `0xBB`=Control)
- Byte 4: Command code
- Bytes 5-6: Parameter (usually `0x0000`)
- Byte 7: Checksum (sum of bytes 0-6, mod 256)

### Response Structure (21 bytes)
- Bytes 0-3: Header `0xAB 0xBA 0x11 0xCC`
- Byte 4: Operating mode (0=Idle, 1=Heating, 2=Cooling, 4=Fan Only)
- Byte 5: Control mode (0=Level, 1=Temperature, 0xFF=Error)
- Byte 6: Level (1-6) / target temp / error code
- Byte 7: Running state (0=Idle, 1=Cooling, 3=Glowplug, 5=Heating, 7=Preheating)
- Byte 8: Auto mode (0=Manual, 1=Auto)
- Byte 9: Supply voltage (whole volts)
- Byte 10: Temperature unit (0=Celsius, 1=Fahrenheit)
- Byte 11: Environment temp (subtract 30 for °C)
- Bytes 12-13: Combustion temp (big-endian, °C)
- Byte 14: Altitude unit (0=meters, 1=feet)
- Byte 15: High altitude mode (0=Off, 1=On)
- Bytes 16-17: Altitude (big-endian)
- Byte 20: Checksum

### Key Commands
| Action | Hex |
|--------|-----|
| Get Status | `BAAB04CC00000035` |
| On/Off | `BAAB04BBA10000C5` |
| Up/Down | `BAAB04BBA20000C6` / `BAAB04BBA30000C7` |
| Fan Mode | `BAAB04BBA40000C8` |
| Level/Temp Mode | `BAAB04BBAC0000D0` / `BAAB04BBAD0000D1` |

## Architecture Notes

This is a Home Assistant custom component. Standard structure:
```
custom_components/diesel_heater_ble/
├── __init__.py          # Integration setup
├── manifest.json        # Component metadata, dependencies
├── config_flow.py       # UI-based configuration
├── coordinator.py       # DataUpdateCoordinator for polling
├── entity.py            # Base entity class
├── switch.py            # On/off control
├── select.py            # Mode selection entities
├── number.py            # Temperature/level setpoints
├── sensor.py            # Status sensors
└── const.py             # Constants, command bytes
```

Use `bleak` for BLE communication (Home Assistant's standard BLE library).
