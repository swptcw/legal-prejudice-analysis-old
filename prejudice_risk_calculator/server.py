#!/usr/bin/env python3
"""
Simple HTTP server for the Legal Prejudice Risk Calculator
"""

import http.server
import socketserver
import os
import webbrowser
from urllib.parse import urlparse

# Configuration
PORT = 8080  # Changed from 8000 to 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler that serves from the current directory"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        # Redirect root to index.html
        if self.path == '/':
            self.path = '/templates/index.html'
        
        # Handle other requests normally
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def log_message(self, format, *args):
        """Log server activity"""
        print(f"[SERVER] {format % args}")

def run_server():
    """Run the HTTP server"""
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}/")
        print(f"Press Ctrl+C to stop the server")
        
        # Open browser automatically
        # Commented out to avoid issues in the sandbox environment
        # webbrowser.open(f"http://localhost:{PORT}/")
        
        # Keep the server running
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    run_server()