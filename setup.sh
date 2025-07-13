#!/bin/bash
# ArmGPT Setup Script - First-time and reset setup for ARM assembly serial communication
# Run this script before using ./acorn_comm

set -e  # Exit on any error

echo "=== ArmGPT Setup Script ==="
echo "Setting up ARM Assembly Serial Communication Project"
echo ""

# Function to check if running on Raspberry Pi
check_platform() {
    if [[ $(uname -m) != arm* ]] && [[ $(uname -m) != aarch64 ]]; then
        echo "⚠️  Warning: Not running on ARM architecture ($(uname -m))"
        echo "   This setup is optimized for Raspberry Pi"
        echo "   Continue anyway? (y/n)"
        read -r response
        if [[ ! $response =~ ^[Yy]$ ]]; then
            echo "Setup cancelled"
            exit 1
        fi
    else
        echo "✓ Running on ARM architecture: $(uname -m)"
    fi
}

# Function to check UART configuration
check_uart() {
    echo ""
    echo "=== UART Configuration Check ==="
    
    if [ -e "/dev/serial0" ]; then
        echo "✓ /dev/serial0 exists"
    else
        echo "✗ /dev/serial0 not found"
        echo ""
        echo "UART needs to be enabled:"
        echo "1. Run: sudo raspi-config"
        echo "2. Go to: Interface Options → Serial Port"
        echo "3. Enable serial port hardware"
        echo "4. Reboot the Pi"
        echo ""
        echo "Would you like to open raspi-config now? (y/n)"
        read -r response
        if [[ $response =~ ^[Yy]$ ]]; then
            sudo raspi-config
            echo ""
            echo "After enabling UART, please reboot and run this setup again"
            exit 1
        fi
    fi
}

# Function to check user permissions
check_permissions() {
    echo ""
    echo "=== User Permissions Check ==="
    
    current_user=$(whoami)
    echo "Current user: $current_user"
    
    if groups | grep -q dialout; then
        echo "✓ User is in dialout group"
    else
        echo "✗ User is NOT in dialout group"
        echo ""
        echo "Adding user to dialout group for serial port access..."
        sudo usermod -a -G dialout $current_user
        echo "✓ Added $current_user to dialout group"
        echo ""
        echo "⚠️  IMPORTANT: You must logout and login again for this to take effect"
        echo "   After logging back in, run this setup script again"
        echo ""
        echo "Logout now? (y/n)"
        read -r response
        if [[ $response =~ ^[Yy]$ ]]; then
            echo "Logging out..."
            sleep 2
            pkill -KILL -u $current_user
        else
            echo "Please logout and login manually, then run setup again"
            exit 1
        fi
    fi
}

# Function to detect USB serial devices
check_usb_serial() {
    echo ""
    echo "=== USB Serial Device Detection ==="
    
    # Run the detection script
    if [ -f "./scripts/detect-usb-serial.sh" ]; then
        echo "Running USB serial detection..."
        ./scripts/detect-usb-serial.sh
    else
        echo "⚠️  USB detection script not found"
        echo "   Checking manually..."
        
        found=false
        for device in /dev/ttyUSB* /dev/ttyACM*; do
            if [ -e "$device" ]; then
                echo "✓ Found USB serial device: $device"
                found=true
            fi
        done
        
        if [ "$found" = false ]; then
            echo "✗ No USB serial devices found"
            echo "   If using USB serial cable, check connections"
        fi
    fi
}

# Function to clean and build the project
build_project() {
    echo ""
    echo "=== Project Build ==="
    
    echo "🧹 Cleaning previous build..."
    make clean 2>/dev/null || echo "No previous build to clean"
    
    echo "🗑️  Removing old logs..."
    rm -f build.log acorn_comm.log
    
    echo "🔨 Building ARM assembly program..."
    if make build-log; then
        echo "✅ Build completed successfully"
        
        if [ -f "build.log" ]; then
            if grep -q "Error:" build.log; then
                echo "❌ Build errors found in build.log:"
                grep "Error:" build.log
                exit 1
            else
                echo "✓ No build errors detected"
            fi
        fi
        
        if [ -f "acorn_comm" ]; then
            echo "✓ acorn_comm binary created"
            ls -la acorn_comm
        else
            echo "❌ acorn_comm binary not found after build"
            exit 1
        fi
    else
        echo "❌ Build failed"
        if [ -f "build.log" ]; then
            echo "Check build.log for details:"
            tail -10 build.log
        fi
        exit 1
    fi
}

# Function to verify everything is ready
verify_setup() {
    echo ""
    echo "=== Setup Verification ==="
    
    checks_passed=0
    total_checks=4
    
    # Check 1: Binary exists
    if [ -f "acorn_comm" ]; then
        echo "✓ acorn_comm binary exists"
        ((checks_passed++))
    else
        echo "✗ acorn_comm binary missing"
    fi
    
    # Check 2: Binary is executable
    if [ -x "acorn_comm" ]; then
        echo "✓ acorn_comm is executable"
        ((checks_passed++))
    else
        echo "✗ acorn_comm is not executable"
        chmod +x acorn_comm 2>/dev/null && echo "  Fixed: Made executable" || echo "  Failed to make executable"
    fi
    
    # Check 3: User in dialout group
    if groups | grep -q dialout; then
        echo "✓ User has serial port permissions"
        ((checks_passed++))
    else
        echo "✗ User not in dialout group"
    fi
    
    # Check 4: Some serial device exists
    if [ -e "/dev/serial0" ] || [ -e "/dev/ttyUSB0" ] || [ -e "/dev/ttyACM0" ]; then
        echo "✓ Serial device available"
        ((checks_passed++))
    else
        echo "✗ No serial devices found"
    fi
    
    echo ""
    echo "Setup verification: $checks_passed/$total_checks checks passed"
    
    if [ $checks_passed -eq $total_checks ]; then
        echo "🎉 Setup complete! Ready to run ./acorn_comm"
        return 0
    else
        echo "⚠️  Setup incomplete. Address the issues above before running ./acorn_comm"
        return 1
    fi
}

# Main setup flow
main() {
    echo "Starting setup process..."
    
    # Check if we're on the right platform
    check_platform
    
    # Check UART configuration
    check_uart
    
    # Check user permissions
    check_permissions
    
    # Detect USB serial devices
    check_usb_serial
    
    # Build the project
    build_project
    
    # Verify everything is ready
    if verify_setup; then
        echo ""
        echo "=== Next Steps ==="
        echo "1. Run: ./acorn_comm"
        echo "2. Or use test script: ./scripts/test-dual-pi.sh"
        echo "3. Check logs in acorn_comm.log for debugging"
        echo ""
        echo "For dual Pi testing:"
        echo "- Run ./scripts/test-listener.sh on receiver Pi"
        echo "- Run ./scripts/test-dual-pi.sh on sender Pi"
    else
        echo ""
        echo "Setup needs attention before proceeding."
        exit 1
    fi
}

# Run main function
main