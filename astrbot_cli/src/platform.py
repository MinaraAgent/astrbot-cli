"""Platform management CLI commands for AstrBot."""

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import tyro

from .platform_utils import (
    get_available_platforms,
    get_platform_config,
    get_platform_config_schema,
    set_platform_config,
    list_platform_configs,
    add_platform_config,
    update_platform_config,
    delete_platform_config,
)


@dataclass
class PlatformList:
    """List platform configurations.

    Show configured platforms. Use --available to see all supported platform types.
    """

    available: bool = False  # Show all available platform types

    def run(self) -> None:
        """Execute the list command."""
        if self.available:
            platforms = get_available_platforms()
            print("\nAvailable Platform Types:")
            print("-" * 60)
            for platform in platforms:
                print(f"  {platform['name']:<20} {platform['desc']}")
        else:
            configs = list_platform_configs()
            if configs:
                print("\nConfigured Platforms:")
                print("-" * 80)
                print(f"{'ID':<20} {'Type':<15} {'Enabled':<10} {'Description':<30}")
                print("-" * 80)
                for config in configs:
                    enabled = "Yes" if config.get("enable", False) else "No"
                    desc = config.get("desc", "")[:28]
                    print(f"{config.get('id', ''):<20} {config.get('type', ''):<15} {enabled:<10} {desc}")
            else:
                print("No platforms configured. Use 'platform add' to add one.")


@dataclass
class Add:
    """Add a new platform configuration.

    Create a new platform configuration with the specified type.
    """

    type: Annotated[str, tyro.conf.Positional]  # Platform type (e.g., telegram, discord, aiocqhttp)
    id: str | None = None  # Platform instance ID (defaults to type name)
    enable: bool = True  # Enable the platform immediately

    def run(self) -> None:
        """Execute the add command."""
        try:
            platform_id = self.id or self.type
            config = add_platform_config(self.type, platform_id, self.enable)
            print(f"\nPlatform '{platform_id}' added successfully!")
            print(f"  Type: {self.type}")
            print(f"  Enabled: {self.enable}")
            print(f"\nConfigure with: python main.py platforms config {platform_id}")
        except ValueError as e:
            print(f"Error: {e}")


@dataclass
class Remove:
    """Remove a platform configuration.

    Delete a platform configuration by its ID.
    """

    id: Annotated[str, tyro.conf.Positional]  # Platform instance ID to remove

    def run(self) -> None:
        """Execute the remove command."""
        try:
            delete_platform_config(self.id)
            print(f"Platform '{self.id}' has been removed")
        except ValueError as e:
            print(f"Error: {e}")


@dataclass
class Enable:
    """Enable a platform.

    Enable a disabled platform by its ID.
    """

    id: Annotated[str, tyro.conf.Positional]  # Platform instance ID to enable

    def run(self) -> None:
        """Execute the enable command."""
        try:
            update_platform_config(self.id, {"enable": True})
            print(f"Platform '{self.id}' has been enabled")
        except ValueError as e:
            print(f"Error: {e}")


@dataclass
class Disable:
    """Disable a platform.

    Disable an enabled platform by its ID.
    """

    id: Annotated[str, tyro.conf.Positional]  # Platform instance ID to disable

    def run(self) -> None:
        """Execute the disable command."""
        try:
            update_platform_config(self.id, {"enable": False})
            print(f"Platform '{self.id}' has been disabled")
        except ValueError as e:
            print(f"Error: {e}")


@dataclass
class Config:
    """Configure a platform.

    View or edit platform configuration.
    """

    id: Annotated[str, tyro.conf.Positional]  # Platform instance ID
    edit: bool = False  # Open config in editor
    set: str | None = None  # Set a config value (format: key=value)
    get: str | None = None  # Get a config value

    def run(self) -> None:
        """Execute the config command."""
        config = get_platform_config(self.id)
        if config is None:
            print(f"Error: Platform '{self.id}' not found")
            return

        schema = get_platform_config_schema(config.get("type", ""))

        if self.get:
            # Get a specific config value
            keys = self.get.split(".")
            value = config
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    value = None
                    break
            if value is not None:
                if isinstance(value, dict | list):
                    print(json.dumps(value, indent=2))
                else:
                    print(value)
            else:
                print(f"Config key '{self.get}' not found")

        elif self.set:
            # Set a config value
            if "=" not in self.set:
                print("Error: --set requires format 'key=value'")
                return

            key, value = self.set.split("=", 1)
            keys = key.split(".")

            # Navigate to the right nested dict
            current = config
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]

            # Try to parse value as JSON, otherwise treat as string
            try:
                parsed = json.loads(value)
            except json.JSONDecodeError:
                parsed = value

            current[keys[-1]] = parsed
            set_platform_config(self.id, config)
            print(f"Set {key} = {parsed}")

        elif self.edit:
            # Open in editor
            config_path = Path.home() / ".config" / "astrbot" / "platforms" / f"{self.id}_config.json"
            config_path.parent.mkdir(parents=True, exist_ok=True)

            if not config_path.exists():
                config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

            editor = os.environ.get("EDITOR", "nano")
            subprocess.run([editor, str(config_path)])

            # Read back the edited config
            try:
                new_config = json.loads(config_path.read_text(encoding="utf-8"))
                set_platform_config(self.id, new_config)
                print("Configuration saved")
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON in config file: {e}")

        else:
            # Display current config
            print(f"\nConfiguration for '{self.id}':")
            print(f"  Type: {config.get('type', 'unknown')}")
            print(f"  Enabled: {config.get('enable', False)}")

            if schema:
                print("\nSchema available. Configurable options:")
                for key, info in schema.items():
                    if key in ["type", "id", "enable"]:
                        continue
                    default = info.get("default", "required")
                    desc = info.get("description", info.get("desc", ""))
                    hint = info.get("hint", "")
                    print(f"  {key}: {desc}")
                    if hint:
                        print(f"    Hint: {hint}")
                    print(f"    Default: {default}")
                    print()

            print("Current configuration:")
            # Hide sensitive fields
            display_config = config.copy()
            for key in ["token", "key", "secret", "password", "access_token"]:
                if key in display_config:
                    display_config[key] = "***"
            print(json.dumps(display_config, indent=2, ensure_ascii=False))


@dataclass
class Info:
    """Show detailed information about a platform.

    Display platform configuration and status.
    """

    id: Annotated[str, tyro.conf.Positional]  # Platform instance ID

    def run(self) -> None:
        """Execute the info command."""
        config = get_platform_config(self.id)
        if config is None:
            print(f"Error: Platform '{self.id}' not found")
            return

        print(f"\n{'=' * 50}")
        print(f"Platform: {self.id}")
        print(f"{'=' * 50}")
        print(f"Type: {config.get('type', 'unknown')}")
        print(f"Enabled: {config.get('enable', False)}")

        # Show other config keys (hiding sensitive ones)
        other_keys = [k for k in config.keys() if k not in ["id", "type", "enable", "desc"]]
        if other_keys:
            print(f"\nConfiguration:")
            for key in other_keys:
                if key in ["token", "key", "secret", "password", "access_token"]:
                    print(f"  {key}: ***")
                else:
                    value = config[key]
                    if isinstance(value, dict | list):
                        print(f"  {key}: {json.dumps(value)}")
                    else:
                        print(f"  {key}: {value}")


# Union type for subcommands
Commands = Annotated[
    PlatformList | Add | Remove | Enable | Disable | Config | Info,
    tyro.conf.subcommand(),
]


def run_platform_command(cmd: PlatformList | Add | Remove | Enable | Disable | Config | Info) -> None:
    """Run a platform command based on its type.

    Args:
        cmd: The platform command to execute

    """
    cmd.run()
