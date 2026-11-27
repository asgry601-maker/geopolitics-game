# -*- coding: utf-8 -*-
"""به‌روزرسانی آفلاین شاخص‌های تکمیلی کشورها از World Bank WDI.
Python 3.8+؛ فقط هنگام اجرای این ابزار اینترنت لازم است. خود بازی آفلاین می‌ماند.
"""
from __future__ import print_function
import json
import os
import sys
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

HERE = os.path.dirname(os.path.abspath(__file__))
PROFILE_PATH = os.path.join(HERE, "..", "phaseA", "data", "country_profiles.json")
START_YEAR = 2020
END_YEAR = 2024
BASE_URL = "https://api.worldbank.org/v2/country/all/indicator/{code}"

INDICATORS = {
    "SP.POP.GROW": ("population_growth_percent", "population_growth_year"),
    "FP.CPI.TOTL.ZG": ("inflation_percent", "inflation_year"),
    "SL.UEM.TOTL.ZS": ("unemployment_percent", "unemployment_year"),
    "NY.GDP.MKTP.KD.ZG": ("gdp_growth_percent", "gdp_growth_year"),
    "NE.EXP.GNFS.CD": ("exports_usd", "exports_year"),
    "NE.IMP.GNFS.CD": ("imports_usd", "imports_year"),
}

def fetch_indicator(code):
    query = urlencode({
        "format": "json",
        "per_page": "20000",
        "date": "%d:%d" % (START_YEAR, END_YEAR),
    })
    url = BASE_URL.format(code=code) + "?" + query
    request = Request(url, headers={"User-Agent": "GeopoliticsGame-DataUpdater/1.0"})
    with urlopen(request, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
        raise RuntimeError("پاسخ نامعتبر از World Bank برای " + code)
    meta = payload[0] or {}
    records = list(payload[1] or [])
    pages = int(meta.get("pages") or 1)
    for page in range(2, pages + 1):
        page_query = urlencode({
            "format": "json",
            "per_page": "20000",
            "date": "%d:%d" % (START_YEAR, END_YEAR),
            "page": str(page),
        })
        req = Request(BASE_URL.format(code=code) + "?" + page_query,
                      headers={"User-Agent": "GeopoliticsGame-DataUpdater/1.0"})
        with urlopen(req, timeout=60) as response:
            page_payload = json.loads(response.read().decode("utf-8"))
        if isinstance(page_payload, list) and len(page_payload) > 1 and page_payload[1]:
            records.extend(page_payload[1])
    latest = {}
    for row in records:
        iso3 = row.get("countryiso3code")
        value = row.get("value")
        year = row.get("date")
        if not iso3 or value is None or not year:
            continue
        try:
            year_num = int(year)
            value_num = float(value)
        except (TypeError, ValueError):
            continue
        old = latest.get(iso3)
        if old is None or year_num > old[0]:
            latest[iso3] = (year_num, value_num)
    return latest

def main():
    if not os.path.isfile(PROFILE_PATH):
        raise RuntimeError("country_profiles.json پیدا نشد: " + PROFILE_PATH)
    with open(PROFILE_PATH, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    countries = payload.get("countries") or {}
    counts = {}
    for code, fields in INDICATORS.items():
        print("دریافت " + code + " ...")
        latest = fetch_indicator(code)
        value_key, year_key = fields
        count = 0
        for iso3, (year, value) in latest.items():
            country = countries.get(iso3)
            if country is None:
                continue
            country[value_key] = round(value, 4)
            country[year_key] = year
            count += 1
        counts[code] = count
        print("  کشور دارای داده: %d" % count)
        time.sleep(0.15)
    for country in countries.values():
        exports = country.get("exports_usd")
        imports = country.get("imports_usd")
        if exports is not None and imports is not None:
            country["trade_balance_usd"] = round(exports - imports, 2)
            country["trade_balance_year"] = min(
                country.get("exports_year") or 0,
                country.get("imports_year") or 0
            ) or None
        else:
            country["trade_balance_usd"] = None
            country["trade_balance_year"] = None
    payload["economic_indicators_period"] = "%d-%d" % (START_YEAR, END_YEAR)
    payload["economic_indicators_source"] = "World Bank World Development Indicators (WDI)"
    payload["economic_indicator_coverage"] = counts
    temp_path = PROFILE_PATH + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temp_path, PROFILE_PATH)
    print("تمام شد؛ پرونده کشورها به‌روزرسانی شد. بازی برای نمایش داده‌ها به اینترنت نیاز ندارد.")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.stderr.write("خطا: %s\n" % exc)
        sys.exit(1)
