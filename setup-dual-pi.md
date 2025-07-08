# Dual Raspberry Pi Serial Communication Setup

## Hardware Requirements
- **2 Raspberry Pi devices** (both with UART enabled)
- **3 jumper wires** for serial connection
- **Common ground** connection

## Physical Wiring
Connect the Pis using GPIO pins:

### Pi 1 (Sender) → Pi 2 (Receiver)
```
Pi 1 Pin 8  (GPIO 14 - TX) → Pi 2 Pin 10 (GPIO 15 - RX)
Pi 1 Pin 10 (GPIO 15 - RX) → Pi 2 Pin 8  (GPIO 14 - TX)  [for bidirectional]
Pi 1 Pin 6  (GND)          → Pi 2 Pin 6  (GND)           [common ground]
```

## Software Setup

### Pi 1 (Sender) - ARM Assembly Program
```bash
# Clone the repository
git clone https://github.com/bpolania/ArmGPT.git
cd ArmGPT

# Build and run
./clean-build.sh
./acorn_comm
```

### Pi 2 (Receiver) - Serial Monitor
```bash
# Clone the same repository 
git clone https://github.com/bpolania/ArmGPT.git
cd ArmGPT

# Run the monitor
./serial-monitor-receiver.sh
```

## Device Configuration

### Both Pis: Enable UART
```bash
sudo raspi-config
# → Interface Options → Serial Port
# → Enable Serial Port: Yes
# → Enable Serial Console: No (for clean communication)
sudo reboot
```

### Both Pis: Check Serial Device
```bash
./check-serial-devices.sh
# Verify /dev/serial0 exists and is accessible
```

## Testing Process
1. **Start monitor on Pi 2**: `./serial-monitor-receiver.sh`
2. **Run program on Pi 1**: `./acorn_comm`
3. **Select option 1** on Pi 1 to send test message
4. **Verify message appears** on Pi 2 monitor

## Expected Results
- Pi 1 should show: "Message sent successfully!"
- Pi 2 should display: "TEST MESSAGE FROM ACORN SYSTEM"
- Log files on both Pis will record the communication

## Troubleshooting
- Verify wiring connections
- Check that both Pis have UART enabled
- Ensure common ground connection
- Verify serial device permissions (dialout group)