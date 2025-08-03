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

1. **Install dependencies:**
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-dev
pip3 install -r requirements-lite.txt
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
python3 serial_llm_interface_lite.py --model models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

### For Systems with More RAM (Full Version)

1. **Install dependencies:**
```bash
pip3 install -r requirements.txt
```

2. **Run the program:**
```bash
python3 serial_llm_interface.py
```

## Configuration

### Serial Port Settings
- Default port: `/dev/serial0` (Raspberry Pi)
- Default baudrate: 115200
- 8 data bits, no parity, 1 stop bit

### Customize Settings

For lite version:
```bash
python3 serial_llm_interface_lite.py --port /dev/ttyUSB0 --baudrate 9600 --model path/to/model.gguf
```

For full version, edit the main() function in the script.

## Usage

1. Connect your serial device to the Raspberry Pi
2. Run the program
3. Send messages via serial (terminated with newline)
4. Receive AI responses back through serial

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
python3 serial_llm_interface_lite.py --port /dev/pts/X

# Terminal 3 (use the second PTY path):
screen /dev/pts/Y 115200
```