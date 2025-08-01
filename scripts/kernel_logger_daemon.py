#!/usr/bin/env python3

import os
import sys
import time
import select
import struct
from datetime import datetime
from loguru import logger

class KernelLoggerDaemon:
    def __init__(self):
        self.kmsg = open("/dev/kmsg", "rb", buffering=0)
        self.setup_logging()
        
    def setup_logging(self):
        log_path = os.getenv("KERNEL_LOG_PATH", "/var/log/kernel")
        log_level = os.getenv("KERNEL_LOG_LEVEL", "DEBUG")
        max_size = os.getenv("KERNEL_LOG_MAX_SIZE", "100MB")
        rotate_count = int(os.getenv("KERNEL_LOG_ROTATE_COUNT", "5"))
        
        # Ensure log directory exists
        os.makedirs(log_path, exist_ok=True)
        
        # Configure loguru logger
        logger.remove()  # Remove default handler
        logger.add(
            f"{log_path}/kernel.log",
            rotation=max_size,
            retention=rotate_count,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}"
        )
        
        # Special handlers for different types of logs
        logger.add(
            f"{log_path}/errors.log",
            rotation=max_size,
            retention=rotate_count,
            level="ERROR",
            filter=lambda record: record["level"].name == "ERROR"
        )
        
        logger.add(
            f"{log_path}/build_errors.log",
            rotation=max_size,
            retention=rotate_count,
            filter=lambda record: "build error" in record["message"].lower()
        )
        
        logger.add(
            f"{log_path}/runtime_errors.log",
            rotation=max_size,
            retention=rotate_count,
            filter=lambda record: "runtime error" in record["message"].lower()
        )

    def parse_kmsg_line(self, line):
        """Parse a kernel message line and extract priority, timestamp, etc."""
        try:
            # Kernel message format: "<priority>timestamp,sequence;message"
            priority = struct.unpack('B', line[1:2])[0]
            parts = line.decode('utf-8').split(';', 1)
            if len(parts) != 2:
                return None
                
            metadata, message = parts
            meta_parts = metadata.split(',')
            if len(meta_parts) != 2:
                return None
                
            timestamp = float(meta_parts[0].split('>')[1]) / 1000000.0  # Convert to seconds
            
            return {
                'priority': priority,
                'timestamp': timestamp,
                'message': message.strip()
            }
        except Exception as e:
            logger.error(f"Error parsing kmsg line: {e}")
            return None

    def log_message(self, msg_data):
        """Log message with appropriate level based on priority"""
        if not msg_data:
            return
            
        priority = msg_data['priority']
        message = msg_data['message']
        
        # Map kernel log levels to loguru levels
        if priority <= 3:  # KERN_ERR or higher
            logger.error(message)
        elif priority == 4:  # KERN_WARNING
            logger.warning(message)
        elif priority == 5:  # KERN_NOTICE
            logger.info(message)
        else:  # KERN_INFO or lower
            logger.debug(message)

    def run(self):
        """Main loop to continuously monitor kernel messages"""
        logger.info("Kernel logger daemon started")
        
        try:
            while True:
                # Use select to wait for data with timeout
                ready, _, _ = select.select([self.kmsg], [], [], 1.0)
                
                if ready:
                    line = self.kmsg.readline()
                    if line:
                        msg_data = self.parse_kmsg_line(line)
                        self.log_message(msg_data)
                        
        except KeyboardInterrupt:
            logger.info("Kernel logger daemon stopped")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.kmsg.close()

if __name__ == "__main__":
    daemon = KernelLoggerDaemon()
    daemon.run()