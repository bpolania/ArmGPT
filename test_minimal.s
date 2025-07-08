@ Minimal test version - no logging
.text
.global _start

@ Include system call definitions
.include "linux_syscalls.inc"

@ Data section
.data
test_msg: .ascii "MINIMAL TEST: Program started\n"
test_len = . - test_msg

menu_msg: .ascii "MINIMAL TEST: Menu reached\n"
menu_len = . - menu_msg

@ BSS section
.bss
dummy: .space 4

@ Return to text section
.text

_start:
    @ Print test message
    mov r0, #STDOUT
    ldr r1, =test_msg
    mov r2, #test_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Simulate the problematic section
    @ This is where the hang occurs in the main program
    
    @ Print menu message (this should appear if we get past the hang point)
    mov r0, #STDOUT
    ldr r1, =menu_msg
    mov r2, #menu_len
    mov r7, #SYS_WRITE
    swi 0
    
    @ Exit successfully
    mov r0, #0
    mov r7, #SYS_EXIT
    swi 0