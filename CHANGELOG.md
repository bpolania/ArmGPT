# Changelog

All notable changes to the ARM Assembly Cross-Platform Serial Communication Project will be documented in this file.

## [Unreleased]

### Added
- Complete ARM assembly program for Acorn computer simulation
- Menu-driven interface with 4 options:
  - Send test message
  - Send continuous data (10 iterations with timing loops)
  - Send custom message input
  - Clean exit with serial port closure
- Full serial port initialization and configuration using Linux syscalls
- Comprehensive error handling and status reporting
- Build system with Makefile supporting:
  - Native ARM compilation
  - Cross-compilation for ARM targets
  - Debug builds with symbols
  - Serial testing utilities
  - Architecture checking
- Linux system call definitions and constants (linux_syscalls.inc)
- Project documentation and usage instructions
- Proper project structure with src/, include/, docs/ directories

### Technical Implementation
- Direct Linux syscall interface for maximum performance
- IOCTL-based serial port configuration (9600 baud, 8N1)
- ARM register usage following AAPCS conventions
- Efficient memory management with minimal footprint
- Conditional execution using ARM-specific features

### Files Added
- `src/main.s` - Main ARM assembly source code
- `include/linux_syscalls.inc` - System call definitions
- `Makefile` - Build configuration and testing targets
- `docs/README.md` - Complete project documentation
- `CLAUDE.md` - Development instructions and guidelines
- `CHANGELOG.md` - This changelog file

## [0.1.0] - Initial Release

### Added
- Initial project structure
- Basic project brief and specifications