from communex.client import CommuneClient
from communex._common import get_node_url
from communex.compat.key import Keypair

comx = CommuneClient(get_node_url())

def get_comx():
    return comx

if __name__ == "__main__":
    print(get_comx())