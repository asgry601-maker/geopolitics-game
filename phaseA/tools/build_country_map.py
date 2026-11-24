# -*- coding: utf-8 -*-
"""ساخت data/country_map.json — ترجمان نام فارسی/انگلیسی/ISO + مرکز جغرافیایی.
   فقط از data/countries.geojson می‌خواند؛ هیچ فایل پروژه اصلی را تغییر نمی‌دهد."""
import json, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # phaseA/
GJ = os.path.join(HERE, "data", "countries.geojson")
OUT = os.path.join(HERE, "data", "country_map.json")

# نام موتور (فارسی) -> (ISO3, نام ADMIN در Natural Earth)
M = {
 "آمریکا": ("USA", "United States of America"), "کانادا": ("CAN", "Canada"),
 "مکزیک": ("MEX", "Mexico"), "ایران": ("IRN", "Iran"), "عراق": ("IRQ", "Iraq"),
 "سوریه": ("SYR", "Syria"), "لبنان": ("LBN", "Lebanon"), "اردن": ("JOR", "Jordan"),
 "اسرائیل": ("ISR", "Israel"), "فلسطین": ("PSE", "Palestine"), "عربستان": ("SAU", "Saudi Arabia"),
 "امارات": ("ARE", "United Arab Emirates"), "قطر": ("QAT", "Qatar"), "کویت": ("KWT", "Kuwait"),
 "بحرین": ("BHR", "Bahrain"), "عمان": ("OMN", "Oman"), "یمن": ("YEM", "Yemen"),
 "ترکیه": ("TUR", "Turkey"), "مصر": ("EGY", "Egypt"), "لیبی": ("LBY", "Libya"),
 "تونس": ("TUN", "Tunisia"), "الجزایر": ("DZA", "Algeria"), "مراکش": ("MAR", "Morocco"),
 "روسیه": ("RUS", "Russia"), "آلمان": ("DEU", "Germany"), "فرانسه": ("FRA", "France"),
 "بریتانیا": ("GBR", "United Kingdom"), "ایتالیا": ("ITA", "Italy"), "اسپانیا": ("ESP", "Spain"),
 "پرتغال": ("PRT", "Portugal"), "هلند": ("NLD", "Netherlands"), "بلژیک": ("BEL", "Belgium"),
 "سوئیس": ("CHE", "Switzerland"), "اتریش": ("AUT", "Austria"), "سوئد": ("SWE", "Sweden"),
 "نروژ": ("NOR", "Norway"), "دانمارک": ("DNK", "Denmark"), "فنلاند": ("FIN", "Finland"),
 "ایسلند": ("ISL", "Iceland"), "ایرلند": ("IRL", "Ireland"), "لهستان": ("POL", "Poland"),
 "چک": ("CZE", "Czechia"), "اسلواکی": ("SVK", "Slovakia"), "مجارستان": ("HUN", "Hungary"),
 "رومانی": ("ROU", "Romania"), "بلغارستان": ("BGR", "Bulgaria"), "یونان": ("GRC", "Greece"),
 "صربستان": ("SRB", "Republic of Serbia"), "کرواسی": ("HRV", "Croatia"), "بوسنی": ("BIH", "Bosnia and Herz."),
 "آلبانی": ("ALB", "Albania"), "مقدونیه شمالی": ("MKD", "North Macedonia"),
 "اسلوونی": ("SVN", "Slovenia"), "مونته‌نگرو": ("MNE", "Montenegro"), "اوکراین": ("UKR", "Ukraine"),
 "بلاروس": ("BLR", "Belarus"), "مولداوی": ("MDA", "Moldova"), "لتونی": ("LVA", "Latvia"),
 "لیتوانی": ("LTU", "Lithuania"), "استونی": ("EST", "Estonia"), "لوکزامبورگ": ("LUX", "Luxembourg"),
 "قبرس": ("CYP", "Cyprus"), "مالت": ("MLT", "Malta"), "چین": ("CHN", "China"),
 "ژاپن": ("JPN", "Japan"), "کره جنوبی": ("KOR", "South Korea"), "کره شمالی": ("PRK", "North Korea"),
 "تایوان": ("TWN", "Taiwan"), "مغولستان": ("MNG", "Mongolia"), "هند": ("IND", "India"),
 "پاکستان": ("PAK", "Pakistan"), "بنگلادش": ("BGD", "Bangladesh"), "سری‌لانکا": ("LKA", "Sri Lanka"),
 "نپال": ("NPL", "Nepal"), "بوتان": ("BTN", "Bhutan"), "مالدیو": ("MDV", "Maldives"),
 "افغانستان": ("AFG", "Afghanistan"), "اندونزی": ("IDN", "Indonesia"), "مالزی": ("MYS", "Malaysia"),
 "سنگاپور": ("SGP", "Singapore"), "تایلند": ("THA", "Thailand"), "ویتنام": ("VNM", "Vietnam"),
 "فیلیپین": ("PHL", "Philippines"), "میانمار": ("MMR", "Myanmar"), "کامبوج": ("KHM", "Cambodia"),
 "لائوس": ("LAO", "Laos"), "برونئی": ("BRN", "Brunei"), "تیمور شرقی": ("TLS", "Timor-Leste"),
 "نیجریه": ("NGA", "Nigeria"), "آفریقای جنوبی": ("ZAF", "South Africa"), "اتیوپی": ("ETH", "Ethiopia"),
 "کنیا": ("KEN", "Kenya"), "غانا": ("GHA", "Ghana"), "سنگال": ("SEN", "Senegal"),
 "ساحل عاج": ("CIV", "Ivory Coast"), "کامرون": ("CMR", "Cameroon"), "اوگاندا": ("UGA", "Uganda"),
 "تانزانیا": ("TZA", "United Republic of Tanzania"), "رواندا": ("RWA", "Rwanda"), "زیمبابوه": ("ZWE", "Zimbabwe"),
 "زامبیا": ("ZMB", "Zambia"), "موزامبیک": ("MOZ", "Mozambique"), "آنگولا": ("AGO", "Angola"),
 "نامیبیا": ("NAM", "Namibia"), "بوتسوانا": ("BWA", "Botswana"), "سودان": ("SDN", "Sudan"),
 "سودان جنوبی": ("SSD", "South Sudan"), "چاد": ("TCD", "Chad"), "نیجر": ("NER", "Niger"),
 "مالی": ("MLI", "Mali"), "موریتانی": ("MRT", "Mauritania"), "بورکینافاسو": ("BFA", "Burkina Faso"),
 "گینه": ("GIN", "Guinea"), "سیرالئون": ("SLE", "Sierra Leone"), "لیبریا": ("LBR", "Liberia"),
 "توگو": ("TGO", "Togo"), "بنین": ("BEN", "Benin"), "گابن": ("GAB", "Gabon"),
 "کنگو": ("COG", "Republic of the Congo"), "کنگو دموکراتیک": ("COD", "Dem. Rep. Congo"),
 "آفریقای مرکزی": ("CAF", "Central African Republic"), "اریتره": ("ERI", "Eritrea"),
 "جیبوتی": ("DJI", "Djibouti"), "سومالی": ("SOM", "Somalia"), "ماداگاسکار": ("MDG", "Madagascar"),
 "موریس": ("MUS", "Mauritius"), "لسوتو": ("LSO", "Lesotho"), "اسواتینی": ("SWZ", "eSwatini"),
 "گامبیا": ("GMB", "Gambia"), "گینه بیسائو": ("GNB", "Guinea-Bissau"),
 "گینه استوایی": ("GNQ", "Equatorial Guinea"), "کیپ‌ورد": ("CPV", "Cape Verde"),
 "برزیل": ("BRA", "Brazil"), "آرژانتین": ("ARG", "Argentina"), "شیلی": ("CHL", "Chile"),
 "کلمبیا": ("COL", "Colombia"), "پرو": ("PER", "Peru"), "ونزوئلا": ("VEN", "Venezuela"),
 "اکوادور": ("ECU", "Ecuador"), "بولیوی": ("BOL", "Bolivia"), "پاراگوئه": ("PRY", "Paraguay"),
 "اوروگوئه": ("URY", "Uruguay"), "گویان": ("GUY", "Guyana"), "سورینام": ("SUR", "Suriname"),
 "کوبا": ("CUB", "Cuba"), "هائیتی": ("HTI", "Haiti"), "دومینیکان": ("DOM", "Dominican Republic"),
 "جامائیکا": ("JAM", "Jamaica"), "ترینیداد و توباگو": ("TTO", "Trinidad and Tobago"),
 "کاستاریکا": ("CRI", "Costa Rica"), "پاناما": ("PAN", "Panama"), "گواتمالا": ("GTM", "Guatemala"),
 "هندوراس": ("HND", "Honduras"), "السالوادور": ("SLV", "El Salvador"),
 "نیکاراگوئه": ("NIC", "Nicaragua"), "بلیز": ("BLZ", "Belize"), "باهاماس": ("BHS", "Bahamas"),
 "باربادوس": ("BRB", "Barbados"), "استرالیا": ("AUS", "Australia"), "نیوزیلند": ("NZL", "New Zealand"),
 "پاپوآ گینه نو": ("PNG", "Papua New Guinea"), "فیجی": ("FJI", "Fiji"), "ساموآ": ("WSM", "Samoa"),
 "تونگا": ("TON", "Tonga"), "وانواتو": ("VUT", "Vanuatu"), "جزایر سلیمان": ("SLB", "Solomon Islands"),
 "قزاقستان": ("KAZ", "Kazakhstan"), "ازبکستان": ("UZB", "Uzbekistan"),
 "ترکمنستان": ("TKM", "Turkmenistan"), "تاجیکستان": ("TJK", "Tajikistan"),
 "قرقیزستان": ("KGZ", "Kyrgyzstan"), "آذربایجان": ("AZE", "Azerbaijan"),
 "ارمنستان": ("ARM", "Armenia"), "گرجستان": ("GEO", "Georgia"),
}
# نام‌های جایگزین در Natural Earth (نسخه‌های 110m قدیمی‌تر)
ALIAS = {
 "United States of America": ["United States"],
 "Czechia": ["Czech Rep.", "Czech Republic"],
 "North Macedonia": ["Macedonia"],
 "Dem. Rep. Congo": ["Democratic Republic of the Congo"],
 "eSwatini": ["Swaziland"],
 "Cape Verde": ["Cabo Verde"],
 "Timor-Leste": ["East Timor"],
 "Turkey": ["Türkiye"],
 "Bosnia and Herz.": ["Bosnia and Herzegovina"],
 "Bahamas": ["The Bahamas"],
}


MANUAL_LL = {
 "بحرین": (26.03, 50.55), "مالت": (35.94, 14.38), "مالدیو": (3.20, 73.22),
 "سنگاپور": (1.35, 103.82), "موریس": (-20.28, 57.57), "کیپ‌ورد": (15.12, -23.61),
 "باهاماس": (24.72, -77.75), "باربادوس": (13.19, -59.54), "ساموآ": (-13.75, -172.10),
 "تونگا": (-21.18, -175.20),
}

def centroid(feat):
    """مرکز بزرگ‌ترین رینگ با شولیس (سطح منحنی ساده) — برای برچسب کافی است."""
    geom = feat["geometry"]
    polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    best, barea = None, -1
    for poly in polys:
        ring = max(poly, key=len)
        if len(ring) < 4:
            continue
        sx = sy = sa = 0.0
        for i in range(len(ring) - 1):
            x1, y1 = ring[i]; x2, y2 = ring[i + 1]
            cr = x1 * y2 - x2 * y1
            sx += (x1 + x2) * cr; sy += (y1 + y2) * cr; sa += cr
        if abs(sa) < 1e-12:
            continue
        cx, cy = sx / (3 * sa), sy / (3 * sa)
        if abs(sa) > barea:
            barea, best = abs(sa), (cy, cx)
    return best  # (lat, lon)

def main():
    gj = json.load(open(GJ, encoding="utf-8"))
    by_en = {}
    for f in gj["features"]:
        by_en.setdefault(f["properties"]["ADMIN"], f)  # اولین = اصلی
    out, missing_en, no_poly = {}, [], []
    for fa, (iso3, en) in M.items():
        cand = None
        for name in [en] + ALIAS.get(en, []):
            if name in by_en:
                cand = name
                break
        if cand:
            c = centroid(by_en[cand]) or (None, None)
            out[fa] = {"en": en, "iso3": iso3, "ne": cand, "lat": round(c[0], 2), "lon": round(c[1], 2)}
        else:
            missing_en.append((fa, en))
            ll = MANUAL_LL.get(fa, (None, None))
            out[fa] = {"en": en, "iso3": iso3, "ne": None,
                       "lat": None if ll[0] is None else round(ll[0], 2),
                       "lon": None if ll[1] is None else round(ll[1], 2)}
    # إن Админист در NE که به هیچ کشور بازی وصل نشد (برای گزارش — معمولاً جزیره‌های خرد)
    used_ne = {v["ne"] for v in out.values() if v["ne"]}
    orphan = sorted(set(by_en) - used_ne)
    points = [fa for fa, v in out.items() if v["ne"] is None]
    json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("mapped:", sum(1 for v in out.values() if v["ne"]), "/", len(out))
    print("MISSING EN (no polygon -> label-point only):")
    for fa, en in missing_en:
        print("   ", fa, "->", en)
    print("NE orphans (no game country):", orphan)
    print("wrote", OUT)

if __name__ == "__main__":
    main()
