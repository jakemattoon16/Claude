"""
SEC Investment Adviser Bulk Data Downloader & Parser
=====================================================
Downloads the SEC IAPD (Investment Adviser Public Disclosure) bulk data
directly from the SEC's official FOIA data page — no scraping required.

Data source:
  https://www.sec.gov/help/foiadocsinvafoiahtm.html

Output:
  sec_investment_advisors.csv  — all registered investment advisers
                                  with full contact information

Requirements:
  pip install requests beautifulsoup4 pandas
"""

import io
import os
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OUTPUT_FILE = "sec_investment_advisors.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SEC-Data-Research/1.0; contact: research@example.com)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Primary bulk data index page
FOIA_INDEX_URL = "https://www.sec.gov/help/foiadocsinvafoiahtm.html"

# Fallback: direct known patterns for the IA extract ZIP
FALLBACK_URLS = [
    "https://www.sec.gov/foia/docs/invafoia.zip",
    "https://www.sec.gov/foia/docs/ia_registration.zip",
]

# IAPD API endpoint (used as second fallback for paginated JSON)
IAPD_API_URL = "https://efts.sec.gov/LATEST/search-index"


# ---------------------------------------------------------------------------
# Step 1 – Find the latest ZIP download link from the FOIA index page
# ---------------------------------------------------------------------------

def find_bulk_zip_url(index_url: str) -> str | None:
    """Scrape the FOIA index page and return the URL of the latest IA ZIP file."""
    print(f"[1] Fetching FOIA index: {index_url}")
    try:
        resp = requests.get(index_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"    WARNING: Could not fetch index page — {exc}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    zip_links = [
        a["href"]
        for a in soup.find_all("a", href=True)
        if a["href"].lower().endswith(".zip") and "ia" in a["href"].lower()
    ]

    if not zip_links:
        print("    WARNING: No ZIP links found on index page.")
        return None

    # Prefer links that look like the IA firm extract
    firm_links = [u for u in zip_links if "firm" in u.lower() or "registration" in u.lower()]
    chosen = firm_links[0] if firm_links else zip_links[0]

    # Make absolute if needed
    if chosen.startswith("http"):
        return chosen
    return "https://www.sec.gov" + ("" if chosen.startswith("/") else "/") + chosen


# ---------------------------------------------------------------------------
# Step 2 – Download a ZIP file and return its bytes
# ---------------------------------------------------------------------------

def download_zip(url: str) -> bytes | None:
    """Download a ZIP from `url` and return the raw bytes."""
    print(f"[2] Downloading: {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=120, stream=True)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        chunks = []
        downloaded = 0
        for chunk in resp.iter_content(chunk_size=1024 * 256):
            chunks.append(chunk)
            downloaded += len(chunk)
            if total:
                pct = downloaded / total * 100
                print(f"\r    Progress: {pct:.1f}% ({downloaded:,} / {total:,} bytes)", end="", flush=True)
        print()  # newline after progress
        return b"".join(chunks)
    except requests.RequestException as exc:
        print(f"    WARNING: Download failed — {exc}")
        return None


# ---------------------------------------------------------------------------
# Step 3 – Inspect the ZIP and load relevant CSVs/pipe-delimited files
# ---------------------------------------------------------------------------

def load_dataframes_from_zip(raw_bytes: bytes) -> dict[str, pd.DataFrame]:
    """
    Open the ZIP in memory and return a dict of {filename: DataFrame}
    for every text/CSV file inside.
    """
    dfs = {}
    with zipfile.ZipFile(io.BytesIO(raw_bytes)) as zf:
        names = zf.namelist()
        print(f"    Files in ZIP: {names}")
        for name in names:
            lower = name.lower()
            if not any(lower.endswith(ext) for ext in (".csv", ".txt", ".dat", ".psv")):
                continue
            print(f"    Loading: {name}")
            with zf.open(name) as f:
                raw = f.read()
                # Detect delimiter
                sample = raw[:4096].decode("utf-8", errors="replace")
                if "|" in sample:
                    sep = "|"
                elif "\t" in sample:
                    sep = "\t"
                else:
                    sep = ","
                try:
                    df = pd.read_csv(
                        io.BytesIO(raw),
                        sep=sep,
                        encoding="utf-8",
                        encoding_errors="replace",
                        low_memory=False,
                        dtype=str,
                    )
                    dfs[name] = df
                    print(f"      Rows: {len(df):,}  Columns: {list(df.columns)}")
                except Exception as exc:
                    print(f"      ERROR reading {name}: {exc}")
    return dfs


# ---------------------------------------------------------------------------
# Step 4 – Normalise column names and extract contact fields
# ---------------------------------------------------------------------------

COLUMN_MAP = {
    # Firm identity
    "org_name":          ["org_name", "firm_name", "name", "adviser_name", "companyname"],
    "crd_number":        ["crd_number", "crd_num", "crd#", "sec_number", "firm_crd"],
    "sec_number":        ["sec_number", "sec_num", "sec#", "secnumber"],
    # Address
    "address_line1":     ["address1", "addr1", "address_line1", "street1", "mailingaddress1"],
    "address_line2":     ["address2", "addr2", "address_line2", "street2", "mailingaddress2"],
    "city":              ["city", "mailing_city", "mailingcity"],
    "state":             ["state", "statecode", "mailing_state", "mailingstate"],
    "zip":               ["zip", "zipcode", "postal_code", "mailingzip"],
    "country":           ["country", "countrycode", "mailingcountry"],
    # Contact
    "phone":             ["phone", "phone_number", "telephone", "bus_phone", "phonenumber"],
    "fax":               ["fax", "fax_number", "facsimile"],
    "website":           ["website", "web_address", "url", "website_address"],
    "email":             ["email", "email_address", "contact_email"],
    # Registration status
    "registration_status": ["reg_stat", "registration_status", "status", "registrationstatus"],
    "registration_date":   ["reg_date", "registration_date", "effectivedate", "registrationdate"],
    # Business type
    "adviser_type":      ["adviser_type", "type_of_adviser", "business_type"],
    # AUM
    "aum":               ["regulatory_aum", "assets_under_mgmt", "aum", "totalassets"],
    "num_employees":     ["num_employees", "employees", "total_employees"],
}


def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename raw column names to a standard set wherever possible."""
    col_lower = {c.lower().replace(" ", "_"): c for c in df.columns}
    rename = {}
    for standard, variants in COLUMN_MAP.items():
        if standard in col_lower:
            rename[col_lower[standard]] = standard
            continue
        for variant in variants:
            key = variant.lower().replace(" ", "_")
            if key in col_lower:
                rename[col_lower[key]] = standard
                break
    return df.rename(columns=rename)


def filter_investment_advisers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only rows that are investment advisers.
    The SEC bulk data may contain broker-dealers and other registrant types;
    filter them out where the data allows.
    """
    # If there's an adviser_type or registration_status column, filter on it
    for col in ["adviser_type", "registration_status", "org_type", "type"]:
        if col in df.columns:
            mask = df[col].str.contains(
                r"invest|adviser|advisor|RIA|IA",
                case=False,
                na=False,
                regex=True,
            )
            if mask.sum() > 0:
                print(f"    Filtered to investment advisers via column '{col}': {mask.sum():,} rows")
                return df[mask].copy()

    # If no type column found, return everything (the IA extract is IA-only by default)
    print("    No type column found — returning all rows (file is likely IA-only).")
    return df.copy()


# ---------------------------------------------------------------------------
# Step 5 – Combine all loaded dataframes into one output CSV
# ---------------------------------------------------------------------------

def build_output(dfs: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Merge / pick the most useful dataframe and standardise it."""
    if not dfs:
        return pd.DataFrame()

    # Prefer a file whose name contains "firm" or "registration"
    preferred = None
    for name, df in dfs.items():
        lower = name.lower()
        if "firm" in lower or "registration" in lower or "adviser" in lower:
            preferred = df
            print(f"    Using file: {name}")
            break
    if preferred is None:
        preferred = next(iter(dfs.values()))

    df = normalise_columns(preferred)
    df = filter_investment_advisers(df)

    # Select only standard contact columns that exist
    desired = [
        "org_name", "crd_number", "sec_number",
        "address_line1", "address_line2", "city", "state", "zip", "country",
        "phone", "fax", "email", "website",
        "registration_status", "registration_date",
        "adviser_type", "aum", "num_employees",
    ]
    present = [c for c in desired if c in df.columns]
    # Also include any remaining columns not in the standard set
    extra = [c for c in df.columns if c not in desired]
    final_cols = present + extra
    return df[final_cols]


# ---------------------------------------------------------------------------
# Fallback: IAPD paginated API
# ---------------------------------------------------------------------------

def fetch_via_iapd_api(max_pages: int = 200) -> pd.DataFrame:
    """
    Pull adviser data from the IAPD search API in pages.
    This is a fallback if the bulk ZIP is unavailable.
    """
    print("\n[FALLBACK] Using IAPD search API …")
    records = []
    page_size = 100

    for page in range(max_pages):
        start = page * page_size
        params = {
            "forms": "ADV",
            "dateRange": "custom",
            "hits.hits._source": "true",
            "hits.hits.total.value": "true",
            "start": start,
            "count": page_size,
        }
        try:
            resp = requests.get(IAPD_API_URL, params=params, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            print(f"    API error on page {page}: {exc}")
            break

        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            break

        for hit in hits:
            src = hit.get("_source", {})
            records.append({
                "org_name":            src.get("display_names", [{}])[0].get("name", "") if src.get("display_names") else "",
                "crd_number":          src.get("entity_id", ""),
                "city":                src.get("city", ""),
                "state":               src.get("state_of_inc", ""),
                "phone":               src.get("phone", ""),
                "website":             src.get("websites", [""])[0] if src.get("websites") else "",
                "registration_status": src.get("registration_status", ""),
                "adviser_type":        "Investment Adviser",
            })

        total = data.get("hits", {}).get("total", {}).get("value", 0)
        fetched = min(start + page_size, total)
        print(f"    Fetched {fetched:,} / {total:,} records", end="\r", flush=True)

        if start + page_size >= total:
            break

    print()
    return pd.DataFrame(records)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("SEC Investment Adviser Bulk Data Downloader")
    print("=" * 60)

    zip_bytes = None

    # -- Attempt 1: scrape FOIA index page for ZIP link
    zip_url = find_bulk_zip_url(FOIA_INDEX_URL)
    if zip_url:
        zip_bytes = download_zip(zip_url)

    # -- Attempt 2: try known fallback URLs
    if not zip_bytes:
        for url in FALLBACK_URLS:
            zip_bytes = download_zip(url)
            if zip_bytes:
                break

    if zip_bytes:
        print("[3] Parsing ZIP contents …")
        dfs = load_dataframes_from_zip(zip_bytes)
        result = build_output(dfs)
    else:
        # -- Attempt 3: IAPD API
        result = fetch_via_iapd_api()

    if result.empty:
        print("\nERROR: Could not retrieve any data. Please check your internet connection.")
        sys.exit(1)

    print(f"\n[4] Writing {len(result):,} adviser records to '{OUTPUT_FILE}' …")
    result.to_csv(OUTPUT_FILE, index=False)
    print(f"    Done.  File saved: {Path(OUTPUT_FILE).resolve()}")
    print(f"\nColumns in output: {list(result.columns)}")
    print(f"\nFirst 5 records preview:")
    print(result.head().to_string())


if __name__ == "__main__":
    main()
