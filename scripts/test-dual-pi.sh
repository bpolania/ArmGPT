#!/bin/bash
# Dual Pi Testing Script - Run on SENDER Pi (Pi 1)
# This script helps coordinate testing between two Raspberry Pis

echo "=== DUAL RASPBERRY PI SERIAL COMMUNICATION TEST ==="
echo ""
echo "SENDER PI (This Pi) - ARM Assembly Program"
echo "RECEIVER PI (Other Pi) - Serial Monitor"
echo ""
echo "Hardware Setup Required:"
echo "- Pi 1 Pin 8  (GPIO 14 - TX) → Pi 2 Pin 10 (GPIO 15 - RX)"
echo "- Pi 1 Pin 10 (GPIO 15 - RX) → Pi 2 Pin 8  (GPIO 14 - TX)"
echo "- Pi 1 Pin 6  (GND)          → Pi 2 Pin 6  (GND)"
echo ""
echo "Before starting:"
echo "1. Verify hardware connections"
echo "2. Start './serial-monitor-receiver.sh' on RECEIVER PI"
echo "3. Press Enter here to continue..."
read -p ""

echo "Checking serial device on SENDER PI..."
if [ ! -e "/dev/serial0" ]; then
    echo "ERROR: /dev/serial0 not found. Enable UART with: sudo raspi-config"
    exit 1
fi

echo "✓ Serial device found"
echo ""

echo "Building ARM assembly program..."
echo "🗑️  Removing old logs..."
rm -f build.log acorn_comm.log

echo "🧹 Cleaning build artifacts..."
make clean

echo "🔨 Building with logging..."
make build-log

if [ $? -ne 0 ]; then
    echo "ERROR: Build failed"
    exit 1
fi

echo "✅ Clean build completed!"

if [ -f build.log ]; then
    echo "📋 Build log created:"
    echo "   - Check 'build.log' for details"
    if grep -q "Error:" build.log; then
        echo "❌ Build errors found in log"
        exit 1
    else
        echo "✅ Build appears successful"
    fi
fi
echo ""

echo "=== READY FOR TESTING ==="
echo "1. Ensure RECEIVER PI is running serial-monitor-receiver.sh"
echo "2. ARM assembly program will start"
echo "3. Select option 1 to send test message"
echo "4. Check RECEIVER PI for incoming message"
echo ""
echo "Starting ARM assembly program in 3 seconds..."
sleep 3

# Run the ARM assembly program
../acorn_comm

echo ""
echo "=== TEST COMPLETED ==="
echo "Check the RECEIVER PI for received messages"
echo "Check receiver_monitor.log on RECEIVER PI for detailed logs"