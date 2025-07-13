#!/bin/bash
# Script to update device paths for USB serial communication
# Run this after detecting your USB serial device

if [ $# -ne 1 ]; then
    echo "Usage: $0 <usb_device>"
    echo "Example: $0 /dev/ttyUSB0"
    echo ""
    echo "First run: ./detect-usb-serial.sh to find your USB device"
    exit 1
fi

USB_DEVICE=$1

echo "=== Updating Device Paths for USB Serial ==="
echo "USB Device: $USB_DEVICE"
echo ""

# Validate device exists
if [ ! -e "$USB_DEVICE" ]; then
    echo "ERROR: Device $USB_DEVICE does not exist"
    echo "Run: ./detect-usb-serial.sh to find available devices"
    exit 1
fi

echo "✓ Device $USB_DEVICE exists"

# Update ARM assembly source code
echo "Updating src/main.s..."
if [ -f "src/main.s" ]; then
    # Backup original
    cp src/main.s src/main.s.backup
    
    # Update serial device path
    sed -i "s|serial_device: .ascii \"/dev/serial0\\0\"|serial_device: .ascii \"$USB_DEVICE\\0\"|g" src/main.s
    sed -i "s|serial_device: .ascii \"/dev/ttyAMA.*\\0\"|serial_device: .ascii \"$USB_DEVICE\\0\"|g" src/main.s
    
    # Update log message
    sed -i "s|log_serial_init: .ascii \"\\[SERIAL\\] Initializing serial port /dev/.*\\\\n\"|log_serial_init: .ascii \"[SERIAL] Initializing serial port $USB_DEVICE\\\\n\"|g" src/main.s
    
    echo "✓ Updated src/main.s"
else
    echo "✗ src/main.s not found"
fi

# Update receiver monitor script
echo "Updating serial-monitor-receiver.sh..."
if [ -f "serial-monitor-receiver.sh" ]; then
    # Backup original
    cp serial-monitor-receiver.sh serial-monitor-receiver.sh.backup
    
    # Update device path
    sed -i "s|DEVICE=\"/dev/.*\"|DEVICE=\"$USB_DEVICE\"|g" serial-monitor-receiver.sh
    
    echo "✓ Updated serial-monitor-receiver.sh"
else
    echo "✗ serial-monitor-receiver.sh not found"
fi

# Update single Pi monitor script
echo "Updating serial-monitor.sh..."
if [ -f "serial-monitor.sh" ]; then
    # Backup original
    cp serial-monitor.sh serial-monitor.sh.backup
    
    # Update device path
    sed -i "s|DEVICE=\"/dev/.*\"|DEVICE=\"$USB_DEVICE\"|g" serial-monitor.sh
    
    echo "✓ Updated serial-monitor.sh"
else
    echo "✗ serial-monitor.sh not found"
fi

echo ""
echo "=== Update Complete ==="
echo "Device paths updated to: $USB_DEVICE"
echo ""
echo "Next steps:"
echo "1. Run on Pi 2 (Receiver): ./serial-monitor-receiver.sh"
echo "2. Run on Pi 1 (Sender): ./test-dual-pi.sh"
echo "3. Select option 1 to test communication"
echo ""
echo "Backup files created (.backup) in case you need to revert"