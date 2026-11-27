# -*- coding: utf-8 -*-
"""Refresh annual country indicators from the World Bank Indicators API.

Run from the repository root:
    python phaseA/tools/update_world_bank_indicators.py

Uses only the Python standard library and is compatible with Python 3.8.
The game itself reads the bundled JSON and does not need an internet connection.
"""
from __future__ import print_function

import json
import os
import sys
import time
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "country_profiles.json")
API_ROOT = "https://api.worldbank.org/v2/country/all/indicator/"

INDICATORS = {
    "inflation_percent": "FP.CPI.TOTL.ZG",
    "unemployment_percent": "SL.UEM.TOTL.ZS",
    "gdp_growth_percent": "NY.GDP.MKTP.KD.ZG",
    "population_growth_percent": "SP.POP.GROW",
    "exports_gdp_percent": "NE.EXP.GNFS.ZS",
    "imports_gdp_percent": "NE.IMP.GNFS.ZS",
}

def fetch_json(url):
    request = Request(url, headers={"User-Agent": "GeopoliticsGame-country-data/1.0"})
    last_error = None
    for attempt in range(3):
        try:
            with urlopen(request, timeout=45) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(2 * (attempt + 1))
    raise RuntimeError("World Bank API request failed: {0}".format(last_error))

def fetch_indicator(code):
    params = urlencode({"format": "json", "mrnev": "1", "per_page": "20000"})
    url = API_ROOT + code + "?" + params
    payload = fetch_json(url)
    if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[0], dict):
        raise RuntimeError("Unexpected World Bank response for {0}".format(code))

    meta = payload[0]
    rows = payload[1] or []
    pages = int(meta.get("pages") or 1)
    for page in range(2, pages + 1):
        page_url = url + "&page=" + str(page)
        page_payload = fetch_json(page_url)
        if isinstance(page_payload, list) and len(page_payload) > 1 and page_payload[1]:
            rows.extend(page_payload[1])

    result = {}
    for row in rows:
        country = row.get("country") or {}
        iso3 = country.get("id")
        value = row.get("value")
        year = row.get("date")
        if not iso3 or value is None or not year:
            continue
        try:
            result[iso3] = {"value": round(float(value), 4), "year": int(year), "code": code}
        except (TypeError, ValueError):
            continue
    return result

def main():
    if not os.path.isfile(DATA_PATH):
        raise RuntimeError("Country profile file not found: " + DATA_PATH)

    with open(DATA_PATH, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    countries = payload.get("countries") or {}
    if not countries:
        raise RuntimeError("No country profiles were found.")

    collected = {}
    for key, code in INDICATORS.items():
        print("Downloading {0} ({1})...".format(key, code))
        collected[key] = fetch_indicator(code)
        print("  values received: {0}".format(len(collected[key])))

    for iso3, profile in countries.items():
        entries = {}
        for key, code in INDICATORS.items():
            entries[key] = collected[key].get(iso3, {
                "value": None, "year": None, "code": code
            })
        profile["indicators"] = entries

    payload["indicator_source"] = "World Bank World Development Indicators (Indicators API v2)"
    payload["indicator_update_utc"] = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    payload["indicator_notes"] = (
        "Each indicator stores its own latest non-null observation and year. "
        "Years can differ by country and indicator. Null means no value was returned; "
        "no values are estimated or fabricated by this updater."
    )

    backup = DATA_PATH + ".bak"
    with open(backup, "w", encoding="utf-8") as handle:
        json.dump(json.load(open(DATA_PATH, "r", encoding="utf-8")), handle,
                  ensure_ascii=False, indent=2)
        handle.write("\n")

    temp_path = DATA_PATH + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temp_path, DATA_PATH)

    print("")
    print("Updated {0} country profiles.".format(len(countries)))
    print("Backup: {0}".format(backup))
    print("Snapshot UTC: {0}".format(payload["indicator_update_utc"]))

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write("ERROR: {0}\n".format(exc))
        sys.exit(1)
