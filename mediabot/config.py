"""Config values for pollbot."""

import os
import sys

import toml

default_config = {
    "telegram": {
        "userbot": True,
        "api_key": "your_telegram_api_key (empty if in userbot mode)",
        "phone_number": "your_phone_number (empty if not in userbot mode)",
        "app_api_id": 0,
        "app_api_hash": "apihash",
    },
    "bot": {
        "backup": False,
        "backup_path": ".",
        "meme_chat_id": "",
        "admin": "your_nickname_or_telegram_id",
    },
    "logging": {
        "sentry_enabled": False,
        "sentry_token": "",
        "debug": False,
    },
}

config_path = os.path.expanduser("~/.config/media_bot.toml")

if not os.path.exists(config_path):
    with open(config_path, "w") as file_descriptor:
        toml.dump(default_config, file_descriptor)
    print("Please adjust the configuration file at '~/.config/media_bot.toml'")
    sys.exit(1)
else:
    config = toml.load(config_path)
    # Set default values for any missing keys in the loaded config
    for key, category in default_config.items():
        for option, value in category.items():
            if option not in config[key]:
                config[key][option] = value
