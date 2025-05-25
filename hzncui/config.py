"""Configuration management for Open Horizon CUI.

This module handles loading and validating configuration from environment variables
and .env files.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class ConfigError(Exception):
    """Raised when there is an error with configuration."""
    pass

def find_env_file() -> Optional[Path]:
    """Find the .env file in various locations.
    
    Returns:
        Path to the .env file if found, None otherwise.
    """
    # List of possible locations for .env file
    possible_locations = [
        Path('.'),  # Current directory
        Path.home(),  # User's home directory
        Path(__file__).parent,  # Package directory
        Path(__file__).parent.parent,  # Project root
    ]
    
    for location in possible_locations:
        env_path = location / '.env'
        if env_path.exists():
            logger.debug(f"Found .env file at: {env_path}")
            return env_path
            
    logger.debug("No .env file found in any of the expected locations")
    return None

def load_config() -> None:
    """Load configuration from .env file and environment variables.
    
    This function will:
    1. Try to load from .env file if it exists
    2. Fall back to environment variables
    3. Validate required configuration is present
    """
    # Try to load .env file
    env_path = find_env_file()
    if env_path:
        logger.info(f"Loading configuration from {env_path}")
        load_dotenv(env_path)
    else:
        logger.info("No .env file found, using environment variables")
    
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