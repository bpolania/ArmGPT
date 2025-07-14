@ Linux System Call Numbers for ARM Assembly
@ ARM Assembly Cross-Platform Serial Communication Project

@ File operations
.equ SYS_READ,      3
.equ SYS_WRITE,     4
.equ SYS_OPEN,      5
.equ SYS_CLOSE,     6
.equ SYS_FSYNC,     118
.equ SYS_IOCTL,     54

@ Process control
.equ SYS_EXIT,      1
.equ SYS_FORK,      2
.equ SYS_GETPID,    20
.equ SYS_WAITPID,   7
.equ SYS_KILL,      37

@ Signal handling
.equ SYS_SIGNAL,    48
.equ SIGCHLD,       17
.equ SIGUSR1,       10

@ Time operations
.equ SYS_TIME,      13
.equ SYS_NANOSLEEP, 162

@ Memory operations
.equ SYS_BRK,       45
.equ SYS_MMAP,      90

@ File descriptors
.equ STDIN,         0
.equ STDOUT,        1
.equ STDERR,        2

@ File access modes
.equ O_RDONLY,      0
.equ O_WRONLY,      1
.equ O_RDWR,        2
.equ O_CREAT,       64
.equ O_EXCL,        128
.equ O_NOCTTY,      256
.equ O_TRUNC,       512
.equ O_APPEND,      1024
.equ O_NONBLOCK,    2048

@ IOCTL commands for serial port configuration
.equ TCGETS,        0x5401
.equ TCSETS,        0x5402
.equ TCSETSW,       0x5403
.equ TCSETSF,       0x5404

@ Termios flags
.equ IGNBRK,        0x00000001
.equ BRKINT,        0x00000002
.equ IGNPAR,        0x00000004
.equ PARMRK,        0x00000008
.equ INPCK,         0x00000010
.equ ISTRIP,        0x00000020
.equ INLCR,         0x00000040
.equ IGNCR,         0x00000080
.equ ICRNL,         0x00000100

@ Baud rates
.equ B9600,         0x0000000D
.equ B19200,        0x0000000E
.equ B38400,        0x0000000F
.equ B57600,        0x00001001
.equ B115200,       0x00001002

@ Character sizes
.equ CS5,           0x00000000
.equ CS6,           0x00000010
.equ CS7,           0x00000020
.equ CS8,           0x00000030

@ Error codes
.equ EBADF,         9
.equ EINVAL,        22
.equ ENOTTY,        25
