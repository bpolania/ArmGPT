#!/bin/bash
# Serial Monitor Script for ARM Assembly Acorn Communication Testing
# SINGLE PI TESTING - Limited by hardware loopback requirements
# For dual Pi testing, use serial-monitor-receiver.sh on the second Pi

DEVICE="/dev/ttyUSB0"
BAUDRATE="9600"
LOG_FILE="serial_monitor.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=== ARM Assembly Serial Monitor ===" | tee $LOG_FILE
echo "Device: $DEVICE" | tee -a $LOG_FILE
echo "Baud Rate: $BAUDRATE" | tee -a $LOG_FILE
echo "Log File: $LOG_FILE" | tee -a $LOG_FILE
echo "Started: $(date)" | tee -a $LOG_FILE
echo "Press Ctrl+C to stop monitoring" | tee -a $LOG_FILE
echo "========================================" | tee -a $LOG_FILE
echo ""

# Check if device exists
if [ ! -e "$DEVICE" ]; then
    echo -e "${RED}ERROR: Serial device $DEVICE does not exist${NC}"
    echo "Available devices:"
    ls -la /dev/serial* /dev/ttyAMA* /dev/ttyS* 2>/dev/null || echo "No serial devices found"
    exit 1
fi

# Check if device is readable
if [ ! -r "$DEVICE" ]; then
    echo -e "${YELLOW}WARNING: Cannot read $DEVICE - trying with sudo${NC}"
    echo "You may need to run: sudo usermod -a -G dialout $USER"
    echo "Then logout and login again, or run this script with sudo"
fi

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Monitoring stopped at $(date)${NC}" | tee -a $LOG_FILE
    echo "Log saved to: $LOG_FILE"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo -e "${GREEN}Monitoring $DEVICE for incoming data...${NC}"
echo ""

# Configure serial port settings using stty
stty -F $DEVICE $BAUDRATE cs8 -cstopb -parenb raw -echo 2>/dev/null || {
    echo -e "${YELLOW}Warning: Could not configure serial port settings${NC}"
}

# Monitor the serial device
while true; do
    if read -r -t 1 line < $DEVICE 2>/dev/null; then
        timestamp=$(date '+%H:%M:%S.%3N')
        
        # Display with timestamp and color
        echo -e "${BLUE}[$timestamp]${NC} ${GREEN}RX:${NC} $line" | tee -a $LOG_FILE
        
        # Also show hex representation for debugging
        if [ -n "$line" ]; then
            hex_data=$(echo -n "$line" | xxd -p | tr -d '\n')
            echo -e "${BLUE}[$timestamp]${NC} ${YELLOW}HEX:${NC} $hex_data" | tee -a $LOG_FILE
        fi
        echo "" | tee -a $LOG_FILE
    else
        # Check if device still exists
        if [ ! -e "$DEVICE" ]; then
            echo -e "${RED}ERROR: Device $DEVICE disappeared${NC}" | tee -a $LOG_FILE
            break
        fi
        
        # Show we're still alive every 10 seconds
        if [ $(($(date +%s) % 10)) -eq 0 ]; then
            echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} Waiting for data..." | tee -a $LOG_FILE
            sleep 1
        fi
    fi
done

cleanup