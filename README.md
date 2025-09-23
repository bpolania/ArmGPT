# ArmGPT - Friendly AI Assistant for Acorn Computers

ArmGPT is a gentle and amicable AI assistant that connects to Acorn computers via serial port. Running on a Raspberry Pi, it provides friendly, knowledgeable responses to Acorn computer enthusiasts.

## Overview

**Serial LLM Interface Lite** (`serial_llm_interface_lite.py`) - Optimized for Raspberry Pi:
- Uses llama-cpp-python with quantized models
- Works on devices with only 2GB RAM
- Faster inference with good quality responses
- Specifically designed for edge devices

## Key Features

- Listens on ttyUSB0 port (configurable)
- Processes messages through local TinyLlama model
- Sends AI-generated responses back via serial
- Robust error handling with comprehensive logging
- Automatic log file creation with timestamps
- Session summary with message and error counts
- Configurable baud rate and port settings

## Quick Start

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-lite.txt

# Download the quantized TinyLlama model
./download_model.sh

# Run the interface
python serial_llm_interface_lite.py --model models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

## Requirements

- Raspberry Pi (2GB+ RAM)
- Python 3.7+
- Serial port enabled on Raspberry Pi

## Configuration

Default settings:
- Port: `/dev/ttyUSB0`
- Baudrate: 115200
- Model: TinyLlama 1.1B (quantized)

Custom configuration:
```bash
python serial_llm_interface_lite.py --port /dev/ttyUSB0 --baudrate 9600 --model path/to/model.gguf
```

## Why TinyLlama?

The lite version uses quantized models (GGUF format) which are much more efficient on Raspberry Pi hardware. TinyLlama is recommended as it's specifically designed for edge devices while still providing good quality responses.

## Setup Details

For detailed setup instructions, troubleshooting, and advanced configuration, see [SERIAL_LLM_SETUP.md](SERIAL_LLM_SETUP.md).