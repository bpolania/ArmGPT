#!/bin/bash
# USB Serial Device Detection Script
# Detects USB serial devices for dual Pi communication

echo "=== USB Serial Device Detection ==="
echo "Date: $(date)"
echo "Host: $(hostname)"
echo ""

echo "=== USB Serial Devices ==="
echo "Checking for USB serial adapters..."

# Check for common USB serial devices
FOUND_DEVICES=()

for device in /dev/ttyUSB* /dev/ttyACM*; do
    if [ -e "$device" ]; then
        echo "✓ Found: $device"
        ls -la "$device"
        FOUND_DEVICES+=("$device")
        
        # Check if device is accessible
        if [ -r "$device" ] && [ -w "$device" ]; then
            echo "  ✓ Device is readable and writable"
        elif [ -r "$device" ]; then
            echo "  ⚠ Device is readable but not writable"
        else
            echo "  ✗ Device exists but not accessible (check permissions)"
        fi
        echo ""
    fi
done

if [ ${#FOUND_DEVICES[@]} -eq 0 ]; then
    echo "✗ No USB serial devices found"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check USB cable connection"
    echo "2. Check dmesg: dmesg | tail -20"
    echo "3. Try different USB ports"
    echo "4. Verify cable compatibility"
else
    echo "=== Recommended Device ==="
    RECOMMENDED=${FOUND_DEVICES[0]}
    echo "Use device: $RECOMMENDED"
    echo ""
    echo "=== Update Configuration ==="
    echo "Pi 1 (Sender): Update src/main.s serial_device to \"$RECOMMENDED\""
    echo "Pi 2 (Receiver): Update serial-monitor-receiver.sh DEVICE to \"$RECOMMENDED\""
fi

echo ""
echo "=== USB Device Information ==="
lsusb | grep -i "serial\|ftdi\|prolific\|cp210\|pl2303"

echo ""
echo "=== Recent USB Events ==="
echo "Last 10 USB-related kernel messages:"
dmesg | grep -i "usb\|tty" | tail -10

echo ""
echo "=== Current User Permissions ==="
echo "Current user: $(whoami)"
echo "Groups: $(groups)"
if groups | grep -q dialout; then
    echo "✓ User is in dialout group"
else
    echo "✗ User is NOT in dialout group"
    echo "  Fix: sudo usermod -a -G dialout $USER"
    echo "  Then logout and login again"
fi

echo ""
echo "=== Detection Complete ==="