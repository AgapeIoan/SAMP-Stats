import json

with open("config.json", "r") as f:
    config = json.load(f)

BOT_TOKEN = config["BOT_TOKEN"]
DEV_ID = config["DEV_ID"]

def is_dev(user_id):
    return user_id == DEV_ID