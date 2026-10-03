\
import time
from pathlib import Path

import pandas as pd
import requests

from config import (
    DATA_RAW, WAW_COLLECTION_CSV, WAW_TREATMENT_CSV,
    WORLD_BANK_API, WDI_INDICATORS
)
from common import checkpoint, save_json, set_seed

set_seed()

HEADERS = {"User-Agent": "PAPER19-reproducibility/1.0"}

def download(url, path, timeout=120):
    path = Path(path)
    if path.exists() and path.stat().st_size > 100:
        print(f"[CACHE] {path.name}")
        return path
    print(f"[GET] {url}")
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    path.write_bytes(r.content)
    print(f"[SAVED] {path} ({path.stat().st_size:,} bytes)")
    return path

def fetch_wdi(code, out_path):
    if out_path.exists() and out_path.stat().st_size > 100:
        print(f"[CACHE] {out_path.name}")
        return
    url = f"{WORLD_BANK_API}/country/all/indicator/{code}"
    params = {"format": "json", "date": "2000:2025", "per_page": 10000}
    print(f"[API] WDI {code}")
    r = requests.get(url, params=params, headers=HEADERS, timeout=120)
    r.raise_for_status()
    payload = r.json()
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    recs = []
    for x in rows:
        if not isinstance(x, dict):
            continue
        value = x.get("value")
        iso3 = x.get("countryiso3code")
        year = x.get("date")
        if iso3 and year and value is not None:
            recs.append({"iso3": iso3, "year": int(year), "value": value})
    pd.DataFrame(recs).to_csv(out_path, index=False)
    time.sleep(0.3)

def fetch_country_metadata():
    out = DATA_RAW / "world_bank_country_metadata.csv"
    if out.exists() and out.stat().st_size > 100:
        print(f"[CACHE] {out.name}")
        return out
    url = f"{WORLD_BANK_API}/country"
    params = {"format": "json", "per_page": 400}
    r = requests.get(url, params=params, headers=HEADERS, timeout=120)
    r.raise_for_status()
    payload = r.json()
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []
    recs = []
    for x in rows:
        if not isinstance(x, dict):
            continue
        recs.append({
            "iso3": x.get("id"),
            "country_wb": x.get("name"),
            "income_group": (x.get("incomeLevel") or {}).get("value"),
            "wb_region": (x.get("region") or {}).get("value"),
        })
    pd.DataFrame(recs).to_csv(out, index=False)
    return out

def main():
    download(WAW_COLLECTION_CSV, DATA_RAW / "WM_COL_COV.csv")
    download(WAW_TREATMENT_CSV, DATA_RAW / "WM_MSW_TREAT.csv")
    fetch_country_metadata()
    for name, code in WDI_INDICATORS.items():
        fetch_wdi(code, DATA_RAW / f"WDI_{name}.csv")
    save_json({
        "waw_collection": WAW_COLLECTION_CSV,
        "waw_treatment": WAW_TREATMENT_CSV,
        "wdi": WDI_INDICATORS,
    }, DATA_RAW / "source_manifest.json")
    checkpoint("01_fetch_data", {"status": "downloaded_and_cached"})
    print("PHASE 01 COMPLETE")

if __name__ == "__main__":
    main()
