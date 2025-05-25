"""Configuration management for Open Horizon CUI.

This module handles loading and validating configuration from environment variables
and .env files.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Tuple
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

def get_env_value(key: str) -> Tuple[Optional[str], str]:
    """Get a value from environment variables and determine its source.
    
    Args:
        key: The environment variable key to check
        
    Returns:
        Tuple of (value, source) where source is either 'env' or 'dotenv'
    """
    # First check if it's in os.environ directly
    if key in os.environ:
        return os.environ[key], 'env'
    
    # Then check if it's in the dotenv environment
    if hasattr(os.environ, '_data'):
        if key in os.environ._data:
            return os.environ._data[key], 'dotenv'
    
    return None, 'not_found'

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
        load_dotenv(env_path, override=True)  # Added override=True to ensure .env values take precedence
    else:
        logger.info("No .env file found, using environment variables")
    
    # Validate required configuration
    required_vars = ['HZN_ORG_ID', 'HZN_EXCHANGE_URL', 'EXCHANGE_USER_ADMIN_PW']
    missing_vars = []
    
    for var in required_vars:
        value, source = get_env_value(var)
        if value is None:
            missing_vars.append(var)
        else:
            logger.info(f"Configuration {var} loaded from {source}")
    
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
    value, source = get_env_value(key)
    if value is None:
        if default is not None:
            logger.info(f"Using default value for {key}")
            return default
        raise ConfigError(f"Required configuration '{key}' not found")
    
    logger.debug(f"Retrieved {key} from {source}")
    return value 