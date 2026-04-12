"""Platform management utilities for AstrBot CLI."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

# Constants
ASTROBOT_CONFIG_PATH = Path.cwd() / "data" / "astrbot" / "data" / "cmd_config.json"

# Known platform types with their descriptions
KNOWN_PLATFORMS = {
    "aiocqhttp": "QQ adapter via OneBot (go-cqhttp, Lagrange, etc.)",
    "telegram": "Telegram Bot API",
    "discord": "Discord Bot",
    "slack": "Slack Bot",
    "kook": "KOOK (开黑啦) Bot",
    "lark": "Lark/Feishu Bot",
    "dingtalk": "DingTalk Bot",
    "wecom": "WeChat Work (企业微信) Bot",
    "wecom_ai_bot": "WeChat Work AI Bot",
    "weixin_official_account": "WeChat Official Account (公众号)",
    "weixin_oc": "WeChat Official Account (旧版)",
    "mattermost": "Mattermost Bot",
    "misskey": "Misskey Bot",
    "matrix": "Matrix Bot",
    "qqofficial": "QQ Official API",
    "qqofficial_webhook": "QQ Official API (Webhook mode)",
    "satori": "Satori Protocol",
    "vocechat": "VoceChat Bot",
    "webchat": "Web Chat (built-in)",
    "line": "LINE Bot",
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
            return {"platform": [], "provider": [], "provider_settings": {}}
    return {"platform": [], "provider": [], "provider_settings": {}}


def save_config(config: dict) -> None:
    """Save AstrBot configuration.

    Args:
        config: Configuration dictionary to save

    """
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def get_available_platforms() -> list[dict[str, str]]:
    """Get list of available platform types.

    Returns:
        List of platform info dicts with name and desc

    """
    platforms = []
    for name, desc in KNOWN_PLATFORMS.items():
        platforms.append({"name": name, "desc": desc})
    return platforms


def list_platform_configs() -> list[dict]:
    """List all configured platforms.

    Returns:
        List of platform configuration dictionaries

    """
    config = load_config()
    return config.get("platform", [])


def get_platform_config(platform_id: str) -> dict | None:
    """Get a platform configuration by ID.

    Args:
        platform_id: Platform instance ID

    Returns:
        Platform configuration dict or None if not found

    """
    config = load_config()
    platforms = config.get("platform", [])
    for platform in platforms:
        if platform.get("id") == platform_id:
            return platform
    return None


def add_platform_config(platform_type: str, platform_id: str, enable: bool = True) -> dict:
    """Add a new platform configuration.

    Args:
        platform_type: Platform type (e.g., telegram, discord)
        platform_id: Platform instance ID
        enable: Whether to enable the platform

    Returns:
        The created platform configuration

    Raises:
        ValueError: If platform ID already exists or type is unknown

    """
    if platform_type not in KNOWN_PLATFORMS:
        raise ValueError(f"Unknown platform type: {platform_type}. Available types: {', '.join(KNOWN_PLATFORMS.keys())}")

    config = load_config()
    platforms = config.get("platform", [])

    # Check if ID already exists
    for platform in platforms:
        if platform.get("id") == platform_id:
            raise ValueError(f"Platform with ID '{platform_id}' already exists")

    # Create new platform config
    new_platform = {
        "id": platform_id,
        "type": platform_type,
        "enable": enable,
    }

    # Add type-specific default config
    type_defaults = get_platform_defaults(platform_type)
    new_platform.update(type_defaults)

    platforms.append(new_platform)
    config["platform"] = platforms
    save_config(config)

    return new_platform


def get_platform_defaults(platform_type: str) -> dict:
    """Get default configuration values for a platform type.

    Args:
        platform_type: Platform type

    Returns:
        Dictionary of default configuration values

    """
    # Defaults from AstrBot's default.py CONFIG_METADATA_2 config_template
    defaults = {
        "telegram": {
            "token": "",
            "telegram_api_base_url": "https://api.telegram.org/bot",
            "telegram_file_base_url": "https://api.telegram.org/file/bot",
            "telegram_command_register": True,
            "telegram_command_auto_refresh": False,
            "telegram_command_register_interval": 300,
            "telegram_polling_restart_delay": 5.0,
        },
        "discord": {
            "discord_token": "",
            "discord_proxy": "",
            "discord_command_register": True,
            "discord_activity_name": "",
            "discord_allow_bot_messages": False,
        },
        "aiocqhttp": {
            "ws_reverse_host": "0.0.0.0",
            "ws_reverse_port": 6199,
            "ws_reverse_token": "",
        },
        "slack": {
            "bot_token": "",
            "app_token": "",
            "signing_secret": "",
            "slack_connection_mode": "socket",
            "unified_webhook_mode": True,
            "webhook_uuid": "",
            "slack_webhook_host": "0.0.0.0",
            "slack_webhook_port": 6197,
            "slack_webhook_path": "/astrbot-slack-webhook/callback",
        },
        "kook": {
            "kook_bot_token": "",
            "kook_reconnect_delay": 5,
            "kook_max_reconnect_delay": 300,
            "kook_max_retry_delay": 60,
            "kook_heartbeat_interval": 30,
            "kook_heartbeat_timeout": 60,
            "kook_max_heartbeat_failures": 3,
            "kook_max_consecutive_failures": 10,
        },
        "lark": {
            "lark_app_id": "",
            "lark_app_secret": "",
            "lark_bot_name": "",
            "lark_encrypt_key": "",
            "lark_verification_token": "",
            "unified_webhook_mode": True,
            "webhook_uuid": "",
            "port": 6193,
        },
        "dingtalk": {
            "dingtalk_client_id": "",
            "dingtalk_client_secret": "",
            "card_template_id": "",
        },
        "wecom": {
            "corpid": "",
            "secret": "",
            "token": "",
            "encoding_aes_key": "",
            "kf_name": "",
            "api_base_url": "https://qyapi.weixin.qq.com/cgi-bin/",
            "unified_webhook_mode": True,
            "webhook_uuid": "",
            "callback_server_host": "0.0.0.0",
            "port": 6195,
        },
        "wecom_ai_bot": {
            "wecom_ai_bot_connection_mode": "long_connection",
            "wecom_ai_bot_name": "",
            "wecomaibot_ws_bot_id": "",
            "wecomaibot_ws_secret": "",
            "wecomaibot_token": "",
            "wecomaibot_encoding_aes_key": "",
            "wecomaibot_init_respond_text": "",
            "wecomaibot_friend_message_welcome_text": "",
            "msg_push_webhook_url": "",
            "only_use_webhook_url_to_send": False,
            "wecomaibot_ws_url": "wss://openws.work.weixin.qq.com",
            "wecomaibot_heartbeat_interval": 30,
            "unified_webhook_mode": True,
            "webhook_uuid": "",
            "port": 6198,
        },
        "weixin_official_account": {
            "appid": "",
            "secret": "",
            "token": "",
            "encoding_aes_key": "",
            "api_base_url": "https://api.weixin.qq.com/cgi-bin/",
            "unified_webhook_mode": True,
            "webhook_uuid": "",
            "callback_server_host": "0.0.0.0",
            "port": 6194,
            "active_send_mode": False,
        },
        "mattermost": {
            "mattermost_url": "",
            "mattermost_token": "",
            "mattermost_team_name": "",
        },
        "misskey": {
            "misskey_instance_url": "https://misskey.example",
            "misskey_token": "",
            "misskey_default_visibility": "public",
            "misskey_local_only": False,
            "misskey_enable_chat": True,
            "misskey_allow_insecure_downloads": False,
            "misskey_download_timeout": 15,
            "misskey_download_chunk_size": 65536,
            "misskey_max_download_bytes": None,
            "misskey_enable_file_upload": True,
            "misskey_upload_concurrency": 3,
            "misskey_upload_folder": "",
        },
        "matrix": {
            "matrix_homeserver": "",
            "matrix_user_id": "",
            "matrix_access_token": "",
            "matrix_device_id": "",
        },
        "qqofficial": {
            "appid": "",
            "secret": "",
            "enable_group_c2c": True,
            "enable_guild_direct_message": True,
        },
        "qqofficial_webhook": {
            "appid": "",
            "secret": "",
            "is_sandbox": False,
            "unified_webhook_mode": True,
            "webhook_uuid": "",
            "callback_server_host": "0.0.0.0",
            "port": 6196,
        },
        "satori": {
            "satori_host": "localhost",
            "satori_port": 8080,
        },
        "vocechat": {
            "vocechat_webhook_url": "",
            "vocechat_api_url": "",
        },
        "webchat": {},
        "line": {
            "channel_access_token": "",
            "channel_secret": "",
            "unified_webhook_mode": True,
            "webhook_uuid": "",
            "line_webhook_host": "0.0.0.0",
            "line_webhook_port": 6192,
        },
        "weixin_oc": {
            "weixin_oc_base_url": "https://ilinkai.weixin.qq.com",
            "weixin_oc_bot_type": "3",
            "weixin_oc_qr_poll_interval": 3,
            "weixin_oc_long_poll_timeout_ms": 30000,
            "weixin_oc_api_timeout_ms": 30000,
            "weixin_oc_token": "",
        },
    }
    return defaults.get(platform_type, {})


def update_platform_config(platform_id: str, updates: dict) -> dict:
    """Update a platform configuration.

    Args:
        platform_id: Platform instance ID
        updates: Dictionary of fields to update

    Returns:
        Updated platform configuration

    Raises:
        ValueError: If platform not found

    """
    config = load_config()
    platforms = config.get("platform", [])

    for i, platform in enumerate(platforms):
        if platform.get("id") == platform_id:
            platforms[i].update(updates)
            config["platform"] = platforms
            save_config(config)
            return platforms[i]

    raise ValueError(f"Platform '{platform_id}' not found")


def set_platform_config(platform_id: str, new_config: dict) -> None:
    """Set the complete configuration for a platform.

    Args:
        platform_id: Platform instance ID
        new_config: New configuration dictionary

    Raises:
        ValueError: If platform not found

    """
    config = load_config()
    platforms = config.get("platform", [])

    for i, platform in enumerate(platforms):
        if platform.get("id") == platform_id:
            # Preserve id and type
            new_config["id"] = platform_id
            new_config["type"] = platform.get("type", new_config.get("type", ""))
            platforms[i] = new_config
            config["platform"] = platforms
            save_config(config)
            return

    raise ValueError(f"Platform '{platform_id}' not found")


def delete_platform_config(platform_id: str) -> None:
    """Delete a platform configuration.

    Args:
        platform_id: Platform instance ID

    Raises:
        ValueError: If platform not found

    """
    config = load_config()
    platforms = config.get("platform", [])

    for i, platform in enumerate(platforms):
        if platform.get("id") == platform_id:
            del platforms[i]
            config["platform"] = platforms
            save_config(config)
            return

    raise ValueError(f"Platform '{platform_id}' not found")


def get_platform_config_schema(platform_type: str) -> dict | None:
    """Get configuration schema for a platform type.

    Args:
        platform_type: Platform type

    Returns:
        Configuration schema dict or None if not available

    """
    # Schema definitions for common platforms (using actual AstrBot field names)
    schemas = {
        "telegram": {
            "token": {
                "type": "string",
                "description": "Telegram Bot Token",
                "required": True,
            },
            "telegram_api_base_url": {
                "type": "string",
                "description": "Telegram API base URL (for proxy)",
                "default": "https://api.telegram.org/bot",
            },
            "telegram_file_base_url": {
                "type": "string",
                "description": "Telegram File API base URL",
                "default": "https://api.telegram.org/file/bot",
            },
            "telegram_command_register": {
                "type": "bool",
                "description": "Register bot commands on Telegram",
                "default": True,
            },
            "telegram_command_auto_refresh": {
                "type": "bool",
                "description": "Auto refresh command registration",
                "default": False,
            },
            "telegram_command_register_interval": {
                "type": "int",
                "description": "Command register interval in seconds",
                "default": 300,
            },
            "telegram_polling_restart_delay": {
                "type": "float",
                "description": "Polling restart delay in seconds",
                "default": 5.0,
            },
        },
        "discord": {
            "discord_token": {
                "type": "string",
                "description": "Discord Bot Token",
                "required": True,
            },
            "discord_proxy": {
                "type": "string",
                "description": "Proxy URL for Discord API",
                "default": "",
            },
            "discord_command_register": {
                "type": "bool",
                "description": "Register slash commands",
                "default": True,
            },
            "discord_activity_name": {
                "type": "string",
                "description": "Bot activity status text",
                "default": "",
            },
            "discord_allow_bot_messages": {
                "type": "bool",
                "description": "Allow bot messages to trigger commands",
                "default": False,
            },
        },
        "aiocqhttp": {
            "ws_reverse_host": {
                "type": "string",
                "description": "WebSocket reverse host",
                "default": "0.0.0.0",
            },
            "ws_reverse_port": {
                "type": "int",
                "description": "WebSocket reverse port",
                "default": 6199,
            },
            "ws_reverse_token": {
                "type": "string",
                "description": "WebSocket reverse access token",
                "default": "",
            },
        },
        "slack": {
            "bot_token": {
                "type": "string",
                "description": "Slack Bot Token (xoxb-...)",
                "required": True,
            },
            "app_token": {
                "type": "string",
                "description": "Slack App Token (xapp-...)",
            },
            "signing_secret": {
                "type": "string",
                "description": "Slack signing secret",
            },
            "slack_connection_mode": {
                "type": "string",
                "description": "Connection mode: socket or webhook",
                "default": "socket",
            },
            "unified_webhook_mode": {
                "type": "bool",
                "description": "Use unified webhook mode",
                "default": True,
            },
            "webhook_uuid": {
                "type": "string",
                "description": "Webhook UUID",
                "default": "",
            },
            "slack_webhook_host": {
                "type": "string",
                "description": "Webhook server host",
                "default": "0.0.0.0",
            },
            "slack_webhook_port": {
                "type": "int",
                "description": "Webhook server port",
                "default": 6197,
            },
            "slack_webhook_path": {
                "type": "string",
                "description": "Webhook path",
                "default": "/astrbot-slack-webhook/callback",
            },
        },
        "kook": {
            "kook_bot_token": {
                "type": "string",
                "description": "KOOK Bot Token",
                "required": True,
            },
            "kook_reconnect_delay": {
                "type": "int",
                "description": "Reconnect delay in seconds",
                "default": 5,
            },
            "kook_max_reconnect_delay": {
                "type": "int",
                "description": "Max reconnect delay in seconds",
                "default": 300,
            },
            "kook_max_retry_delay": {
                "type": "int",
                "description": "Max retry delay in seconds",
                "default": 60,
            },
            "kook_heartbeat_interval": {
                "type": "int",
                "description": "Heartbeat interval in seconds",
                "default": 30,
            },
            "kook_heartbeat_timeout": {
                "type": "int",
                "description": "Heartbeat timeout in seconds",
                "default": 60,
            },
            "kook_max_heartbeat_failures": {
                "type": "int",
                "description": "Max heartbeat failures before reconnect",
                "default": 3,
            },
            "kook_max_consecutive_failures": {
                "type": "int",
                "description": "Max consecutive failures before give up",
                "default": 10,
            },
        },
        "lark": {
            "lark_app_id": {
                "type": "string",
                "description": "Lark App ID",
                "required": True,
            },
            "lark_app_secret": {
                "type": "string",
                "description": "Lark App Secret",
                "required": True,
            },
            "lark_bot_name": {
                "type": "string",
                "description": "Lark Bot Name",
                "default": "",
            },
            "lark_encrypt_key": {
                "type": "string",
                "description": "Lark encrypt key",
                "default": "",
            },
            "lark_verification_token": {
                "type": "string",
                "description": "Lark verification token",
                "default": "",
            },
            "unified_webhook_mode": {
                "type": "bool",
                "description": "Use unified webhook mode",
                "default": True,
            },
            "webhook_uuid": {
                "type": "string",
                "description": "Webhook UUID",
                "default": "",
            },
            "port": {
                "type": "int",
                "description": "Webhook server port",
                "default": 6193,
            },
        },
        "dingtalk": {
            "dingtalk_client_id": {
                "type": "string",
                "description": "DingTalk Client ID",
                "required": True,
            },
            "dingtalk_client_secret": {
                "type": "string",
                "description": "DingTalk Client Secret",
                "required": True,
            },
            "card_template_id": {
                "type": "string",
                "description": "Card template ID",
                "default": "",
            },
        },
        "wecom": {
            "corpid": {
                "type": "string",
                "description": "WeChat Work Corp ID",
                "required": True,
            },
            "secret": {
                "type": "string",
                "description": "WeChat Work Secret",
                "required": True,
            },
            "token": {
                "type": "string",
                "description": "WeChat Work Token",
                "default": "",
            },
            "encoding_aes_key": {
                "type": "string",
                "description": "Encoding AES Key",
                "default": "",
            },
            "kf_name": {
                "type": "string",
                "description": "Customer service name",
                "default": "",
            },
            "api_base_url": {
                "type": "string",
                "description": "API base URL",
                "default": "https://qyapi.weixin.qq.com/cgi-bin/",
            },
            "unified_webhook_mode": {
                "type": "bool",
                "description": "Use unified webhook mode",
                "default": True,
            },
            "webhook_uuid": {
                "type": "string",
                "description": "Webhook UUID",
                "default": "",
            },
            "callback_server_host": {
                "type": "string",
                "description": "Callback server host",
                "default": "0.0.0.0",
            },
            "port": {
                "type": "int",
                "description": "Callback server port",
                "default": 6195,
            },
        },
        "wecom_ai_bot": {
            "wecom_ai_bot_connection_mode": {
                "type": "string",
                "description": "Connection mode: long_connection or webhook",
                "default": "long_connection",
            },
            "wecom_ai_bot_name": {
                "type": "string",
                "description": "WeChat AI Bot name",
                "default": "",
            },
            "wecomaibot_ws_bot_id": {
                "type": "string",
                "description": "WebSocket bot ID",
                "default": "",
            },
            "wecomaibot_ws_secret": {
                "type": "string",
                "description": "WebSocket secret",
                "default": "",
            },
            "wecomaibot_token": {
                "type": "string",
                "description": "Token",
                "default": "",
            },
            "wecomaibot_encoding_aes_key": {
                "type": "string",
                "description": "Encoding AES Key",
                "default": "",
            },
            "wecomaibot_init_respond_text": {
                "type": "string",
                "description": "Initial respond text",
                "default": "",
            },
            "wecomaibot_friend_message_welcome_text": {
                "type": "string",
                "description": "Friend message welcome text",
                "default": "",
            },
            "msg_push_webhook_url": {
                "type": "string",
                "description": "Message push webhook URL",
                "default": "",
            },
            "only_use_webhook_url_to_send": {
                "type": "bool",
                "description": "Only use webhook URL to send",
                "default": False,
            },
            "wecomaibot_ws_url": {
                "type": "string",
                "description": "WebSocket URL",
                "default": "wss://openws.work.weixin.qq.com",
            },
            "wecomaibot_heartbeat_interval": {
                "type": "int",
                "description": "Heartbeat interval in seconds",
                "default": 30,
            },
            "unified_webhook_mode": {
                "type": "bool",
                "description": "Use unified webhook mode",
                "default": True,
            },
            "webhook_uuid": {
                "type": "string",
                "description": "Webhook UUID",
                "default": "",
            },
            "port": {
                "type": "int",
                "description": "Webhook server port",
                "default": 6198,
            },
        },
        "weixin_official_account": {
            "appid": {
                "type": "string",
                "description": "WeChat App ID",
                "required": True,
            },
            "secret": {
                "type": "string",
                "description": "WeChat App Secret",
                "required": True,
            },
            "token": {
                "type": "string",
                "description": "WeChat Token",
                "required": True,
            },
            "encoding_aes_key": {
                "type": "string",
                "description": "Encoding AES Key",
                "default": "",
            },
            "api_base_url": {
                "type": "string",
                "description": "API base URL",
                "default": "https://api.weixin.qq.com/cgi-bin/",
            },
            "unified_webhook_mode": {
                "type": "bool",
                "description": "Use unified webhook mode",
                "default": True,
            },
            "webhook_uuid": {
                "type": "string",
                "description": "Webhook UUID",
                "default": "",
            },
            "callback_server_host": {
                "type": "string",
                "description": "Callback server host",
                "default": "0.0.0.0",
            },
            "port": {
                "type": "int",
                "description": "Callback server port",
                "default": 6194,
            },
            "active_send_mode": {
                "type": "bool",
                "description": "Active send mode",
                "default": False,
            },
        },
        "mattermost": {
            "mattermost_url": {
                "type": "string",
                "description": "Mattermost server URL",
                "required": True,
            },
            "mattermost_token": {
                "type": "string",
                "description": "Bot access token",
                "required": True,
            },
            "mattermost_team_name": {
                "type": "string",
                "description": "Team name",
                "default": "",
            },
        },
        "misskey": {
            "misskey_instance_url": {
                "type": "string",
                "description": "Misskey server URL",
                "required": True,
            },
            "misskey_token": {
                "type": "string",
                "description": "Access token",
                "required": True,
            },
            "misskey_default_visibility": {
                "type": "string",
                "description": "Default visibility",
                "default": "public",
            },
            "misskey_local_only": {
                "type": "bool",
                "description": "Local only posts",
                "default": False,
            },
            "misskey_enable_chat": {
                "type": "bool",
                "description": "Enable chat",
                "default": True,
            },
            "misskey_allow_insecure_downloads": {
                "type": "bool",
                "description": "Allow insecure downloads",
                "default": False,
            },
            "misskey_download_timeout": {
                "type": "int",
                "description": "Download timeout in seconds",
                "default": 15,
            },
            "misskey_download_chunk_size": {
                "type": "int",
                "description": "Download chunk size",
                "default": 65536,
            },
            "misskey_max_download_bytes": {
                "type": "int",
                "description": "Max download bytes",
                "default": None,
            },
            "misskey_enable_file_upload": {
                "type": "bool",
                "description": "Enable file upload",
                "default": True,
            },
            "misskey_upload_concurrency": {
                "type": "int",
                "description": "Upload concurrency",
                "default": 3,
            },
            "misskey_upload_folder": {
                "type": "string",
                "description": "Upload folder path",
                "default": "",
            },
        },
        "matrix": {
            "matrix_homeserver": {
                "type": "string",
                "description": "Matrix homeserver URL",
                "required": True,
            },
            "matrix_user_id": {
                "type": "string",
                "description": "Matrix user ID (@user:server)",
                "required": True,
            },
            "matrix_access_token": {
                "type": "string",
                "description": "Access token",
                "required": True,
            },
            "matrix_device_id": {
                "type": "string",
                "description": "Device ID",
                "default": "",
            },
        },
        "qqofficial": {
            "appid": {
                "type": "string",
                "description": "QQ Official App ID",
                "required": True,
            },
            "secret": {
                "type": "string",
                "description": "QQ Official Secret",
                "required": True,
            },
            "enable_group_c2c": {
                "type": "bool",
                "description": "Enable group C2C",
                "default": True,
            },
            "enable_guild_direct_message": {
                "type": "bool",
                "description": "Enable guild direct message",
                "default": True,
            },
        },
        "qqofficial_webhook": {
            "appid": {
                "type": "string",
                "description": "QQ Official App ID",
                "required": True,
            },
            "secret": {
                "type": "string",
                "description": "QQ Official Secret",
                "required": True,
            },
            "is_sandbox": {
                "type": "bool",
                "description": "Use sandbox environment",
                "default": False,
            },
            "unified_webhook_mode": {
                "type": "bool",
                "description": "Use unified webhook mode",
                "default": True,
            },
            "webhook_uuid": {
                "type": "string",
                "description": "Webhook UUID",
                "default": "",
            },
            "callback_server_host": {
                "type": "string",
                "description": "Callback server host",
                "default": "0.0.0.0",
            },
            "port": {
                "type": "int",
                "description": "Webhook server port",
                "default": 6196,
            },
        },
        "satori": {
            "satori_host": {
                "type": "string",
                "description": "Satori server host",
                "default": "localhost",
            },
            "satori_port": {
                "type": "int",
                "description": "Satori server port",
                "default": 8080,
            },
        },
        "vocechat": {
            "vocechat_webhook_url": {
                "type": "string",
                "description": "VoceChat webhook URL",
                "required": True,
            },
            "vocechat_api_url": {
                "type": "string",
                "description": "VoceChat API URL",
                "default": "",
            },
        },
        "webchat": {},
        "line": {
            "channel_access_token": {
                "type": "string",
                "description": "LINE Channel Access Token",
                "required": True,
            },
            "channel_secret": {
                "type": "string",
                "description": "LINE Channel Secret",
                "required": True,
            },
            "unified_webhook_mode": {
                "type": "bool",
                "description": "Use unified webhook mode",
                "default": True,
            },
            "webhook_uuid": {
                "type": "string",
                "description": "Webhook UUID",
                "default": "",
            },
            "line_webhook_host": {
                "type": "string",
                "description": "Webhook server host",
                "default": "0.0.0.0",
            },
            "line_webhook_port": {
                "type": "int",
                "description": "Webhook server port",
                "default": 6192,
            },
        },
        "weixin_oc": {
            "weixin_oc_base_url": {
                "type": "string",
                "description": "WeChat OC base URL",
                "default": "https://ilinkai.weixin.qq.com",
            },
            "weixin_oc_bot_type": {
                "type": "string",
                "description": "Bot type",
                "default": "3",
            },
            "weixin_oc_qr_poll_interval": {
                "type": "int",
                "description": "QR poll interval in seconds",
                "default": 3,
            },
            "weixin_oc_long_poll_timeout_ms": {
                "type": "int",
                "description": "Long poll timeout in ms",
                "default": 30000,
            },
            "weixin_oc_api_timeout_ms": {
                "type": "int",
                "description": "API timeout in ms",
                "default": 30000,
            },
            "weixin_oc_token": {
                "type": "string",
                "description": "WeChat OC Token",
                "default": "",
            },
        },
    }
    return schemas.get(platform_type)
