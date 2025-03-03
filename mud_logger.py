#!/usr/bin/env python3

import telnetlib
import sys
import json
import os
import time
from datetime import datetime
import threading
import queue

class MudLogger:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.log_dir = os.path.expanduser("~/mud_logs")
        self.session_data = {
            "host": host,
            "port": port,
            "start_time": datetime.now().isoformat(),
            "interactions": [],
            "end_time": None
        }
        os.makedirs(self.log_dir, exist_ok=True)
        self.filename = os.path.join(
            self.log_dir,
            f"mud_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        self.tn = None
        self.input_queue = queue.Queue()

    def save_session(self):
        """Save the session data to JSON file"""
        self.session_data["end_time"] = datetime.now().isoformat()
        with open(self.filename, 'w') as f:
            json.dump(self.session_data, f, indent=2)
        print(f"\nSession saved to {self.filename}")

    def handle_input(self):
        """Handle user input in a separate thread"""
        while True:
            try:
                user_input = input().strip() + "\n"
                if user_input.lower() == "quit\n":
                    break
                self.input_queue.put(user_input)
                self.session_data["interactions"].append({
                    "timestamp": datetime.now().isoformat(),
                    "type": "input",
                    "data": user_input.strip()
                })
            except EOFError:
                break

    def run(self):
        """Main telnet session loop"""
        try:
            # Start telnet connection
            self.tn = telnetlib.Telnet(self.host, self.port)
            print(f"Connected to {self.host}:{self.port}")
            print("Type 'quit' on a new line to exit")

            # Start input thread
            input_thread = threading.Thread(target=self.handle_input, daemon=True)
            input_thread.start()

            while True:
                # Check for server output
                try:
                    output = self.tn.read_eager().decode('ascii', errors='replace')
                    if output:
                        print(output, end='', flush=True)
                        self.session_data["interactions"].append({
                            "timestamp": datetime.now().isoformat(),
                            "type": "output",
                            "data": output
                        })
                except EOFError:
                    break

                # Check for user input
                try:
                    user_input = self.input_queue.get_nowait()
                    self.tn.write(user_input.encode('ascii'))
                except queue.Empty:
                    pass

                # Small sleep to prevent CPU hogging
                time.sleep(0.01)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            if self.tn:
                self.tn.close()
            self.save_session()

def main():
    if len(sys.argv) != 3:
        print("Usage: python mud_logger.py <host> <port>")
        print("Example: python mud_logger.py discworld.starturtle.net 4242")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    logger = MudLogger(host, port)
    logger.run()

if __name__ == "__main__":
    main()
