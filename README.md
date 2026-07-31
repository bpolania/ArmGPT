# ArmGPT - Friendly AI Assistant for Acorn Computers

ArmGPT connects an Acorn or Archimedes computer to an AI assistant over a serial link. The host machine listens on a serial port, sends each received line to an AI backend, and writes a short response back to the Acorn.

## Backends

| Backend | Script | Best for | Inference path |
|---------|--------|----------|----------------|
| Unified server | `acorn_server.py` | Switching between local and Codex from the Acorn | Routes to Ollama or Codex CLI per message |
| Ollama with RAG | `arm_gpt_server.py` | Normal local setup with ARM history grounding | Local Ollama chat and embedding models |
| Codex CLI | `serial_codex_interface.py` | Using an existing Codex CLI login instead of a local model | Shells out to `codex exec` |
| llama-cpp legacy | `serial_llm_interface_lite.py` | Offline GGUF model on limited hardware | Local `llama-cpp-python` model |
| Transformers legacy | `serial_llm_interface.py` | Systems with more RAM | Local Hugging Face Transformers model |

The unified server is the preferred entry point when you want to choose the backend from the Acorn. The Ollama and Codex scripts remain useful for testing one backend directly.

## Common Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-lite.txt
```

Enable and test your serial device before running any backend. The default USB adapter port is `/dev/ttyUSB0`, and the default Raspberry Pi GPIO serial port is `/dev/serial0`.

## Recommended: Unified Acorn Server

The unified server listens on one serial port and lets the Acorn choose the backend with text commands.

```bash
python acorn_server.py usb --default-backend local
python acorn_server.py serial --default-backend codex
```

Runtime commands from the Acorn:

```text
/mode local
/mode codex
/local Tell me about Sophie Wilson.
/codex Tell me about the Acorn Archimedes.
/status
/help
```

Plain messages use the current mode. `/local <prompt>` and `/codex <prompt>` are one-shot overrides that do not change the current mode.

Useful options:

```bash
python acorn_server.py usb --chat-model qwen2.5:1.5b --index data/arm_index.jsonl
python acorn_server.py usb --codex-model gpt-5 --codex-timeout 240
python acorn_server.py usb --docs-dir data/arm_docs --codex-top-k 4 --max-context-chars 3600
python acorn_server.py usb --port-path /dev/pts/X
```

## Direct Ollama Server

Install Ollama, pull the chat and embedding models, then build the local vector index:

```bash
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text
python build_index.py
```

Run with a USB serial adapter:

```bash
python arm_gpt_server.py usb
```

Run with Raspberry Pi GPIO serial:

```bash
python arm_gpt_server.py serial
```

Useful options:

```bash
python arm_gpt_server.py usb --baudrate 115200
python arm_gpt_server.py serial --chat-model llama3.2:1b --embed-model nomic-embed-text
```

`build_index.py` reads `data/arm_docs/*.txt` and writes `data/arm_index.jsonl`. That generated index is ignored by git, so rebuild it after cloning or after changing source documents.

## Direct Codex CLI Interface

Use this when the host already has a working Codex CLI installation and login. This script does not use the OpenAI API directly and does not load a local GGUF model. It calls `codex exec` for each serial message and injects relevant snippets from `data/arm_docs/*.txt` into the prompt.

Check Codex first:

```bash
codex --version
codex doctor
```

Run the serial bridge:

```bash
python serial_codex_interface.py --port /dev/ttyUSB0 --baudrate 9600
```

If `codex` is not on `PATH`, pass the executable path:

```bash
python serial_codex_interface.py --codex-command /Users/you/.local/bin/codex
```

Useful options:

```bash
python serial_codex_interface.py --port /dev/serial0
python serial_codex_interface.py --codex-model gpt-5 --timeout 240
python serial_codex_interface.py --codex-cwd /path/to/ArmGPT
python serial_codex_interface.py --docs-dir data/arm_docs --top-k 4 --max-context-chars 3600
```

The Codex runner invokes `codex exec` with a read-only sandbox and `--skip-git-repo-check`, plus an ArmGPT prompt that tells Codex to answer conversationally rather than edit files. It uses lightweight keyword retrieval over `data/arm_docs`, so it does not require the Ollama vector index.

## Legacy llama-cpp Interface

Use this only when you want a fully offline local GGUF model.

```bash
pip install pyserial llama-cpp-python
chmod +x download_model.sh
./download_model.sh
python serial_llm_interface_lite.py --port /dev/ttyUSB0 --baudrate 9600 --model models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
```

## Legacy Transformers Interface

This path is heavier and usually not suitable for low-memory Raspberry Pi setups.

```bash
pip install -r requirements.txt
python serial_llm_interface.py
```

## Script Reference

### `acorn_server.py`

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `usb` or `serial` | Yes | none | `usb` = `/dev/ttyUSB0`, `serial` = `/dev/serial0` |
| `--port-path` | No | unset | Explicit serial path; overrides shortcut |
| `--baudrate` | No | `9600` | Baud rate |
| `--default-backend` | No | `local` | Backend for plain messages: `local` or `codex` |
| `--ollama-url` | No | `http://localhost:11434` | Ollama API base URL |
| `--chat-model` | No | `qwen2.5:1.5b` | Ollama chat model |
| `--embed-model` | No | `nomic-embed-text` | Ollama embedding model |
| `--index` | No | `data/arm_index.jsonl` | Ollama JSONL vector index |
| `--local-top-k` | No | `5` | Local RAG chunks to retrieve |
| `--codex-command` | No | `codex` | Codex executable or path |
| `--codex-model` | No | unset | Optional Codex model override |
| `--codex-cwd` | No | `.` | Working directory passed to Codex |
| `--docs-dir` | No | `data/arm_docs` | Directory of `.txt` docs for Codex grounding |
| `--codex-top-k` | No | `4` | Codex documentation chunks to retrieve |
| `--max-context-chars` | No | `3600` | Maximum Codex docs context characters per prompt |
| `--codex-timeout` | No | `180` | Codex timeout in seconds |
| `--codex-arg` | No | unset | Extra `codex exec` argument; repeat for multiple args |

### `arm_gpt_server.py`

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `usb` or `serial` | Yes | none | `usb` = `/dev/ttyUSB0`, `serial` = `/dev/serial0` |
| `--baudrate` | No | `9600` | Baud rate |
| `--chat-model` | No | `qwen2.5:1.5b` | Ollama chat model |
| `--embed-model` | No | `nomic-embed-text` | Ollama embedding model |
| `--ollama-url` | No | `http://localhost:11434` | Ollama API base URL |
| `--index` | No | `data/arm_index.jsonl` | JSONL vector index |

### `build_index.py`

| Argument | Default | Description |
|----------|---------|-------------|
| `--docs-dir` | `data/arm_docs` | Directory containing `.txt` source documents |
| `--output` | `data/arm_index.jsonl` | Output JSONL index path |
| `--embed-model` | `nomic-embed-text` | Ollama embedding model |
| `--ollama-url` | `http://localhost:11434` | Ollama API base URL |

### `serial_codex_interface.py`

| Argument | Default | Description |
|----------|---------|-------------|
| `--port` | `/dev/ttyUSB0` | Serial port |
| `--baudrate` | `9600` | Baud rate |
| `--codex-command` | `codex` | Codex executable or path |
| `--codex-model` | unset | Optional Codex model override |
| `--codex-cwd` | `.` | Working directory passed to Codex |
| `--docs-dir` | `data/arm_docs` | Directory of `.txt` docs for prompt grounding |
| `--top-k` | `4` | Number of documentation chunks to retrieve |
| `--max-context-chars` | `3600` | Maximum documentation context characters per prompt |
| `--timeout` | `180` | Timeout per Codex response, in seconds |
| `--codex-arg` | unset | Extra `codex exec` argument; repeat for multiple args |

### `serial_llm_interface_lite.py`

| Argument | Default | Description |
|----------|---------|-------------|
| `--port` | `/dev/ttyUSB0` | Serial port |
| `--baudrate` | `9600` | Baud rate |
| `--model` | `tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf` | Local GGUF model path |

## Logs

Runtime logs are written to `logs/`. Generated model files, Python caches, and the RAG index are ignored by git.

## Codex Contributor Notes

`AGENTS.md` contains repo-specific instructions for Codex. In particular, prompt and response-generation changes should preserve grounding from `data/arm_docs/*.txt`.

## More Setup Detail

See [SERIAL_LLM_SETUP.md](SERIAL_LLM_SETUP.md) for serial-port troubleshooting and hardware testing notes.
