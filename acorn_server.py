#!/usr/bin/env python3
"""
Acorn Server - unified serial bridge for local Ollama and Codex CLI backends.

Runtime commands from the Acorn serial terminal:
  /mode local      Switch future messages to the local Ollama backend
  /mode codex      Switch future messages to the Codex CLI backend
  /local <prompt>  Use the local backend for this message only
  /codex <prompt>  Use the Codex backend for this message only
  /status          Show current backend status
  /help            Show command summary
"""

import argparse
import json
import logging
import math
import os
import re
import sys
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from serial_codex_interface import SerialCodexInterface


SERIAL_PORTS = {
    "usb": "/dev/ttyUSB0",
    "serial": "/dev/serial0",
}

BACKENDS = {"local", "codex"}

logger = logging.getLogger(__name__)
log_filename = ""


SYSTEM_PROMPT = """You are ArmGPT, a friendly and knowledgeable AI assistant connected to an Acorn computer via serial port. You have a warm, gentle personality and enjoy helping Acorn enthusiasts with their computing needs.

Key traits:
- Always introduce yourself as ArmGPT when greeting users
- Be enthusiastic about retro computing and Acorn computers
- Keep responses as SHORT as possible - aim for 1-2 sentences, maximum 2 short paragraphs only when absolutely necessary
- Use a conversational, amicable tone
- Show interest in what the user is working on
- If asked about yourself, mention you're running on a Raspberry Pi connected to their Acorn

IMPORTANT: Be concise! Serial terminals are limited. Give complete but brief answers.

Remember: You're not generic customer support - you're ArmGPT, a specialized companion for Acorn computer users!"""

RAG_GROUNDING = """You also have access to ARM history documentation. Use the context below to ground your answers when relevant. If the context doesn't cover the question, you can still answer from general knowledge, but let the user know you're going beyond your documentation."""

CONVERSATIONAL_PATTERNS = [
    r"^(hi|hello|hey|howdy|greetings|yo|hiya)\b",
    r"^(thanks|thank you|cheers|ta|much appreciated)",
    r"^(bye|goodbye|see you|later|good night|gn)\b",
    r"^(how are you|how's it going|what's up|whats up)\b",
    r"^(good morning|good afternoon|good evening)\b",
    r"^(yes|no|ok|okay|sure|yep|nope|yeah|nah)\b",
    r"^(who are you|what are you|tell me about yourself)\b",
]


def setup_logging() -> None:
    global log_filename

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(
        log_dir, f"acorn_server_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    root_logger.handlers = [file_handler, stream_handler]
    logger.info("Logging to file: %s", log_filename)


def is_conversational(message: str) -> bool:
    msg = message.strip().lower()
    return any(re.match(pattern, msg) for pattern in CONVERSATIONAL_PATTERNS)


def cosine_similarity(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class LocalOllamaBackend:
    def __init__(
        self,
        ollama_url: str,
        chat_model: str,
        embed_model: str,
        index_path: str,
        top_k: int = 5,
    ):
        self.ollama_url = ollama_url
        self.chat_model = chat_model
        self.embed_model = embed_model
        self.index_path = index_path
        self.top_k = top_k
        self.index = self.load_index(index_path)
        self._reachable: Optional[bool] = None

    def check_available(self) -> bool:
        try:
            import requests

            resp = requests.get(self.ollama_url, timeout=5)
            self._reachable = resp.status_code == 200
        except ImportError:
            logger.warning("requests is not installed. Install it with: pip install -r requirements-lite.txt")
            self._reachable = False
        except Exception:
            self._reachable = False

        if self._reachable:
            logger.info("Ollama is reachable at %s", self.ollama_url)
        else:
            logger.warning("Ollama is not reachable at %s", self.ollama_url)
        return bool(self._reachable)

    def load_index(self, index_path: str) -> List[Dict[str, Any]]:
        chunks: List[Dict[str, Any]] = []
        if not os.path.exists(index_path):
            logger.warning("Index file not found: %s", index_path)
            return chunks

        try:
            with open(index_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        chunks.append(json.loads(line))
        except (OSError, json.JSONDecodeError) as e:
            logger.error("Failed to load index %s: %s", index_path, e)
            return []

        logger.info("Loaded %d local RAG chunks from %s", len(chunks), index_path)
        return chunks

    def embed_query(self, text: str) -> Optional[List[float]]:
        try:
            import requests
        except ImportError:
            logger.error("requests is not installed. Install it with: pip install -r requirements-lite.txt")
            return None

        url = f"{self.ollama_url}/api/embed"
        payload = {"model": self.embed_model, "input": [text]}
        try:
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.error("Embedding request failed: %s", e)
            return None

        if isinstance(data, dict) and "embeddings" in data:
            embeddings = data["embeddings"]
            if isinstance(embeddings, list) and embeddings and isinstance(embeddings[0], list):
                return embeddings[0]

        if isinstance(data, dict) and "embedding" in data:
            embedding = data["embedding"]
            if isinstance(embedding, list) and embedding:
                return embedding

        logger.warning("Unexpected embedding response structure")
        return None

    def retrieve_context(self, query_embedding: Optional[List[float]]) -> str:
        if not self.index:
            return ""

        if query_embedding is None:
            selected = self.index[:self.top_k]
        else:
            scored = []
            for chunk in self.index:
                embedding = chunk.get("embedding", [])
                if embedding:
                    scored.append((cosine_similarity(query_embedding, embedding), chunk))
            scored.sort(key=lambda item: item[0], reverse=True)
            selected = [chunk for _, chunk in scored[:self.top_k]]

        parts = []
        for chunk in selected:
            source = chunk.get("source", "unknown")
            text = chunk.get("text", "")
            parts.append(f"[{source}]\n{text}")
        return "\n\n".join(parts)

    def chat(self, messages: List[Dict[str, str]]) -> str:
        try:
            import requests
        except ImportError:
            logger.error("requests is not installed. Install it with: pip install -r requirements-lite.txt")
            return ""

        url = f"{self.ollama_url}/api/chat"
        payload = {
            "model": self.chat_model,
            "messages": messages,
            "stream": False,
        }
        try:
            resp = requests.post(url, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "").strip()
        except Exception as e:
            logger.error("Chat request failed: %s", e)
            return ""

    def generate(self, message: str) -> str:
        if self._reachable is not True and not self.check_available():
            return "Local Ollama is not reachable. Try /mode codex or start Ollama."

        if is_conversational(message):
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ]
        else:
            query_embedding = self.embed_query(message)
            context = self.retrieve_context(query_embedding)
            system_content = SYSTEM_PROMPT
            if context:
                system_content = (
                    SYSTEM_PROMPT
                    + "\n\n"
                    + RAG_GROUNDING
                    + "\n\n--- Retrieved Context ---\n"
                    + context
                )
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": message},
            ]

        response = self.chat(messages)
        return response or "Sorry, I couldn't generate a local response just now."

    def status(self) -> str:
        reachable = "unknown"
        if self._reachable is True:
            reachable = "yes"
        elif self._reachable is False:
            reachable = "no"
        return (
            f"local: Ollama {self.chat_model}, reachable {reachable}, "
            f"index chunks {len(self.index)}"
        )


class CodexCliBackend:
    def __init__(
        self,
        codex_command: str,
        codex_model: Optional[str],
        codex_cwd: str,
        docs_dir: str,
        max_context_chars: int,
        top_k: int,
        timeout: int,
        extra_args: Optional[List[str]] = None,
    ):
        self.interface = SerialCodexInterface(
            codex_command=codex_command,
            codex_model=codex_model,
            codex_cwd=codex_cwd,
            docs_dir=docs_dir,
            max_context_chars=max_context_chars,
            top_k=top_k,
            timeout=timeout,
            extra_args=extra_args or [],
        )
        self._available: Optional[bool] = None

    def check_available(self) -> bool:
        self._available = self.interface.init_codex()
        return bool(self._available)

    def generate(self, message: str) -> str:
        if self._available is not True and not self.check_available():
            return "Codex CLI is not available. Try /mode local or check codex."
        return self.interface.generate_response(message)

    def status(self) -> str:
        available = "unknown"
        if self._available is True:
            available = "yes"
        elif self._available is False:
            available = "no"
        model = self.interface.codex_model or "config default"
        return (
            f"codex: command {self.interface.codex_command}, model {model}, "
            f"available {available}, doc chunks {len(self.interface.doc_chunks)}"
        )


class CommandRouter:
    def __init__(self, default_backend: str):
        self.current_backend = default_backend

    def handle(
        self,
        raw_message: str,
        local_backend: LocalOllamaBackend,
        codex_backend: CodexCliBackend,
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Return (backend, message, immediate_response).
        If immediate_response is set, send it without calling a backend.
        """
        message = raw_message.strip()
        lower = message.lower()

        if lower in {"/help", "/?"}:
            return None, None, self.help_text()

        if lower == "/status":
            return None, None, self.status_text(local_backend, codex_backend)

        mode_match = re.match(r"^/mode\s+(\w+)\s*$", message, flags=re.IGNORECASE)
        if mode_match:
            backend = mode_match.group(1).lower()
            if backend not in BACKENDS:
                return None, None, "Unknown mode. Use /mode local or /mode codex."
            self.current_backend = backend
            return None, None, f"Mode set to {backend}."

        one_shot_match = re.match(r"^/(local|codex)\b(?:\s+(.*))?$", message, flags=re.IGNORECASE | re.DOTALL)
        if one_shot_match:
            backend = one_shot_match.group(1).lower()
            prompt = (one_shot_match.group(2) or "").strip()
            if not prompt:
                return None, None, f"Usage: /{backend} your question"
            return backend, prompt, None

        if lower.startswith("/"):
            return None, None, "Unknown command. Try /help."

        return self.current_backend, message, None

    def help_text(self) -> str:
        return (
            "Commands: /mode local, /mode codex, /local <q>, "
            "/codex <q>, /status. Plain text uses current mode."
        )

    def status_text(self, local_backend: LocalOllamaBackend, codex_backend: CodexCliBackend) -> str:
        return (
            f"Mode: {self.current_backend}. "
            f"{local_backend.status()}. {codex_backend.status()}."
        )


def init_serial(port: str, baudrate: int) -> Optional[Any]:
    try:
        import serial

        conn = serial.Serial()
        conn.port = port
        conn.baudrate = baudrate
        conn.bytesize = serial.EIGHTBITS
        conn.parity = serial.PARITY_NONE
        conn.stopbits = serial.STOPBITS_ONE
        conn.timeout = 2.0
        conn.xonxoff = False
        conn.rtscts = False
        conn.dsrdtr = False

        conn.open()
        time.sleep(0.1)
        conn.flushInput()
        conn.flushOutput()
        time.sleep(0.1)

        logger.info("Serial port %s opened successfully at %d baud", port, baudrate)
        return conn
    except ImportError:
        logger.error("pyserial is not installed. Install it with: pip install -r requirements-lite.txt")
        return None
    except Exception as e:
        logger.error("Failed to open serial port: %s", e)
        return None


def read_serial_message(conn: Any, processing: bool) -> Optional[str]:
    try:
        if processing:
            if conn.in_waiting > 0:
                discarded = conn.read(conn.in_waiting)
                logger.info("Ignored message while processing: %s", discarded)
            return None

        if conn.in_waiting <= 0:
            return None

        raw_message = conn.readline()
        if not raw_message:
            return None

        message = raw_message.decode("utf-8", errors="replace").strip()
        logger.info("Received raw bytes: %s", raw_message)
        logger.info("Decoded message: %r", message)

        print("\n" + "=" * 60)
        print("MESSAGE FROM ACORN:")
        print(f"    Raw bytes: {raw_message}")
        print(f"    UTF-8: {message!r} (len: {len(message)})")
        print("=" * 60)

        return message if message else "empty_message"
    except Exception as e:
        logger.error("Error reading serial: %s", e)
        return None


# The model reaches for typographic characters ("I’m", "1987 — the year"). A
# 7-bit line cannot carry them, and as UTF-8 they arrive as multi-byte garbage,
# so fold them down to their ASCII equivalents before transmitting.
ASCII_FOLD = {
    '‘': "'", '’': "'", '‚': "'", '‛': "'",
    '“': '"', '”': '"', '„': '"',
    '–': '-', '—': '-', '−': '-',
    '…': '...', ' ': ' ', '•': '*',
}


def to_ascii(text: str) -> str:
    """Flatten to 7-bit-safe ASCII for the serial link."""
    for uni, plain in ASCII_FOLD.items():
        text = text.replace(uni, plain)
    return text.encode('ascii', errors='replace').decode('ascii')


def send_serial_response(conn: Any, response: str) -> None:
    try:
        ascii_response = to_ascii(response)
        if ascii_response != response:
            logger.info("Response folded to ASCII for the 7-bit serial line")
        response_bytes = (ascii_response + "\n").encode("ascii")
        conn.write(response_bytes)
        conn.flush()
        logger.info("Response sent: %s", ascii_response)

        print("\nARMGPT RESPONSE TO ACORN:")
        print(f"    {ascii_response}")
        print("-" * 60 + "\n")
    except Exception as e:
        logger.error("Error sending response: %s", e)


def run(
    port: str,
    baudrate: int,
    default_backend: str,
    local_backend: LocalOllamaBackend,
    codex_backend: CodexCliBackend,
) -> None:
    router = CommandRouter(default_backend)

    logger.info("=" * 60)
    logger.info("Starting Acorn Server")
    logger.info("Port: %s", port)
    logger.info("Baudrate: %d", baudrate)
    logger.info("Default backend: %s", default_backend)
    logger.info("=" * 60)

    conn = init_serial(port, baudrate)
    if conn is None:
        return

    if default_backend == "local":
        local_backend.check_available()
    elif default_backend == "codex":
        codex_backend.check_available()

    print("\nAcorn Server is ready and listening.")
    print(f"Serial port: {port} at {baudrate} baud")
    print(f"Default mode: {default_backend}")
    print(f"Logs: {log_filename}")
    print("Commands: /mode local, /mode codex, /local <q>, /codex <q>, /status")
    print("\n" + "=" * 60)
    print("  Waiting for messages from Acorn...")
    print("=" * 60 + "\n")

    message_count = 0
    error_count = 0
    processing = False

    try:
        while True:
            raw_message = read_serial_message(conn, processing)
            if raw_message:
                message_count += 1
                processing = True
                start_time = time.time()

                try:
                    backend_name, prompt, immediate_response = router.handle(
                        raw_message,
                        local_backend,
                        codex_backend,
                    )
                    if immediate_response is not None:
                        response = immediate_response
                    elif backend_name == "local" and prompt is not None:
                        logger.info("Routing message #%d to local backend", message_count)
                        response = local_backend.generate(prompt)
                    elif backend_name == "codex" and prompt is not None:
                        logger.info("Routing message #%d to Codex backend", message_count)
                        response = codex_backend.generate(prompt)
                    else:
                        response = "I could not route that message. Try /help."
                        error_count += 1

                    elapsed = time.time() - start_time
                    logger.info("Message #%d completed in %.2f seconds", message_count, elapsed)
                    print(f"  Response time: {elapsed:.2f} seconds")
                    send_serial_response(conn, response)
                finally:
                    processing = False

            time.sleep(0.01)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error("Unexpected error: %s", e, exc_info=True)
        error_count += 1
    finally:
        logger.info("=" * 60)
        logger.info("Session Summary")
        logger.info("Total messages processed: %d", message_count)
        logger.info("Total errors: %d", error_count)
        logger.info("Log file: %s", log_filename)
        logger.info("=" * 60)

        if conn and conn.is_open:
            conn.close()
            logger.info("Serial port closed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Unified Acorn serial AI server")
    parser.add_argument("port", choices=["usb", "serial"], help="Serial port shortcut")
    parser.add_argument("--port-path", default=None, help="Explicit serial device path; overrides port shortcut")
    parser.add_argument("--baudrate", type=int, default=9600, help="Baud rate")
    parser.add_argument(
        "--default-backend",
        choices=sorted(BACKENDS),
        default="local",
        help="Backend used for plain messages",
    )

    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama API base URL")
    parser.add_argument("--chat-model", default="qwen2.5:1.5b", help="Ollama chat model")
    parser.add_argument("--embed-model", default="nomic-embed-text", help="Ollama embedding model")
    parser.add_argument("--index", default="data/arm_index.jsonl", help="Ollama JSONL vector index")
    parser.add_argument("--local-top-k", type=int, default=5, help="Local RAG chunks to retrieve")

    parser.add_argument("--codex-command", default="codex", help="Codex executable or path")
    parser.add_argument("--codex-model", default=None, help="Optional Codex model override")
    parser.add_argument("--codex-cwd", default=".", help="Working directory for Codex")
    parser.add_argument("--docs-dir", default="data/arm_docs", help="Directory of .txt docs for Codex grounding")
    parser.add_argument(
        "--max-context-chars",
        type=int,
        default=3600,
        help="Maximum Codex documentation context characters per prompt",
    )
    parser.add_argument("--codex-top-k", type=int, default=4, help="Codex documentation chunks to retrieve")
    parser.add_argument("--codex-timeout", type=int, default=180, help="Codex timeout in seconds")
    parser.add_argument(
        "--codex-arg",
        action="append",
        default=[],
        help="Extra argument to pass to `codex exec`; repeat for multiple args",
    )

    args = parser.parse_args()
    setup_logging()

    local_backend = LocalOllamaBackend(
        ollama_url=args.ollama_url,
        chat_model=args.chat_model,
        embed_model=args.embed_model,
        index_path=args.index,
        top_k=args.local_top_k,
    )
    codex_backend = CodexCliBackend(
        codex_command=args.codex_command,
        codex_model=args.codex_model,
        codex_cwd=args.codex_cwd,
        docs_dir=args.docs_dir,
        max_context_chars=args.max_context_chars,
        top_k=args.codex_top_k,
        timeout=args.codex_timeout,
        extra_args=args.codex_arg,
    )

    run(
        port=args.port_path or SERIAL_PORTS[args.port],
        baudrate=args.baudrate,
        default_backend=args.default_backend,
        local_backend=local_backend,
        codex_backend=codex_backend,
    )


if __name__ == "__main__":
    main()
