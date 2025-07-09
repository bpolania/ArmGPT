#!/bin/bash
# Fix USB Serial Device Permissions
# The issue: /dev/ttyUSB0 is owned by plugdev group, not dialout

echo "=== USB Serial Permission Fix ==="
echo "Issue: /dev/ttyUSB0 requires plugdev group access"
echo ""

# Check current groups
echo "Current user: $(whoami)"
echo "Current groups: $(groups)"
echo ""

# Check device permissions
echo "Current /dev/ttyUSB0 permissions:"
ls -la /dev/ttyUSB0

echo ""
echo "Adding user to plugdev group..."
sudo usermod -a -G plugdev $USER

echo ""
echo "User now in groups:"
groups $USER

echo ""
echo "=== IMPORTANT ==="
echo "You must LOGOUT and LOGIN again for group changes to take effect"
echo "Or run the ARM program with sudo:"
echo "  sudo ./acorn_comm"
echo ""
echo "After logout/login, verify with: groups"
echo "You should see both 'dialout' and 'plugdev' groups"