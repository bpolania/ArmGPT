# ARM Assembly Cross-Platform Serial Communication Project
# Makefile for building on Raspberry Pi and other ARM platforms

TARGET = acorn_comm
SRC_DIR = src
INCLUDE_DIR = include
MAIN_SRC = $(SRC_DIR)/main.s

# Default target for native ARM compilation
all: $(TARGET)

# Native ARM compilation (for Raspberry Pi)
$(TARGET): $(MAIN_SRC)
	@echo "Building native ARM assembly..."
	as -o $(TARGET).o $(MAIN_SRC) -I$(INCLUDE_DIR)
	ld -o $(TARGET) $(TARGET).o

# Cross-compilation target (if needed)
$(TARGET)-cross: $(MAIN_SRC)
	@echo "Cross-compiling for ARM..."
	arm-linux-gnueabihf-as -o $(TARGET).o $(MAIN_SRC) -I$(INCLUDE_DIR)
	arm-linux-gnueabihf-ld -o $(TARGET) $(TARGET).o

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f *.o $(TARGET) $(TARGET)-cross

# Test the program
test: $(TARGET)
	@echo "Running $(TARGET)..."
	./$(TARGET)

# Serial port testing
serial-test: $(TARGET)
	@echo "Testing serial communication..."
	@echo "Starting serial monitor in background..."
	@sudo timeout 10 cat /dev/ttyS0 &
	@sleep 1
	@echo "Running program..."
	./$(TARGET)

# Debug build with symbols
debug: $(MAIN_SRC)
	@echo "Building with debug symbols..."
	as -g -o $(TARGET).o $(MAIN_SRC) -I$(INCLUDE_DIR)
	ld -o $(TARGET) $(TARGET).o

# Check if running on ARM architecture
arch-check:
	@echo "Current architecture: $(shell uname -m)"
	@echo "Checking ARM compatibility..."
	@if [ "$(shell uname -m | grep -E 'arm|aarch')" ]; then \
		echo "✓ ARM architecture detected"; \
	else \
		echo "⚠ Non-ARM architecture - cross-compilation may be needed"; \
	fi

# Install development dependencies (Raspberry Pi)
install-deps:
	@echo "Installing ARM development tools..."
	sudo apt update
	sudo apt install -y build-essential binutils-arm-linux-gnueabihf
	@echo "Development tools installed"

# Enable serial port on Raspberry Pi
enable-serial:
	@echo "Enabling serial port on Raspberry Pi..."
	@echo "Please run: sudo raspi-config"
	@echo "Then: Interface Options -> Serial -> Enable"

# Show available serial devices
show-serial:
	@echo "Available serial devices:"
	@ls -la /dev/tty* | grep -E "(ttyS|ttyUSB|ttyACM)"

# Build with logging
build-log: $(MAIN_SRC)
	@echo "Building with full logging..."
	@echo "Build started at: $(shell date)" > build.log
	as -o $(TARGET).o $(MAIN_SRC) -I$(INCLUDE_DIR) 2>&1 | tee -a build.log
	ld -o $(TARGET) $(TARGET).o 2>&1 | tee -a build.log
	@echo "Build completed at: $(shell date)" >> build.log

# Build with error logging only
build-errors: $(MAIN_SRC)
	@echo "Building with error logging..."
	as -o $(TARGET).o $(MAIN_SRC) -I$(INCLUDE_DIR) 2> errors.log
	ld -o $(TARGET) $(TARGET).o 2>> errors.log
	@if [ -s errors.log ]; then \
		echo "❌ Build errors found in errors.log"; \
		cat errors.log; \
	else \
		echo "✅ Build completed successfully"; \
	fi

# Test minimal version
test-minimal: test_minimal.s
	@echo "Building minimal test..."
	as -o test_minimal.o test_minimal.s -I$(INCLUDE_DIR)
	ld -o test_minimal test_minimal.o
	@echo "Running minimal test..."
	./test_minimal

# Help target
help:
	@echo "Available targets:"
	@echo "  all          - Build native ARM executable"
	@echo "  cross        - Cross-compile for ARM"
	@echo "  build-log    - Build with full logging to build.log"
	@echo "  build-errors - Build with error logging to errors.log"
	@echo "  clean        - Remove build artifacts"
	@echo "  test         - Run the program"
	@echo "  serial-test  - Test with serial monitoring"
	@echo "  debug        - Build with debug symbols"
	@echo "  arch-check   - Check system architecture"
	@echo "  install-deps - Install development tools"
	@echo "  enable-serial- Instructions for enabling serial port"
	@echo "  show-serial  - Show available serial devices"
	@echo "  help         - Show this help message"

.PHONY: all clean test serial-test debug arch-check install-deps enable-serial show-serial help build-log build-errors