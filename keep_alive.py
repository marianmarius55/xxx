from flask import Flask, render_template_string
from threading import Thread
import time

app = Flask('')

# Global variables to store logs and stats
logs = []
stats = {"accounts": 0, "orders": 0}
max_logs = 1000

def add_log(level, message):
    """Add a log entry"""
    global logs
    timestamp = time.strftime('%H:%M:%S')
    logs.append(f"[{timestamp}] {level}: {message}")
    if len(logs) > max_logs:
        logs.pop(0)

def update_stats(accounts=None, orders=None):
    """Update statistics"""
    global stats
    if accounts is not None:
        stats["accounts"] = accounts
    if orders is not None:
        stats["orders"] = orders

@app.route('/')
def home():
    return '<meta http-equiv="refresh" content="0; URL=https://phantom.is-a.dev/support"/>'

@app.route('/logs')
def show_logs():
    """Display logs in real-time"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Registration Logs</title>
        <meta http-equiv="refresh" content="2">
        <style>
            body { font-family: monospace; background: #1a1a1a; color: #00ff00; margin: 20px; }
            .stats { background: #333; padding: 10px; margin-bottom: 20px; border-radius: 5px; }
            .log-container { background: #000; padding: 15px; border-radius: 5px; height: 70vh; overflow-y: auto; }
            .success { color: #00ff00; }
            .error { color: #ff4444; }
            .info { color: #4488ff; }
            .progress-bar { background: #333; height: 20px; border-radius: 10px; margin: 5px 0; }
            .progress-fill { background: #00ff00; height: 100%; border-radius: 10px; transition: width 0.3s; }
        </style>
    </head>
    <body>
        <h1>🤖 Registration Bot Status</h1>
        
        <div class="stats">
            <h3>📊 Statistics</h3>
            <p>Accounts Created: <strong>{{ stats.accounts }}</strong></p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {{ (stats.accounts // 10) | min(100) }}%"></div>
            </div>
            
            <p>Orders Created: <strong>{{ stats.orders }}</strong></p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {{ (stats.orders // 100) | min(100) }}%"></div>
            </div>
        </div>
        
        <div class="log-container">
            <h3>📝 Live Logs (Auto-refresh every 2 seconds)</h3>
            {% for log in logs[-50:] %}
                <div class="{% if 'SUCCESS' in log %}success{% elif 'ERROR' in log %}error{% else %}info{% endif %}">
                    {{ log }}
                </div>
            {% endfor %}
        </div>
        
        <p><em>Last updated: {{ current_time }}</em></p>
    </body>
    </html>
    """
    
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    return render_template_string(html_template, logs=logs, stats=stats, current_time=current_time)

@app.route('/success')
def show_success_only():
    """Display only success logs"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Success Logs</title>
        <meta http-equiv="refresh" content="2">
        <style>
            body { font-family: monospace; background: #1a1a1a; color: #00ff00; margin: 20px; }
            .stats { background: #333; padding: 10px; margin-bottom: 20px; border-radius: 5px; }
            .log-container { background: #000; padding: 15px; border-radius: 5px; height: 70vh; overflow-y: auto; }
            .success { color: #00ff00; }
            .progress-bar { background: #333; height: 20px; border-radius: 10px; margin: 5px 0; }
            .progress-fill { background: #00ff00; height: 100%; border-radius: 10px; transition: width 0.3s; }
        </style>
    </head>
    <body>
        <h1>✅ Success Logs Only</h1>
        
        <div class="stats">
            <h3>📊 Statistics</h3>
            <p>Accounts Created: <strong>{{ stats.accounts }}</strong></p>
            <p>Orders Created: <strong>{{ stats.orders }}</strong></p>
            <p><a href="/logs" style="color: #4488ff;">View All Logs</a></p>
        </div>
        
        <div class="log-container">
            <h3>🎉 Success Logs (Auto-refresh every 2 seconds)</h3>
            {% for log in success_logs[-50:] %}
                <div class="success">{{ log }}</div>
            {% endfor %}
        </div>
        
        <p><em>Last updated: {{ current_time }}</em></p>
    </body>
    </html>
    """
    
    success_logs = [log for log in logs if "SUCCESS" in log]
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    return render_template_string(html_template, success_logs=success_logs, stats=stats, current_time=current_time)

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# Export functions for use in main script
__all__ = ['keep_alive', 'add_log', 'update_stats']

