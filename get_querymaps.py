import json
import time
from pathlib import Path
from loguru import logger

from communex._common import get_node_url
from communex.client import CommuneClient

comx = CommuneClient(get_node_url())



SUBNET_QUERY_MAP = {
    "key": comx.query_map_key,
    "address": comx.query_map_address,
    "weights": comx.query_map_weights
}

QUERY_MAP = {
    "balances": comx.query_map_balances,
    "emissions": comx.query_map_emission,
    "dividens": comx.query_map_dividend,
    "incentives": comx.query_map_incentive,
    "staketo": comx.query_map_staketo,
    "stakefrom": comx.query_map_stakefrom
}



QUERY_KEYS = list(QUERY_MAP.keys())

SUBNET_QUERY_KEYS = list(SUBNET_QUERY_MAP.keys())

SUBNETS = list(range(23))
def get_query_map(query_key: str):
    logger.info(f"Getting query map {query_key}")
    if query_key in QUERY_MAP.keys():
        return QUERY_MAP[query_key]
    if query_key in SUBNET_QUERY_MAP.keys():
        return SUBNET_QUERY_MAP[query_key]
    else:
        raise ValueError(f"Invalid query key: {query_key}")
    

def get_querymaps():
    logger.info("Getting all query maps")
    query_map_dir = Path("./data/querymaps")
    if not query_map_dir.exists():
        query_map_dir.mkdir(parents=True)
    
    for subnet in SUBNETS:
        subnet_path = query_map_dir / str(subnet)
        if not subnet_path.exists():
            subnet_path.mkdir(parents=True)
        for query_key in SUBNET_QUERY_KEYS:
            query_map = get_query_map(query_key)(netuid=subnet)
        with open(subnet_path / f"{query_key}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(query_map, indent=4))

    for query_key in QUERY_KEYS:
        query_map = get_query_map(query_key)()
        with open(f"./{query_map}/{query_key}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(query_map, indent=4))
            
if __name__ == "__main__":
    while True:
        get_querymaps()
        time.sleep(1800)