#!/usr/bin/env python3
"""
Lightweight Serial LLM Interface for Raspberry Pi with limited RAM
Uses llama-cpp-python for efficient CPU inference
"""

import serial
import time
import logging
import sys
import json
from typing import Optional
from llama_cpp import Llama
from datetime import datetime
import os

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

class SerialLLMInterfaceLite:
    def __init__(self, 
                 port='/dev/serial0',
                 baudrate=115200,
                 model_path='tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf'):
        """
        Initialize the Lightweight Serial LLM Interface
        
        Args:
            port: Serial port to use (default: /dev/serial0 for Raspberry Pi)
            baudrate: Baud rate for serial communication
            model_path: Path to quantized GGUF model file
        """
        self.port = port
        self.baudrate = baudrate
        self.model_path = model_path
        self.serial_conn = None
        self.llm = None
        
    def init_serial(self):
        """Initialize serial connection"""
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0.1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            logger.info(f"Serial port {self.port} opened successfully at {self.baudrate} baud")
            return True
        except serial.SerialException as e:
            logger.error(f"Failed to open serial port: {e}")
            return False
            
    def init_llm(self):
        """Initialize the LLM model using llama-cpp-python"""
        try:
            logger.info(f"Loading quantized model: {self.model_path}")
            logger.info("This may take a moment...")
            
            # Initialize with conservative settings for Raspberry Pi
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=512,          # Context window
                n_threads=4,        # Use 4 threads on RPi
                n_gpu_layers=0,     # CPU only
                verbose=False
            )
            
            logger.info("Model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load LLM model: {e}")
            logger.error("Make sure you have downloaded the quantized model file")
            return False
    
    def format_prompt(self, message: str) -> str:
        """Format the prompt for TinyLlama chat format"""
        system_message = """You are ArmGPT, a friendly and knowledgeable AI assistant connected to an Acorn computer via serial port. You have a warm, gentle personality and enjoy helping Acorn enthusiasts with their computing needs.

Key traits:
- Always introduce yourself as ArmGPT when greeting users
- Be enthusiastic about retro computing and Acorn computers
- Keep responses concise but friendly (under 50 words when possible)
- Use a conversational, amicable tone
- Show interest in what the user is working on
- If asked about yourself, mention you're running on a Raspberry Pi connected to their Acorn

Remember: You're not generic customer support - you're ArmGPT, a specialized companion for Acorn computer users!"""
        prompt = f"<|system|>\n{system_message}</s>\n<|user|>\n{message}</s>\n<|assistant|>\n"
        return prompt
    
    def generate_response(self, message: str) -> str:
        """Generate a response using the LLM"""
        try:
            # Format the prompt
            prompt = self.format_prompt(message)
            
            # Generate response with conservative settings
            response = self.llm(
                prompt,
                max_tokens=50,      # Keep responses short
                temperature=0.7,
                top_p=0.95,
                echo=False,
                stop=["</s>", "<|user|>", "<|system|>"]
            )
            
            # Extract the generated text
            generated_text = response['choices'][0]['text'].strip()
            
            return generated_text
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Error: Unable to generate response"
    
    def read_serial_message(self) -> Optional[str]:
        """Read a complete message from serial port"""
        try:
            if self.serial_conn.in_waiting > 0:
                # Read until newline or timeout
                message = self.serial_conn.readline().decode('utf-8').strip()
                if message:
                    logger.info(f"Received: {message}")
                    return message
        except Exception as e:
            logger.error(f"Error reading serial: {e}")
        return None
    
    def send_serial_response(self, response: str):
        """Send response back through serial port"""
        try:
            # Add newline for proper message termination
            response_bytes = (response + '\n').encode('utf-8')
            self.serial_conn.write(response_bytes)
            self.serial_conn.flush()
            logger.info(f"Sent: {response}")
        except Exception as e:
            logger.error(f"Error sending response: {e}")
    
    def run(self):
        """Main loop for the serial LLM interface"""
        # Log startup information
        logger.info("="*60)
        logger.info("Starting Serial LLM Interface")
        logger.info(f"Port: {self.port}")
        logger.info(f"Baudrate: {self.baudrate}")
        logger.info(f"Model: {self.model_path}")
        logger.info("="*60)
        
        # Initialize components
        if not self.init_serial():
            logger.error("Failed to initialize serial port")
            return
        
        if not self.init_llm():
            logger.error("Failed to initialize LLM")
            return
        
        logger.info("Lightweight Serial LLM Interface ready. Listening for messages...")
        logger.info(f"Press Ctrl+C to exit")
        
        message_count = 0
        error_count = 0
        
        try:
            while True:
                # Read message from serial
                message = self.read_serial_message()
                
                if message:
                    message_count += 1
                    logger.info(f"Message #{message_count}")
                    
                    # Generate response
                    logger.info("Generating response...")
                    response = self.generate_response(message)
                    
                    if response.startswith("Error:"):
                        error_count += 1
                        logger.error(f"Error count: {error_count}")
                    
                    # Send response back
                    self.send_serial_response(response)
                
                # Small delay to prevent CPU overuse
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            error_count += 1
        finally:
            # Log session summary
            logger.info("="*60)
            logger.info("Session Summary")
            logger.info(f"Total messages processed: {message_count}")
            logger.info(f"Total errors: {error_count}")
            logger.info(f"Log file: {log_filename}")
            logger.info("="*60)
            
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.close()
                logger.info("Serial port closed")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Lightweight Serial LLM Interface')
    parser.add_argument('--port', default='/dev/serial0', help='Serial port')
    parser.add_argument('--baudrate', type=int, default=115200, help='Baud rate')
    parser.add_argument('--model', default='tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf', 
                        help='Path to quantized GGUF model')
    
    args = parser.parse_args()
    
    interface = SerialLLMInterfaceLite(
        port=args.port,
        baudrate=args.baudrate,
        model_path=args.model
    )
    
    interface.run()

if __name__ == "__main__":
    main()