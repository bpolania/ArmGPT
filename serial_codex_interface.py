#!/usr/bin/env python3
"""
Serial Codex Interface

Listens on a serial port, sends each received message to `codex exec`,
and writes Codex's final response back to the serial port.
"""

import argparse
import glob
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)
log_filename = ""


def setup_logging() -> None:
    global log_filename

    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_filename = os.path.join(
        log_dir, f"serial_codex_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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


BASE_SYSTEM_PROMPT = """You are ArmGPT, a friendly and knowledgeable AI assistant connected to an Acorn computer via serial port.

Reply as ArmGPT, not as a coding assistant. Keep replies short because the user is reading them on a serial terminal. Aim for one or two concise sentences. Be warm, gentle, and interested in Acorn and retro computing. Use plain text only - no markdown, links, headings, tables, or emoji, since the terminal cannot render them.

Do not edit files, run shell commands, or inspect the repository. Just answer the user's message conversationally.

You may be given documentation context about ARM, Acorn, Archimedes, RISC OS, and ArmGPT history. When it is relevant, prefer it and ground your answer in it. When it is not relevant or does not contain the answer, just answer from your own general knowledge.

Either way, answer the question naturally and directly. Never mention the documentation, the context, or whether it covered the question, and never say things like "the docs don't cover this" or "the provided history doesn't mention that" - the user cannot see any of that and does not need to know it exists. Just give the answer.
"""

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "i",
    "in",
    "is",
    "it",
    "me",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "were",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
    "you",
}


class SerialCodexInterface:
    def __init__(
        self,
        port: str = "/dev/ttyUSB0",
        baudrate: int = 9600,
        codex_command: str = "codex",
        codex_model: Optional[str] = None,
        codex_cwd: str = ".",
        docs_dir: str = "data/arm_docs",
        max_context_chars: int = 3600,
        top_k: int = 4,
        timeout: int = 180,
        extra_args: Optional[List[str]] = None,
    ):
        self.port = port
        self.baudrate = baudrate
        self.codex_command = codex_command
        self.codex_model = codex_model
        self.codex_cwd = codex_cwd
        self.docs_dir = docs_dir
        self.max_context_chars = max_context_chars
        self.top_k = top_k
        self.timeout = timeout
        self.extra_args = extra_args or []
        self.serial_conn = None
        self.serial_module = None
        self.processing = False
        self.doc_chunks = self.load_doc_chunks()

    def resolve_path(self, path: str) -> str:
        if os.path.isabs(path):
            return path
        return os.path.join(self.codex_cwd, path)

    def tokenize(self, text: str) -> List[str]:
        return [
            token
            for token in re.findall(r"[a-z0-9][a-z0-9']+", text.lower())
            if token not in STOPWORDS and len(token) > 1
        ]

    def expand_query_tokens(self, message: str, tokens: List[str]) -> List[str]:
        expanded = list(tokens)
        token_set = set(tokens)
        msg = message.lower()

        if "arm" in token_set and any(word in token_set for word in ["created", "invented", "designed"]):
            expanded.extend(["sophie", "wilson", "steve", "furber"])

        if "arm" in token_set and any(word in token_set for word in ["origin", "origins", "history"]):
            expanded.extend(["acorn", "sophie", "wilson", "steve", "furber"])

        if "archimedes" in token_set or "a310" in token_set or "a310" in msg:
            expanded.extend(["archimedes", "a310", "risc", "home", "computer"])

        return expanded

    def chunk_text(self, text: str, max_words: int = 180, overlap: int = 35) -> List[str]:
        words = text.split()
        if not words:
            return []

        step = max_words - overlap if max_words > overlap else max_words
        chunks = []
        for start in range(0, len(words), step):
            chunk = " ".join(words[start:start + max_words]).strip()
            if chunk:
                chunks.append(chunk)
        return chunks

    def load_doc_chunks(self) -> List[Dict[str, object]]:
        docs_path = self.resolve_path(self.docs_dir)
        paths = sorted(glob.glob(os.path.join(docs_path, "*.txt")))
        chunks: List[Dict[str, object]] = []

        if not paths:
            logger.warning("No documentation files found in %s", docs_path)
            return chunks

        for path in paths:
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except OSError as e:
                logger.warning("Could not read documentation file %s: %s", path, e)
                continue

            source = os.path.basename(path)
            for index, chunk in enumerate(self.chunk_text(text)):
                tokens = set(self.tokenize(source.replace("_", " ") + " " + chunk))
                chunks.append({
                    "order": len(chunks),
                    "source": source,
                    "chunk_id": index,
                    "text": chunk,
                    "tokens": tokens,
                })

        logger.info("Loaded %d documentation chunks from %s", len(chunks), docs_path)
        return chunks

    def score_doc_chunk(self, query_tokens: List[str], message: str, chunk: Dict[str, object]) -> int:
        token_set = chunk.get("tokens", set())
        if not isinstance(token_set, set):
            return 0

        score = len(set(query_tokens) & token_set)
        text = str(chunk.get("text", "")).lower()
        source = str(chunk.get("source", "")).lower().replace("_", " ")
        searchable = source + " " + text
        msg = message.lower()

        for token in query_tokens:
            if token in token_set:
                score += query_tokens.count(token) - 1

        phrase_boosts = [
            ("sophie wilson", 4),
            ("steve furber", 4),
            ("acorn archimedes", 3),
            ("risc based home computer", 3),
            ("risc-based home computer", 3),
            ("arm1", 2),
            ("arm2", 2),
            ("a310", 3),
        ]
        for phrase, boost in phrase_boosts:
            if phrase in searchable:
                score += boost

        if "who" in msg and any(word in msg for word in ["created", "invented", "designed"]):
            if "sophie" in token_set or "furber" in token_set:
                score += 6

        if ("archimedes" in msg or "a310" in msg) and ("archimedes" in token_set or "a310" in token_set):
            score += 5

        return score

    def retrieve_doc_context(self, message: str) -> str:
        if not self.doc_chunks:
            return ""

        query_tokens = self.expand_query_tokens(message, self.tokenize(message))
        if not query_tokens:
            return ""

        scored: List[Tuple[int, int, Dict[str, object]]] = []
        for chunk in self.doc_chunks:
            score = self.score_doc_chunk(query_tokens, message, chunk)
            if score:
                order = int(chunk.get("order", 0))
                scored.append((score, order, chunk))

        scored.sort(key=lambda item: (-item[0], item[1]))
        selected = scored[:self.top_k]
        if not selected:
            return ""

        parts = []
        total_chars = 0
        for score, _, chunk in selected:
            source = str(chunk.get("source", "unknown"))
            chunk_id = chunk.get("chunk_id", "?")
            text = str(chunk.get("text", "")).strip()
            entry = f"[{source} chunk {chunk_id}, score {score}]\n{text}"

            remaining = self.max_context_chars - total_chars
            if remaining <= 0:
                break
            if len(entry) > remaining:
                entry = entry[:remaining].rsplit(" ", 1)[0].strip()

            parts.append(entry)
            total_chars += len(entry)

        return "\n\n".join(parts)

    def init_serial(self) -> bool:
        try:
            import serial

            self.serial_module = serial
            self.serial_conn = serial.Serial()
            self.serial_conn.port = self.port
            self.serial_conn.baudrate = self.baudrate
            self.serial_conn.bytesize = serial.EIGHTBITS
            self.serial_conn.parity = serial.PARITY_NONE
            self.serial_conn.stopbits = serial.STOPBITS_ONE
            self.serial_conn.timeout = 2.0
            self.serial_conn.xonxoff = False
            self.serial_conn.rtscts = False
            self.serial_conn.dsrdtr = False

            self.serial_conn.open()
            time.sleep(0.1)
            self.serial_conn.flushInput()
            self.serial_conn.flushOutput()
            time.sleep(0.1)

            logger.info("Serial port %s opened successfully at %d baud", self.port, self.baudrate)
            return True
        except ImportError:
            logger.error("pyserial is not installed. Install it with: pip install -r requirements-lite.txt")
            return False
        except Exception as e:
            logger.error("Failed to open serial port: %s", e)
            return False

    def init_codex(self) -> bool:
        resolved = shutil.which(self.codex_command)
        if not resolved:
            logger.error("Codex command not found: %s", self.codex_command)
            return False

        logger.info("Using Codex command: %s", resolved)
        return True

    def format_prompt(self, message: str) -> str:
        context = self.retrieve_doc_context(message)
        prompt_parts = [BASE_SYSTEM_PROMPT]
        if context:
            prompt_parts.append("Relevant repository documentation context from data/arm_docs:\n" + context)
        prompt_parts.append("User message from the Acorn serial terminal:\n" + message)
        return "\n\n".join(prompt_parts)

    def build_codex_command(self, output_path: str) -> List[str]:
        cmd = [
            self.codex_command,
            "exec",
            "--sandbox",
            "read-only",
            "--skip-git-repo-check",
            "--cd",
            self.codex_cwd,
            "--output-last-message",
            output_path,
            "--color",
            "never",
        ]
        if self.codex_model:
            cmd.extend(["--model", self.codex_model])
        cmd.extend(self.extra_args)
        cmd.append("-")
        return cmd

    def generate_response(self, message: str) -> str:
        prompt = self.format_prompt(message)
        start_time = time.time()

        with tempfile.NamedTemporaryFile(prefix="armgpt_codex_", suffix=".txt", delete=False) as tmp:
            output_path = tmp.name

        try:
            cmd = self.build_codex_command(output_path)
            logger.info("Running Codex command: %s", " ".join(cmd[:-1]) + " -")

            completed = subprocess.run(
                cmd,
                input=prompt,
                text=True,
                capture_output=True,
                timeout=self.timeout,
                cwd=self.codex_cwd,
            )

            generation_time = time.time() - start_time
            logger.info("Codex completed in %.2f seconds with code %d", generation_time, completed.returncode)
            if completed.stderr:
                logger.info("Codex stderr: %s", completed.stderr.strip())

            response = ""
            if os.path.exists(output_path):
                with open(output_path, "r", encoding="utf-8", errors="replace") as f:
                    response = f.read().strip()

            if not response:
                response = completed.stdout.strip()

            if completed.returncode != 0:
                logger.error("Codex failed: %s", completed.stderr.strip())
                return "Sorry, Codex could not answer that just now."

            return self.clean_response(response)
        except subprocess.TimeoutExpired:
            logger.error("Codex timed out after %d seconds", self.timeout)
            return "Sorry, Codex took too long to reply."
        except Exception as e:
            logger.error("Error running Codex: %s", e)
            return "Sorry, Codex could not answer that just now."
        finally:
            try:
                os.unlink(output_path)
            except OSError:
                pass

    def clean_response(self, response: str) -> str:
        response = response.strip()
        if not response:
            return "Sorry, I could not generate a response just now."

        lines = [line.strip() for line in response.splitlines() if line.strip()]
        response = " ".join(lines)
        return response[:900]

    def read_serial_message(self) -> Optional[str]:
        try:
            if self.processing:
                if self.serial_conn.in_waiting > 0:
                    discarded = self.serial_conn.read(self.serial_conn.in_waiting)
                    logger.info("Ignored message while processing: %s", discarded)
                return None

            if self.serial_conn.in_waiting <= 0:
                return None

            raw_message = self.serial_conn.readline()
            if not raw_message:
                return None

            message = raw_message.decode("utf-8", errors="replace").strip()
            logger.info("Received raw bytes: %s", raw_message)
            logger.info("Decoded message: %r", message)

            print("\n" + "=" * 60)
            print("MESSAGE FROM ACORN A310:")
            print(f"    Raw bytes: {raw_message}")
            print(f"    UTF-8: {message!r} (len: {len(message)})")
            print("=" * 60)

            return message if message else "empty_message"
        except Exception as e:
            logger.error("Error reading serial: %s", e)
            return None

    def send_serial_response(self, response: str) -> None:
        try:
            response_bytes = (response + "\n").encode("utf-8")
            self.serial_conn.write(response_bytes)
            self.serial_conn.flush()
            logger.info("Response sent: %s", response)

            print("\nARMGPT RESPONSE TO ACORN:")
            print(f"    {response}")
            print("-" * 60 + "\n")
        except Exception as e:
            logger.error("Error sending response: %s", e)

    def run(self) -> None:
        logger.info("=" * 60)
        logger.info("Starting Serial Codex Interface")
        logger.info("Port: %s", self.port)
        logger.info("Baudrate: %d", self.baudrate)
        logger.info("Codex command: %s", self.codex_command)
        logger.info("Codex cwd: %s", self.codex_cwd)
        logger.info("=" * 60)

        if not self.init_serial():
            return
        if not self.init_codex():
            return

        print("\nArmGPT Codex interface is ready and listening.")
        print(f"Serial port: {self.port} at {self.baudrate} baud")
        print(f"Codex command: {self.codex_command}")
        print(f"Logs: {log_filename}")
        print("\n" + "=" * 60)
        print("  Waiting for messages from Acorn Archimedes A310...")
        print("=" * 60 + "\n")

        message_count = 0
        error_count = 0

        try:
            while True:
                message = self.read_serial_message()
                if message:
                    message_count += 1
                    self.processing = True
                    try:
                        logger.info("Generating response for message #%d", message_count)
                        response = self.generate_response(message)
                        if response.startswith("Sorry, Codex"):
                            error_count += 1
                        self.send_serial_response(response)
                    finally:
                        self.processing = False

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

            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
                logger.info("Serial port closed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Serial interface backed by Codex CLI")
    parser.add_argument("--port", default="/dev/ttyUSB0", help="Serial port")
    parser.add_argument("--baudrate", type=int, default=9600, help="Baud rate")
    parser.add_argument("--codex-command", default="codex", help="Codex executable or path")
    parser.add_argument("--codex-model", default=None, help="Optional Codex model override")
    parser.add_argument("--codex-cwd", default=".", help="Working directory for Codex")
    parser.add_argument("--docs-dir", default="data/arm_docs", help="Directory of .txt docs for prompt grounding")
    parser.add_argument(
        "--max-context-chars",
        type=int,
        default=3600,
        help="Maximum documentation context characters included per prompt",
    )
    parser.add_argument("--top-k", type=int, default=4, help="Number of documentation chunks to retrieve")
    parser.add_argument("--timeout", type=int, default=180, help="Codex timeout in seconds")
    parser.add_argument(
        "--codex-arg",
        action="append",
        default=[],
        help="Extra argument to pass to `codex exec`; repeat for multiple args",
    )

    args = parser.parse_args()
    setup_logging()

    interface = SerialCodexInterface(
        port=args.port,
        baudrate=args.baudrate,
        codex_command=args.codex_command,
        codex_model=args.codex_model,
        codex_cwd=args.codex_cwd,
        docs_dir=args.docs_dir,
        max_context_chars=args.max_context_chars,
        top_k=args.top_k,
        timeout=args.timeout,
        extra_args=args.codex_arg,
    )
    interface.run()


if __name__ == "__main__":
    main()
