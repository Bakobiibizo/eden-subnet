import json
import os
import time
import subprocess


SUBNETS = [3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]


def get_vali_key():
    with open("data/vali_keys.json", "r", encoding="utf-8") as f:
        data = json.loads(f.read())
        for name, key in data.items():
            return name, key


def check_register():
    vali_name, key = get_vali_key()
    for subnet in SUBNETS:
        is_registered = False
        keypath = f"data/querymaps/{subnet}/ss58key.json"
        if os.path.exists(keypath):
            with open(keypath, "r", encoding="utf-8") as f:
                json_data = json.loads(f.read())
                for uid, ss58key in json_data.items():
                    if ss58key == key:
                        is_registered = True
                        break
        if not is_registered:
            print(vali_name, key)
            print("Not Registered on Subnet", subnet)
            subprocess.run(["comx", "module", "register", f"{vali_name}", f"{vali_name}", f"{subnet}", "--ip", "0.0.0.0", "--port", "8787"])
    

if __name__ == "__main__":
    while True:
        check_register()
        time.sleep(86400)
    