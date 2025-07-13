.section __TEXT,__text,regular,pure_instructions
.globl _main
.align 4

_main:
    # macOS x86_64 version - simulate ARM assembly logic
    # Initialize log file
    call init_log
    
    # Log startup message
    lea log_startup(%rip), %rsi
    mov $log_startup_len, %rdx
    call write_log
    
    # Print startup message
    mov $0x2000004, %rax  # sys_write on macOS
    mov $1, %rdi          # stdout
    lea startup_msg(%rip), %rsi
    mov $startup_len, %rdx
    syscall
    
    # Print test message
    mov $0x2000004, %rax  # sys_write on macOS
    mov $1, %rdi          # stdout
    lea test_msg(%rip), %rsi
    mov $test_len, %rdx
    syscall
    
    # Log main loop entry
    lea log_main_loop(%rip), %rsi
    mov $log_main_loop_len, %rdx
    call write_log
    
    # Main menu loop
main_loop:
    # Show menu with logging
    call show_menu
    
    # Get user input
    call get_input
    
    # Process choice (stored in %al)
    cmp $'1', %al
    je option_1
    cmp $'2', %al
    je option_2
    cmp $'3', %al
    je option_3
    cmp $'4', %al
    je option_4
    
    # Invalid choice, loop again
    jmp main_loop
    
option_1:
    # Print test message action
    mov $0x2000004, %rax
    mov $1, %rdi
    lea test_action_msg(%rip), %rsi
    mov $test_action_len, %rdx
    syscall
    jmp main_loop
    
option_2:
    # Print continuous action
    mov $0x2000004, %rax
    mov $1, %rdi
    lea continuous_action_msg(%rip), %rsi
    mov $continuous_action_len, %rdx
    syscall
    jmp main_loop
    
option_3:
    # Custom message - this is where we test the issue
    call send_custom
    jmp main_loop
    
option_4:
    # Log exit
    lea log_exit(%rip), %rsi
    mov $log_exit_len, %rdx
    call write_log
    
    # Exit cleanly
    mov $0x2000001, %rax  # sys_exit on macOS
    mov $0, %rdi          # exit code
    syscall
    
init_log:
    # Open log file for writing
    mov $0x2000005, %rax  # sys_open on macOS
    lea log_file(%rip), %rdi
    mov $0x601, %rsi      # O_WRONLY|O_CREAT|O_APPEND
    mov $0644, %rdx       # File permissions
    syscall
    mov %rax, log_fd(%rip)
    ret
    
write_log:
    # Save registers
    push %rax
    push %rdx
    push %rsi
    push %rdi
    
    # Check if log file is open
    mov log_fd(%rip), %rax
    cmp $0, %rax
    jle write_log_exit
    
    # Write to log file
    mov $0x2000004, %rax  # sys_write on macOS
    mov log_fd(%rip), %rdi
    # rsi and rdx already contain message address and length from caller
    syscall
    
write_log_exit:
    # Restore registers
    pop %rdi
    pop %rsi
    pop %rdx
    pop %rax
    ret
    
show_menu:
    # Log menu display
    lea log_menu(%rip), %rsi
    mov $log_menu_len, %rdx
    call write_log
    
    # Print menu
    mov $0x2000004, %rax  # sys_write on macOS
    mov $1, %rdi          # stdout
    lea menu_msg(%rip), %rsi
    mov $menu_len, %rdx
    syscall
    ret

get_input:
    # Read one character from stdin
    mov $0x2000003, %rax  # sys_read on macOS
    mov $0, %rdi          # stdin
    lea input_char(%rip), %rsi
    mov $1, %rdx          # read 1 character
    syscall
    
    # Load the character into %al for return
    mov input_char(%rip), %al
    ret

send_custom:
    # Print custom message prompt
    mov $0x2000004, %rax
    mov $1, %rdi
    lea custom_prompt(%rip), %rsi
    mov $custom_prompt_len, %rdx
    syscall
    
    # Force flush stdout
    mov $0x2000006, %rax  # sys_close on macOS (substitute for fsync)
    mov $1, %rdi
    syscall
    
    # Read custom message line
    mov $0x2000003, %rax  # sys_read on macOS
    mov $0, %rdi          # stdin
    lea custom_buffer(%rip), %rsi
    mov $255, %rdx        # read up to 255 characters
    syscall
    
    # Check if we got input
    cmp $0, %rax
    jle custom_error
    
    # Print success message
    mov $0x2000004, %rax
    mov $1, %rdi
    lea success_msg(%rip), %rsi
    mov $success_len, %rdx
    syscall
    ret
    
custom_error:
    # Print error message
    mov $0x2000004, %rax
    mov $1, %rdi
    lea error_msg(%rip), %rsi
    mov $error_len, %rdx
    syscall
    ret

.section __TEXT,__cstring,cstring_literals
startup_msg:
    .asciz "Acorn Communication Simulator - ARM Assembly (Mac Simulation)\n"
startup_len = . - startup_msg - 1

test_msg:
    .asciz "TEST: Reached critical section\n"
test_len = . - test_msg - 1

menu_msg:
    .asciz "\n=== Acorn Serial Communication Menu ===\n1. Send test message\n2. Send continuous data\n3. Send custom message\n4. Exit\nSelect option: "
menu_len = . - menu_msg - 1

log_file:
    .asciz "acorn_comm.log"

log_startup:
    .asciz "[STARTUP] Acorn Communication Simulator started\n"
log_startup_len = . - log_startup - 1

log_main_loop:
    .asciz "[DEBUG] Entering main loop\n"
log_main_loop_len = . - log_main_loop - 1

log_menu:
    .asciz "[DEBUG] Showing menu\n"
log_menu_len = . - log_menu - 1

log_exit:
    .asciz "[EXIT] Program terminated normally\n"
log_exit_len = . - log_exit - 1

test_action_msg:
    .asciz "Sending test message...\nMessage sent successfully!\n"
test_action_len = . - test_action_msg - 1

continuous_action_msg:
    .asciz "Sending continuous data...\nMessage sent successfully!\n"
continuous_action_len = . - continuous_action_msg - 1

custom_prompt:
    .asciz "Enter custom message (max 255 chars): "
custom_prompt_len = . - custom_prompt - 1

success_msg:
    .asciz "Message sent successfully!\n"
success_len = . - success_msg - 1

error_msg:
    .asciz "Error: Failed to read input\n"
error_len = . - error_msg - 1

.section __DATA,__data
log_fd:
    .quad 0
    
input_char:
    .byte 0
    
custom_buffer:
    .space 256
