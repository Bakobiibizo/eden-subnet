from communex.client import CommuneClient
from communex._common import get_node_url
from communex.compat.key import classic_load_key, Keypair
from loguru import logger
import argparse
import time
import timeout_decorator


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key_name", type=str, required=False, help="Name of the validator as it will appear on chain")
    parser.add_argument("--module_path", type=str, required=False, help="Filename with out the .json suffix in the ~/.commune/key directory")
    parser.add_argument("--host", type=str, required=False, help="Host address for the validator")
    parser.add_argument("--port", type=int, required=False, help="Port for the validator")
    parser.add_argument("--subnet", type=int,required=False, help="Subnet number")
    parser.add_argument("--delegation_fee", type=int, required=False, help="Delegation fee")
    return parser.parse_args()

ARGS = parse_arguments()

comx = CommuneClient(get_node_url())
   
    
def update_module(
    module_path=None,
    address=None,
    delegation_fee=None,
    subnet=None,
    keypair=None
    ) -> None:
    
    logger.info(f"Updating module {module_path} on subnet {subnet}")
    try:
        result = comx.update_module(keypair, name=module_path, address=address, delegation_fee=delegation_fee, netuid=subnet)
        print(result.extrinsic)
        if "code" in result.extrinsic:
            if result.extrinsic["code"] == 1014:
                time.sleep(1)
            update_module(module_path=module_path, address=address, delegation_fee=delegation_fee, subnet=subnet, keypair=keypair)
            
    except Exception as e:
        print(f"Error updating module: {e}")
    


@timeout_decorator.timeout(60)  # 60 second timeout
def update_module_with_timeout(
    module_path=None,
    address=None,
    delegation_fee=None,
    subnet=None,
    keypair=None
) -> None:
    return update_module(module_path, address, delegation_fee, subnet, keypair)

def main():
    key_name = ARGS.key_name
    module_path = ARGS.module_path
    host = ARGS.host
    port = ARGS.port
    address = f"http://{host}:{port}"
    delegation_fee = ARGS.delegation_fee
    keypair = classic_load_key(ARGS.module_path)
    for i in range(3, 20):
        try:
            update_module_with_timeout(module_path, address, delegation_fee, i, keypair)
        except timeout_decorator.TimeoutError:
            logger.warning(f"Timeout occurred for subnet {i}. Retrying...")
            time.sleep(1)  # Wait for 1 second before retrying
            i -= 1  # Decrement i to retry the same subnet
        except Exception as e:
            logger.error(f"Error updating module for subnet {i}: {e}")
        
        
if __name__ == "__main__":
    main()
