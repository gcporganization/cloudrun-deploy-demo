# appengine-deployment/src/main.py
import os
from flask import Flask, render_template_string, request
from google.auth.transport import requests
from google.oauth2 import id_token
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# HTML template for the welcome page
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ app_title }}</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
            max-width: 600px;
            width: 90%;
        }
        h1 {
            color: #333;
            margin-bottom: 1rem;
        }
        .welcome-message {
            color: #666;
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
        }
        .user-info {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        .status {
            color: #28a745;
            font-weight: bold;
        }
        .footer {
            margin-top: 2rem;
            color: #999;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎉 {{ app_title }}</h1>
        <div class="welcome-message">
            <p>Congratulations! Your App Engine application is running successfully.</p>
            <p class="status">✅ Azure AD Integration: Ready for Configuration</p>
        </div>
        
        <div class="user-info">
            <h3>User Information</h3>
            {% if user_email %}
                <p><strong>Email:</strong> {{ user_email }}</p>
                <p><strong>Name:</strong> {{ user_name or 'Not provided' }}</p>
            {% else %}
                <p>No user information available (IAP not configured yet)</p>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>Powered by Google App Engine + Identity-Aware Proxy</p>
            <p>Ready for Azure AD integration</p>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def hello_world():
    # Get user information from IAP headers (when configured)
    user_email = request.headers.get('X-Goog-Authenticated-User-Email', '').replace('accounts.google.com:', '')
    user_name = request.headers.get('X-Goog-Authenticated-User-Name', '')
    
    app_title = os.environ.get('APP_TITLE', 'Hello World App')
    
    return render_template_string(
        HTML_TEMPLATE,
        app_title=app_title,
        user_email=user_email if user_email else None,
        user_name=user_name if user_name else None
    )

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'App Engine service is running'}, 200

@app.route('/info')
def info():
    return {
        'service': 'App Engine Hello World',
        'version': '1.0.0',
        'iap_ready': True,
        'azure_ad_integration': 'Pending Configuration'
    }

if __name__ == '__main__':
    # This is used when running locally only. When deploying to App Engine,
    # the gunicorn webserver is used to run the app.
    app.run(host='127.0.0.1', port=8080, debug=True)