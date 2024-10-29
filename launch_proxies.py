import subprocess

for i in range(22):
    value = 7002 + i
    command = ["pm2", "start", f"cargo run launch-proxy 0.0.0.0 {value} http://localhost:7091", "-n", f"miner_proxy_{i+2}"]
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(result.stdout)
    print(result.stderr)