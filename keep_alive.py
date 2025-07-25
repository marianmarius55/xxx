from flask import Flask, render_template_string, request
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
def dashboard():
    """Main dashboard with progress bars and filterable logs"""
    filter_type = request.args.get('filter', 'all')
    
    if filter_type == 'success':
        filtered_logs = [log for log in logs if "SUCCESS" in log]
    else:
        filtered_logs = logs
    
    # Calculate progress percentages
    accounts_progress = min(100, (stats["accounts"] * 2))
    orders_progress = min(100, (stats["orders"] / 50))
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Registration Bot Dashboard</title>
        <meta http-equiv="refresh" content="2">
        <style>
            body { 
                font-family: 'Courier New', monospace; 
                background: #0d1117; 
                color: #c9d1d9; 
                margin: 0; 
                padding: 20px;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid #21262d;
                padding-bottom: 20px;
            }
            .stats-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
            }
            .stat-number {
                font-size: 2.5em;
                font-weight: bold;
                color: #58a6ff;
                margin: 10px 0;
            }
            .progress-bar {
                background: #21262d;
                height: 25px;
                border-radius: 12px;
                margin: 15px 0;
                overflow: hidden;
                position: relative;
            }
            .progress-fill {
                background: linear-gradient(90deg, #238636, #2ea043);
                height: 100%;
                border-radius: 12px;
                transition: width 0.5s ease;
                position: relative;
            }
            .progress-text {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            .filter-container {
                margin-bottom: 20px;
                text-align: center;
            }
            .filter-btn {
                background: #21262d;
                border: 1px solid #30363d;
                color: #c9d1d9;
                padding: 10px 20px;
                margin: 0 5px;
                border-radius: 6px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                transition: all 0.3s;
            }
            .filter-btn:hover {
                background: #30363d;
                border-color: #58a6ff;
            }
            .filter-btn.active {
                background: #58a6ff;
                border-color: #58a6ff;
                color: white;
            }
            .logs-container {
                background: #0d1117;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 20px;
                height: 60vh;
                overflow-y: auto;
            }
            .log-entry {
                padding: 8px 12px;
                margin: 2px 0;
                border-radius: 4px;
                border-left: 3px solid transparent;
                font-family: 'Courier New', monospace;
                font-size: 13px;
            }
            .log-success {
                background: rgba(35, 134, 54, 0.1);
                border-left-color: #2ea043;
                color: #7ee787;
            }
            .log-error {
                background: rgba(248, 81, 73, 0.1);
                border-left-color: #f85149;
                color: #ffa198;
            }
            .log-info {
                background: rgba(88, 166, 255, 0.1);
                border-left-color: #58a6ff;
                color: #79c0ff;
            }
            .footer {
                text-align: center;
                margin-top: 20px;
                color: #8b949e;
                font-size: 12px;
            }
            .emoji {
                font-size: 1.2em;
                margin-right: 8px;
            }
            ::-webkit-scrollbar {
                width: 8px;
            }
            ::-webkit-scrollbar-track {
                background: #161b22;
            }
            ::-webkit-scrollbar-thumb {
                background: #30363d;
                border-radius: 4px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: #484f58;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1><span class="emoji">🤖</span>Registration Bot Dashboard</h1>
            <p>Real-time monitoring and statistics</p>
        </div>
        
        <div class="stats-container">
            <div class="stat-card">
                <h3><span class="emoji">👥</span>Accounts Created</h3>
                <div class="stat-number">{{ stats.accounts }}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ accounts_progress }}%">
                        <div class="progress-text">{{ accounts_progress }}%</div>
                    </div>
                </div>
                <small>Target: 50 accounts</small>
            </div>
            
            <div class="stat-card">
                <h3><span class="emoji">💳</span>Orders Created</h3>
                <div class="stat-number">{{ stats.orders }}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{ orders_progress }}%">
                        <div class="progress-text">{{ orders_progress | round(1) }}%</div>
                    </div>
                </div>
                <small>Target: 5000 orders</small>
            </div>
        </div>
        
        <div class="filter-container">
            <h3><span class="emoji">📊</span>Activity Logs</h3>
            <a href="/?filter=all" class="filter-btn {% if filter_type == 'all' %}active{% endif %}">
                <span class="emoji">📋</span>All Logs
            </a>
            <a href="/?filter=success" class="filter-btn {% if filter_type == 'success' %}active{% endif %}">
                <span class="emoji">✅</span>Success Only
            </a>
        </div>
        
        <div class="logs-container">
            {% if filtered_logs %}
                {% for log in filtered_logs[-100:] %}
                    <div class="log-entry {% if 'SUCCESS' in log %}log-success{% elif 'ERROR' in log %}log-error{% else %}log-info{% endif %}">
                        {{ log }}
                    </div>
                {% endfor %}
            {% else %}
                <div class="log-entry log-info">
                    <span class="emoji">⏳</span>Waiting for logs...
                </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>Last updated: {{ current_time }} | Auto-refresh every 2 seconds</p>
            <p><span class="emoji">🔗</span>Dashboard URL: <code>http://localhost:8080</code></p>
        </div>
    </body>
    </html>
    """
    
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    return render_template_string(html_template, 
                                logs=logs, 
                                stats=stats, 
                                current_time=current_time,
                                filter_type=filter_type,
                                filtered_logs=filtered_logs,
                                accounts_progress=accounts_progress,
                                orders_progress=orders_progress)

@app.route('/logs')
def show_logs():
    """Redirect to main dashboard"""
    return dashboard()

@app.route('/success')
def show_success_only():
    """Redirect to success filter"""
    return dashboard() + "?filter=success"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# Export functions for use in main script
__all__ = ['keep_alive', 'add_log', 'update_stats']


