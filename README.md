# AstrBot CLI

A command-line tool for managing [AstrBot](https://github.com/AstrBotDevs/AstrBot) – an open‑source, agentic chatbot infrastructure that integrates multiple IM platforms, LLMs, plugins, and AI capabilities.

## Features

- **Quick Start** – One-command installation and startup
- **Bot Management** – Configure platform connections (Telegram, Discord, QQ, etc.)
- **Provider Management** – Set up LLM providers (OpenAI, DeepSeek, Ollama, etc.)
- **Profile System** – Link providers, personas, and plugins together
- **Plugin Management** – Install, configure, and manage plugins
- **Workflow Integration** – Stateful automation via [dagu](https://github.com/dagu-dev/dagu)
- **System Management** – Start, stop, restart, and monitor AstrBot service

## Installation

```bash
# Clone the repository
git clone https://github.com/MinaraAgent/astrbot-cli.git
cd astrbot-cli

# Install dependencies with uv
uv sync
```

## Quick Start

```bash
# Install and start AstrBot
astrbot-cli quick-start

# Or specify a custom path
astrbot-cli quick-start --path ~/my-astrbot
```

## Command Reference

### System Commands

Manage the AstrBot service itself using PM2.

| Command | Description |
|---------|-------------|
| `astrbot-cli system init` | Initialize AstrBot environment |
| `astrbot-cli system upgrade` | Upgrade AstrBot installation |
| `astrbot-cli system start` | Start AstrBot service |
| `astrbot-cli system stop` | Stop AstrBot service |
| `astrbot-cli system restart` | Restart AstrBot service |
| `astrbot-cli system status` | Show service status (PID, uptime, memory, CPU) |
| `astrbot-cli system logs [lines]` | View service logs (`--follow` for streaming) |
| `astrbot-cli system info` | Show version, path, Python environment |
| `astrbot-cli system version` | Alias for `info` |

### Path Management

```bash
# Show current AstrBot installation path
astrbot-cli path

# Set AstrBot path manually
astrbot-cli path --set /path/to/astrbot

# Force set path (even if AstrBot not installed there yet)
astrbot-cli path --set /new/path --force
```

### Bot Commands

Manage platform connections (each "bot" is a platform instance).

| Command | Description |
|---------|-------------|
| `astrbot-cli bots list` | List configured bots |
| `astrbot-cli bots list --available` | List available bot types |
| `astrbot-cli bots add <type>` | Add a new bot |
| `astrbot-cli bots remove <id>` | Remove a bot |
| `astrbot-cli bots enable <id>` | Enable a bot |
| `astrbot-cli bots disable <id>` | Disable a bot |
| `astrbot-cli bots config <id>` | Configure a bot |
| `astrbot-cli bots info <id>` | Show bot info |

**Available bot types:** `telegram`, `discord`, `aiocqhttp`, `lark`, `dingtalk`, `wechat`, `wechatcom`, `wechatpak`, `wecom`, `wechatapponline`, `wechatofficial`, `wechatofficialv2`, `wechathzy`, `weixinhzy`, `weixinofficial`, `weixin`, `qq-botpy`, `qq-guild`, `kook`, `milkpick`

### Provider Commands

Manage LLM / model service providers.

| Command | Description |
|---------|-------------|
| `astrbot-cli providers list` | List configured providers |
| `astrbot-cli providers list --available` | List available provider types |
| `astrbot-cli providers add <type>` | Add a new provider |
| `astrbot-cli providers remove <id>` | Remove a provider |
| `astrbot-cli providers enable <id>` | Enable a provider |
| `astrbot-cli providers disable <id>` | Disable a provider |
| `astrbot-cli providers config <id>` | Configure a provider |
| `astrbot-cli providers info <id>` | Show provider info |

**Available provider types:** `openai`, `anthropic`, `deepseek`, `ollama`, `gemini`, `zhipu`, `moonshot`, `dashscope`, `lmdeploy`, `gemini_pro`, `yi`, `doubao`, `mistral`, `groq`

### Profile Commands

Manage configuration profiles that link providers, personas, and plugins.

| Command | Description |
|---------|-------------|
| `astrbot-cli profiles list` | List all profiles |
| `astrbot-cli profiles create <name>` | Create a new profile |
| `astrbot-cli profiles delete <id>` | Delete a profile |
| `astrbot-cli profiles show [id]` | Show profile details |
| `astrbot-cli profiles set <id> --provider X` | Set profile provider |
| `astrbot-cli profiles set <id> --persona X` | Set profile persona |
| `astrbot-cli profiles set <id> --plugins X,Y` | Set profile plugins |
| `astrbot-cli profiles use <id>` | Set active profile |

### Persona Commands

Manage persona definitions that shape bot behavior.

| Command | Description |
|---------|-------------|
| `astrbot-cli personas list` | List all personas |
| `astrbot-cli personas create <id> <prompt>` | Create a persona |
| `astrbot-cli personas edit <id> --prompt X` | Edit persona prompt |
| `astrbot-cli personas delete <id>` | Delete a persona |
| `astrbot-cli personas show <id>` | Show persona details |

### Plugin Commands

Manage AstrBot plugins.

| Command | Description |
|---------|-------------|
| `astrbot-cli plugins list` | List installed plugins |
| `astrbot-cli plugins list --all` | List all available plugins |
| `astrbot-cli plugins install <name>` | Install a plugin |
| `astrbot-cli plugins uninstall <name>` | Uninstall a plugin |
| `astrbot-cli plugins update [name]` | Update plugin(s) |
| `astrbot-cli plugins search <query>` | Search for plugins |
| `astrbot-cli plugins config <name>` | Configure a plugin |
| `astrbot-cli plugins info <name>` | Show plugin info |

### Config Commands

Manage global configuration settings.

| Command | Description |
|---------|-------------|
| `astrbot-cli config show` | Show current settings |
| `astrbot-cli config show --defaults` | Show default settings |
| `astrbot-cli config get <key>` | Get a setting value |
| `astrbot-cli config set <key> <value>` | Set a setting value |
| `astrbot-cli config edit` | Edit settings in editor |
| `astrbot-cli config reset --confirm` | Reset to defaults |
| `astrbot-cli config schema` | Show settings schema |

### Workflow Commands

Manage stateful workflows via dagu integration.

| Command | Description |
|---------|-------------|
| `astrbot-cli workflows list` | List all workflows |
| `astrbot-cli workflows start <name>` | Start a workflow |
| `astrbot-cli workflows stop <name>` | Stop a workflow |
| `astrbot-cli workflows status <name>` | Show workflow status |
| `astrbot-cli workflows logs <name>` | Show workflow logs |
| `astrbot-cli workflows create <name>` | Create a new workflow |

## Configuration Files

| File | Purpose |
|------|---------|
| `data/cmd_config.json` | Bots, providers, global config |
| `data/profiles.json` | Profile definitions |
| `data/data_v4.db` | SQLite database (personas) |
| `data/workflows/` | Workflow YAML files |
| `~/.astrbot-cli/config.json` | CLI settings (AstrBot path) |

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) – Python package manager
- [Node.js](https://nodejs.org/) – For dashboard
- [pnpm](https://pnpm.io/) – Node package manager
- [PM2](https://pm2.keymetrics.io/) – Process manager

## Development

```bash
# Run CLI in development
uv run astrbot-cli --help

# Run tests
uv run pytest
```

## License

MIT License
