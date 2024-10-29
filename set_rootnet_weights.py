import json
from communex.client import CommuneClient
from communex._common import get_node_url
from communex.compat.key import Keypair

comx = CommuneClient(get_node_url())


def get_keypair():
    key_data = "/home/administrator/.commune/key/vali::eden.json"
    with open(key_data, "r", encoding="utf-8") as f:
        key = json.loads(f.read())["data"]
        data = json.loads(key)
        private_key = data["private_key"]
        public_key = data["public_key"]
        ss58address = data["ss58_address"]
        return Keypair(ss58_address=ss58address, public_key=public_key, private_key=private_key)
    
def vote():
    subnet = 0
    keypair = get_keypair()
    uids = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    weights = [39.39, 18.05, 0, 5.09, 0, 5.49, 0, 1.38, 0, 1.53, 10, 0, 1.38, 0, 3.05, 1.38, 0, 0, 0.69, 1.05, 11.18, 0, 0.33, 0]
    weights = [int(weight * 100) for weight in weights]
    print (len(uids), len(weights))
    if len(uids) == len(weights):
        for uid, weight in zip(uids, weights):
            print(uid, weight)
        comx.vote(keypair, uids, weights, subnet)
        
if __name__ == "__main__":
    vote()