import random
import time
import uuid
from typing import Any, Callable, Dict, Optional

import requests

FAKE_PUBLIC_IPS = [
    "8.8.8.8",        # Google
    "1.1.1.1",        # Cloudflare
    "208.67.222.222", # OpenDNS
    "185.199.108.153",# GitHub
    "151.101.1.69",   # Fastly
    "13.227.37.63",   # AWS CloudFront
]

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile/15E148 Safari/604.1",
    "curl/7.88.1",
    "python-requests/2.31.0",
]

REFERERS = [
    "https://www.google.com/search?q=observability",
    "https://duckduckgo.com/?q=elk+stack",
    "https://news.ycombinator.com/",
    "https://www.facebook.com/ads/click",
    "https://partner.example.com/campaign",
    "https://t.co/shortlink",
]

ACCEPT_LANGUAGES = [
    "en-US,en;q=0.9",
    "vi-VN,vi;q=0.8,en;q=0.6",
    "fr-FR,fr;q=0.9,en;q=0.8",
    "ja-JP,ja;q=0.7,en;q=0.5",
]

PRODUCT_IDS = [f"SKU-{i:04d}" for i in range(101, 121)]
SEARCH_TERMS = ["ssd", "router", "t-shirt", "điện thoại", "gaming pc", "shoes", "laptop", "watch"]
LOCATIONS = ["us-east", "us-west", "apac", "eu-central", "sa-east"]

BASE_URL = "http://127.0.0.1:8080"


def random_ipv4_address() -> str:
    """Generate a pseudo-random IPv4 address."""
    return ".".join(str(random.randint(2, 254)) for _ in range(4))


def random_headers(forced_ip: Optional[str] = None, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    headers = {
        "X-Forwarded-For": forced_ip or random.choice(FAKE_PUBLIC_IPS + [random_ipv4_address()]),
        "User-Agent": random.choice(USER_AGENTS),
        "Referer": random.choice(REFERERS),
        "Accept-Language": random.choice(ACCEPT_LANGUAGES),
        "X-Request-ID": uuid.uuid4().hex,
        "X-Device-Type": random.choice(["desktop", "mobile", "tablet"]),
    }
    if extra:
        headers.update(extra)
    return headers


def random_cookies() -> Dict[str, str]:
    return {
        "session_id": uuid.uuid4().hex[:16],
        "ab_bucket": random.choice(["A", "B", "C"]),
    }


def hit_endpoint(
    method: str,
    path: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    json_body: Optional[Dict[str, Any]] = None,
    cookies: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    forced_ip: Optional[str] = None,
    tag: str = ".",
) -> None:
    request_headers = random_headers(forced_ip=forced_ip, extra=headers)
    request_cookies = cookies or random_cookies()
    try:
        requests.request(
            method,
            f"{BASE_URL}{path}",
            params=params,
            data=data,
            json=json_body,
            headers=request_headers,
            cookies=request_cookies,
            timeout=2,
        )
        print(tag, end="", flush=True)
    except requests.RequestException:
        print("E", end="", flush=True)


def _callable_or_value(value: Optional[Callable[[], Any]]) -> Optional[Any]:
    if callable(value):
        return value()
    return value


def simulate_normal_traffic(duration_minutes: int = 1) -> None:
    """Simulate casual browsing with random delays and varied payloads."""
    print(f"--- Simulating NORMAL traffic for {duration_minutes} minute(s) ---")
    pages = [
        {"path": "/", "method": "GET"},
        {"path": "/index.html", "method": "GET"},
        {"path": "/about-us", "method": "GET"},
        {"path": "/products/{product_id}", "method": "GET", "path_builder": lambda: f"/products/{random.choice(PRODUCT_IDS)}"},
        {
            "path": "/search",
            "method": "GET",
            "params": lambda: {"q": random.choice(SEARCH_TERMS), "page": random.randint(1, 3), "sort": random.choice(["popular", "price", "new"])},
        },
        {
            "path": "/cart",
            "method": "POST",
            "json": lambda: {"product_id": random.choice(PRODUCT_IDS), "qty": random.randint(1, 3)},
        },
        {
            "path": "/signup",
            "method": "POST",
            "json": lambda: {"email": f"user{random.randint(1000, 9999)}@example.com", "newsletter": random.choice([True, False])},
        },
    ]
    deadline = time.time() + duration_minutes * 60
    while time.time() < deadline:
        page = random.choice(pages)
        path_builder = page.get("path_builder")
        path = path_builder() if callable(path_builder) else page["path"]
        params = _callable_or_value(page.get("params"))
        payload = _callable_or_value(page.get("data"))
        json_body = _callable_or_value(page.get("json"))
        hit_endpoint(page["method"], path, params=params, data=payload, json_body=json_body, tag=".")
        time.sleep(random.uniform(0.3, 2.5))
    print("\nNormal traffic simulation finished.")


def simulate_search_spike(duration_seconds: int = 30, rpm: int = 120) -> None:
    """Generate a short spike of campaign traffic to search endpoint."""
    print(f"\n*** Simulating SEARCH spike ({duration_seconds}s @ {rpm} rpm) ***")
    interval = max(60 / max(rpm, 1), 0.05)
    deadline = time.time() + duration_seconds
    while time.time() < deadline:
        params = {
            "q": random.choice(SEARCH_TERMS),
            "device": random.choice(["desktop", "mobile"]),
            "utm_campaign": random.choice(["spring_sale", "black_friday", "retargeting"]),
        }
        cookies = {"session_id": uuid.uuid4().hex[:16], "campaign": params["utm_campaign"]}
        hit_endpoint("GET", "/search", params=params, cookies=cookies, headers={"X-Geo-Region": random.choice(LOCATIONS)}, tag="?")
        time.sleep(interval)
    print("\nSearch spike simulation finished.")


def simulate_bruteforce(attempts: int = 40) -> None:
    """Send a burst of /login POST requests to mimic brute-force."""
    print(f"\n!!! Simulating brute-force attack ({attempts} attempts) !!!")
    attacker_ips = [random_ipv4_address() for _ in range(max(3, attempts // 5))]
    usernames = ["admin", "root", "support", "sales", "ops"]
    for _ in range(attempts):
        payload = {"username": random.choice(usernames), "password": uuid.uuid4().hex[:8]}
        hit_endpoint(
            "POST",
            "/login",
            data=payload,
            forced_ip=random.choice(attacker_ips),
            headers={"Content-Type": "application/x-www-form-urlencoded", "X-Threat-Score": str(random.randint(60, 99))},
            tag="x",
        )
        time.sleep(0.1)
    print("\nBrute-force simulation finished.")


def simulate_directory_scan(pages_to_scan: int = 60) -> None:
    """Probe random admin paths to emulate a scanner."""
    print(f"\n!!! Simulating directory scan ({pages_to_scan} guesses) !!!")
    scanner_ip = random_ipv4_address()
    wordlist = ["admin", "backup", "config", "db", "phpinfo", "old", "staging"]
    for _ in range(pages_to_scan):
        target = random.choice(wordlist)
        path = f"/admin_backup/{target}_{random.randint(1, 999)}.cfg"
        hit_endpoint("GET", path, forced_ip=scanner_ip, headers={"User-Agent": "dirbuster/2.0"}, tag="s")
        time.sleep(0.15)
    print("\nDirectory scan simulation finished.")


def simulate_api_noise(events: int = 50) -> None:
    """Stress the API with mixed HTTP verbs and payloads."""
    print(f"\n+++ Simulating API noise ({events} calls) +++")
    api_calls = [
        {
            "method": "GET",
            "path_builder": lambda: f"/api/v1/orders/{random.randint(1000, 1050)}",
            "params": lambda: {"expand": random.choice(["items", "payments", "customer"])},
        },
        {
            "method": "PATCH",
            "path_builder": lambda: f"/api/v1/orders/{random.randint(1000, 1050)}",
            "json": lambda: {"status": random.choice(["pending", "processing", "canceled"])},
        },
        {
            "method": "POST",
            "path": "/api/v1/orders",
            "json": lambda: {
                "product_id": random.choice(PRODUCT_IDS),
                "qty": random.randint(1, 5),
                "region": random.choice(LOCATIONS),
            },
        },
        {
            "method": "DELETE",
            "path_builder": lambda: f"/api/v1/orders/{random.randint(900, 920)}",
        },
    ]
    for _ in range(events):
        call = random.choice(api_calls)
        path_builder = call.get("path_builder")
        path = path_builder() if callable(path_builder) else call["path"]
        params = _callable_or_value(call.get("params"))
        json_body = _callable_or_value(call.get("json"))
        hit_endpoint(call["method"], path, params=params, json_body=json_body, headers={"X-Service": "backend-api"}, tag="a")
        time.sleep(random.uniform(0.05, 0.4))
    print("\nAPI noise simulation finished.")


def simulate_conditional_requests(requests_count: int = 25) -> None:
    """Trigger cache-style conditional GETs to elicit 304 responses."""
    print(f"\n~~~ Simulating conditional GETs ({requests_count} requests) ~~~")
    future_date = "Fri, 01 Jan 2100 00:00:00 GMT"
    past_date = "Fri, 01 Jan 1999 00:00:00 GMT"
    for i in range(requests_count):
        headers = {"If-Modified-Since": future_date if i % 3 else past_date}
        hit_endpoint("GET", "/index.html", headers=headers, tag="m")
        time.sleep(random.uniform(0.1, 0.4))
    print("\nConditional request simulation finished.")


def simulate_range_requests(events: int = 30) -> None:
    """Request byte ranges to create 206 Partial Content and 416 errors."""
    print(f"\n=== Simulating RANGE requests ({events} calls) ===")
    for _ in range(events):
        if random.random() < 0.65:
            end = random.randint(150, 400)
            headers = {"Range": f"bytes=0-{end}"}
            hit_endpoint("GET", "/index.html", headers=headers, tag="p")
        else:
            start = random.randint(50000, 90000)
            end = start + random.randint(100, 500)
            headers = {"Range": f"bytes={start}-{end}"}
            hit_endpoint("GET", "/index.html", headers=headers, tag="!")
        time.sleep(random.uniform(0.05, 0.3))
    print("\nRange request simulation finished.")


def simulate_malformed_requests(events: int = 15) -> None:
    """Send deliberately malformed URIs to provoke 400-class errors."""
    print(f"\n@@@ Simulating malformed requests ({events} attempts) @@@")
    bad_paths = ["/%", "/%zz", "/%2", "/%AB%GH", "/%%%/../../etc/passwd", "/%AE%AE%AE"]
    for _ in range(events):
        path = random.choice(bad_paths)
        hit_endpoint("GET", path, headers={"X-Malformed": "true"}, tag="!")
        time.sleep(0.2)
    print("\nMalformed request simulation finished.")


if __name__ == "__main__":
    simulate_normal_traffic(duration_minutes=1)
    time.sleep(3)
    simulate_search_spike(duration_seconds=30, rpm=90)
    time.sleep(3)
    simulate_bruteforce(attempts=40)
    time.sleep(3)
    simulate_api_noise(events=60)
    time.sleep(3)
    simulate_conditional_requests(requests_count=25)
    time.sleep(3)
    simulate_range_requests(events=30)
    time.sleep(3)
    simulate_malformed_requests(events=15)
    time.sleep(3)
    simulate_directory_scan(pages_to_scan=60)
