# USB Serial Cable Setup for Dual Pi Communication

## Hardware Requirements
- **2 Raspberry Pi devices**
- **1 USB male-to-male serial cable** (USB-to-Serial adapter cable)
- **No GPIO wiring required!**

## Physical Connection
Simply connect the USB serial cable between the two Pis:
```
Pi 1 (Sender) USB Port ←→ USB Serial Cable ←→ Pi 2 (Receiver) USB Port
```

## Device Detection and Setup

### Step 1: Connect Cable and Detect Device
On **both Pis**, after connecting the USB cable:
```bash
# Check for USB serial devices
ls -la /dev/ttyUSB* /dev/ttyACM*

# Or use our detection script
./check-serial-devices.sh
```

Common USB serial devices:
- `/dev/ttyUSB0` (most common)
- `/dev/ttyACM0` (some adapters)

### Step 2: Update Device Configuration
Once you identify the USB serial device (e.g., `/dev/ttyUSB0`), update the configuration:

#### Pi 1 (Sender) - Update ARM Assembly Program
```bash
# Edit the device path in source code
# Change serial_device from "/dev/serial0" to "/dev/ttyUSB0"
```

#### Pi 2 (Receiver) - Update Monitor Script
```bash
# Edit serial-monitor-receiver.sh
# Change DEVICE from "/dev/serial0" to "/dev/ttyUSB0"
```

## Testing Process
1. **Connect USB cable** between both Pis
2. **Detect USB serial device** on both Pis
3. **Update device paths** in code and scripts
4. **Pi 2**: Run `./serial-monitor-receiver.sh`
5. **Pi 1**: Run `./test-dual-pi.sh`
6. **Test communication**: Select option 1 on Pi 1

## Advantages of USB Serial
- ✅ **No GPIO wiring** required
- ✅ **Automatic device detection**
- ✅ **Plug and play** setup
- ✅ **Galvanic isolation** (safer)
- ✅ **Standard USB power** and signaling

## Troubleshooting
- **Device not found**: Check `dmesg | tail` after plugging in cable
- **Permission denied**: Add user to dialout group: `sudo usermod -a -G dialout $USER`
- **Multiple devices**: Use `ls -la /dev/ttyUSB*` to find the correct one

## Expected USB Device Names
- **FTDI-based cables**: `/dev/ttyUSB0`
- **Prolific-based cables**: `/dev/ttyUSB0`
- **CP210x-based cables**: `/dev/ttyUSB0`
- **CDC-ACM devices**: `/dev/ttyACM0`