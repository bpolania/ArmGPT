@ ARM Assembly Cross-Platform Serial Communication Project
@ Main program file for Acorn computer communication simulation
@ Compatible with Raspberry Pi and other ARM platforms

.text
.global _start

@ Include system call definitions
.include "linux_syscalls.inc"

@ Data section
.data
platform_msg: .ascii "Acorn Communication Simulator - ARM Assembly\n"
platform_len = . - platform_msg

menu_msg: .ascii "\n=== Acorn Serial Communication Menu ===\n1. Send test message\n2. Send continuous data\n3. Send custom message\n4. Exit\nSelect option: "
menu_len = . - menu_msg

test_msg: .ascii "TEST MESSAGE FROM ACORN SYSTEM\n"
test_len = . - test_msg

success_msg: .ascii "Message sent successfully!\n"
success_len = . - success_msg

error_msg: .ascii "Error: Serial port operation failed\n"
error_len = . - error_msg

serial_init_msg: .ascii "Initializing serial port...\n"
serial_init_len = . - serial_init_msg

serial_device: .ascii "/dev/ttyS0\0"
custom_prompt: .ascii "Enter custom message (max 255 chars): "
custom_prompt_len = . - custom_prompt

continuous_msg: .ascii "Sending continuous data... (press Ctrl+C to stop)\n"
continuous_len = . - continuous_msg

@ BSS section for uninitialized data
.bss
serial_fd: .space 4
input_buffer: .space 256
counter: .space 4
termios_buf: .space 36

@ Main program entry point
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
    
    @ Store file descriptor
    ldr r1, =serial_fd
    str r0, [r1]
    
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

@ Send test message function
send_test:
    @ Send test message to serial port
    ldr r0, =serial_fd
    ldr r0, [r0]
    ldr r1, =test_msg
    mov r2, #test_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Check for errors
    cmp r0, #0
    blt send_error
    
    @ Print success message
    mov r0, #STDOUT
    ldr r1, =success_msg
    mov r2, #success_len
    mov r7, #SYS_WRITE
    swi 0
    
    b main_loop

@ Send continuous data function
send_continuous:
    @ Print continuous message
    mov r0, #STDOUT
    ldr r1, =continuous_msg
    mov r2, #continuous_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Initialize counter
    ldr r4, =counter
    mov r5, #0
    str r5, [r4]
    
continuous_loop:
    @ Send test message
    ldr r0, =serial_fd
    ldr r0, [r0]
    ldr r1, =test_msg
    mov r2, #test_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Check for errors
    cmp r0, #0
    blt send_error
    
    @ Increment counter
    ldr r4, =counter
    ldr r5, [r4]
    add r5, r5, #1
    str r5, [r4]
    
    @ Simple delay loop
    ldr r6, =1000000
delay_loop:
    subs r6, r6, #1
    bne delay_loop
    
    @ Check if we should continue (simplified - just loop for now)
    @ In a real implementation, you'd check for interrupts or user input
    cmp r5, #10  @ Send 10 messages then stop
    blt continuous_loop
    
    b main_loop

@ Send custom message function
send_custom:
    @ Print prompt
    mov r0, #STDOUT
    ldr r1, =custom_prompt
    mov r2, #custom_prompt_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Read custom message
    mov r0, #STDIN
    ldr r1, =input_buffer
    mov r2, #255
    mov r7, #SYS_READ
    swi 0
    
    @ Store length
    mov r3, r0
    
    @ Send custom message to serial port
    ldr r0, =serial_fd
    ldr r0, [r0]
    ldr r1, =input_buffer
    mov r2, r3
    mov r7, #SYS_WRITE
    swi 0
    
    @ Check for errors
    cmp r0, #0
    blt send_error
    
    @ Print success message
    mov r0, #STDOUT
    ldr r1, =success_msg
    mov r2, #success_len
    mov r7, #SYS_WRITE
    swi 0
    
    b main_loop

@ Initialize serial port function
init_serial:
    @ Print initialization message
    mov r0, #STDOUT
    ldr r1, =serial_init_msg
    mov r2, #serial_init_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Open serial device
    ldr r0, =serial_device
    mov r1, #O_RDWR
    mov r2, #0
    mov r7, #SYS_OPEN
    swi 0
    
    @ Check for error
    cmp r0, #0
    blt init_error
    
    @ Store file descriptor for later use
    mov r4, r0
    
    @ Get current termios settings
    mov r0, r4
    mov r1, #TCGETS
    ldr r2, =termios_buf
    mov r7, #SYS_IOCTL
    swi 0
    
    @ Configure serial port settings
    @ This is a simplified version - in practice you'd modify specific bits
    ldr r1, =termios_buf
    
    @ Set baud rate to 9600
    ldr r2, =B9600
    str r2, [r1, #8]    @ c_cflag offset
    
    @ Set 8N1 (8 data bits, no parity, 1 stop bit)
    ldr r2, [r1, #8]
    orr r2, r2, #CS8
    str r2, [r1, #8]
    
    @ Apply settings
    mov r0, r4
    mov r1, #TCSETS
    ldr r2, =termios_buf
    mov r7, #SYS_IOCTL
    swi 0
    
    @ Return file descriptor
    mov r0, r4
    bx lr

init_error:
    @ Serial port initialization failed
    mov r0, #STDERR
    ldr r1, =error_msg
    mov r2, #error_len
    mov r7, #SYS_WRITE
    swi 0
    
    mov r0, #-1
    bx lr

@ Show menu function
show_menu:
    mov r0, #STDOUT
    ldr r1, =menu_msg
    mov r2, #menu_len
    mov r7, #SYS_WRITE
    swi 0
    bx lr

@ Get input function
get_input:
    @ Read single character from stdin
    mov r0, #STDIN
    ldr r1, =input_buffer
    mov r2, #1
    mov r7, #SYS_READ
    swi 0
    
    @ Load the character
    ldr r1, =input_buffer
    ldrb r0, [r1]
    bx lr

@ Send error handler
send_error:
    mov r0, #STDERR
    ldr r1, =error_msg
    mov r2, #error_len
    mov r7, #SYS_WRITE
    swi 0
    b main_loop

@ Clean exit function
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

@ Error exit function
exit_error:
    mov r0, #STDERR
    ldr r1, =error_msg
    mov r2, #error_len
    mov r7, #SYS_WRITE
    swi 0
    
    mov r0, #1
    mov r7, #SYS_EXIT
    swi 0
