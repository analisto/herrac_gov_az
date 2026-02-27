"""
Scraper for herrac.gov.az auction data.
Fetches all ONGOING auctions (paginated) and saves to data/data.csv.

Usage:
    pip install requests pandas
    python scripts/scraper.py

Response structure:
    {"data": {"content": [...], "totalPages": N, "totalElements": N}, "key": "SUCCESS"}
"""

import sys
import time
from pathlib import Path

import requests
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_URL  = "https://herrac.gov.az/gw/os/v1/auctions"
CLIENT_ID = "222b1b03-d079-42af-8f0f-1a2174eacfc5"

HEADERS = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,ru;q=0.7,az;q=0.6",
    "content-type": "application/json",
    "cookie": f"clientId={CLIENT_ID}",
    "dnt": "1",
    "host": "herrac.gov.az",
    "origin": "https://herrac.gov.az",
    "referer": "https://herrac.gov.az/?page=2",
    "sec-ch-ua": '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/145.0.0.0 Safari/537.36"
    ),
    "x-client-id": CLIENT_ID,
}

PAGE_SIZE     = 24
DELAY_SECONDS = 0.4
OUTPUT_PATH   = Path("data/data.csv")

# ---------------------------------------------------------------------------


def fetch_page(page: int) -> tuple[list[dict], int]:
    """Return (items, total_pages) for the given page number."""
    params = {
        "size": PAGE_SIZE,
        "userFilter": "false",
        "status": "ONGOING",
        "includeNotStarted": "true",
        "page": page,
    }
    resp = requests.post(BASE_URL, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()

    body = resp.json()

    # Unwrap {"data": {"content": [...], "totalPages": N}}
    inner      = body.get("data", {}) if isinstance(body, dict) else {}
    items      = inner.get("content", []) if isinstance(inner, dict) else []
    total_pages = int(inner.get("totalPages", 1)) if isinstance(inner, dict) else 1

    return items, total_pages


def flatten_auction(item: dict) -> dict:
    """Flatten one auction record into a single-level dict for CSV export."""
    row = {}

    # Top-level scalar fields
    scalar_keys = [
        "id", "auctionOrderId", "lotName", "urlPath", "categoryId",
        "categoryName", "lotDataHighlight", "roundNumber", "startAt",
        "validUntil", "initialPrice", "lastBidPrice", "attendantsCount",
        "isFavorite", "status", "attendanceStatus",
    ]
    for k in scalar_keys:
        row[k] = item.get(k)

    # lotData: list of {paramName, valueText} → expand into named columns
    for entry in item.get("lotData", []):
        param = entry.get("paramName", "")
        value = entry.get("valueText", "")
        if param:
            row[f"lotData.{param}"] = value

    # Image URLs joined
    row["lotImageUrls"] = "|".join(item.get("lotImageUrls", []))

    return row


def scrape_all() -> list[dict]:
    records: list[dict] = []
    page = 1
    total_pages = None

    while True:
        print(f"  Fetching page {page}" + (f"/{total_pages}" if total_pages else "") + " ...", flush=True)
        try:
            items, total_pages = fetch_page(page)
        except requests.HTTPError as exc:
            print(f"  HTTP error on page {page}: {exc}")
            break
        except Exception as exc:
            print(f"  Unexpected error on page {page}: {exc}")
            break

        if not items:
            print("  No items returned – stopping.")
            break

        records.extend(flatten_auction(item) for item in items)
        print(f"    -> {len(items)} items fetched (total so far: {len(records)})")

        if page >= total_pages:
            break

        page += 1
        time.sleep(DELAY_SECONDS)

    return records


def save_csv(records: list[dict]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not records:
        print("\nNo records – writing empty CSV.")
        OUTPUT_PATH.write_text("", encoding="utf-8-sig")
        return

    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    print(f"\nSaved {len(df)} rows x {len(df.columns)} columns -> {OUTPUT_PATH}")
    print(f"Columns: {list(df.columns)}")


def main():
    print("herrac.gov.az auction scraper")
    print(f"  URL    : {BASE_URL}")
    print(f"  Status : ONGOING (includeNotStarted=true)")
    print(f"  Output : {OUTPUT_PATH}\n")

    records = scrape_all()
    save_csv(records)


if __name__ == "__main__":
    main()
