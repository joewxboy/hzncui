"""Configuration management for Open Horizon CUI.

This module handles loading and validating configuration from environment variables
and .env files.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

class ConfigError(Exception):
    """Raised when there is an error with configuration."""
    pass

def load_config() -> None:
    """Load configuration from .env file and environment variables.
    
    This function will:
    1. Try to load from .env file if it exists
    2. Fall back to environment variables
    3. Validate required configuration is present
    """
    # Try to load .env file
    env_path = Path('.') / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    
    # Validate required configuration
    required_vars = ['HZN_ORG_ID', 'HZN_EXCHANGE_URL', 'EXCHANGE_USER_ADMIN_PW']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ConfigError(
            f"Missing required configuration: {', '.join(missing_vars)}\n"
            "Please set these in your .env file or environment variables."
        )

def get_config(key: str, default: Optional[str] = None) -> str:
    """Get a configuration value.
    
    Args:
        key: The configuration key to retrieve
        default: Optional default value if key is not found
        
    Returns:
        The configuration value
        
    Raises:
        ConfigError: If the key is required but not found
    """
    value = os.getenv(key, default)
    if value is None:
        raise ConfigError(f"Required configuration '{key}' not found")
    return value 