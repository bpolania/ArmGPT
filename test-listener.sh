#!/bin/bash
# Test different listener approaches to diagnose the issue

DEVICE="/dev/ttyUSB0"

echo "=== Testing Different Listener Approaches ==="
echo "Device: $DEVICE"
echo ""

echo "1. Testing with simple cat (will show any data):"
echo "   Run this and send data from other Pi"
echo "   cat $DEVICE"
echo ""

echo "2. Testing with xxd (shows raw hex data):"
echo "   xxd $DEVICE"
echo ""

echo "3. Testing with dd (byte-by-byte):"
echo "   dd if=$DEVICE bs=1 count=100 2>/dev/null | xxd"
echo ""

echo "4. Testing with timeout but no line requirement:"
echo "   timeout 10 dd if=$DEVICE bs=1 2>/dev/null | xxd"
echo ""

echo "Choose test method (1-4):"
read choice

case $choice in
    1)
        echo "Starting cat test - send data from other Pi now..."
        cat $DEVICE
        ;;
    2)
        echo "Starting xxd test - send data from other Pi now..."
        timeout 10 xxd $DEVICE
        ;;
    3)
        echo "Starting dd test - send data from other Pi now..."
        dd if=$DEVICE bs=1 count=100 2>/dev/null | xxd
        ;;
    4)
        echo "Starting timeout dd test - send data from other Pi now..."
        timeout 10 dd if=$DEVICE bs=1 2>/dev/null | xxd
        ;;
    *)
        echo "Invalid choice"
        ;;
esac