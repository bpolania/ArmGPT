# Claude Instructions for ArmGPT Project

## STRICT NO ATTRIBUTION POLICY

**ABSOLUTE REQUIREMENT**: Claude must NEVER include any attribution, co-authorship, or reference to AI assistance in ANY file, commit, or contribution to this repository.

### Git Commit Guidelines

When creating git commits for this project:

- **NEVER** include "🤖 Generated with [Claude Code](https://claude.ai/code)" or ANY attribution text
- **NEVER** include "Co-Authored-By: Claude <noreply@anthropic.com>" or ANY co-authorship attributions
- **NEVER** mention AI assistance, Claude, or automated generation in commit messages
- **NEVER** add attribution comments or headers to source files
- Keep commit messages clean and focused on the technical changes
- Use conventional commit format when appropriate
- Focus on the "why" rather than the "what" in commit messages

### File Modification Guidelines

- **NEVER** add attribution comments to source files
- **NEVER** include AI-generated disclaimers in documentation
- **NEVER** reference Claude or AI assistance in README files
- **NEVER** add metadata indicating AI involvement

## Project Context

This is an ARM assembly cross-platform serial communication project that simulates Acorn computer communication. The project is designed to work on both Raspberry Pi (Linux) and Acorn computers (RISC OS).

## Development Notes

- Always test on ARM architecture before committing
- Maintain compatibility with both native and cross-compilation
- Document any changes in CHANGELOG.md
- Follow ARM assembly best practices and conventions

## Development Workflow

**IMPORTANT**: This ARM assembly project must be built and tested on the Raspberry Pi, not on the local development machine.

### Typical Workflow:
1. Make changes to source files locally
2. Commit and push changes to the repository
3. On the Raspberry Pi: `git pull` to get latest changes
4. On the Raspberry Pi: Run `./setup.sh` or `make clean && make` to build
5. On the Raspberry Pi: Test the ARM assembly program with `./acorn_comm`

### Why Pi-based Testing is Required:
- ARM assembly code is architecture-specific
- Serial device paths (`/dev/ttyUSB0`, `/dev/serial0`) only exist on Pi
- System calls and hardware interfaces are Pi-specific
- Build tools and linker behavior may differ between architectures