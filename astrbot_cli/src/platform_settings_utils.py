"""Platform settings management utilities for AstrBot CLI."""

import json
from pathlib import Path

# Constants
ASTROBOT_CONFIG_PATH = Path.cwd() / "data" / "astrbot" / "data" / "cmd_config.json"

# Default platform settings
DEFAULT_PLATFORM_SETTINGS = {
    "unique_session": False,
    "rate_limit": {
        "time": 60,
        "count": 30,
        "strategy": "stall",  # stall, discard
    },
    "reply_prefix": "",
    "forward_threshold": 1500,
    "enable_id_white_list": True,
    "id_whitelist": [],
    "id_whitelist_log": True,
    "wl_ignore_admin_on_group": True,
    "wl_ignore_admin_on_friend": True,
    "reply_with_mention": False,
    "reply_with_quote": False,
    "path_mapping": [],
    "segmented_reply": {
        "enable": False,
        "only_llm_result": True,
        "interval_method": "random",
        "interval": "1.5,3.5",
        "log_base": 2.6,
        "words_count_threshold": 150,
        "split_mode": "regex",
        "regex": ".*?[。？！~…]+|.+$",
        "split_words": ["。", "？", "！", "~", "…"],
        "content_cleanup_rule": "",
    },
    "no_permission_reply": True,
    "empty_mention_waiting": True,
    "empty_mention_waiting_need_reply": True,
    "friend_message_needs_wake_prefix": False,
    "ignore_bot_self_message": False,
    "ignore_at_all": False,
}

# Settings schema with descriptions
SETTINGS_SCHEMA = {
    "unique_session": {
        "type": "bool",
        "description": "Enable unique session mode (one conversation per user)",
        "hint": "When enabled, each user gets their own conversation context",
    },
    "rate_limit": {
        "type": "object",
        "description": "Rate limiting settings",
        "fields": {
            "time": {"type": "int", "description": "Time window in seconds"},
            "count": {"type": "int", "description": "Max requests in time window"},
            "strategy": {"type": "string", "options": ["stall", "discard"], "description": "Strategy when limit reached"},
        },
    },
    "reply_prefix": {
        "type": "string",
        "description": "Prefix to add to all bot replies",
        "hint": "e.g., '[Bot] ' or empty for none",
    },
    "forward_threshold": {
        "type": "int",
        "description": "Character threshold for message forwarding",
        "hint": "Messages longer than this will be forwarded",
    },
    "enable_id_white_list": {
        "type": "bool",
        "description": "Enable ID whitelist for access control",
        "hint": "When enabled, only whitelisted users can use the bot",
    },
    "id_whitelist": {
        "type": "list",
        "description": "List of user/group IDs allowed to use the bot",
        "hint": "Add user IDs or group IDs here",
    },
    "id_whitelist_log": {
        "type": "bool",
        "description": "Log blocked attempts from non-whitelisted users",
    },
    "wl_ignore_admin_on_group": {
        "type": "bool",
        "description": "Ignore whitelist for admins in group chats",
    },
    "wl_ignore_admin_on_friend": {
        "type": "bool",
        "description": "Ignore whitelist for admins in friend messages",
    },
    "reply_with_mention": {
        "type": "bool",
        "description": "Mention user when replying",
        "hint": "Bot will @ mention the user in replies",
    },
    "reply_with_quote": {
        "type": "bool",
        "description": "Quote original message when replying",
    },
    "path_mapping": {
        "type": "list",
        "description": "Path mapping for file access",
        "hint": "List of [from_path, to_path] mappings",
    },
    "segmented_reply": {
        "type": "object",
        "description": "Segmented/streaming reply settings",
        "fields": {
            "enable": {"type": "bool", "description": "Enable segmented replies"},
            "only_llm_result": {"type": "bool", "description": "Only segment LLM responses"},
            "interval_method": {"type": "string", "options": ["random", "fixed"], "description": "Interval calculation method"},
            "interval": {"type": "string", "description": "Interval range (e.g., '1.5,3.5')"},
            "words_count_threshold": {"type": "int", "description": "Minimum words to trigger segmentation"},
            "split_mode": {"type": "string", "options": ["regex", "words"], "description": "How to split messages"},
            "regex": {"type": "string", "description": "Regex pattern for splitting"},
        },
    },
    "no_permission_reply": {
        "type": "bool",
        "description": "Reply when user has no permission",
    },
    "empty_mention_waiting": {
        "type": "bool",
        "description": "Wait for content after empty @mention",
    },
    "empty_mention_waiting_need_reply": {
        "type": "bool",
        "description": "Send a reply while waiting for content",
    },
    "friend_message_needs_wake_prefix": {
        "type": "bool",
        "description": "Require wake prefix for friend messages",
        "hint": "When disabled, all friend messages will trigger the bot",
    },
    "ignore_bot_self_message": {
        "type": "bool",
        "description": "Ignore messages from the bot itself",
    },
    "ignore_at_all": {
        "type": "bool",
        "description": "Ignore @all mentions",
    },
}


def get_astrbot_root() -> Path:
    """Get the AstrBot root directory."""
    return Path.cwd() / "data" / "astrbot"


def get_config_path() -> Path:
    """Get the AstrBot config file path."""
    return ASTROBOT_CONFIG_PATH


def load_config() -> dict:
    """Load AstrBot configuration.

    Returns:
        dict: Configuration dictionary
    """
    config_path = get_config_path()
    if config_path.exists():
        try:
            return json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"platform": [], "provider": [], "provider_settings": {}, "platform_settings": DEFAULT_PLATFORM_SETTINGS}
    return {"platform": [], "provider": [], "provider_settings": {}, "platform_settings": DEFAULT_PLATFORM_SETTINGS}


def save_config(config: dict) -> None:
    """Save AstrBot configuration.

    Args:
        config: Configuration dictionary to save
    """
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def get_platform_settings() -> dict:
    """Get platform settings.

    Returns:
        dict: Platform settings dictionary
    """
    config = load_config()
    settings = config.get("platform_settings", {})
    # Merge with defaults for missing keys
    result = DEFAULT_PLATFORM_SETTINGS.copy()
    result.update(settings)
    return result


def update_platform_settings(updates: dict) -> dict:
    """Update platform settings.

    Args:
        updates: Dictionary of settings to update

    Returns:
        Updated platform settings dictionary
    """
    config = load_config()
    current = config.get("platform_settings", DEFAULT_PLATFORM_SETTINGS.copy())

    # Deep merge for nested dicts
    def deep_merge(base: dict, update: dict) -> dict:
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    updated = deep_merge(current, updates)
    config["platform_settings"] = updated
    save_config(config)
    return updated


def reset_platform_settings() -> dict:
    """Reset platform settings to defaults.

    Returns:
        Default platform settings dictionary
    """
    config = load_config()
    config["platform_settings"] = DEFAULT_PLATFORM_SETTINGS.copy()
    save_config(config)
    return config["platform_settings"]


def get_settings_schema() -> dict:
    """Get settings schema with descriptions.

    Returns:
        Settings schema dictionary
    """
    return SETTINGS_SCHEMA
