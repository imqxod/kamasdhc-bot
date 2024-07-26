import json, os, sys
sys.dont_write_bytecode = True

current_dir = os.path.dirname(os.path.abspath(__file__))
cfg_file = os.path.join(current_dir, "../config.json")

with open(cfg_file, "r") as file:
    cfg_content = json.load(file)

def get_token():
    return cfg_content["Bot"]["Token"]

def get_guild_ids():
    return cfg_content["Bot"]["GuildIds"]

def get_ticket_count():
    return cfg_content["TicketCount"]

def get_ticketmanager_role():
    return cfg_content["Roles"]["TicketManager"]

def get_dropper_role():
    return cfg_content["Roles"]["Dropper"]

def get_verified_role():
    return cfg_content["Roles"]["Verified"]

def get_verify_channel():
    return cfg_content["Channels"]["Verification"]

def get_vouch_channel():
    return cfg_content["Channels"]["Vouch"]

def is_administrator_role(roleid):
    return roleid in cfg_content["administrationroles"]

def set_verify_channel(chanid):
    cfg_content["Channels"]["Verification"] = str(chanid)
    save_config()

def set_ticket_count(count):
    cfg_content["TicketCount"] = str(count)
    save_config()

def get_jailed_role():
    return cfg_content["Roles"]["Jailed"]

def save_config():
    with open(cfg_file, "w") as file:
        json.dump(cfg_content, file, indent=4)