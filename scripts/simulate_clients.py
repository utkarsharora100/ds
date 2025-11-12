import threading
import time
from invoke import run
import random

# Simulate multiple client processes by running the existing client script
# This script will spawn multiple threads; each thread runs a separate
# Python process executing client/client.py which registers/logs-in and books.

CLIENT_SCRIPT = r"venv\Scripts\python client\client.py"

def spawn_client_instance(instance_id: int):
    # Optional: pass a deterministic random seed or environment variable
    print(f"[SIM] Starting client instance {instance_id}")
    try:
        # run the client script as a separate process
        # hide=False to show output in the terminal
        result = run(f"{CLIENT_SCRIPT}", hide=False, warn=True)
        if result.exited == 0:
            print(f"[SIM] Client {instance_id} finished successfully")
        else:
            print(f"[SIM] Client {instance_id} exited with code {result.exited}")
    except Exception as e:
        print(f"[SIM] Client {instance_id} error: {e}")


def simulate_many(count=5, stagger=0.2):
    threads = []
    for i in range(count):
        t = threading.Thread(target=spawn_client_instance, args=(i+1,))
        t.start()
        threads.append(t)
        time.sleep(stagger)  # small stagger to avoid perfect simultaneity

    # Wait for all threads to finish
    for t in threads:
        t.join()

    print('[SIM] All client instances completed')


if __name__ == '__main__':
    # number of clients to spawn
    simulate_many(count=10, stagger=0.1)
