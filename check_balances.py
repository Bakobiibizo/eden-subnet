import json
import datetime
import time
import argparse
from pathlib import Path
from loguru import logger
from communex.client import CommuneClient
from communex._common import get_node_url
from communex.compat.key import Ss58Address, Keypair
from scripts.get_querymaps import get_querymaps

comx = CommuneClient(get_node_url())


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key_name", type=str, default="vali::eden")
    parser.add_argument("--keyring", type=str, default=None)
    return parser.parse_args()
    

ARGS = parse_arguments()
            

def load_keypair_from_mnemnoic(mnemonic):
    logger.info(f"Loading keypair from mnemonic: {mnemonic}")
    return Keypair.create_from_mnemonic(mnemonic)

def load_keypair_from_local(keypath):
    logger.info(f"Loading keypair from local: {keypath}")
    with open(keypath, "r", encoding="utf-8") as f:
        key = json.loads(f.read())["data"]
        data = json.loads(key)
        private_key = data["private_key"]
        public_key = data["public_key"]
        ss58address = data["ss58_address"]
        return Keypair(ss58_address=ss58address, public_key=public_key, private_key=private_key)
    

def open_key_dict(keypath): 
    logger.info("Opening key dict")
    with open(keypath, "r", encoding="utf-8") as f:
        return json.loads(f.read())


def checktime():
    logger.info("Checking time")
    nowtime = datetime.datetime.now().timestamp()
    time_path = Path("data/time.json")
    if not time_path.exists():
        time_path.write_text(json.dumps({"time": nowtime}))
        return False
    with open(time_path, "r", encoding="utf-8") as f:
        last_time = json.loads(f.read())["time"]
    return nowtime - last_time > 180
    

def get_balance(ss58key):
    logger.info(f"Getting balance for {ss58key}")
    query_map_balance_path = Path("data/querymaps/balances.json")
    with open(query_map_balance_path, "r", encoding="utf-8") as f:
        balances = json.loads(f.read())
        if ss58key not in balances.keys():
            return 0
        return balances[ss58key]["data"]["free"]
        
    
def get_staketo(ss58key):
    logger.info(f"Getting staketo for {ss58key}")
    query_map_staketo_path = Path("data/querymaps/staketo.json")
    with open(query_map_staketo_path, "r", encoding="utf-8") as f:
        staketo_map = json.loads(f.read())
        if ss58key not in staketo_map.keys():
            return 0
        return sum(stakes[1] for stakes in staketo_map[ss58key])

def get_stakefrom(ss58key):
    logger.info(f"Getting stakefrom for {ss58key}")
    query_map_stakefrom_path = Path("data/querymaps/stakefrom.json")
    with open(query_map_stakefrom_path, "r", encoding="utf-8") as f:
        stakefrom_map = json.loads(f.read())
        if ss58key not in stakefrom_map.keys():
            return 0
        return sum(stakes[1] for stakes in stakefrom_map[ss58key])


def normalize_balances(balance):
    balance = balance / 1_000_000_000
    return round(balance, 2)


def get_balances(key, all_text=None):
    if not all_text:
        all_text = ""
        
    balance = 0
    staketo = 0
    stakefrom = 0
    balances = {}
    try: 
        balance = get_balance(key)
        balance = normalize_balances(balance)
    except Exception as e:
        print(f"Error getting balance: {e}")
    try:
        staketo = get_staketo(key)
        staketo = normalize_balances(staketo)
    except Exception as e:
        print(f"Error getting staketo: {e}")
    try:
        stakefrom = get_stakefrom(key)
        stakefrom = normalize_balances(stakefrom)
    except Exception as e:
        print(f"Error getting stakefrom: {e}")
    if balance > 50 or staketo > 50 or stakefrom > 50:
        lines = [
            f"Key: {key}",
            f"Balance:   {balance}",
            f"StakeTo:   {staketo}",
            f"Total:     {balance + staketo}",
            f"StakeFrom: {stakefrom}",
            ""
            ]
        all_text += "\n".join(lines)
    balances[key] = {
        "balance": balance,
        "staketo": staketo,
        "stakefrom": stakefrom
    }
    return all_text, balances

    
def check_keyring():
    if not checktime():
        get_querymaps()
    all_keys_path = Path(ARGS.keyring)
    keyring = json.loads(all_keys_path.read_text(encoding="utf-8"))
    
    all_text = ""
    for key in keyring.keys():
        all_text, _ = get_balances(key)
    
    with open("data/balances.txt", "w", encoding="utf-8") as f:
        f.write(all_text)
        

def check_key():
    keypair = load_keypair_from_local(f"/home/administrator/.commune/key/{ARGS.key_name}.json")
    if not checktime():
        get_querymaps()
    now_time = datetime.datetime.now().timestamp()
    _, balances = get_balances(keypair.ss58_address)
    time_log = {
        now_time: balances,
    }
    with open("data/vali_balances.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(time_log) + "\n")


def main():
    if ARGS.keyring:
        check_keyring()
    else:
        check_key()
        
        
if __name__ == "__main__":
    while True:
        main()
        time.sleep(86400)
        