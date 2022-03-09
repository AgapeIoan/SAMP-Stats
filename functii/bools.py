import json
from functii.debug import DEBUG_STATE

config_dir = "storage/configs/"
config_filename = config_dir + "deb_config.json" if DEBUG_STATE else config_dir + "config.json"

with open(config_filename, "r") as f:
    config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]
DEV_ID = config["DEV_ID"]
LOGIN_USERNAME = config["LOGIN_USERNAME"]
LOGIN_PASSWORD = config["LOGIN_PASSWORD"]
USER_IDENTIFIER = config["USER_IDENTIFIER"]
USER_TOKEN = config["USER_TOKEN"]

def is_dev(user_id):
    return user_id == DEV_ID