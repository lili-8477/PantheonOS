"""
Knowledge Base Configuration Loading

Configuration priority (low to high):
1. config.yaml default configuration file
2. User-specified configuration file (if provided)
3. Environment variable overrides
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


def expand_path(path: str, context: Dict[str, str]) -> str:
    """
    Expand variables in path.
    Example: ${storage_path}/qdrant_storage -> /home/user/.pantheon-knowledge/qdrant_storage
    """
    for key, value in context.items():
        path = path.replace(f"${{{key}}}", value)
    return os.path.expanduser(path)


def deep_update(base_dict: Dict, update_dict: Dict) -> None:
    """Deep merge dictionaries (modifies base_dict in place)."""
    for key, value in update_dict.items():
        if key in base_dict and isinstance(base_dict[key], dict) and isinstance(value, dict):
            deep_update(base_dict[key], value)
        else:
            base_dict[key] = value


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration file.

    Configuration loading order:
    1. Try to load from Settings module (.pantheon/settings.json)
    2. Load knowledge/config.yaml as default configuration
    3. If config_path provided, deep merge user configuration
    4. Override specific fields with environment variables

    Args:
        config_path: User configuration file path (optional)

    Returns:
        Configuration dictionary

    Environment variable overrides:
        QDRANT_LOCATION: Override qdrant.location
        QDRANT_PATH: Override qdrant.path
        QDRANT_API_KEY: Override qdrant.api_key
        QDRANT_PREFER_GRPC: Override qdrant.prefer_grpc
    """
    import copy

    # 1. Try to load from Settings module
    settings_knowledge_config = None
    try:
        from pantheon.settings import get_settings
        settings = get_settings()
        settings_knowledge_config = settings.get_knowledge_config()
    except Exception:
        pass

    # 2. Load default config file (knowledge/config.yaml)
    default_config_path = Path(__file__).parent / "config.yaml"
    with open(default_config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 3. If Settings module loaded successfully, merge configuration
    if settings_knowledge_config:
        # Merge storage_path
        if settings_knowledge_config.get("storage_path"):
            config["knowledge"]["storage_path"] = settings_knowledge_config["storage_path"]
        # Merge qdrant config
        qdrant_settings = settings_knowledge_config.get("qdrant", {})
        for key, value in qdrant_settings.items():
            if value is not None:
                config["knowledge"]["qdrant"][key] = value

    # 4. If user config file provided, deep merge
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            user_config = yaml.safe_load(f)
            if user_config and "knowledge" in user_config:
                deep_update(config["knowledge"], user_config["knowledge"])

    knowledge_config = config["knowledge"]

    # 5. Environment variable overrides (highest priority)
    # Note: Path variables not expanded yet, env vars can contain variables
    if os.getenv("QDRANT_LOCATION"):
        knowledge_config["qdrant"]["location"] = os.getenv("QDRANT_LOCATION")

    if os.getenv("QDRANT_PATH"):
        knowledge_config["qdrant"]["path"] = os.getenv("QDRANT_PATH")

    if os.getenv("QDRANT_API_KEY"):
        knowledge_config["qdrant"]["api_key"] = os.getenv("QDRANT_API_KEY")

    if os.getenv("QDRANT_PREFER_GRPC"):
        knowledge_config["qdrant"]["prefer_grpc"] = os.getenv("QDRANT_PREFER_GRPC").lower() == "true"

    # Expand path variables
    storage_path = os.path.expanduser(knowledge_config["storage_path"])
    context = {"storage_path": storage_path}

    # Expand qdrant.location (if contains variables)
    if knowledge_config["qdrant"]["location"]:
        location = knowledge_config["qdrant"]["location"]
        if isinstance(location, str):
            knowledge_config["qdrant"]["location"] = expand_path(location, context)

    # Expand qdrant.path (if exists and not empty)
    if knowledge_config["qdrant"]["path"]:
        knowledge_config["qdrant"]["path"] = expand_path(
            knowledge_config["qdrant"]["path"], context
        )

    # Expand metadata.path
    knowledge_config["metadata"]["path"] = expand_path(
        knowledge_config["metadata"]["path"], context
    )

    # Ensure necessary directories exist
    Path(storage_path).mkdir(parents=True, exist_ok=True)

    # If location is local path (not :memory: and not URL), create directory
    location = knowledge_config["qdrant"]["location"]
    if location and location != ":memory:" and not location.startswith("http"):
        Path(location).mkdir(parents=True, exist_ok=True)

    return config


def get_storage_path(config: Optional[Dict[str, Any]] = None) -> Path:
    """Get storage path."""
    if config is None:
        config = load_config()
    return Path(os.path.expanduser(config["knowledge"]["storage_path"]))


def get_qdrant_params(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract Qdrant client parameters from configuration.

    Returns a parameter dict that can be passed directly to QdrantClient.

    Qdrant client supported parameters:
    - location: str | None - Storage location (":memory:", local path, or empty for url)
    - url: str | None - Remote server URL
    - path: str | None - Local storage path (deprecated, use location)
    - api_key: str | None - API key
    - prefer_grpc: bool - Whether to use gRPC
    """
    qdrant_config = config["knowledge"]["qdrant"]
    params = {}

    location = qdrant_config.get("location")

    # Determine location type
    if location == ":memory:":
        # Memory mode
        params["location"] = ":memory:"
    elif location and location.startswith("http"):
        # URL mode (remote server)
        params["url"] = location
        if qdrant_config.get("api_key"):
            params["api_key"] = qdrant_config["api_key"]
        if qdrant_config.get("prefer_grpc"):
            params["prefer_grpc"] = qdrant_config["prefer_grpc"]
    elif location:
        # Local path mode
        params["path"] = location
    elif qdrant_config.get("path"):
        # Backward compatibility: if no location but has path
        params["path"] = qdrant_config["path"]
    else:
        # Default to memory mode
        params["location"] = ":memory:"

    return params
