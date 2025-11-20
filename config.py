"""
Configuration file for environment variables
"""
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')

# Smithery Configuration
SMITHERY_API_KEY = os.getenv('SMITHERY_API_KEY')
SMITHERY_PROFILE_ID = os.getenv('SMITHERY_PROFILE_ID')
SMITHERY_API_URL = 'https://api.smithery.ai/v1'

# Flask Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = None  # 16 * 1024 * 1024
# 16MB

# Aurite Configuration
AURITE_PROJECT_NAME = 'csv-data-analysis-agent'
AURITE_SERVER_NAME = 'csv-analysis-server'





