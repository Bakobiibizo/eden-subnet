from communex.client import CommuneClient
from communex._common import get_node_url
from communex.compat.key import Keypair, classic_load_key


comx = CommuneClient(get_node_url())


def load_key(key_name: str) -> Keypair:
    return classic_load_key(key_name)

def get_querymap(subnet: int) -> dict:
    return comx.query_map_weights(netuid=subnet)


def main():
    query = "Balances"
    query_map = get_querymap(10)
    weights = query_map[633]
    print(weights)
    
        
        
    
    
if __name__ == "__main__":
    main()