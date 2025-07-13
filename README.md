# ARM Assembly Cross-Platform Serial Communication Project

## 🚀 **Quick Start**

### **Setup and Run (First Time)**
```bash
# 1. Setup (handles UART, permissions, build)
./setup.sh

# 2. Run the program
./acorn_comm
```

That's it! The setup script handles everything needed to get the ARM assembly serial communication working.

---

## 🎯 **Project Status: FULLY FUNCTIONAL + AI INTEGRATION PHASE**

### 📖 **Project Origin**
This project creates a native ARM assembly program that simulates Acorn computer communication over serial port, leveraging the shared ARM architecture between Raspberry Pi and Acorn computers for cross-platform compatibility. The assembly approach provides maximum performance with direct hardware control, educational value for low-level programming, and an authentic experience closer to original Acorn software development.

### ✅ **Phase 1: COMPLETED - ARM Assembly Serial Communication**
Professional ARM assembly program with dual Raspberry Pi serial communication successfully implemented and tested.

### 🚀 **Phase 2: IN PROGRESS - TinyLLM AI Integration**
Extending the serial communication system to integrate with TinyLLM for AI-powered message processing.

---

## 📋 **Current System Overview**

### **Dual Pi Architecture**
```
┌─────────────────┐    USB Serial   ┌─────────────────┐
│   SENDER PI     │     Cable       │   RECEIVER PI   │
│                 │ ──────────────▶ │                 │
│ ARM Assembly    │  /dev/ttyUSB0   │ Serial Monitor  │
│ Program         │   9600 baud     │ Scripts         │
│                 │                 │                 │
│ • Menu System   │                 │ • Data Capture  │
│ • Test Messages │                 │ • Logging       │
│ • Custom Input  │                 │ • Validation    │
│ • Continuous    │                 │ • Diagnostics   │
└─────────────────┘                 └─────────────────┘
```

### **✅ Verified Working Features**
- **ARM Assembly Program**: Full menu-driven interface with 4 options (ALL WORKING)
- **Serial Communication**: Real hardware transmission via USB cable
- **Message Types**: Test messages, continuous data, custom user input (FIXED)
- **Interactive Menu**: Complete user input handling with proper line consumption
- **Error Handling**: Robust fallback mechanisms and logging
- **Cross-Platform**: Works on Raspberry Pi (ARM) and macOS (simulation)
- **Development Workflow**: Git, automated testing, comprehensive documentation

---

## 🔮 **Next Phase: TinyLLM Integration Architecture**

### **Proposed AI Integration Pipeline**

```
┌─────────────────┐    Serial     ┌─────────────────┐    Process    ┌─────────────────┐
│   SENDER PI     │   USB Cable   │   RECEIVER PI   │   & Forward   │    TinyLLM      │
│                 │ ──────────────▶                 │ ──────────────▶                 │
│ ARM Assembly    │               │ Serial Monitor  │               │ AI Processing   │
│ Program         │               │ + LLM Bridge    │               │ Response Gen    │
│                 │               │                 │               │                 │
│ • User Input    │               │ • Message Parse │               │ • Text Analysis │
│ • Custom Msgs   │               │ • Format Clean  │               │ • AI Response   │
│ • Continuous    │               │ • LLM Forward   │               │ • Generation    │
│ • Test Data     │               │ • Response Log  │               │ • Processing    │
└─────────────────┘               └─────────────────┘               └─────────────────┘
```

### **Integration Components**

#### 1. **Enhanced Receiver Script** (`serial-to-llm.sh`)
- **Message Capture**: Real-time serial data monitoring
- **Data Processing**: Parse and clean ARM assembly message format
- **LLM Integration**: Forward processed messages to TinyLLM
- **Response Handling**: Capture and log AI responses
- **Error Management**: Robust error handling for AI pipeline

#### 2. **Message Processing Pipeline**
- **Format Cleaning**: Strip ARM assembly formatting and headers
- **Content Extraction**: Extract actual message content for AI processing
- **Input Preparation**: Format messages for TinyLLM input requirements
- **Response Processing**: Handle AI responses and logging

#### 3. **Bidirectional Communication** (Future Enhancement)
- **Response Forwarding**: Send AI responses back to sender Pi
- **Interactive Mode**: Enable real-time conversation through serial link
- **Message Threading**: Track conversation context across messages

---

## 🛠️ **Technical Implementation**

### **Current ARM Assembly Features**
- **Native Linux System Calls**: Direct syscall interface for performance
- **Serial Port Configuration**: Hardware UART at 9600 baud, 8N1
- **Buffer Management**: SYS_FSYNC buffer flushing for reliable transmission
- **ARM Calling Conventions**: Proper register preservation and function calls
- **Comprehensive Logging**: Debug and operational logging to `acorn_comm.log`

### **Message Format**
```
Current: "TEST MESSAGE FROM ACORN SYSTEM\n"
Custom:  User input up to 255 characters
Continuous: Repeated test messages with timing
```

### **Serial Configuration**
- **Device**: `/dev/ttyUSB0` (USB serial cable)
- **Baud Rate**: 9600
- **Format**: 8N1 (8 data bits, no parity, 1 stop bit)
- **Flow Control**: None
- **Buffer Flush**: SYS_FSYNC for immediate transmission

---

## 📁 **Project Structure**

```
ArmGPT/
├── src/
│   └── main.s                 # ARM Assembly main program
├── include/
│   └── linux_syscalls.inc    # System call definitions
├── docs/
│   ├── setup-dual-pi.md      # GPIO setup guide (legacy)
│   └── setup-usb-serial.md   # USB serial setup guide
├── scripts/
│   ├── test-dual-pi.sh         # Main testing script with integrated build
│   ├── detect-usb-serial.sh    # USB serial device detection
│   ├── test-listener.sh        # Diagnostic testing and debugging
│   └── git-update.sh           # Git workflow automation
├── Makefile                   # ARM build system
├── Makefile.mac              # macOS simulation build
├── CHANGELOG.md              # Development history
└── README.md                 # This file
```

---

## 🚀 **Getting Started**

### **Prerequisites**
- 2x Raspberry Pi (any model with USB ports)
- 1x USB Male-to-Male Serial Cable
- ARM development tools (`build-essential`, `binutils`)
- TinyLLM installed on receiver Pi

### **Phase 1: ARM Assembly Serial Communication**
```bash
# Clone and build
git clone <repository>
cd ArmGPT
make clean && make

# Run sender Pi
./acorn_comm

# Run receiver Pi (separate terminal/Pi)
./scripts/serial-monitor-receiver.sh
```

### **Phase 2: TinyLLM Integration** (In Development)
```bash
# Switch to AI integration branch
git checkout feature/tinyLLM-integration

# Run enhanced receiver with AI
./scripts/serial-to-llm.sh
```

---

## 🔧 **Development Workflow**

### **Build System**
```bash
make clean        # Clean build artifacts
make              # Build ARM assembly
make build-log    # Build with logging
make test         # Run program
```

### **Testing**
```bash
./scripts/test-dual-pi.sh     # Automated dual Pi testing
./scripts/test-listener.sh    # Diagnostic listener tests
./scripts/detect-usb-serial.sh # Hardware detection
```

### **Debugging**
- **Logs**: `acorn_comm.log` (sender), `receiver_monitor.log` (receiver)
- **Build Logs**: `build.log` for compilation debugging
- **Serial Diagnostics**: Multiple listener options for troubleshooting

---

## 📊 **Performance Characteristics**

### **ARM Assembly Performance**
- **Memory Footprint**: Minimal - direct syscalls, no libc
- **Execution Speed**: Native ARM performance
- **Latency**: Sub-millisecond message transmission
- **Reliability**: Robust error handling and fallback mechanisms

### **Serial Communication**
- **Throughput**: 9600 baud (960 bytes/second theoretical)
- **Reliability**: Hardware-level transmission with buffer flushing
- **Range**: USB cable length (typically 3-5 meters)
- **Compatibility**: Standard USB serial - works across Pi models

---

## 🎯 **Project Achievements**

### **Technical Milestones**
- ✅ **Native ARM Assembly**: Professional-grade implementation
- ✅ **Real Hardware Communication**: USB serial cable transmission
- ✅ **Dual Pi Infrastructure**: Complete testing and validation workflow
- ✅ **Cross-Platform Development**: ARM Linux + macOS simulation
- ✅ **Buffer Flush Fix**: Solved kernel buffer transmission issues
- ✅ **Menu System**: Interactive user interface with multiple options
- ✅ **Error Handling**: Comprehensive fallback and recovery mechanisms

### **Development Practices**
- ✅ **Git Workflow**: Branching, commits, comprehensive changelogs
- ✅ **Documentation**: Extensive guides and troubleshooting
- ✅ **Testing**: Automated testing scripts and diagnostic tools
- ✅ **Logging**: Comprehensive debug and operational logging
- ✅ **Build System**: Makefile with multiple targets and platforms

---

## 🔮 **Future Enhancements**

### **AI Integration Roadmap**
1. **TinyLLM Message Processing**: Forward serial messages to AI
2. **Response Handling**: Capture and log AI responses
3. **Bidirectional Communication**: Send AI responses back to sender
4. **Interactive Mode**: Real-time conversation through serial link
5. **Context Management**: Track conversation history and context

### **Advanced Features**
- **Multiple LLM Support**: Integration with different AI models
- **Message Filtering**: Intelligent message routing and processing
- **Response Formatting**: Custom response formats for ARM assembly
- **Performance Optimization**: Faster message processing and transmission
- **Web Interface**: Monitor and control system via web dashboard

---

## 🏆 **Project Status: MISSION ACCOMPLISHED (Phase 1)**

The ARM Assembly Cross-Platform Serial Communication Project has successfully achieved its primary goal of creating a professional-grade ARM assembly program that can communicate between two Raspberry Pi devices via USB serial cable. The system is fully functional, tested, and ready for AI integration.

**Branch: `feature/tinyLLM-integration`** - Ready for Phase 2 AI development!

---

## 📚 **Documentation**

- **[CHANGELOG.md](CHANGELOG.md)**: Complete development history
- **[setup-usb-serial.md](setup-usb-serial.md)**: USB serial cable setup guide
- **[setup-dual-pi.md](setup-dual-pi.md)**: GPIO setup guide (legacy)
- **[assembly_project_brief.md](assembly_project_brief.md)**: Original project specification

---

## 🤝 **Contributing**

This project demonstrates professional ARM assembly development practices with comprehensive testing, documentation, and real hardware integration. The codebase is ready for extension and enhancement.

**Current Development**: TinyLLM AI integration for intelligent message processing.

---

## 🔧 **Detailed Technical Information**

### **ARM Assembly Features**
- **System Calls**: Direct Linux syscall interface for maximum performance
- **Memory Management**: Efficient use of ARM registers following AAPCS
- **Conditional Execution**: ARM-specific conditional branches
- **IOCTL Operations**: Direct serial port configuration via termios
- **Error Handling**: Comprehensive error checking and recovery

### **Performance Optimizations**
- **Direct Syscalls**: No libc overhead, native kernel interface
- **Efficient Register Usage**: Following ARM Procedure Call Standard (AAPCS)
- **Minimal Memory Footprint**: Direct hardware control without bloat
- **Fast Execution**: No interpreted code, pure ARM assembly performance

### **Cross-Platform Implementation Notes**

#### **Raspberry Pi (Linux)**
- **System Calls**: `SYS_OPEN`, `SYS_WRITE`, `SYS_IOCTL`, `SYS_FSYNC`
- **Serial Configuration**: Termios structure for hardware configuration
- **Device Files**: `/dev/ttyUSB0`, `/dev/serial0`, `/dev/ttyAMA*`
- **Build Tools**: GNU assembler (gas), ARM Linux toolchain

#### **Acorn Computers (RISC OS) - Future**
- **System Interface**: RISC OS SWI calls (Software Interrupts)
- **Serial Access**: RISC OS specific device drivers
- **Build Requirements**: Acorn assembler, RISC OS development tools

---

## 🛠️ **Detailed Setup and Troubleshooting**

### **Development Environment Setup**
```bash
# Install ARM development tools
sudo apt update
sudo apt install build-essential binutils-arm-linux-gnueabihf

# Enable serial port on Raspberry Pi
sudo raspi-config
# Navigate to: Interface Options → Serial → Enable

# Add user to dialout group for serial access
sudo usermod -a -G dialout $USER
# Logout and login again for group changes to take effect
```

### **Common Issues and Solutions**

#### **1. Permission Denied on Serial Port**
```bash
# Check current groups
groups

# Add user to dialout group
sudo usermod -a -G dialout $USER

# Alternative: Run with sudo (not recommended)
sudo ./acorn_comm
```

#### **2. Serial Port Not Found**
```bash
# Check available serial devices
ls -la /dev/tty{S,USB,ACM,AMA}*

# Use detection script
./detect-usb-serial.sh

# Update device path in source if needed
# Edit src/main.s, change serial_device path
```

#### **3. Build Errors**
```bash
# Verify ARM tools installation
make install-deps

# Check system architecture
make arch-check

# Clean build with logging
make clean && make build-log

# Check build.log for detailed errors
cat build.log
```

#### **4. USB Serial Cable Issues**
```bash
# Check USB device detection
lsusb

# Verify device permissions
ls -la /dev/ttyUSB*

# Check if device exists
./scripts/detect-usb-serial.sh
```

#### **5. Serial Port Permission Issues**
If you get "Permission denied" when accessing `/dev/ttyUSB0`:

**Problem**: User not in correct groups to access serial devices.

**Symptoms**:
- `Permission denied` errors when running ARM assembly program
- `/dev/ttyUSB0` owned by `dialout` or `plugdev` group

**Solution**:
```bash
# Add user to both serial-related groups
sudo usermod -a -G dialout,plugdev $USER

# Verify groups (after logout/login)
groups

# Alternative: run with sudo (not recommended)
sudo ./acorn_comm
```

**Important**: You must logout and login again for group changes to take effect.

### **Testing and Diagnostics**
```bash
# Test listener (the breakthrough tool!)
./scripts/test-listener.sh

# Monitor serial port manually
cat /dev/ttyUSB0

# Check serial port configuration
stty -F /dev/ttyUSB0

# Hardware detection
./scripts/detect-usb-serial.sh
```

---

## 🚀 **Future Technical Enhancements**

### **Platform Extensions**
- **RISC OS Compatibility**: Native Acorn computer support
- **Multiple ARM Variants**: ARMv6, ARMv7, ARMv8 optimizations
- **Embedded Targets**: Bare metal ARM implementations

### **Communication Improvements**
- **Interrupt-driven I/O**: Replace polling with efficient interrupts
- **DMA Support**: Direct Memory Access for bulk transfers
- **Protocol Implementation**: Framing, checksums, error correction
- **Multiple Baud Rates**: Dynamic speed configuration
- **Flow Control**: Hardware and software flow control

### **Performance Optimizations**
- **Real-time Timing**: Precise timing control for protocols
- **Buffer Management**: Optimized circular buffers
- **Zero-copy Operations**: Minimize memory copying overhead