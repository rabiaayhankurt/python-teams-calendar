"""
CORS support for Flask API
Add this to enable cross-origin requests from Power Platform
"""
from flask_cors import CORS

def init_cors(app):
    """Initialize CORS for the Flask app"""
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "https://make.powerapps.com",
                "https://make.powerautomate.com",
                "https://*.copilotstudio.microsoft.com",
                "https://*.powerplatform.com"
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-API-Key"],
            "expose_headers": ["Content-Type"],
            "max_age": 3600
        }
    })
    
    return app
