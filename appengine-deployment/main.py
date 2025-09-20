# appengine-deployment/src/main.py
import os
from flask import Flask, render_template_string, request
import base64
import json
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
        .user-info, .claims-info {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
            text-align: left;
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
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
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
                <p><strong>Groups:</strong> {{ user_groups | join(', ') if user_groups else 'No groups assigned' }}</p>
            {% else %}
                <p>No user information available (IAP not configured yet)</p>
            {% endif %}
        </div>

        <div class="claims-info">
            <h3>IAP JWT Claims</h3>
            {% if iap_claims %}
                <pre>{{ iap_claims | tojson(indent=2) }}</pre>
            {% else %}
                <p>No IAP JWT claims available</p>
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

def decode_iap_jwt(iap_jwt):
    """Decode IAP JWT payload (without signature verification)"""
    try:
        parts = iap_jwt.split('.')
        if len(parts) != 3:
            return {}
        payload_b64 = parts[1] + "=" * (-len(parts[1]) % 4)  # pad base64
        payload_json = base64.urlsafe_b64decode(payload_b64.encode('utf-8'))
        payload = json.loads(payload_json.decode("utf-8"))
        return payload
    except Exception as e:
        logging.error(f"Failed to decode IAP JWT: {e}")
        return {"error": str(e)}

@app.route('/')
def hello_world():
    iap_jwt = request.headers.get('x-goog-iap-jwt-assertion')
    user_email = None
    user_name = None
    user_groups = []
    iap_claims = {}

    if iap_jwt:
        payload = decode_iap_jwt(iap_jwt)
        iap_claims = {k: {"type": type(v).__name__, "value": str(v)[:200]} for k, v in payload.items()}
        user_email = payload.get('email')
        user_name = payload.get('name') or payload.get('given_name')
        user_groups = payload.get('groups', [])

    app_title = os.environ.get('APP_TITLE', 'Hello World App')

    return render_template_string(
        HTML_TEMPLATE,
        app_title=app_title,
        user_email=user_email,
        user_name=user_name,
        user_groups=user_groups,
        iap_claims=iap_claims
    )

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'message': 'App Engine service is running'}, 200

@app.route('/info')
def info():
    return {
        'service': 'App Engine Hello World',
        'version': '1.0.2',
        'iap_ready': True,
        'azure_ad_integration': 'Pending Configuration'
    }

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
