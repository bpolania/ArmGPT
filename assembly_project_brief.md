# ARM Assembly Cross-Platform Serial Communication Project

## Project Overview
Create an ARM assembly program that simulates Acorn computer communication over serial port. Since both Raspberry Pi and Acorn computers use ARM processors, we can write native ARM assembly that works on both platforms with minimal modifications.

## Why Assembly?
- **Maximum Performance**: Direct hardware control, no overhead
- **Native Compatibility**: Both Raspberry Pi and Acorn use ARM architecture
- **Educational Value**: Learn ARM assembly and low-level serial communication
- **Authentic Experience**: Closer to how original Acorn software was written
- **Hardware Control**: Direct access to serial registers and system calls

## Platform Details
- **Raspberry Pi**: ARMv6/v7/v8 (32-bit mode), Linux system calls
- **Acorn**: ARM2/ARM3 processors, RISC OS system calls
- **Common Ground**: ARM instruction set, similar serial hardware concepts

## Technical Specifications
- **Assembly Flavor**: ARM assembly (32-bit)
- **Serial Settings**: 9600 baud, 8N1
- **Raspberry Pi**: Use Linux system calls (open, write, ioctl)
- **Acorn**: Use RISC OS SWI calls
- **Build Tools**: GNU assembler (gas) for Pi, Acorn assembler for Acorn

## Initial Code Structure

```assembly
.text
.global _start

@ Constants
.equ SYS_WRITE, 4
.equ SYS_OPEN, 5
.equ SYS_CLOSE, 6
.equ SYS_EXIT, 1
.equ STDOUT, 1

@ Data section
.data
platform_msg: .ascii "Acorn Communication Simulator - ARM Assembly\n"
platform_len = . - platform_msg

menu_msg: .ascii "\n1. Send test message\n2. Send continuous data\n3. Send custom message\n4. Exit\nSelect option: "
menu_len = . - menu_msg

test_msg: .ascii "TEST MESSAGE FROM ACORN SYSTEM\n"
test_len = . - test_msg

serial_device: .ascii "/dev/ttyS0\0"

.bss
serial_fd: .space 4
input_buffer: .space 256

_start:
    @ Print platform message
    mov r0, #STDOUT
    ldr r1, =platform_msg
    mov r2, #platform_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Initialize serial port
    bl init_serial
    cmp r0, #0
    blt exit_error
    
main_loop:
    @ Show menu
    bl show_menu
    
    @ Get user choice
    bl get_input
    
    @ Process choice
    cmp r0, #'1'
    beq send_test
    cmp r0, #'2'
    beq send_continuous
    cmp r0, #'3'
    beq send_custom
    cmp r0, #'4'
    beq exit_program
    
    @ Invalid choice, loop again
    b main_loop

send_test:
    @ Send test message to serial port
    ldr r0, =serial_fd
    ldr r0, [r0]
    ldr r1, =test_msg
    mov r2, #test_len
    mov r7, #SYS_WRITE
    swi 0
    b main_loop

send_continuous:
    @ Implementation for continuous data
    @ TODO: Add counter and loop with timing
    b main_loop

send_custom:
    @ Implementation for custom message
    @ TODO: Read user input and send
    b main_loop

init_serial:
    @ Open serial device
    ldr r0, =serial_device
    mov r1, #2          @ O_RDWR
    mov r2, #0
    mov r7, #SYS_OPEN
    swi 0
    
    @ Store file descriptor
    ldr r1, =serial_fd
    str r0, [r1]
    
    @ TODO: Configure serial port (baud rate, etc.)
    @ This would use ioctl system calls
    
    mov r0, #0          @ Success
    bx lr

show_menu:
    mov r0, #STDOUT
    ldr r1, =menu_msg
    mov r2, #menu_len
    mov r7, #SYS_WRITE
    swi 0
    bx lr

get_input:
    @ Read single character from stdin
    mov r0, #0          @ stdin
    ldr r1, =input_buffer
    mov r2, #1
    mov r7, #4          @ sys_read
    swi 0
    
    ldr r1, =input_buffer
    ldrb r0, [r1]       @ Load the character
    bx lr

exit_program:
    @ Close serial port
    ldr r0, =serial_fd
    ldr r0, [r0]
    mov r7, #SYS_CLOSE
    swi 0
    
    @ Exit successfully
    mov r0, #0
    mov r7, #SYS_EXIT
    swi 0

exit_error:
    mov r0, #1
    mov r7, #SYS_EXIT
    swi 0
```

## Development Environment Setup

### Raspberry Pi Setup
```bash
# Install ARM assembler and linker
sudo apt update
sudo apt install binutils-arm-linux-gnueabihf

# Or for native compilation
sudo apt install build-essential

# Enable serial port
sudo raspi-config
# Interface Options -> Serial -> Enable
```

### Build Process
```makefile
# Makefile
TARGET = acorn_comm
SRC = main.s

# For Raspberry Pi
$(TARGET): $(SRC)
	as -o $(TARGET).o $(SRC)
	ld -o $(TARGET) $(TARGET).o

# For cross-compilation (if needed)
$(TARGET)-cross: $(SRC)
	arm-linux-gnueabihf-as -o $(TARGET).o $(SRC)
	arm-linux-gnueabihf-ld -o $(TARGET) $(TARGET).o

clean:
	rm -f *.o $(TARGET)

test: $(TARGET)
	./$(TARGET)

serial-test:
	# Monitor serial output
	sudo cat /dev/ttyS0 &
	./$(TARGET)
```

## Development Phases

### Phase 1: Basic Framework
1. Set up ARM assembly build environment
2. Implement basic menu system using Linux system calls
3. Test compilation and execution on Raspberry Pi
4. Add basic input/output functionality

### Phase 2: Serial Communication
1. Implement serial port opening with proper file operations
2. Add serial port configuration (baud rate, parity, etc.) using ioctl
3. Implement message transmission functions
4. Test with serial loopback or monitoring tools

### Phase 3: Advanced Features
1. Add continuous data transmission with timing loops
2. Implement custom message input and transmission
3. Add error handling and status reporting
4. Optimize for performance and code size

### Phase 4: Acorn Compatibility Layer
1. Research RISC OS SWI (Software Interrupt) calls
2. Create conditional assembly for Acorn-specific code
3. Implement Acorn serial port access methods
4. Document platform differences and build procedures

## Key Assembly Concepts to Implement

### System Calls (Linux)
- File operations: open, close, read, write
- Serial configuration: ioctl with termios structures
- Process control: exit, timing

### ARM Assembly Techniques
- Register usage conventions
- Branch and link for subroutines
- Conditional execution
- Memory addressing modes
- Immediate vs. register operands

### Serial Port Programming
- Device file operations (/dev/ttyS0)
- Termios structure manipulation
- Non-blocking I/O
- Buffer management

## File Structure
```
project/
├── src/
│   ├── main.s           # Main assembly source
│   ├── serial_linux.s   # Linux-specific serial functions
│   ├── serial_acorn.s   # Acorn-specific serial functions
│   └── common.s         # Shared utility functions
├── include/
│   ├── linux_syscalls.inc    # Linux system call numbers
│   └── acorn_swi.inc         # Acorn SWI definitions
├── Makefile
├── README.md
└── docs/
    ├── arm_assembly_guide.md
    ├── serial_programming.md
    └── platform_differences.md
```

## Testing Strategy
1. **Unit Testing**: Test individual functions (menu, input, output)
2. **Serial Testing**: Use `minicom` or `screen` to monitor serial output
3. **Loopback Testing**: Connect TX to RX for echo testing
4. **Performance Testing**: Measure timing and throughput
5. **Cross-Platform Testing**: Validate on different ARM variants

## Advanced Features to Consider
- **Interrupt-driven I/O**: Handle serial interrupts in assembly
- **DMA Integration**: Use direct memory access for bulk transfers
- **Protocol Implementation**: Add packet framing and checksums
- **Real-time Timing**: Precise timing loops for baud rate generation

## Learning Resources Needed
- ARM Assembly Language Programming
- Linux system call interface
- Serial communication protocols
- RISC OS programming (for Acorn compatibility)
- Hardware register programming

## Success Criteria
- Compiles and runs native ARM assembly on Raspberry Pi
- Successfully opens and configures serial port
- Transmits data visible on serial monitoring tools
- Clean, well-documented assembly code
- Ready for porting to Acorn platform

## Why This Approach is "Crazy" Good
- **Ultimate Performance**: No compiler overhead, pure machine code
- **Educational**: Deep understanding of ARM architecture and serial communication
- **Authentic**: Similar to how original Acorn software was developed
- **Portable**: ARM assembly works across ARM platforms
- **Impressive**: Hand-coded assembly demonstrates serious programming skills
- **Fun**: Challenge of low-level programming with immediate hardware results

This approach will give you maximum control and performance while providing an excellent learning experience in ARM assembly programming!