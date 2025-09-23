# ArmGPT - Friendly AI Assistant for Acorn Computers

ArmGPT is a gentle and amicable AI assistant that connects to Acorn computers via serial port. Running on a Raspberry Pi, it provides intelligent responses using **ChatGPT when online** or **local TinyLlama when offline** - the best of both worlds!

## Overview

**Serial LLM Interface Lite** (`serial_llm_interface_lite.py`) - Optimized for Raspberry Pi:
- Uses llama-cpp-python with quantized models
- Works on devices with only 2GB RAM
- Faster inference with good quality responses
- Specifically designed for edge devices

## Key Features

- **Hybrid AI System**: ChatGPT API when online, TinyLlama when offline
- **Smart Fallback**: Automatically switches between online/offline modes
- **Real-time Connectivity**: Checks internet status for each query
- Listens on ttyUSB0 port (configurable)
- Robust error handling with comprehensive logging
- Automatic log file creation with timestamps
- Session summary with message and error counts
- Configurable baud rate and port settings
- Response timing for performance monitoring

## Quick Start

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-lite.txt

# Download the quantized TinyLlama model (for offline use)
./download_model.sh

# Set up OpenAI API key (for online ChatGPT - optional)
cp .env.example .env
# Edit .env and add your OpenAI API key

# Run with ChatGPT integration
python serial_llm_interface_lite.py --model models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf --openai-key your_api_key

# Or run with environment variable
export OPENAI_API_KEY=your_api_key_here
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