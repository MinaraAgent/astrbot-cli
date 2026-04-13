"""Main entry point for AstrBot CLI."""

import sys
from dataclasses import dataclass
from pathlib import Path

import tyro

from .src.plugin import Install, Uninstall, Update, PluginList, Search, Config as PluginConfig, Info as PluginInfo
from .src.platform import PlatformList, Add, Remove, Enable, Disable, Config as PlatformConfig, Info as PlatformInfo
from .src.platform_settings import Show, Set as SettingsSet, Get, Reset, Edit, Schema
from .src.quick_start import main as quick_start_main
from .src.path_config import (
    print_current_path,
    set_astrbot_path,
    validate_astrbot_path,
)


@dataclass
class PathCommand:
    """Show or set the AstrBot installation path."""
    set: Path | None = None  # Set a new AstrBot path
    force: bool = False  # Force set even if AstrBot not installed at path


@dataclass
class QuickStart:
    """Quick start AstrBot from source code.

    This command will:
    1. Check required dependencies (python3, uv, node, pnpm, pm2)
    2. Clone AstrBot repository to the specified path
    3. Setup Python environment with uv
    4. Build the dashboard
    5. Start AstrBot with PM2
    """
    force: bool = False
    skip_deps: bool = False
    path: Path | None = None  # Custom installation path


def print_help() -> None:
    """Print CLI help message."""
    print("""
AstrBot CLI - Command Line Interface for AstrBot

Usage:
    astrbot-cli <command> [options]

Commands:
    quick-start        Quick start AstrBot from source code
    path              Show or set the AstrBot installation path
    plugins           Manage AstrBot plugins
    platforms         Manage AstrBot platforms
    platform-settings Configure platform settings

Path Commands:
    astrbot-cli path                  Show current AstrBot path
    astrbot-cli path --set <path>     Set AstrBot path manually

Quick Start Options:
    astrbot-cli quick-start                    Start AstrBot (uses saved/default path)
    astrbot-cli quick-start --path /my/path    Start AstrBot at specific path
    astrbot-cli quick-start --force            Force reinstall
    astrbot-cli quick-start --help             Show all options

Plugin Commands:
    astrbot-cli plugins list              List installed plugins
    astrbot-cli plugins list --all        List all available plugins
    astrbot-cli plugins install <name>    Install a plugin
    astrbot-cli plugins uninstall <name>  Uninstall a plugin
    astrbot-cli plugins update [name]     Update plugin(s)
    astrbot-cli plugins search <query>    Search for plugins
    astrbot-cli plugins config <name>     Configure a plugin
    astrbot-cli plugins info <name>       Show plugin info

Platform Commands:
    astrbot-cli platforms list              List configured platforms
    astrbot-cli platforms list --available  List available platform types
    astrbot-cli platforms add <type>        Add a new platform
    astrbot-cli platforms remove <id>       Remove a platform
    astrbot-cli platforms enable <id>       Enable a platform
    astrbot-cli platforms disable <id>      Disable a platform
    astrbot-cli platforms config <id>       Configure a platform
    astrbot-cli platforms info <id>         Show platform info

Platform Settings Commands:
    astrbot-cli platform-settings show              Show current settings
    astrbot-cli platform-settings show --defaults   Show default settings
    astrbot-cli platform-settings get <key>         Get a setting value
    astrbot-cli platform-settings set <key> <value> Set a setting value
    astrbot-cli platform-settings edit              Edit settings in editor
    astrbot-cli platform-settings reset --confirm   Reset to defaults
    astrbot-cli platform-settings schema            Show settings schema

Examples:
    astrbot-cli quick-start                        Start AstrBot at default location
    astrbot-cli quick-start --path ~/my-astrbot    Start AstrBot at custom location
    astrbot-cli path                               Show where AstrBot is installed
    astrbot-cli plugins list --all                 See all available plugins
    astrbot-cli platforms add telegram             Add Telegram platform
    astrbot-cli platform-settings show             Show platform settings
""")


def main() -> None:
    """AstrBot CLI main entry point."""
    if len(sys.argv) < 2:
        print_help()
        return

    subcommand = sys.argv[1]

    if subcommand in ["--help", "-h", "help"]:
        print_help()
        return

    # Plugin subcommands
    if subcommand == "plugins":
        if len(sys.argv) < 3:
            print("Usage: astrbot-cli plugins <command>")
            print("Commands: install, uninstall, update, list, search, config, info")
            return

        plugin_cmd = sys.argv[2]
        # Parse remaining args for the plugin subcommand
        cmd_args = sys.argv[3:]

        if plugin_cmd == "install":
            args = tyro.cli(Install, args=cmd_args)
            args.run()
        elif plugin_cmd == "uninstall":
            args = tyro.cli(Uninstall, args=cmd_args)
            args.run()
        elif plugin_cmd == "update":
            args = tyro.cli(Update, args=cmd_args)
            args.run()
        elif plugin_cmd == "list":
            args = tyro.cli(PluginList, args=cmd_args)
            args.run()
        elif plugin_cmd == "search":
            args = tyro.cli(Search, args=cmd_args)
            args.run()
        elif plugin_cmd == "config":
            args = tyro.cli(PluginConfig, args=cmd_args)
            args.run()
        elif plugin_cmd == "info":
            args = tyro.cli(PluginInfo, args=cmd_args)
            args.run()
        else:
            print(f"Unknown plugin command: {plugin_cmd}")
            print("Commands: install, uninstall, update, list, search, config, info")

    # Platform subcommands
    elif subcommand == "platforms":
        if len(sys.argv) < 3:
            print("Usage: astrbot-cli platforms <command>")
            print("Commands: list, add, remove, enable, disable, config, info")
            return

        platform_cmd = sys.argv[2]
        # Parse remaining args for the platform subcommand
        cmd_args = sys.argv[3:]

        if platform_cmd == "list":
            args = tyro.cli(PlatformList, args=cmd_args)
            args.run()
        elif platform_cmd == "add":
            args = tyro.cli(Add, args=cmd_args)
            args.run()
        elif platform_cmd == "remove":
            args = tyro.cli(Remove, args=cmd_args)
            args.run()
        elif platform_cmd == "enable":
            args = tyro.cli(Enable, args=cmd_args)
            args.run()
        elif platform_cmd == "disable":
            args = tyro.cli(Disable, args=cmd_args)
            args.run()
        elif platform_cmd == "config":
            args = tyro.cli(PlatformConfig, args=cmd_args)
            args.run()
        elif platform_cmd == "info":
            args = tyro.cli(PlatformInfo, args=cmd_args)
            args.run()
        else:
            print(f"Unknown platform command: {platform_cmd}")
            print("Commands: list, add, remove, enable, disable, config, info")

    # Platform settings subcommands
    elif subcommand == "platform-settings":
        if len(sys.argv) < 3:
            print("Usage: astrbot-cli platform-settings <command>")
            print("Commands: show, get, set, edit, reset, schema")
            return

        settings_cmd = sys.argv[2]
        # Parse remaining args for the settings subcommand
        cmd_args = sys.argv[3:]

        if settings_cmd == "show":
            args = tyro.cli(Show, args=cmd_args)
            args.run()
        elif settings_cmd == "get":
            args = tyro.cli(Get, args=cmd_args)
            args.run()
        elif settings_cmd == "set":
            args = tyro.cli(SettingsSet, args=cmd_args)
            args.run()
        elif settings_cmd == "edit":
            args = tyro.cli(Edit, args=cmd_args)
            args.run()
        elif settings_cmd == "reset":
            args = tyro.cli(Reset, args=cmd_args)
            args.run()
        elif settings_cmd == "schema":
            args = tyro.cli(Schema, args=cmd_args)
            args.run()
        else:
            print(f"Unknown platform-settings command: {settings_cmd}")
            print("Commands: show, get, set, edit, reset, schema")

    # Path command
    elif subcommand == "path":
        if len(sys.argv) < 3:
            # No subcommand, show current path
            print_current_path()
            return

        path_cmd = sys.argv[2]
        if path_cmd == "--set" or path_cmd == "-s":
            if len(sys.argv) < 4:
                print("Usage: astrbot-cli path --set <path> [--force]")
                return
            new_path = Path(sys.argv[3]).resolve()
            # Check for --force flag
            force_set = "--force" in sys.argv or "-f" in sys.argv
            if force_set or (new_path / "main.py").exists():
                set_astrbot_path(new_path)
                print(f"✅ AstrBot path set to: {new_path}")
            else:
                print(f"❌ AstrBot not found at: {new_path}")
                print("   Use --force to set this path anyway.")
                sys.exit(1)
        elif path_cmd in ["--help", "-h"]:
            print("""
astrbot-cli path - Show or set AstrBot installation path

Usage:
    astrbot-cli path                  Show current AstrBot path
    astrbot-cli path --set <path>     Set AstrBot path manually
    astrbot-cli path --set <path> --force  Force set path (even if AstrBot not installed)

The path is saved in ~/.astrbot-cli/config.json and is used by all
CLI commands to locate the AstrBot installation.

Examples:
    astrbot-cli path
    astrbot-cli path --set ~/my-astrbot
    astrbot-cli path --set /opt/astrbot
    astrbot-cli path --set /new/path --force  # Set path before installing
""")
        else:
            # Try to parse as PathCommand
            args = tyro.cli(PathCommand, args=sys.argv[2:])
            if args.set:
                if args.force or (args.set / "main.py").exists():
                    set_astrbot_path(args.set)
                    print(f"✅ AstrBot path set to: {args.set}")
                else:
                    print(f"❌ AstrBot not found at: {args.set}")
                    print("   Use --force to set this path anyway.")
                    sys.exit(1)
            else:
                print_current_path()

    elif subcommand == "quick-start":
        args = tyro.cli(QuickStart, args=sys.argv[2:])
        quick_start_main(force=args.force, skip_deps=args.skip_deps, path=args.path)
    else:
        # Treat as quick-start with legacy args for backward compatibility
        args = tyro.cli(QuickStart, args=sys.argv[1:])
        quick_start_main(force=args.force, skip_deps=args.skip_deps, path=args.path)


if __name__ == "__main__":
    main()
