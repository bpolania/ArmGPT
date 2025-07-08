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
  - Build logging with `build-log` and `build-errors` targets
- Linux system call definitions and constants (linux_syscalls.inc)
- Project documentation and usage instructions
- Proper project structure with src/, include/, docs/ directories
- Comprehensive logging system to `acorn_comm.log`
- Utility scripts for development workflow:
  - `git-update.sh` - Automated git add, commit, and push
  - `clean-build.sh` - Clean rebuild with logging and log cleanup
- Robust error handling and fallback mode for serial operations
- Debug logging for program flow tracking

### Technical Implementation
- Direct Linux syscall interface for maximum performance
- IOCTL-based serial port configuration (9600 baud, 8N1)
- ARM register usage following AAPCS conventions
- Efficient memory management with minimal footprint
- Conditional execution using ARM-specific features
- File-based logging with proper permissions handling
- Graceful degradation when serial hardware unavailable
- Safe fallback to `/dev/null` for testing without serial ports

### Bug Fixes
- Fixed BSS section errors by properly separating data and code sections
- Corrected ARM immediate value limitations using `ldr` instead of `mov`
- Fixed file permissions format (octal to decimal conversion)
- Added missing newlines to assembly files to prevent assembler warnings
- Implemented robust serial port error handling to prevent infinite loops
- Added serial availability checks in all communication functions
- **CRITICAL FIX**: Resolved program hang caused by register corruption in write_log function
- Fixed register preservation to save all modified registers in logging functions
- Implemented pinpoint debugging to isolate exact hang location
- Removed complex timestamp system that was causing instability

### Files Added
- `src/main.s` - Main ARM assembly source code
- `include/linux_syscalls.inc` - System call definitions
- `Makefile` - Build configuration and testing targets
- `docs/README.md` - Complete project documentation
- `CLAUDE.md` - Development instructions and guidelines
- `CHANGELOG.md` - This changelog file
- `git-update.sh` - Git workflow automation script
- `clean-build.sh` - Clean build and logging script

### Development Workflow Improvements
- Enhanced Makefile with comprehensive build targets
- Automated logging and error tracking
- Git workflow scripts for rapid development
- Debug logging system for troubleshooting
- Clean build process with log management
- Pinpoint debugging methodology for isolating program hangs
- Systematic debugging approach with sequential log tracking
- Register corruption analysis and ARM assembly debugging techniques

## [0.2.0] - 2025-07-08 - Production Ready Release

### Major Features
- Fully functional ARM assembly serial communication program
- Comprehensive logging and debugging system
- Robust error handling and fallback mechanisms
- Complete development workflow with automation scripts

### Highlights
- Native ARM assembly implementation
- Cross-platform compatibility (Raspberry Pi focus)
- Professional development practices with comprehensive testing
- Complete documentation and setup instructions

## [0.1.0] - Initial Release

### Added
- Initial project structure
- Basic project brief and specifications