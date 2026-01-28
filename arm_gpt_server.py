#!/usr/bin/env python3
"""
ArmGPT Server - Serial LLM Interface for Raspberry Pi
Uses Ollama for inference with RAG from ARM documentation index
"""

import serial
import time
import logging
import sys
import json
import math
import re
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
import argparse

import requests

# Serial port mappings
SERIAL_PORTS = {
    'usb': '/dev/ttyUSB0',
    'serial': '/dev/serial0',
}

# Create logs directory if it doesn't exist
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure logging to both console and file
log_filename = os.path.join(log_dir, f'serial_llm_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Logging to file: {log_filename}")

# ArmGPT personality system prompt
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

# Simple patterns for conversational messages that don't need RAG
CONVERSATIONAL_PATTERNS = [
    r'^(hi|hello|hey|howdy|greetings|yo|hiya)\b',
    r'^(thanks|thank you|cheers|ta|much appreciated)',
    r'^(bye|goodbye|see you|later|good night|gn)\b',
    r'^(how are you|how\'s it going|what\'s up|whats up)\b',
    r'^(good morning|good afternoon|good evening)\b',
    r'^(yes|no|ok|okay|sure|yep|nope|yeah|nah)\b',
    r'^(who are you|what are you|tell me about yourself)\b',
]


def is_conversational(message: str) -> bool:
    """Check if a message is simple conversation that doesn't need RAG."""
    msg = message.strip().lower()
    for pattern in CONVERSATIONAL_PATTERNS:
        if re.match(pattern, msg):
            return True
    return False


# ─── Ollama helpers ──────────────────────────────────────────────

def check_ollama(ollama_url: str) -> bool:
    """Verify Ollama is reachable."""
    try:
        resp = requests.get(ollama_url, timeout=5)
        if resp.status_code == 200:
            logger.info(f"Ollama is reachable at {ollama_url}")
            return True
    except requests.ConnectionError:
        pass
    logger.error(f"Cannot reach Ollama at {ollama_url}")
    return False


def embed_query(text: str, ollama_url: str, embed_model: str) -> Optional[List[float]]:
    """Get an embedding vector for a query string."""
    url = f"{ollama_url}/api/embed"
    payload = {"model": embed_model, "input": [text]}
    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if isinstance(data, dict) and "embeddings" in data:
            embs = data["embeddings"]
            if isinstance(embs, list) and len(embs) > 0 and isinstance(embs[0], list):
                return embs[0]

        if isinstance(data, dict) and "embedding" in data:
            possible = data["embedding"]
            if isinstance(possible, list) and possible:
                return possible

        logger.warning("Unexpected embedding response structure")
        return None
    except Exception as e:
        logger.error(f"Embedding request failed: {e}")
        return None


def ollama_chat(messages: List[Dict[str, str]], ollama_url: str, chat_model: str) -> str:
    """Send a chat completion request to Ollama."""
    url = f"{ollama_url}/api/chat"
    payload = {
        "model": chat_model,
        "messages": messages,
        "stream": False,
    }
    try:
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        return data.get("message", {}).get("content", "").strip()
    except Exception as e:
        logger.error(f"Chat request failed: {e}")
        return ""


# ─── RAG helpers ─────────────────────────────────────────────────

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def load_index(index_path: str) -> List[Dict[str, Any]]:
    """Load the JSONL vector index from disk."""
    chunks: List[Dict[str, Any]] = []
    if not os.path.exists(index_path):
        logger.error(f"Index file not found: {index_path}")
        return chunks
    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    logger.info(f"Loaded {len(chunks)} chunks from {index_path}")
    return chunks


def retrieve_context(query_embedding: Optional[List[float]],
                     index: List[Dict[str, Any]],
                     top_k: int = 5) -> str:
    """
    Retrieve the top-K most relevant chunks.
    Falls back to first K chunks if query_embedding is None.
    """
    if not index:
        return ""

    if query_embedding is None:
        # Fallback: return the first K chunks
        logger.warning("No query embedding; falling back to first %d chunks", top_k)
        selected = index[:top_k]
    else:
        scored = []
        for chunk in index:
            emb = chunk.get("embedding", [])
            if emb:
                score = cosine_similarity(query_embedding, emb)
                scored.append((score, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        selected = [c for _, c in scored[:top_k]]

    parts = []
    for chunk in selected:
        source = chunk.get("source", "unknown")
        text = chunk.get("text", "")
        parts.append(f"[{source}]\n{text}")

    return "\n\n".join(parts)


# ─── Serial helpers (unchanged) ─────────────────────────────────

def init_serial(port: str, baudrate: int) -> Optional[serial.Serial]:
    """Initialize serial connection."""
    try:
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

        logger.info(f"Serial port {port} opened successfully at {baudrate} baud")
        logger.info(f"DTR: {conn.dtr}, RTS: {conn.rts}")
        return conn
    except serial.SerialException as e:
        logger.error(f"Failed to open serial port: {e}")
        return None


def read_serial_message(conn: serial.Serial, processing: bool) -> Optional[str]:
    """Read a complete message from serial port."""
    try:
        if processing:
            if conn.in_waiting > 0:
                discarded_bytes = conn.read(conn.in_waiting)
                logger.info(f"Ignored message while processing: {discarded_bytes}")
            return None

        bytes_waiting = conn.in_waiting
        if bytes_waiting > 0:
            logger.info(f"Bytes waiting: {bytes_waiting}")

            raw_message_line = conn.readline()

            conn.reset_input_buffer()
            time.sleep(0.1)
            bytes_waiting = conn.in_waiting
            if bytes_waiting > 0:
                raw_message_all = conn.read(bytes_waiting)
            else:
                raw_message_all = b''

            logger.info(f"Readline result: {raw_message_line} (hex: {raw_message_line.hex()})")
            logger.info(f"Read all result: {raw_message_all} (hex: {raw_message_all.hex()})")

            raw_message = raw_message_line if raw_message_line else raw_message_all

            if raw_message:
                try:
                    message_utf8 = raw_message.decode('utf-8', errors='replace').strip()
                    message_ascii = raw_message.decode('ascii', errors='replace').strip()
                    message_latin1 = raw_message.decode('latin-1', errors='replace').strip()
                except Exception:
                    message_utf8 = message_ascii = message_latin1 = "DECODE_ERROR"

                logger.info(f"UTF-8 decoded: '{message_utf8}' (length: {len(message_utf8)})")
                logger.info(f"ASCII decoded: '{message_ascii}' (length: {len(message_ascii)})")

                print(f"\n{'='*60}")
                print(f"MESSAGE FROM ACORN A310:")
                print(f"    Raw bytes: {raw_message}")
                print(f"    Hex: {raw_message.hex()}")
                print(f"    UTF-8: '{message_utf8}' (len: {len(message_utf8)})")
                print(f"    ASCII: '{message_ascii}' (len: {len(message_ascii)})")
                print(f"{'='*60}")

                message = message_utf8 or message_ascii or message_latin1
                return message if message and message.strip() else "empty_message"

    except Exception as e:
        logger.error(f"Error reading serial: {e}")
    return None


def send_serial_response(conn: serial.Serial, response: str):
    """Send response back through serial port."""
    try:
        response_bytes = (response + '\n').encode('utf-8')
        conn.write(response_bytes)
        conn.flush()
        logger.info(f"Response sent: {response}")
        print(f"\nARMGPT RESPONSE TO ACORN:")
        print(f"    {response}")
        print(f"{'─'*60}\n")
    except Exception as e:
        logger.error(f"Error sending response: {e}")


# ─── Main loop ───────────────────────────────────────────────────

def run(port: str, baudrate: int, ollama_url: str,
        chat_model: str, embed_model: str, index_path: str):
    """Main server loop."""
    logger.info("=" * 60)
    logger.info("Starting ArmGPT Server")
    logger.info(f"Port: {port}")
    logger.info(f"Baudrate: {baudrate}")
    logger.info(f"Chat model: {chat_model}")
    logger.info(f"Embed model: {embed_model}")
    logger.info(f"Index: {index_path}")
    logger.info("=" * 60)

    # 1. Check Ollama
    if not check_ollama(ollama_url):
        logger.error("Ollama is not reachable. Please start Ollama and try again.")
        return

    # 2. Load index
    index = load_index(index_path)
    if not index:
        logger.warning("No index loaded — RAG context will be unavailable.")

    # 3. Init serial
    conn = init_serial(port, baudrate)
    if conn is None:
        logger.error("Failed to initialize serial port")
        return

    logger.info("ArmGPT Server ready. Listening for messages...")

    print(f"\nArmGPT Server is ready and listening!")
    print(f"Serial port: {port} at {baudrate} baud")
    print(f"Chat model: {chat_model}")
    print(f"Embed model: {embed_model}")
    print(f"Index chunks: {len(index)}")
    print(f"Logs: {log_filename}")
    print(f"\n{'='*60}")
    print(f"  Waiting for messages from Acorn Archimedes A310...")
    print(f"{'='*60}\n")

    message_count = 0
    error_count = 0
    processing = False

    try:
        while True:
            message = read_serial_message(conn, processing)

            if message:
                message_count += 1
                logger.info(f"Message #{message_count}")

                processing = True

                try:
                    logger.info("Generating response...")
                    start_time = time.time()

                    if is_conversational(message):
                        # Simple conversation — personality only, no RAG
                        logger.info("Conversational message detected, skipping RAG")
                        messages = [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": message},
                        ]
                    else:
                        # Substantive query — use RAG
                        query_emb = embed_query(message, ollama_url, embed_model)
                        context = retrieve_context(query_emb, index, top_k=5)

                        if context:
                            system_content = (
                                SYSTEM_PROMPT + "\n\n" + RAG_GROUNDING +
                                "\n\n--- Retrieved Context ---\n" + context
                            )
                        else:
                            system_content = SYSTEM_PROMPT

                        messages = [
                            {"role": "system", "content": system_content},
                            {"role": "user", "content": message},
                        ]

                    response = ollama_chat(messages, ollama_url, chat_model)

                    generation_time = time.time() - start_time
                    logger.info(f"Response generation completed in {generation_time:.2f} seconds")
                    print(f"  Generation time: {generation_time:.2f} seconds")

                    if not response:
                        response = "Sorry, I couldn't generate a response right now. Please try again!"
                        error_count += 1
                        logger.error(f"Empty response — error count: {error_count}")

                    send_serial_response(conn, response)

                finally:
                    processing = False

            time.sleep(0.01)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        error_count += 1
    finally:
        logger.info("=" * 60)
        logger.info("Session Summary")
        logger.info(f"Total messages processed: {message_count}")
        logger.info(f"Total errors: {error_count}")
        logger.info(f"Log file: {log_filename}")
        logger.info("=" * 60)

        if conn and conn.is_open:
            conn.close()
            logger.info("Serial port closed")


def main():
    parser = argparse.ArgumentParser(description='ArmGPT Server - Serial LLM Interface')
    parser.add_argument('port', choices=['usb', 'serial'],
                        help="Serial port to use: 'usb' for /dev/ttyUSB0, 'serial' for /dev/serial0")
    parser.add_argument('--baudrate', type=int, default=9600,
                        help='Baud rate (default: 9600)')
    parser.add_argument('--chat-model', default='qwen2.5:1.5b',
                        help='Ollama chat model (default: qwen2.5:1.5b)')
    parser.add_argument('--embed-model', default='nomic-embed-text',
                        help='Ollama embedding model (default: nomic-embed-text)')
    parser.add_argument('--ollama-url', default='http://localhost:11434',
                        help='Ollama API base URL (default: http://localhost:11434)')
    parser.add_argument('--index', default='data/arm_index.jsonl',
                        help='Path to JSONL vector index (default: data/arm_index.jsonl)')

    args = parser.parse_args()

    port = SERIAL_PORTS[args.port]
    print(f"Using serial port: {port} ({args.port})")

    run(
        port=port,
        baudrate=args.baudrate,
        ollama_url=args.ollama_url,
        chat_model=args.chat_model,
        embed_model=args.embed_model,
        index_path=args.index,
    )


if __name__ == "__main__":
    main()
