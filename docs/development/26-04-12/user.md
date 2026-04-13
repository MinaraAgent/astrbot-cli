- [x] create a command, user can quick start an astrbot
  - start astrbot from code source
    0. use `cwd`/data/astrbot as the working directory
    1. check the dependencies: python3, uv, node, pnpm, pm2 if not exist, prompt user to install
    2. clone the repo: `https://github.com/AstrBotDevs/AstrBot.git`, and cd into the repo
    3. build from codesource
      - init python env
        1. create a virtual environment: `uv venv`
        2. install dependencies: `uv sync`
      - init dashboard env(node)
        1. cd into dashboard: `cd dashboard`
        2. install dependencies: `pnpm install`
        3. build dashboard: `pnpm run build`
    4. use pm2 to start astrbot: `python main.py --webui-dir dashboard/dist`

  - the command i mean is to create a command line, in python use tyro
- [x] when i run python main.py, i want the command show the help, not start directly or error command
- [x] the path should more flexible, not hard code to `cwd`/data/astrbot(it's the default path), user can choose where to create the astrbot, and the command should cd into the path and start the astrbot. and the cli should flow the path where the astrbot started, so that user can run the command in any path and it will work
- [ ] 'astrbot-cli plugins config --name astrbot_plugins', should add a option to show all the config of the plugin

- [ ] create a command, user can config platforms
- [ ] create a command, user can config platform_settings
- [ ] create a command, user can config providers
- [ ] create a command, user can install/uninstall/update/list/config plugins
  - should be `python main.py plugins list/xx`, it's more clear than `python main.py list/xx`

- [ ] test the debug skill use the cli is work

- [ ] create a command, user can config persona
