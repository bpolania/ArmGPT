#!/bin/bash
# Script to check available serial devices on Raspberry Pi
# Run this on the Pi to identify which serial devices are available

LOG_FILE="serial_devices.log"

echo "=== Raspberry Pi Serial Device Detection ===" > $LOG_FILE
echo "Date: $(date)" >> $LOG_FILE
echo "Host: $(hostname)" >> $LOG_FILE
echo "Kernel: $(uname -r)" >> $LOG_FILE
echo "" >> $LOG_FILE

echo "=== All TTY devices ===" >> $LOG_FILE
ls -la /dev/tty* >> $LOG_FILE 2>&1
echo "" >> $LOG_FILE

echo "=== Serial-specific devices ===" >> $LOG_FILE
ls -la /dev/tty* 2>/dev/null | grep -E "(ttyS|ttyAMA|serial|ttyUSB|ttyACM)" >> $LOG_FILE
echo "" >> $LOG_FILE

echo "=== Common serial device paths ===" >> $LOG_FILE
for device in /dev/ttyS0 /dev/ttyS1 /dev/ttyAMA0 /dev/ttyAMA1 /dev/serial0 /dev/serial1 /dev/ttyUSB0 /dev/ttyUSB1; do
    if [ -e "$device" ]; then
        echo "✓ $device exists" >> $LOG_FILE
        ls -la "$device" >> $LOG_FILE
    else
        echo "✗ $device does not exist" >> $LOG_FILE
    fi
done
echo "" >> $LOG_FILE

echo "=== Serial symbolic links ===" >> $LOG_FILE
ls -la /dev/serial* 2>/dev/null >> $LOG_FILE
echo "" >> $LOG_FILE

echo "=== UART configuration (if available) ===" >> $LOG_FILE
if command -v raspi-config >/dev/null; then
    echo "raspi-config available for UART configuration" >> $LOG_FILE
else
    echo "raspi-config not available" >> $LOG_FILE
fi
echo "" >> $LOG_FILE

echo "=== Device tree info ===" >> $LOG_FILE
if [ -f /boot/config.txt ]; then
    echo "UART-related config.txt settings:" >> $LOG_FILE
    grep -E "(uart|serial)" /boot/config.txt 2>/dev/null >> $LOG_FILE || echo "No UART settings found in config.txt" >> $LOG_FILE
else
    echo "/boot/config.txt not found" >> $LOG_FILE
fi
echo "" >> $LOG_FILE

echo "=== Current user permissions ===" >> $LOG_FILE
echo "Current user: $(whoami)" >> $LOG_FILE
echo "Groups: $(groups)" >> $LOG_FILE
echo "dialout group membership:" >> $LOG_FILE
if groups | grep -q dialout; then
    echo "✓ User is in dialout group" >> $LOG_FILE
else
    echo "✗ User is NOT in dialout group" >> $LOG_FILE
    echo "  To fix: sudo usermod -a -G dialout \$USER" >> $LOG_FILE
fi
echo "" >> $LOG_FILE

echo "=== Test device accessibility ===" >> $LOG_FILE
for device in /dev/ttyS0 /dev/ttyAMA0 /dev/serial0; do
    if [ -e "$device" ]; then
        if [ -r "$device" ] && [ -w "$device" ]; then
            echo "✓ $device is readable and writable" >> $LOG_FILE
        elif [ -r "$device" ]; then
            echo "⚠ $device is readable but not writable" >> $LOG_FILE
        else
            echo "✗ $device exists but not accessible (try sudo)" >> $LOG_FILE
        fi
    fi
done
echo "" >> $LOG_FILE

echo "=== Recommendations ===" >> $LOG_FILE
echo "1. If no serial devices found, enable UART with: sudo raspi-config" >> $LOG_FILE
echo "2. Go to Interface Options → Serial → Enable" >> $LOG_FILE
echo "3. If permission denied, add user to dialout group" >> $LOG_FILE
echo "4. Common working devices on Pi: /dev/ttyAMA0, /dev/serial0" >> $LOG_FILE
echo "5. For USB serial adapters: /dev/ttyUSB0" >> $LOG_FILE
echo "" >> $LOG_FILE

echo "=== Log complete ===" >> $LOG_FILE
echo "Serial device detection complete. Results saved to: $LOG_FILE"
echo "You can now read this file to see available serial devices."