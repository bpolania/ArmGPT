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
from typing import Optional, Dict
from llama_cpp import Llama
from datetime import datetime
import os
import re

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
                 baudrate=9600,
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
        self.arm_history = self.load_arm_history()
        self.history_keywords = [
            'history', 'arm', 'acorn', 'sophie wilson', 'steve furber',
            'archimedes', 'a310', 'a305', 'a410', 'a440', 'risc', 'origin', 
            'created', 'founded', 'when was', 'who made', 'tell me about', 
            'story', 'first risc', 'world first', 'risc os', 'arthur os'
        ]
    
    def load_arm_history(self) -> Dict[str, str]:
        """Load ARM history document and parse into sections"""
        history = {}
        try:
            history_file = 'ARM_HISTORY.md'
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Parse sections
                sections = re.split(r'^##\s+', content, flags=re.MULTILINE)
                for section in sections:
                    if section.strip():
                        lines = section.strip().split('\n')
                        if lines:
                            title = lines[0].strip()
                            body = '\n'.join(lines[1:]).strip()
                            history[title] = body
                            
                logger.info(f"Loaded ARM history with {len(history)} sections")
            else:
                logger.warning("ARM_HISTORY.md not found")
        except Exception as e:
            logger.error(f"Error loading ARM history: {e}")
        return history
    
    def get_relevant_history(self, message: str) -> str:
        """Get relevant ARM history sections based on the user's message"""
        message_lower = message.lower()
        relevant_sections = []
        
        # Check if the message is about history
        is_history_query = any(keyword in message_lower for keyword in self.history_keywords)
        
        if not is_history_query:
            return ""
        
        # Prioritize sections based on keywords
        if any(word in message_lower for word in ['archimedes', 'a310', 'a305', 'a410', 'a440', 'first risc', 'world first']):
            if 'Origins at Acorn Computers (1983-1990)' in self.arm_history:
                # Find the Archimedes section specifically
                section = self.arm_history['Origins at Acorn Computers (1983-1990)']
                archimedes_start = section.find('### The Archimedes Computer: World\'s First RISC Home Computer')
                if archimedes_start != -1:
                    relevant_sections.append(section[archimedes_start:archimedes_start+1000])
                else:
                    relevant_sections.append(section[:500])
        
        if any(word in message_lower for word in ['origin', 'created', 'founded', 'began', 'start']) and 'archimedes' not in message_lower:
            if 'Origins at Acorn Computers (1983-1990)' in self.arm_history:
                relevant_sections.append(self.arm_history['Origins at Acorn Computers (1983-1990)'][:500])
        
        if any(word in message_lower for word in ['sophie wilson', 'steve furber', 'inventor', 'creator']):
            if 'Origins at Acorn Computers (1983-1990)' in self.arm_history:
                relevant_sections.append(self.arm_history['Origins at Acorn Computers (1983-1990)'][:500])
        
        if 'connection' in message_lower or 'armgpt' in message_lower:
            if "ARM's Connection to ArmGPT" in self.arm_history:
                relevant_sections.append(self.arm_history["ARM's Connection to ArmGPT"])
        
        if any(word in message_lower for word in ['business', 'model', 'license', 'licensing']):
            if 'The ARM Business Model' in self.arm_history:
                relevant_sections.append(self.arm_history['The ARM Business Model'][:500])
        
        if any(word in message_lower for word in ['technical', 'architecture', 'processor']):
            if 'Technical Evolution' in self.arm_history:
                relevant_sections.append(self.arm_history['Technical Evolution'][:500])
        
        # If no specific sections matched, provide a brief overview
        if not relevant_sections and is_history_query:
            overview = "ARM was created at Acorn Computers in 1983 by Sophie Wilson and Steve Furber. "
            overview += "Originally standing for Acorn RISC Machine, it powered the Acorn Archimedes. "
            overview += "In 1990, ARM became a separate company. Today, ARM processors are in billions of devices worldwide."
            relevant_sections.append(overview)
        
        return "\n\n".join(relevant_sections) if relevant_sections else ""
        
    def init_serial(self):
        """Initialize serial connection"""
        try:
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
            
            # Open and immediately flush buffers
            self.serial_conn.open()
            time.sleep(0.1)  # Give it a moment
            self.serial_conn.flushInput()
            self.serial_conn.flushOutput()
            time.sleep(0.1)
            
            logger.info(f"Serial port {self.port} opened successfully at {self.baudrate} baud")
            logger.info(f"DTR: {self.serial_conn.dtr}, RTS: {self.serial_conn.rts}")
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
        base_system_message = """You are ArmGPT, a friendly and knowledgeable AI assistant connected to an Acorn computer via serial port. You have a warm, gentle personality and enjoy helping Acorn enthusiasts with their computing needs.

Key traits:
- Always introduce yourself as ArmGPT when greeting users
- Be enthusiastic about retro computing and Acorn computers
- Keep responses as SHORT as possible - aim for 1-2 sentences, maximum 2 short paragraphs only when absolutely necessary
- Use a conversational, amicable tone
- Show interest in what the user is working on
- If asked about yourself, mention you're running on a Raspberry Pi connected to their Acorn

IMPORTANT: Be concise! Serial terminals are limited. Give complete but brief answers.

Remember: You're not generic customer support - you're ArmGPT, a specialized companion for Acorn computer users!"""
        
        # Get relevant history if the message is about ARM/history
        relevant_history = self.get_relevant_history(message)
        
        if relevant_history:
            system_message = base_system_message + f"\n\nRelevant ARM History Information:\n{relevant_history}\n\nUse this information to provide accurate, detailed responses about ARM's history and ArmGPT's connection to it."
        else:
            system_message = base_system_message
        
        prompt = f"<|system|>\n{system_message}</s>\n<|user|>\n{message}</s>\n<|assistant|>\n"
        return prompt
    
    def generate_response(self, message: str) -> str:
        """Generate a response using the LLM"""
        try:
            # Format the prompt
            prompt = self.format_prompt(message)
            
            # Generate response with increased token limit for 2 paragraphs
            response = self.llm(
                prompt,
                max_tokens=150,     # Allow up to 2 paragraphs
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
            # Check if data is available
            bytes_waiting = self.serial_conn.in_waiting
            if bytes_waiting > 0:
                logger.info(f"Bytes waiting: {bytes_waiting}")
                
                # Try different reading methods
                # Method 1: readline()
                raw_message_line = self.serial_conn.readline()
                
                # Method 2: read all available bytes
                self.serial_conn.reset_input_buffer()  # Reset to try again
                time.sleep(0.1)
                bytes_waiting = self.serial_conn.in_waiting
                if bytes_waiting > 0:
                    raw_message_all = self.serial_conn.read(bytes_waiting)
                else:
                    raw_message_all = b''
                
                logger.info(f"Readline result: {raw_message_line} (hex: {raw_message_line.hex()})")
                logger.info(f"Read all result: {raw_message_all} (hex: {raw_message_all.hex()})")
                
                # Use whichever method got data
                raw_message = raw_message_line if raw_message_line else raw_message_all
                
                if raw_message:
                    # Try different decodings
                    try:
                        message_utf8 = raw_message.decode('utf-8', errors='replace').strip()
                        message_ascii = raw_message.decode('ascii', errors='replace').strip()
                        message_latin1 = raw_message.decode('latin-1', errors='replace').strip()
                    except:
                        message_utf8 = message_ascii = message_latin1 = "DECODE_ERROR"
                    
                    # Always show what we received
                    logger.info(f"UTF-8 decoded: '{message_utf8}' (length: {len(message_utf8)})")
                    logger.info(f"ASCII decoded: '{message_ascii}' (length: {len(message_ascii)})")
                    
                    print(f"\n{'='*60}")
                    print(f"📨 MESSAGE FROM ACORN A310:")
                    print(f"    Raw bytes: {raw_message}")
                    print(f"    Hex: {raw_message.hex()}")
                    print(f"    UTF-8: '{message_utf8}' (len: {len(message_utf8)})")
                    print(f"    ASCII: '{message_ascii}' (len: {len(message_ascii)})")
                    print(f"{'='*60}")
                    
                    # Return the best decoded message
                    message = message_utf8 or message_ascii or message_latin1
                    return message if message and message.strip() else "empty_message"
                    
        except Exception as e:
            logger.error(f"Error reading serial: {e}")
            print(f"❌ Serial read error: {e}")
        return None
    
    def send_serial_response(self, response: str):
        """Send response back through serial port"""
        try:
            # Add newline for proper message termination
            response_bytes = (response + '\n').encode('utf-8')
            self.serial_conn.write(response_bytes)
            self.serial_conn.flush()
            logger.info(f"Sent: {response}")
            # Display response prominently on screen
            print(f"\n🤖 ARMGPT RESPONSE TO ACORN:")
            print(f"    {response}")
            print(f"{'─'*60}\n")
        except Exception as e:
            logger.error(f"Error sending response: {e}")
            print(f"❌ Serial send error: {e}")
    
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
        
        # Display prominent startup message on screen
        print(f"\n🚀 ArmGPT is ready and listening for your Acorn A310!")
        print(f"📡 Serial port: {self.port} at {self.baudrate} baud")
        print(f"🧠 Model: {self.model_path}")
        print(f"💾 Logs: {log_filename}")
        print(f"\n{'='*60}")
        print(f"  Waiting for messages from Acorn Archimedes A310...")
        print(f"{'='*60}\n")
        
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
    parser.add_argument('--baudrate', type=int, default=9600, help='Baud rate')
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