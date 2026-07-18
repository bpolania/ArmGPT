# Serial Interface Setup Guide

This guide covers the serial side of ArmGPT and the available AI backends.

## Choose A Backend

| Backend | Script | Install profile |
|---------|--------|-----------------|
| Ollama with RAG | `arm_gpt_server.py` | `requirements-lite.txt`, Ollama, `qwen2.5:1.5b`, `nomic-embed-text` |
| Codex CLI | `serial_codex_interface.py` | `requirements-lite.txt`, installed and logged-in Codex CLI |
| llama-cpp legacy | `serial_llm_interface_lite.py` | `pyserial`, `llama-cpp-python`, local GGUF model |
| Transformers legacy | `serial_llm_interface.py` | `requirements.txt`, enough RAM for Transformers |

Use the Ollama backend for local RAG-grounded answers. Use the Codex CLI backend when you want to reuse a Codex CLI session instead of running a local model.

## Serial Port Setup

### Raspberry Pi UART

Enable UART in `/boot/config.txt`:

```bash
enable_uart=1
```

Disable the login console on the serial port if needed:

```bash
sudo systemctl disable serial-getty@ttyS0.service
```

### Permissions

If opening the serial port fails with a permission error:

```bash
sudo usermod -a -G dialout $USER
```

Log out and back in after changing groups.

### Defaults

- USB serial adapter: `/dev/ttyUSB0`
- Raspberry Pi GPIO serial: `/dev/serial0`
- Baud rate used by the scripts: `9600`
- Serial framing: 8 data bits, no parity, 1 stop bit

## Ollama Backend

Install Python dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-lite.txt
```

Prepare Ollama:

```bash
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
python build_index.py
```

Run:

```bash
python arm_gpt_server.py usb
python arm_gpt_server.py serial
```

The generated RAG index is `data/arm_index.jsonl`. If the index is missing, the server still runs, but ARM documentation retrieval will be unavailable.

## Codex CLI Backend

Install Python dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-lite.txt
```

Verify Codex:

```bash
codex --version
codex doctor
```

Run:

```bash
python serial_codex_interface.py --port /dev/ttyUSB0 --baudrate 9600
```

If Codex is not on `PATH`:

```bash
python serial_codex_interface.py --codex-command /path/to/codex
```

Useful options:

```bash
python serial_codex_interface.py --port /dev/serial0
python serial_codex_interface.py --codex-model gpt-5 --timeout 240
python serial_codex_interface.py --codex-cwd /path/to/ArmGPT
python serial_codex_interface.py --docs-dir data/arm_docs --top-k 4 --max-context-chars 3600
```

Behavior notes:

- The script calls `codex exec` once per serial message.
- Codex receives an ArmGPT personality prompt plus the user message.
- The prompt includes lightweight retrieved context from `data/arm_docs/*.txt`.
- Codex is invoked with `--sandbox read-only`, `--ask-for-approval never`, and `--ephemeral`.
- The script captures Codex's final answer with `--output-last-message`.
- This backend depends on the host's Codex CLI login and availability.

## Legacy llama-cpp Backend

Use this for a fully offline GGUF model:

```bash
python3 -m venv venv
source venv/bin/activate
pip install pyserial llama-cpp-python
chmod +x download_model.sh
./download_model.sh
python serial_llm_interface_lite.py --port /dev/ttyUSB0 --baudrate 9600 --model models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

On small Raspberry Pi systems, building or installing `llama-cpp-python` can be the hardest part of this path. The Codex CLI and Ollama paths avoid loading this GGUF model in Python.

## Legacy Transformers Backend

Use this only on systems with enough memory:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python serial_llm_interface.py
```

## Testing Without Acorn Hardware

Use `socat` to create a pair of pseudo terminals:

```bash
socat -d -d pty,raw,echo=0 pty,raw,echo=0
```

In another terminal, run one backend with the first PTY path:

```bash
source venv/bin/activate
python serial_codex_interface.py --port /dev/pts/X
```

In a third terminal, connect to the second PTY path:

```bash
screen /dev/pts/Y 9600
```

The same PTY approach works for `arm_gpt_server.py` and `serial_llm_interface_lite.py`; pass the PTY with each script's serial-port option.

## Troubleshooting

### Serial Port Does Not Open

- Check the port path exists: `ls /dev/ttyUSB* /dev/serial0`
- Check group permissions.
- Confirm another process is not holding the port open.
- Try the same baud rate on both machines.

### Codex Backend Fails

- Run `codex doctor`.
- Check that `codex exec "hello"` works in the same shell.
- Pass `--codex-command /path/to/codex` if the script cannot find the executable.
- Increase `--timeout` if replies take longer than expected.

### Ollama Backend Fails

- Confirm Ollama is running.
- Confirm the chat and embedding models are pulled.
- Rebuild the index with `python build_index.py`.

### llama-cpp Backend Fails

- Confirm the GGUF model path exists.
- Confirm `llama-cpp-python` imports in the active virtual environment.
- Use a smaller quantized model on memory-constrained hardware.

## Logging

The active scripts write timestamped logs in `logs/` and print received serial bytes plus generated responses to the console.
