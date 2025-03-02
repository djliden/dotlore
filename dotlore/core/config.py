import os
import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    "embedding": {
        "provider": "openai",
        "model": "text-embedding-3-small",
    },
    "reranking": {
        "method": "rrf",
    },
    "retrieval": {
        "max_context_length": 4000,
        "chunk_size": 1000,
        "chunk_overlap": 200,
    },
    "api_keys": {
        "openai": "${OPENAI_API_KEY}",
        "anthropic": "${ANTHROPIC_API_KEY}",
    }
}

def get_config_path():
    """Get the path to the config file."""
    return Path('.lore/config.yaml')

def create_default_config():
    """Create the default configuration file."""
    config_path = get_config_path()
    
    # Ensure the .lore directory exists
    config_path.parent.mkdir(exist_ok=True)
    
    # Write the default config
    with open(config_path, 'w') as f:
        yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)
    
    return config_path

def load_config():
    """Load the configuration from the config file."""
    config_path = get_config_path()
    
    if not config_path.exists():
        return None
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def get_config_value(key=None):
    """Get a configuration value by key."""
    config = load_config()
    
    if not config:
        return None
    
    if not key:
        return config
    
    # Handle nested keys like "embedding.model"
    parts = key.split('.')
    value = config
    for part in parts:
        if part in value:
            value = value[part]
        else:
            return None
    
    return value

def set_config_value(key, value):
    """Set a configuration value by key."""
    config = load_config() or DEFAULT_CONFIG
    
    # Handle nested keys like "embedding.model"
    parts = key.split('.')
    
    # Navigate to the right level
    current = config
    for i, part in enumerate(parts[:-1]):
        if part not in current:
            current[part] = {}
        current = current[part]
    
    # Set the value
    current[parts[-1]] = value
    
    # Write back to file
    with open(get_config_path(), 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    return True
