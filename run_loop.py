import subprocess
import time

command = "python scripts/loop.py".split(" ")
while True:
    subprocess.run(command, check=True)
    time.sleep(3000)
    