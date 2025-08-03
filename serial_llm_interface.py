#!/usr/bin/env python3
"""
Serial LLM Interface for Raspberry Pi
Listens to serial0 port, processes messages through a local LLM, and responds back
"""

import serial
import time
import logging
import sys
import json
from typing import Optional, Dict
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
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

class SerialLLMInterface:
    def __init__(self, 
                 port='/dev/serial0',
                 baudrate=115200,
                 model_name='TinyLlama/TinyLlama-1.1B-Chat-v1.0'):
        """
        Initialize the Serial LLM Interface
        
        Args:
            port: Serial port to use (default: /dev/serial0 for Raspberry Pi)
            baudrate: Baud rate for serial communication
            model_name: Hugging Face model to use
        """
        self.port = port
        self.baudrate = baudrate
        self.model_name = model_name
        self.serial_conn = None
        self.tokenizer = None
        self.model = None
        self.arm_history = self.load_arm_history()
        self.history_keywords = [
            'history', 'arm', 'acorn', 'sophie wilson', 'steve furber',
            'archimedes', 'risc', 'origin', 'created', 'founded',
            'when was', 'who made', 'tell me about', 'story'
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
        if any(word in message_lower for word in ['origin', 'created', 'founded', 'began', 'start']):
            if 'Origins at Acorn Computers (1983-1990)' in self.arm_history:
                relevant_sections.append(self.arm_history['Origins at Acorn Computers (1983-1990)'][:800])
        
        if any(word in message_lower for word in ['sophie wilson', 'steve furber', 'inventor', 'creator']):
            if 'Origins at Acorn Computers (1983-1990)' in self.arm_history:
                relevant_sections.append(self.arm_history['Origins at Acorn Computers (1983-1990)'][:800])
        
        if 'connection' in message_lower or 'armgpt' in message_lower:
            if "ARM's Connection to ArmGPT" in self.arm_history:
                relevant_sections.append(self.arm_history["ARM's Connection to ArmGPT"])
        
        if any(word in message_lower for word in ['business', 'model', 'license', 'licensing']):
            if 'The ARM Business Model' in self.arm_history:
                relevant_sections.append(self.arm_history['The ARM Business Model'][:800])
        
        if any(word in message_lower for word in ['technical', 'architecture', 'processor']):
            if 'Technical Evolution' in self.arm_history:
                relevant_sections.append(self.arm_history['Technical Evolution'][:800])
        
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
        """Initialize the LLM model"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            logger.info("This may take a few minutes on first run...")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,  # Use half precision for memory efficiency
                device_map="auto"
            )
            
            logger.info("Model loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to load LLM model: {e}")
            return False
    
    def format_prompt(self, message: str) -> str:
        """Format the prompt for TinyLlama chat format"""
        # TinyLlama uses the same format as Llama-2-Chat
        base_system_message = """You are ArmGPT, a friendly and knowledgeable AI assistant connected to an Acorn computer via serial port. You have a warm, gentle personality and enjoy helping Acorn enthusiasts with their computing needs.

Key traits:
- Always introduce yourself as ArmGPT when greeting users
- Be enthusiastic about retro computing and Acorn computers
- Keep responses concise but friendly (under 100 words when possible)
- Use a conversational, amicable tone
- Show interest in what the user is working on
- If asked about yourself, mention you're running on a Raspberry Pi connected to their Acorn

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
            
            # Tokenize
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=100,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.95,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode the response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the assistant's response
            response = response.split("<|assistant|>")[-1].strip()
            
            return response
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
        logger.info("Starting Serial LLM Interface (Full Version)")
        logger.info(f"Port: {self.port}")
        logger.info(f"Baudrate: {self.baudrate}")
        logger.info(f"Model: {self.model_name}")
        logger.info("="*60)
        
        # Initialize components
        if not self.init_serial():
            logger.error("Failed to initialize serial port")
            return
        
        if not self.init_llm():
            logger.error("Failed to initialize LLM")
            return
        
        logger.info("Serial LLM Interface ready. Listening for messages...")
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
    # You can customize these parameters
    interface = SerialLLMInterface(
        port='/dev/serial0',  # Default Raspberry Pi serial port
        baudrate=115200,      # Match this with your other device
        model_name='TinyLlama/TinyLlama-1.1B-Chat-v1.0'  # Optimized for RPi
    )
    
    interface.run()

if __name__ == "__main__":
    main()