# ArmGPT - Friendly AI Assistant for Acorn Computers

ArmGPT is a gentle and amicable AI assistant that connects to Acorn computers via serial port. Running on a Raspberry Pi, it provides friendly, knowledgeable responses to Acorn computer enthusiasts.

## Overview

**ArmGPT Server** (`arm_gpt_server.py`) - The recommended way to run ArmGPT:
- Simple `usb` or `serial` argument to select your serial port
- Uses Ollama for local LLM inference (chat + embeddings)
- RAG pipeline grounded in ARM history documentation
- Conversational messages (greetings, thanks) bypass RAG for snappy replies

**Serial LLM Interface Lite** (`serial_llm_interface_lite.py`) - Legacy interface:
- Uses llama-cpp-python with quantized models
- Works on devices with only 2GB RAM
- Faster inference with good quality responses
- Specifically designed for edge devices

## Key Features

- Listens on ttyUSB0 port (configurable)
- Processes messages through Ollama (local LLM)
- RAG-grounded answers from ARM documentation
- Sends AI-generated responses back via serial
- Robust error handling with comprehensive logging
- Automatic log file creation with timestamps
- Session summary with message and error counts
- Configurable baud rate and port settings

## Quick Start

### 1. Install Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull the required models

```bash
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
```

### 3. Set up the Python environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-lite.txt
```

### 4. Build the vector index

```bash
python build_index.py
```

This reads the `.txt` files in `data/arm_docs/` and writes `data/arm_index.jsonl`.

### 5. Run the server

```bash
# Run with USB-to-serial adapter (/dev/ttyUSB0)
python arm_gpt_server.py usb

# Or run with Raspberry Pi GPIO serial (/dev/serial0)
python arm_gpt_server.py serial
```

### Legacy interface

```bash
python serial_llm_interface_lite.py --model models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

## Requirements

- Raspberry Pi (2GB+ RAM) or any machine that can run Ollama
- Python 3.7+
- Ollama installed and running
- Serial port enabled on Raspberry Pi

## Configuration

### arm_gpt_server.py

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `usb` or `serial` | Yes | — | `usb` = `/dev/ttyUSB0`, `serial` = `/dev/serial0` |
| `--baudrate` | No | `9600` | Baud rate for serial communication |
| `--chat-model` | No | `qwen2.5:1.5b` | Ollama chat model name |
| `--embed-model` | No | `nomic-embed-text` | Ollama embedding model name |
| `--ollama-url` | No | `http://localhost:11434` | Ollama API base URL |
| `--index` | No | `data/arm_index.jsonl` | Path to JSONL vector index |

```bash
python arm_gpt_server.py usb --baudrate 115200 --chat-model qwen2.5:1.5b
python arm_gpt_server.py serial --chat-model llama3.2:1b --embed-model nomic-embed-text
```

### build_index.py

| Argument | Default | Description |
|----------|---------|-------------|
| `--docs-dir` | `data/arm_docs` | Directory containing `.txt` source documents |
| `--output` | `data/arm_index.jsonl` | Output JSONL index path |
| `--embed-model` | `nomic-embed-text` | Ollama embedding model name |
| `--ollama-url` | `http://localhost:11434` | Ollama API base URL |

### serial_llm_interface_lite.py (legacy)

Default settings:
- Port: `/dev/ttyUSB0`
- Baudrate: 115200
- Model: TinyLlama 1.1B (quantized)

```bash
python serial_llm_interface_lite.py --port /dev/ttyUSB0 --baudrate 9600 --model path/to/model.gguf
```

## Setup Details

For detailed setup instructions, troubleshooting, and advanced configuration, see [SERIAL_LLM_SETUP.md](SERIAL_LLM_SETUP.md).
