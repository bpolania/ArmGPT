#!/bin/bash
# Download quantized TinyLlama model for use with llama-cpp-python

echo "Downloading quantized TinyLlama model..."
echo "This is optimized for Raspberry Pi with limited RAM"

# Create models directory if it doesn't exist
mkdir -p models

# Download the Q4_K_M quantized model (about 670MB)
wget -O models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf \
    https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf

echo "Model downloaded to models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
echo "You can now run the lightweight interface with:"
echo "source venv/bin/activate"
echo "python serial_llm_interface_lite.py --model models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"