from communex._common import get_node_url
from communex.client import CommuneClient
from communex.compat.key import Keypair
from pathlib import Path
from typing import Dict, Tuple, Any, Optional, List
import os
import subprocess
import json
import time
import argparse
from loguru import logger
comx = CommuneClient(get_node_url())


QUERYMAPS = ("address", "weights", "ss58key")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vali_key", type=str, default="vali::eden", help="Your validator key name or ss58 address")
    parser.add_argument("--copy_key", type=str, default="5H9YPS9FJX6nbFXkm9zVhoySJBX9RRfWF36abisNz5Ps9YaX", help="Validator ss58 address")
    parser.add_argument("--pull_querymaps", action="store_true", help="Pull querymaps regardless of last time they were pulled")
    return parser.parse_args()
    
ARGS = parse_arguments()
VALI_KEY = "embrace_forest"
SYNTHIA_VALIDATOR = ARGS.copy_key
PULL_QUERYMAPS = ARGS.pull_querymaps
    

def open_file(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
    
def write_file(file_path: str, data: Any):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(data)
        
def serialize_data(data: dict):
    return json.dumps(data)

def deserialize_data(data: str):
    return json.loads(data)

def check_time(data_path = "./data/"):
    json_data = open_file(f"{data_path}/time.json")
    last_time_check = deserialize_data(json_data)["time"]
    current_time = int(time.time())
    write_file(f"{data_path}/time.json", serialize_data({"time": current_time}))    
    result = current_time - last_time_check > 600
    return True if ARGS.pull_querymaps else result

def pull_maps(data_path = "./data", subnet=10):
    """
    Pull the maps from the Commune network if the local time has changed more than 10 minutes
    since the last pull. This function is intended to be run on startup and periodically
    while the process is running. The stored time is in a file named "./data/time.json".
    """
    map_path = f"{data_path}/querymaps/{subnet}"
    if len(os.listdir(map_path)) < len(QUERYMAPS):
        return get_querymaps(subnet)
    query_map = {}
    for query_name in QUERYMAPS:
        map_path = f"{data_path}/querymaps/{subnet}/{query_name}.json"
        json_data = open_file(map_path)
        query_map[query_name] = deserialize_data(json_data)
    return query_map["address"], query_map["weights"], query_map["ss58key"]
    

def get_keypair(key_name) -> Keypair:
    if not key_name:
        args = parse_arguments()
        key_name = args.vali_key
    logger.info(f"Getting keypair for {key_name}")
    file_path = Path(f"~/.commune/key/{key_name}.json").expanduser().resolve()
    with open(file_path, "r", encoding="utf-8") as f:
        json_data = json.loads(f.read())
        data = json.loads(json_data["data"])
        private_key = data["private_key"]
        public_key = data["public_key"]
        ss58_address = data["ss58_address"]
    return Keypair(ss58_address=ss58_address, public_key=public_key, private_key=private_key)


def get_querymaps(subnet=10) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str]]:
    logger.info(f"Getting query maps for subnet {subnet}")
    address_map = comx.query_map_address(subnet)
    weights_map = comx.query_map_weights(subnet)
    ss58key_map = comx.query_map_key(subnet)
    return address_map, weights_map, ss58key_map


VALI_KEY_MAP = {
    1: "5H9YPS9FJX6nbFXkm9zVhoySJBX9RRfWF36abisNz5Ps9YaX",
    2: "5CXiWwsS76H2vwroWu4SvdAS3kxprb7aFtqWLxxZC5FNhYri"
}


def get_all_querymaps() -> Tuple[Dict[str, dict], Dict[str, dict], Dict[str, dict]]:
    logger.info("Getting all query maps")
    subnets = [2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    address_maps = {}
    weights_maps = {}
    ss58key_maps = {}
    is_time = check_time()
    for subnet in subnets:
        if not os.path.exists(f"./data/querymaps/{subnet}"):
            os.makedirs(f"./data/querymaps/{subnet}")
        address_maps[f"{subnet}"] = {}
        weights_maps[f"{subnet}"] = {}
        ss58key_maps[f"{subnet}"] = {}
        if is_time:
            address_map, weights_map, ss58key_map = get_querymaps(subnet)
            address_maps[f"{subnet}"] = address_map
            weights_maps[f"{subnet}"] = weights_map
            ss58key_maps[f"{subnet}"] = ss58key_map
            with open(f"./data/querymaps/{subnet}/address.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(address_maps[f"{subnet}"], indent=4))
            with open(f"./data/querymaps/{subnet}/weights.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(weights_maps[f"{subnet}"], indent=4))
            with open(f"./data/querymaps/{subnet}/ss58key.json", "w", encoding="utf-8") as f:
                f.write(json.dumps(ss58key_maps[f"{subnet}"], indent=4))
        else:
            address_map, weights_map, ss58key_map = pull_maps(
                data_path="./data/", subnet=subnet
            )
            address_maps[f"{subnet}"] = address_map
            weights_maps[f"{subnet}"] = weights_map
            ss58key_maps[f"{subnet}"] = ss58key_map
    return address_maps, weights_maps, ss58key_maps

ADDRESS_MAPS, WEIGHTS_MAPS, SS58KEY_MAPS = get_all_querymaps()

def rootnet(keypair):
    with open("./data/querymaps/0/weights.json", "r", encoding="utf-8") as f:
        weights = json.loads(f.read())["105"]
        uids = [   0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        weights = [5, 3, 0, 3, 0, 2, 0, 1, 0, 1,  4,  0,  1,  0,  2,  1,  0,  0,  1,  1,  1]
        try:
            result = comx.vote(keypair, uids, weights, 0)
            print(f"Rootnet vote: {result.extrinsic}")
        except Exception as e:
            logger.error(f"Error voting for subnet 0: {e}")
            return

def get_ss58key_info(subnet=10, ss58key=None) -> Tuple[Optional[int], Optional[List[Tuple[int, int]]]]:
    if not ss58key:
        ss58key = VALI_KEY_MAP[1]
    logger.info(f"Getting ss58key info for subnet {subnet} and ss58key {ss58key}")
    try:
        vali_uid = next(
            (
                int(uid)
                for uid, key in SS58KEY_MAPS[f"{subnet}"].items()
                if key == ss58key
            ),
            None,
        )
    except Exception as e:
        if ss58key == VALI_KEY_MAP[2]:
            logger.error(f"Error getting ss58key info for subnet {subnet} and ss58key {ss58key}: {e}")
        else:
            ss58key == VALI_KEY_MAP[2]
            get_ss58key_info(subnet, ss58key)

        
    logger.debug(f"uid: {vali_uid}", f"subnet: {subnet}")
    if vali_uid is None:
        logger.warning(f"No uid found for ss58key {ss58key} on subnet {subnet}")
        return None, None

    weights = WEIGHTS_MAPS[f"{subnet}"].get(str(vali_uid))
    if weights is None:
        logger.warning(f"No weights found for uid {vali_uid} on subnet {subnet}")
        return None, None

    return vali_uid, weights

def get_selfuid(subnet):
    logger.info("Getting self UID")
    with open(f"./data/querymaps/{subnet}/ss58key.json", "r", encoding="utf-8") as f:
        json_data = json.loads(f.read())
        for uid, key in json_data.items():
            if key == VALI_KEY.ss58_address:
                logger.info(f"Self UID: {uid}")
                return int(uid)
    return None

def subnet10(keypair, selfuid):
    logger.info("Voting for subnet 10")
    uids = []
    weights = []
    # for i in range(820):
        # if i == selfuid:
            # continue
        # uids.append(i)
        # weights.append(30)
    with open("./data/weights.json", "r", encoding="utf-8") as f:
        data = json.loads(f.read())
        uids = data["uids"]
        weights = data["weights"]

    logger.info(f"UIDs: {uids} | Weights: {weights}")
    result = comx.vote(keypair, uids, weights, 10)
    if result.is_success:
        logger.info(f"Vote success on subnet 10: {result.extrinsic}")
    else:
        logger.error(f"Error voting for subnet 10: {result.extrinsic}")
        return
    
    try:
        logger.info(f"UIDs: {uids} | Weights: {weights}")
        result = comx.vote(keypair, uids, weights, 10)
        if result.is_success:
            logger.info(f"Vote success on subnet 10: {result.extrinsic}")
    except Exception as e:
        logger.error(f"Error voting for subnet 10: {e}\n{result.extrinsic}")
        return
    return
    

def main():
    logger.info("Starting main loop")
    selfuid = get_selfuid(10)
    subnet10(VALI_KEY, selfuid)
    rootnet(VALI_KEY)
    for subnet in ADDRESS_MAPS.keys():
        self_uid = get_selfuid(subnet)
        logger.info(f"Processing subnet {subnet}")
        
        uids = []
        weights = []
        _, synthia_weights = get_ss58key_info(subnet=subnet)
        if not synthia_weights:
            logger.warning(f"No weights found for subnet {subnet}")
            continue
        
        
        for weight_pair in synthia_weights:
            
            uid = weight_pair[0]
            weight = weight_pair[1]
            if uid == self_uid:
                print(uid)
                print(self_uid)
                continue
            uids.append(uid)
            weights.append(weight)
        print(f"Subnet {subnet}: {uids} {weights}")
        try:
            reciept = comx.vote(VALI_KEY, uids, weights, subnet)
            if reciept.is_success:
                print(f"Vote success on subnet {subnet}: {reciept.extrinsic}")
        except Exception as e:
            print(f"Vote failed on subnet {subnet}: {e}")

if __name__ == "__main__":
    ADDRESS_MAPS, WEIGHTS_MAPS, SS58KEY_MAPS = get_all_querymaps()
    VALI_KEY = get_keypair(key_name="vali::eden")
    
    main()
    
    logger.info("Sleeping for 60 seconds")
            
    


   
   
