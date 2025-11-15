"""Configuration settings for the Meeting Planner Assistant."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    
    # Mock Mode
    USE_MOCK_API = os.getenv('USE_MOCK_API', 'False').lower() == 'true'
    
    # Microsoft Graph API
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    TENANT_ID = os.getenv('TENANT_ID')
    
    # Graph API endpoints
    AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
    SCOPE = ['https://graph.microsoft.com/.default']
    GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'
    
    # Flask settings
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    @staticmethod
    def validate():
        """Validate that required configuration is present."""
        # Skip validation if using mock API
        if Config.USE_MOCK_API:
            print("⚠️  Running in MOCK MODE - No real Graph API calls will be made")
            return
            
        required = ['CLIENT_ID', 'CLIENT_SECRET', 'TENANT_ID']
        missing = [key for key in required if not getattr(Config, key)]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
