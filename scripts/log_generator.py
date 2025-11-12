import random
import time

import requests

BASE_URL = "http://127.0.0.1:8080"


def simulate_normal_traffic(duration_minutes: int = 1) -> None:
    """Simulate casual browsing with random delays."""
    print(f"--- Simulating NORMAL traffic for {duration_minutes} minute(s) ---")
    pages = ["/", "/index.html", "/products", "/about-us"]
    deadline = time.time() + duration_minutes * 60
    while time.time() < deadline:
        path = random.choice(pages)
        try:
            requests.get(f"{BASE_URL}{path}", timeout=2)
            print(".", end="", flush=True)
        except requests.RequestException:
            print("E", end="", flush=True)
        time.sleep(random.uniform(0.5, 3))
    print("\nNormal traffic simulation finished.")


def simulate_bruteforce(attempts: int = 40) -> None:
    """Send a burst of /login requests to mimic brute-force."""
    print(f"\n!!! Simulating brute-force attack ({attempts} attempts) !!!")
    for _ in range(attempts):
        try:
            requests.get(f"{BASE_URL}/login", timeout=2)
            print("x", end="", flush=True)
        except requests.RequestException:
            print("E", end="", flush=True)
        time.sleep(0.1)
    print("\nBrute-force simulation finished.")


def simulate_directory_scan(pages_to_scan: int = 60) -> None:
    """Probe random admin paths to emulate a scanner."""
    print(f"\n!!! Simulating directory scan ({pages_to_scan} guesses) !!!")
    for i in range(pages_to_scan):
        try:
            requests.get(f"{BASE_URL}/admin_backup/config_{i}.txt", timeout=2)
            print("s", end="", flush=True)
        except requests.RequestException:
            print("E", end="", flush=True)
        time.sleep(0.2)
    print("\nDirectory scan simulation finished.")


if __name__ == "__main__":
    simulate_normal_traffic(duration_minutes=1)
    time.sleep(5)
    simulate_bruteforce(attempts=40)
    time.sleep(5)
    simulate_directory_scan(pages_to_scan=60)
