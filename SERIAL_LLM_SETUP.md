# Serial LLM Interface Setup Guide

This guide helps you set up a Python program that listens to the serial port, processes messages through a local LLM, and sends responses back.

## Two Versions Available

### 1. **Full Version** (`serial_llm_interface.py`)
- Uses Hugging Face Transformers
- Requires 4GB+ RAM
- Better response quality
- Slower on Raspberry Pi

### 2. **Lite Version** (`serial_llm_interface_lite.py`) - Recommended for RPi
- Uses llama-cpp-python with quantized models
- Works with 2GB RAM
- Faster inference
- Slightly reduced quality

## Installation

### For Raspberry Pi (Recommended: Lite Version)

1. **Install system dependencies and create virtual environment:**
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-dev python3-venv

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements-lite.txt
```

2. **Download the quantized model:**
```bash
chmod +x download_model.sh
./download_model.sh
```

3. **Enable serial port on Raspberry Pi:**
```bash
# Add to /boot/config.txt:
enable_uart=1

# Disable console on serial:
sudo systemctl disable serial-getty@ttyS0.service
```

4. **Run the program:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the program
python serial_llm_interface_lite.py --model models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

### For Systems with More RAM (Full Version)

1. **Create virtual environment and install dependencies:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Run the program:**
```bash
python serial_llm_interface.py
```

## Configuration

### Serial Port Settings
- Default port: `/dev/ttyUSB0` (Raspberry Pi)
- Default baudrate: 115200
- 8 data bits, no parity, 1 stop bit

### Customize Settings

For lite version:
```bash
python serial_llm_interface_lite.py --port /dev/ttyUSB0 --baudrate 9600 --model path/to/model.gguf
```

For full version, edit the main() function in the script.

## Usage

1. Connect your serial device to the Raspberry Pi
2. Run the program
3. Send messages via serial (terminated with newline)
4. Receive AI responses back through serial
5. Check logs in the `logs/` directory for debugging

## Logging

Both versions automatically create timestamped log files in the `logs/` directory:
- Log files are named: `serial_llm_YYYYMMDD_HHMMSS.log`
- Logs include all messages, responses, errors, and session statistics
- Logs are written to both console and file simultaneously
- Session summary shows total messages processed and error count

## Troubleshooting

### Permission Denied on Serial Port
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

### Out of Memory
- Use the lite version
- Try a smaller quantized model (Q3_K_S instead of Q4_K_M)
- Reduce context window in the code

### Slow Response Time
- This is normal on Raspberry Pi
- Consider using a more powerful board or the lite version
- Reduce max_tokens for shorter responses

## Model Recommendations

For Raspberry Pi 4 (4GB):
- TinyLlama Q4_K_M (best balance)
- TinyLlama Q3_K_S (if memory constrained)

For Raspberry Pi 4 (8GB):
- Can try the full version with TinyLlama
- Or use larger quantized models with lite version

## Testing

Test without hardware using socat:
```bash
# Terminal 1:
socat -d -d pty,raw,echo=0 pty,raw,echo=0

# Terminal 2 (use the first PTY path from socat):
source venv/bin/activate
python serial_llm_interface_lite.py --port /dev/pts/X

# Terminal 3 (use the second PTY path):
screen /dev/pts/Y 115200
```