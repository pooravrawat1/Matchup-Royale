#!/usr/bin/env python3
"""
Configuration settings for Matchup Royale
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class to manage application settings"""
    
    def __init__(self):
        # API Configuration
        self.CLASH_ROYALE_API_TOKEN = os.getenv('CLASH_ROYALE_API_TOKEN')
        self.API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.clashroyale.com/v1')
        
        # Database Configuration
        self.DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/matchup_royale.db')
        
        # Logging Configuration
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
        
        # Data Collection Configuration
        self.UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '3600'))  # 1 hour default
        self.MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
        
    def validate(self) -> bool:
        """Validate configuration settings"""
        errors = []
        
        # Check required API token
        if not self.CLASH_ROYALE_API_TOKEN:
            errors.append("CLASH_ROYALE_API_TOKEN is required")
        
        # Check database directory exists
        db_dir = os.path.dirname(self.DATABASE_PATH)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create database directory {db_dir}: {e}")
        
        # Check logs directory exists
        log_dir = os.path.dirname(self.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create logs directory {log_dir}: {e}")
        
        if errors:
            print("Configuration errors:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        return True
    
    def get_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary"""
        return {
            'CLASH_ROYALE_API_TOKEN': self.CLASH_ROYALE_API_TOKEN,
            'API_BASE_URL': self.API_BASE_URL,
            'DATABASE_PATH': self.DATABASE_PATH,
            'LOG_LEVEL': self.LOG_LEVEL,
            'LOG_FILE': self.LOG_FILE,
            'UPDATE_INTERVAL': self.UPDATE_INTERVAL,
            'MAX_RETRIES': self.MAX_RETRIES
        }

# Global configuration instance
config = Config()