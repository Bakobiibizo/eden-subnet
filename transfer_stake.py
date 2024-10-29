import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from loguru import logger
from communex.client import CommuneClient 
from communex._common import get_node_url
from communex.compat.key import Keypair
from scripts.get_querymaps import get_querymaps

comx = CommuneClient(get_node_url())


def load_local_keypair(name):
    keypath = Path(f"~/.commune/key/{name}.json").expanduser().resolve()
    with open(keypath, "r", encoding="utf-8") as f:
        json_data = json.loads(f.read())["data"]
        data = json.loads(json_data)
        private_key = data["private_key"]
        public_key = data["public_key"]
        ss58_address = data["ss58_address"]
        return Keypair(ss58_address=ss58_address, public_key=public_key, private_key=private_key)
    

def get_staketo(keypair):
    query_map_path = Path("./data/querymaps/staketo.json")
    if query_map_path.exists():
        staketo_map = json.loads(query_map_path.read_text())
    
    staketo = staketo_map[keypair.ss58_address][0] if keypair.ss58_address in staketo_map else None
    return round((staketo[1] / 1_000_000_000), 2) if staketo else None
        

def transfer_stake(keypair, amount, to_ss58key):
    logger.info(f"Transfering {amount} from {keypair.ss58_address} to {to_ss58key}")
    result = comx.transfer_stake(key=keypair, amount=amount * 1_000_000_000, from_module_key=keypair.ss58_address, dest_module_address=to_ss58key)
    print(result.extrinsic)
    
    
def unstake(keypair, amount):
    logger.info(f"Unstaking {amount} from {keypair.ss58_address}")
    result = comx.unstake(key=keypair, amount=amount * 1_000_000_000, dest=keypair.ss58_address)
    print(result.extrinsic)
    
def transfer_balance(keypair, amount, to_ss58key):
    logger.info(f"Transfering {amount} from {keypair.ss58_address} to {to_ss58key}")
    result = comx.transfer(key=keypair, amount=amount * 1_000_000_000, dest=to_ss58key)
    print(result.extrinsic)

    
def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key_name", type=str, default="vali::eden")
    parser.add_argument("--to_ss58key", type=str, default="5Df8AUJhN9G3CtyV3cGNLr2g388kRDmYUA9ZYvdPz79x3hA2")
    return parser.parse_args()


def main():
    args = parse_arguments()
    keypair = load_local_keypair(args.key_name)
    # get_querymaps()
    staketo_balance = get_staketo(keypair) - 5
    logger.info(f"Current balance: {staketo_balance}")
    
    if staketo_balance > 0:
        unstake(keypair, staketo_balance)
        transfer_balance(keypair, staketo_balance, args.to_ss58key)
        log_entry = {
            "time": datetime.now().timestamp(),
            "from": keypair.ss58_address,
            "amount": staketo_balance,
            "to": args.to_ss58key,
        }
        with open("data/transfer_log.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
        
    

if __name__ == "__main__":
    while True:
        main()
        time.sleep(86400)