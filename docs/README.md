# ARM Assembly Cross-Platform Serial Communication Project

A native ARM assembly program that simulates Acorn computer communication over serial port, designed for cross-platform compatibility between Raspberry Pi and Acorn computers.

## Features

- **Native ARM Assembly**: Hand-coded ARM assembly for maximum performance
- **Cross-Platform**: Works on Raspberry Pi (Linux) and Acorn computers (RISC OS)
- **Serial Communication**: Full serial port control at 9600 baud, 8N1
- **Interactive Menu**: User-friendly menu system with multiple options
- **Error Handling**: Comprehensive error detection and reporting
- **Real-time Operation**: Direct system calls for optimal performance

## Project Structure

```
ArmGPT/
├── src/
│   └── main.s              # Main ARM assembly source code
├── include/
│   └── linux_syscalls.inc  # Linux system call definitions
├── docs/
│   └── README.md           # This file
├── Makefile                # Build configuration
└── assembly_project_brief.md # Original project specification
```

## Requirements

### Raspberry Pi
- ARM-based Raspberry Pi (any model)
- Raspberry Pi OS or compatible Linux distribution
- Serial port enabled (via `raspi-config`)
- Build tools: `binutils`, `gcc-arm-linux-gnueabihf`

### Development Tools
```bash
# Install required packages
sudo apt update
sudo apt install build-essential binutils-arm-linux-gnueabihf

# Enable serial port
sudo raspi-config
# Navigate to: Interface Options -> Serial -> Enable
```

## Building

```bash
# Build native ARM executable
make

# Cross-compile (if needed)
make cross

# Build with debug symbols
make debug

# Check system architecture
make arch-check
```

## Usage

### Running the Program
```bash
# Run directly
./acorn_comm

# Run with serial monitoring
make serial-test
```

### Menu Options
1. **Send test message** - Sends a predefined test message
2. **Send continuous data** - Sends repeated messages (10 iterations)
3. **Send custom message** - Allows user input for custom messages
4. **Exit** - Cleanly closes serial port and exits

## Serial Port Configuration

The program automatically configures the serial port with:
- **Baud Rate**: 9600 bps
- **Data Bits**: 8
- **Parity**: None
- **Stop Bits**: 1
- **Flow Control**: None

Default device: `/dev/ttyS0`

## Testing

### Serial Port Testing
```bash
# Show available serial devices
make show-serial

# Monitor serial output in another terminal
sudo cat /dev/ttyS0

# Test with loopback (connect TX to RX)
# Then run the program and observe echo
```

### Debugging
```bash
# Build with debug symbols
make debug

# Use GDB for debugging
gdb ./acorn_comm
```

## Technical Details

### ARM Assembly Features Used
- **System Calls**: Direct Linux syscall interface
- **Memory Management**: Efficient use of ARM registers
- **Conditional Execution**: ARM-specific conditional branches
- **IOCTL Operations**: Direct serial port configuration
- **Error Handling**: Comprehensive error checking

### Performance Optimizations
- Direct syscalls (no libc overhead)
- Efficient register usage following ARM AAPCS
- Minimal memory footprint
- Fast execution with no interpreted code

## Troubleshooting

### Common Issues

1. **Permission Denied on Serial Port**
   ```bash
   # Add user to dialout group
   sudo usermod -a -G dialout $USER
   # Then logout and login again
   ```

2. **Serial Port Not Found**
   ```bash
   # Check available ports
   make show-serial
   # Edit serial_device in main.s if needed
   ```

3. **Build Errors**
   ```bash
   # Ensure ARM tools are installed
   make install-deps
   
   # Check architecture
   make arch-check
   ```

## Cross-Platform Notes

### Raspberry Pi (Linux)
- Uses Linux syscalls (`SYS_OPEN`, `SYS_WRITE`, `SYS_IOCTL`)
- Termios structure for serial configuration
- Device file: `/dev/ttyS0`

### Acorn Computers (RISC OS)
- Would use RISC OS SWI calls (Software Interrupts)
- Different serial port access methods
- Platform-specific build requirements

## Future Enhancements

- [ ] RISC OS compatibility layer
- [ ] Interrupt-driven I/O
- [ ] DMA support for bulk transfers
- [ ] Protocol implementation (framing, checksums)
- [ ] Multiple baud rate support
- [ ] Real-time timing improvements

## License

This project is for educational purposes, demonstrating low-level ARM assembly programming and serial communication.

## Contributing

This is an educational project. Feel free to study the code and adapt it for your own learning purposes.

---

*Built with native ARM assembly for maximum performance and educational value.*