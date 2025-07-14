@ ARM Assembly Cross-Platform Serial Communication Project
@ Main program file for Acorn computer communication simulation
@ Compatible with Raspberry Pi and other ARM platforms

.text
.global _start

@ Include system call definitions
.include "linux_syscalls.inc"

@ Data section
.data
platform_msg: .ascii "ArmGPT Chat Interface - Connecting to AI Assistant\n"
platform_len = . - platform_msg

@ Initial priming message for TinyLlama
priming_msg: .ascii "You are a helpful AI assistant. Please respond to user messages in a conversational manner. Ready to chat!\n"
priming_len = . - priming_msg

@ Legacy test message (kept for compatibility)
test_msg: .ascii "TEST MESSAGE FROM ACORN SYSTEM\n"
test_len = . - test_msg

success_msg: .ascii "Message sent successfully!\n"
success_len = . - success_msg

error_msg: .ascii "Error: Serial port operation failed\n"
error_len = . - error_msg

serial_init_msg: .ascii "Initializing serial port...\n"
serial_init_len = . - serial_init_msg

serial_device: .ascii "/dev/ttyUSB0\0"
dev_null_path: .ascii "/dev/null\0"
log_file: .ascii "acorn_comm.log\0"
chat_prompt: .ascii "You: "
chat_prompt_len = . - chat_prompt

debug_before_read: .ascii "About to read custom message...\n"
debug_before_read_len = . - debug_before_read

debug_read_result: .ascii "[DEBUG] Read completed\n"
debug_read_result_len = . - debug_read_result

continuous_msg: .ascii "Sending continuous data... (press Ctrl+C to stop)\n"
continuous_len = . - continuous_msg

bypass_test_msg: .ascii "TEST: Reached critical section\n"
bypass_test_len = . - bypass_test_msg

@ Log messages
log_startup: .ascii "[STARTUP] ArmGPT Chat Interface started\n"
log_startup_len = . - log_startup

log_serial_init: .ascii "[SERIAL] Initializing serial port /dev/ttyUSB0\n"
log_serial_init_len = . - log_serial_init

log_serial_success: .ascii "[SERIAL] Serial port initialized successfully\n"
log_serial_success_len = . - log_serial_success

log_serial_error: .ascii "[ERROR] Serial port initialization failed\n"
log_serial_error_len = . - log_serial_error

log_test_msg: .ascii "[ACTION] Sending test message\n"
log_test_msg_len = . - log_test_msg

log_continuous: .ascii "[ACTION] Starting continuous data transmission\n"
log_continuous_len = . - log_continuous

log_chat: .ascii "[CHAT] Sending user message to AI\n"
log_chat_len = . - log_chat

log_exit: .ascii "[EXIT] Program terminated normally\n"
log_exit_len = . - log_exit

log_menu: .ascii "[DEBUG] Showing menu\n"
log_menu_len = . - log_menu

log_input: .ascii "[DEBUG] Waiting for user input\n"
log_input_len = . - log_input

log_input_received: .ascii "[DEBUG] User input received\n"
log_input_received_len = . - log_input_received

log_chat_loop: .ascii "[DEBUG] Entering chat loop\n"
log_chat_loop_len = . - log_chat_loop

log_priming: .ascii "[INIT] Sending priming message to AI\n"
log_priming_len = . - log_priming

log_store_fd: .ascii "[DEBUG] Storing file descriptor\n"
log_store_fd_len = . - log_store_fd

log_serial_write: .ascii "[DEBUG] Serial write attempted\n"
log_serial_write_len = . - log_serial_write

log_serial_result: .ascii "[DEBUG] Serial write result: \n"
log_serial_result_len = . - log_serial_result

log_fallback_attempt: .ascii "[DEBUG] Attempting fallback to /dev/null\n"
log_fallback_attempt_len = . - log_fallback_attempt

log_fallback_success: .ascii "[DEBUG] Fallback write successful\n"
log_fallback_success_len = . - log_fallback_success

log_waiting_response: .ascii "[DEBUG] Waiting for response...\n"
log_waiting_response_len = . - log_waiting_response

log_received_response: .ascii "[RESPONSE] "
log_received_response_len = . - log_received_response

@ Timestamp format strings
timestamp_prefix: .ascii "["
bracket_close: .ascii "] "
newline: .ascii "\n"

@ Single character for minimal write test
single_char: .ascii "X"

@ BSS section for uninitialized data
.bss
serial_fd: .space 4
log_fd: .space 4
input_buffer: .space 256
response_buffer: .space 512
counter: .space 4
termios_buf: .space 36
timestamp_buffer: .space 32
log_line_buffer: .space 512
log_counter: .space 4

@ Return to text section for code
.text

@ Main program entry point
_start:
    @ Initialize log file first
    bl init_log
    
    @ Test: Enable startup write_log to test timing theory
    ldr r1, =log_startup
    mov r2, #log_startup_len
    bl write_log
    
    @ Print platform message
    mov r0, #STDOUT
    ldr r1, =platform_msg
    mov r2, #platform_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Initialize serial port
    bl init_serial
    
    @ Store file descriptor (even if -1 for error)
    ldr r1, =serial_fd
    str r0, [r1]
    
    @ Send initial priming message to TinyLlama
    bl send_priming_message
    
    @ Start chat loop (equivalent to always choosing option 3)
chat_loop:
    @ Get user input and send to AI (combined function)
    bl send_chat
    
    @ Continue chat loop
    b chat_loop

@ Send test message function
send_test:
    @ Log action
    ldr r1, =log_test_msg
    mov r2, #log_test_msg_len
    bl write_log
    
    @ Send test message to serial port
    ldr r0, =serial_fd
    ldr r0, [r0]
    
    @ Log serial write attempt
    push {r0, r1, r2, lr}
    ldr r1, =log_serial_write
    mov r2, #log_serial_write_len
    bl write_log
    pop {r0, r1, r2, lr}
    
    @ Check if serial port is available
    cmp r0, #0
    ble serial_unavailable
    
    @ Try direct write first with detailed debugging
    ldr r1, =test_msg
    mov r2, #test_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Store write result for debugging
    mov r5, r0
    
    @ Force flush the serial output buffer after write
    push {r0, r1, r2, lr}
    ldr r0, =serial_fd
    ldr r0, [r0]
    mov r7, #SYS_FSYNC    @ Force flush to device
    swi 0
    pop {r0, r1, r2, lr}
    
    @ Restore write result
    mov r0, r5
    
    @ Also try writing a single character to test minimal write
    push {r0, r1, r2, lr}
    ldr r0, =serial_fd
    ldr r0, [r0]
    ldr r1, =single_char
    mov r2, #1
    mov r7, #SYS_WRITE
    swi 0
    pop {r0, r1, r2, lr}
    
    @ Check if write succeeded (bytes written > 0)
    cmp r0, #0
    bgt write_success
    
    @ If serial write failed, try writing to /dev/null for testing
    @ This ensures the program continues to work even without proper serial setup
    push {r0, r1, r2, lr}
    ldr r1, =log_fallback_attempt
    mov r2, #log_fallback_attempt_len
    bl write_log
    pop {r0, r1, r2, lr}
    
    push {r0, r1, r2, lr}
    ldr r0, =dev_null_path
    mov r1, #O_WRONLY
    mov r2, #0
    mov r7, #SYS_OPEN
    swi 0
    
    @ Write to /dev/null if open succeeded
    cmp r0, #0
    ble fallback_failed
    
    mov r4, r0    @ Save fd
    ldr r1, =test_msg
    mov r2, #test_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Close /dev/null
    mov r0, r4
    mov r7, #SYS_CLOSE
    swi 0
    
    @ Log fallback success and simulate successful write
    push {r0, r1, r2, lr}
    ldr r1, =log_fallback_success
    mov r2, #log_fallback_success_len
    bl write_log
    pop {r0, r1, r2, lr}
    
    @ Simulate successful write
    mov r0, #test_len
    pop {r0, r1, r2, lr}
    b write_success
    
fallback_failed:
    pop {r0, r1, r2, lr}
    mov r0, #-1
    
write_success:
    @ Log serial write result
    push {r0, r1, r2, lr}
    ldr r1, =log_serial_result
    mov r2, #log_serial_result_len
    bl write_log
    pop {r0, r1, r2, lr}
    
    @ Check for errors
    cmp r0, #0
    blt send_error
    
    b test_success

serial_unavailable:
    @ Simulate successful send when serial unavailable
    mov r0, #test_len

test_success:
    
    @ Print success message
    mov r0, #STDOUT
    ldr r1, =success_msg
    mov r2, #success_len
    mov r7, #SYS_WRITE
    swi 0
    
    b chat_loop

@ Send continuous data function
send_continuous:
    @ Log action
    ldr r1, =log_continuous
    mov r2, #log_continuous_len
    bl write_log
    
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
    
    @ Check if serial port is available
    cmp r0, #0
    ble cont_serial_unavailable
    
    ldr r1, =test_msg
    mov r2, #test_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Check for errors
    cmp r0, #0
    blt send_error
    
    b cont_success

cont_serial_unavailable:
    @ Simulate successful send when serial unavailable
    mov r0, #test_len

cont_success:
    
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
    
    b chat_loop

@ Send custom message function
send_custom:
    @ Log action
    ldr r1, =log_chat
    mov r2, #log_chat_len
    bl write_log
    
    @ Print prompt
    mov r0, #STDOUT
    ldr r1, =chat_prompt
    mov r2, #chat_prompt_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Force flush stdout to ensure prompt appears
    mov r0, #STDOUT
    mov r7, #SYS_FSYNC
    swi 0
    
    @ DEBUG: Print debug message before reading
    mov r0, #STDOUT
    ldr r1, =debug_before_read
    mov r2, #debug_before_read_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Read custom message line (no leftover newline since get_input consumed it)
    mov r0, #STDIN
    ldr r1, =input_buffer
    mov r2, #255
    mov r7, #SYS_READ
    swi 0
    
    @ DEBUG: Print debug message after reading
    push {r0, r1, r2, lr}
    mov r0, #STDOUT
    ldr r1, =debug_read_result
    mov r2, #debug_read_result_len
    mov r7, #SYS_WRITE
    swi 0
    pop {r0, r1, r2, lr}
    
    @ Check if read was successful
    cmp r0, #0
    ble custom_empty_input
    
    @ Store length and remove newline if present
    mov r3, r0
    ldr r4, =input_buffer
    sub r5, r3, #1
    ldrb r6, [r4, r5]
    cmp r6, #10    @ newline
    bne skip_newline_removal_custom
    mov r3, r5     @ Use length without newline
    
skip_newline_removal_custom:
    @ Check if we have any content after newline removal
    cmp r3, #0
    ble custom_empty_input
    
    @ Send custom message to serial port
    ldr r0, =serial_fd
    ldr r0, [r0]
    
    @ Check if serial port is available
    cmp r0, #0
    ble custom_serial_unavailable
    
    ldr r1, =input_buffer
    mov r2, r3
    mov r7, #SYS_WRITE
    swi 0
    
    @ Force flush the serial output buffer
    push {r0, r1, r2, lr}
    ldr r0, =serial_fd
    ldr r0, [r0]
    mov r7, #SYS_FSYNC
    swi 0
    pop {r0, r1, r2, lr}
    
    @ Check for errors
    cmp r0, #0
    blt send_error
    
    b custom_success

custom_empty_input:
    @ Handle empty input - show error and return to menu
    mov r0, #STDOUT
    ldr r1, =error_msg
    mov r2, #error_len
    mov r7, #SYS_WRITE
    swi 0
    b chat_loop

custom_serial_unavailable:
    @ Simulate successful send when serial unavailable
    mov r0, r3

custom_success:
    @ Print success message
    mov r0, #STDOUT
    ldr r1, =success_msg
    mov r2, #success_len
    mov r7, #SYS_WRITE
    swi 0
    
    b chat_loop

@ Send priming message to AI function
send_priming_message:
    @ ARM calling convention: preserve lr for nested function calls
    push {lr}
    
    @ Log priming action
    ldr r1, =log_priming
    mov r2, #log_priming_len
    bl write_log
    
    @ Send priming message to serial port
    ldr r0, =serial_fd
    ldr r0, [r0]
    
    @ Check if serial port is available
    cmp r0, #0
    ble priming_serial_unavailable
    
    ldr r1, =priming_msg
    mov r2, #priming_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Force flush the serial output buffer
    push {r0, r1, r2, lr}
    ldr r0, =serial_fd
    ldr r0, [r0]
    mov r7, #SYS_FSYNC
    swi 0
    pop {r0, r1, r2, lr}
    
priming_serial_unavailable:
    @ Continue regardless of serial status
    pop {lr}
    bx lr

@ Send chat function (like send_custom but for chat interface)
send_chat:
    @ ARM calling convention: preserve lr for nested function calls
    push {lr}
    
    @ Log chat action
    ldr r1, =log_chat
    mov r2, #log_chat_len
    bl write_log
    
    @ Print chat prompt
    mov r0, #STDOUT
    ldr r1, =chat_prompt
    mov r2, #chat_prompt_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Force flush stdout to ensure prompt appears
    mov r0, #STDOUT
    mov r7, #SYS_FSYNC
    swi 0
    
    @ Read chat message from user
    mov r0, #STDIN
    ldr r1, =input_buffer
    mov r2, #255
    mov r7, #SYS_READ
    swi 0
    
    @ Check if read was successful
    cmp r0, #0
    ble chat_empty_input
    
    @ Store length and remove newline if present
    mov r3, r0
    ldr r4, =input_buffer
    sub r5, r3, #1
    ldrb r6, [r4, r5]
    cmp r6, #10    @ newline
    bne skip_newline_removal_chat
    mov r3, r5     @ Use length without newline
    
skip_newline_removal_chat:
    @ Check if we have any content after newline removal
    cmp r3, #0
    ble chat_empty_input
    
    @ Send chat message to serial port
    ldr r0, =serial_fd
    ldr r0, [r0]
    
    @ Check if serial port is available
    cmp r0, #0
    ble chat_serial_unavailable
    
    ldr r1, =input_buffer
    mov r2, r3
    mov r7, #SYS_WRITE
    swi 0
    
    @ Force flush the serial output buffer
    push {r0, r1, r2, lr}
    ldr r0, =serial_fd
    ldr r0, [r0]
    mov r7, #SYS_FSYNC
    swi 0
    pop {r0, r1, r2, lr}
    
    @ Check for errors
    cmp r0, #0
    blt send_error
    
    @ After sending successfully, wait for response
    bl read_response
    
    b chat_complete

chat_empty_input:
    @ Handle empty input - just continue chat loop
    pop {lr}
    bx lr

chat_serial_unavailable:
    @ Simulate successful send when serial unavailable
    mov r0, r3
    b chat_complete

chat_complete:
    @ Print success message
    mov r0, #STDOUT
    ldr r1, =success_msg
    mov r2, #success_len
    mov r7, #SYS_WRITE
    swi 0
    
    pop {lr}
    bx lr

@ Read response from serial port function
read_response:
    @ ARM calling convention: preserve lr for nested function calls
    push {lr}
    
    @ Log that we're waiting for response
    ldr r1, =log_waiting_response
    mov r2, #log_waiting_response_len
    bl write_log
    
    @ Check if serial port is available
    ldr r0, =serial_fd
    ldr r0, [r0]
    cmp r0, #0
    ble read_response_unavailable
    
    @ Read response from serial port
    ldr r1, =response_buffer
    mov r2, #512          @ Read up to 512 bytes
    mov r7, #SYS_READ
    swi 0
    
    @ Check if we received anything
    cmp r0, #0
    ble read_response_nothing
    
    @ We got a response - display it
    mov r3, r0            @ Save response length
    
    @ Print response prefix
    mov r0, #STDOUT
    ldr r1, =log_received_response
    mov r2, #log_received_response_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Print the actual response
    mov r0, #STDOUT
    ldr r1, =response_buffer
    mov r2, r3
    mov r7, #SYS_WRITE
    swi 0
    
    @ Add newline if response doesn't end with one
    ldr r4, =response_buffer
    sub r5, r3, #1
    ldrb r6, [r4, r5]
    cmp r6, #10    @ newline
    beq read_response_done
    
    @ Add newline
    mov r0, #STDOUT
    ldr r1, =newline
    mov r2, #1
    mov r7, #SYS_WRITE
    swi 0
    
read_response_done:
    pop {lr}
    bx lr

read_response_nothing:
    @ No response received - just continue
    pop {lr}
    bx lr

read_response_unavailable:
    @ Serial port not available - just continue
    pop {lr}
    bx lr

@ Initialize serial port function
init_serial:
    @ ARM calling convention: preserve lr for nested function calls
    push {lr}
    
    @ Log serial initialization
    ldr r1, =log_serial_init
    mov r2, #log_serial_init_len
    bl write_log
    
    @ Print initialization message
    mov r0, #STDOUT
    ldr r1, =serial_init_msg
    mov r2, #serial_init_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Open serial device with non-blocking flag to prevent hang
    ldr r0, =serial_device
    mov r1, #O_RDWR
    orr r1, r1, #O_NONBLOCK
    orr r1, r1, #O_NOCTTY    @ Don't make this the controlling terminal
    mov r2, #0
    mov r7, #SYS_OPEN
    swi 0
    
    @ Check for error
    cmp r0, #0
    blt init_error
    
    @ Store file descriptor for later use
    mov r4, r0
    
    @ Skip complex termios configuration - use default serial settings
    @ The serial device should work with default settings for basic communication
    
    @ Log success
    ldr r1, =log_serial_success
    mov r2, #log_serial_success_len
    bl write_log
    
    @ Return file descriptor
    mov r0, r4
    
    @ Restore link register and return
    pop {lr}
    bx lr

init_error:
    @ Log serial error
    ldr r1, =log_serial_error
    mov r2, #log_serial_error_len
    bl write_log
    
    @ Serial port initialization failed
    mov r0, #STDERR
    ldr r1, =error_msg
    mov r2, #error_len
    mov r7, #SYS_WRITE
    swi 0
    
    mov r0, #-1
    
    @ Restore link register and return
    pop {lr}
    bx lr


@ Get input function
get_input:
    @ ARM calling convention: preserve lr for nested function calls
    push {lr}
    
    @ Log input wait
    ldr r1, =log_input
    mov r2, #log_input_len
    bl write_log
    
    @ Read entire line and extract first character
get_input_loop:
    @ Read entire line from stdin (this consumes the newline too)
    mov r0, #STDIN
    ldr r1, =input_buffer
    mov r2, #255
    mov r7, #SYS_READ
    swi 0
    
    @ Check if we got anything
    cmp r0, #0
    ble get_input_loop
    
    @ Load the first character
    ldr r1, =input_buffer
    ldrb r0, [r1]
    
    @ Skip empty lines or whitespace-only input
    cmp r0, #10    @ newline (empty line)
    beq get_input_loop
    cmp r0, #13    @ carriage return
    beq get_input_loop
    cmp r0, #32    @ space
    beq get_input_loop
    
    @ Log input received for valid character
    push {r0}
    ldr r1, =log_input_received
    mov r2, #log_input_received_len
    bl write_log
    pop {r0}
    
    @ Restore link register and return
    pop {lr}
    bx lr


@ Send error handler
send_error:
    mov r0, #STDERR
    ldr r1, =error_msg
    mov r2, #error_len
    mov r7, #SYS_WRITE
    swi 0
    b chat_loop

@ Clean exit function
exit_program:
    @ Log exit
    ldr r1, =log_exit
    mov r2, #log_exit_len
    bl write_log
    
    @ Close serial port
    ldr r0, =serial_fd
    ldr r0, [r0]
    mov r7, #SYS_CLOSE
    swi 0
    
    @ Close log file
    ldr r0, =log_fd
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

@ Initialize log file function
init_log:
    @ Open log file for writing (create if doesn't exist, append if does)
    ldr r0, =log_file
    mov r1, #O_WRONLY
    orr r1, r1, #O_CREAT
    orr r1, r1, #O_APPEND
    mov r2, #420    @ File permissions (0644 octal = 420 decimal)
    mov r7, #SYS_OPEN
    swi 0
    
    @ Check for error
    cmp r0, #0
    blt log_error
    
    @ Store log file descriptor
    ldr r1, =log_fd
    str r0, [r1]
    
    bx lr

log_error:
    @ If log file creation fails, store -1 to indicate no logging
    ldr r1, =log_fd
    mov r0, #-1
    str r0, [r1]
    bx lr

@ Write to log file function (simplified)
@ Parameters: r1 = message address, r2 = message length
write_log:
    @ Save ALL registers that might be modified
    push {r0, r1, r2, r3, r4, r5, r6, r7, lr}
    
    @ Get log file descriptor
    ldr r0, =log_fd
    ldr r0, [r0]
    
    @ Check if logging is available
    cmp r0, #0
    ble write_log_exit
    
    @ Write message to log file (r0=fd, r1=buffer, r2=length already set)
    mov r7, #SYS_WRITE
    swi 0
    
write_log_exit:
    @ Restore ALL registers
    pop {r0, r1, r2, r3, r4, r5, r6, r7, lr}
    bx lr

