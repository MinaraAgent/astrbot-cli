"""Platform settings (Profile) management CLI commands for AstrBot."""

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import tyro

from .platform_settings_utils import (
    get_platform_settings,
    get_settings_schema,
    reset_platform_settings,
    update_platform_settings,
    DEFAULT_PLATFORM_SETTINGS,
)


@dataclass
class Show:
    """Show current platform settings.

    Display all platform configuration settings.
    """

    defaults: bool = False  # Show default values instead of current

    def run(self) -> None:
        """Execute the show command."""
        if self.defaults:
            settings = DEFAULT_PLATFORM_SETTINGS
            print("\nDefault Platform Settings:")
        else:
            settings = get_platform_settings()
            print("\nCurrent Platform Settings:")

        print("-" * 60)

        # Display in organized sections
        print("\n[Session & Rate Limiting]")
        print(f"  unique_session: {settings.get('unique_session', False)}")
        rate_limit = settings.get("rate_limit", {})
        print(f"  rate_limit.time: {rate_limit.get('time', 60)} seconds")
        print(f"  rate_limit.count: {rate_limit.get('count', 30)} requests")
        print(f"  rate_limit.strategy: {rate_limit.get('strategy', 'stall')}")

        print("\n[Reply Formatting]")
        print(f"  reply_prefix: '{settings.get('reply_prefix', '')}'")
        print(f"  reply_with_mention: {settings.get('reply_with_mention', False)}")
        print(f"  reply_with_quote: {settings.get('reply_with_quote', False)}")
        print(f"  forward_threshold: {settings.get('forward_threshold', 1500)} chars")

        print("\n[Access Control - Whitelist]")
        print(f"  enable_id_white_list: {settings.get('enable_id_white_list', True)}")
        print(f"  id_whitelist: {settings.get('id_whitelist', [])}")
        print(f"  id_whitelist_log: {settings.get('id_whitelist_log', True)}")
        print(f"  wl_ignore_admin_on_group: {settings.get('wl_ignore_admin_on_group', True)}")
        print(f"  wl_ignore_admin_on_friend: {settings.get('wl_ignore_admin_on_friend', True)}")

        print("\n[Segmented Reply]")
        seg = settings.get("segmented_reply", {})
        print(f"  segmented_reply.enable: {seg.get('enable', False)}")
        print(f"  segmented_reply.only_llm_result: {seg.get('only_llm_result', True)}")
        print(f"  segmented_reply.interval_method: {seg.get('interval_method', 'random')}")
        print(f"  segmented_reply.interval: {seg.get('interval', '1.5,3.5')}")

        print("\n[Message Handling]")
        print(f"  no_permission_reply: {settings.get('no_permission_reply', True)}")
        print(f"  empty_mention_waiting: {settings.get('empty_mention_waiting', True)}")
        print(f"  friend_message_needs_wake_prefix: {settings.get('friend_message_needs_wake_prefix', False)}")
        print(f"  ignore_bot_self_message: {settings.get('ignore_bot_self_message', False)}")
        print(f"  ignore_at_all: {settings.get('ignore_at_all', False)}")

        print("\n[Full JSON Configuration]")
        print(json.dumps(settings, indent=2, ensure_ascii=False))


@dataclass
class Set:
    """Set a platform setting.

    Update a specific platform configuration value.
    """

    key: Annotated[str, tyro.conf.Positional]  # Setting key (supports dot notation like 'rate_limit.time')
    value: Annotated[str, tyro.conf.Positional]  # New value (JSON or string)

    def run(self) -> None:
        """Execute the set command."""
        # Parse key path
        keys = self.key.split(".")

        # Try to parse value as JSON, otherwise use string
        try:
            parsed = json.loads(self.value)
        except json.JSONDecodeError:
            parsed = self.value

        # Build nested update dict
        update = {}
        current = update
        for i, key in enumerate(keys[:-1]):
            current[key] = {}
            current = current[key]
        current[keys[-1]] = parsed

        try:
            updated = update_platform_settings(update)
            print(f"Set {self.key} = {parsed}")
            print("\nUpdated settings:")
            print(json.dumps(updated, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Error: {e}")


@dataclass
class Get:
    """Get a platform setting.

    Display a specific platform configuration value.
    """

    key: Annotated[str, tyro.conf.Positional]  # Setting key (supports dot notation like 'rate_limit.time')

    def run(self) -> None:
        """Execute the get command."""
        settings = get_platform_settings()
        keys = self.key.split(".")
        value = settings
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                value = None
                break

        if value is not None:
            if isinstance(value, dict | list):
                print(json.dumps(value, indent=2, ensure_ascii=False))
            else:
                print(value)
        else:
            print(f"Setting '{self.key}' not found")
            print("\nAvailable settings:")
            schema = get_settings_schema()
            for key in schema:
                print(f"  {key}")


@dataclass
class Reset:
    """Reset platform settings.

    Reset all platform settings to default values.
    """

    confirm: bool = False  # Confirm reset

    def run(self) -> None:
        """Execute the reset command."""
        if not self.confirm:
            print("Warning: This will reset ALL platform settings to defaults.")
            print("Use --confirm to proceed.")
            return

        settings = reset_platform_settings()
        print("Platform settings have been reset to defaults.")
        print(json.dumps(settings, indent=2, ensure_ascii=False))


@dataclass
class Edit:
    """Edit platform settings.

    Open platform settings in a text editor for full configuration.
    """

    def run(self) -> None:
        """Execute the edit command."""
        config_path = Path.home() / ".config" / "astrbot" / "platform_settings.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        if not config_path.exists():
            settings = get_platform_settings()
            config_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")

        editor = os.environ.get("EDITOR", "nano")
        subprocess.run([editor, str(config_path)])

        # Read back the edited config
        try:
            new_settings = json.loads(config_path.read_text(encoding="utf-8"))
            update_platform_settings(new_settings)
            print("Platform settings saved")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config file: {e}")


@dataclass
class Schema:
    """Show settings schema.

    Display all available settings with descriptions.
    """

    def run(self) -> None:
        """Execute the schema command."""
        schema = get_settings_schema()
        print("\nPlatform Settings Schema:")
        print("=" * 60)

        for key, info in schema.items():
            type_str = info.get("type", "unknown")
            desc = info.get("description", "")
            hint = info.get("hint", "")

            print(f"\n{key} ({type_str}):")
            print(f"  {desc}")
            if hint:
                print(f"  Hint: {hint}")

            if type_str == "object" and "fields" in info:
                for field_key, field_info in info["fields"].items():
                    print(f"    {key}.{field_key}: {field_info.get('description', '')}")
                    if "options" in field_info:
                        print(f"      Options: {', '.join(field_info['options'])}")


# Union type for subcommands
Commands = Annotated[
    Show | Set | Get | Reset | Edit | Schema,
    tyro.conf.subcommand(),
]


def run_platform_settings_command(cmd: Show | Set | Get | Reset | Edit | Schema) -> None:
    """Run a platform settings command based on its type.

    Args:
        cmd: The platform settings command to execute
    """
    cmd.run()
