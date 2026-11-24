#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B1 — ساخت داده استان‌های جهان از geoBoundaries ADM1 (CC-BY 4.0).
توسعه‌دهنده-سمت: جزئی از بازی/ZIP نیست (فقط ابزار ساخت داده).
Usage:
  python3 build_provinces.py --budget 240          # پردازش sequential تا سقف ثانیه (resumable)
  python3 build_provinces.py --iso IRN --iso BHR   # کشورهای مشخص
  python3 build_provinces.py --index               # بازسازی index.json
  python3 build_provinces.py --report              # گزارش اعتبارسنجی/پوشش
"""
import sys, os, json, time, math, argparse
import urllib.request
from urllib.error import HTTPError, URLError

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROV = os.path.join(ROOT, "phaseA", "data", "provinces")
CACHE_META = "/tmp/gb_meta"
CACHE_RAW = "/tmp/gb_raw"
PROGRESS = "/tmp/gb_progress.json"
CAP = "/tmp/gb_nodata.json"
API = "https://www.geoboundaries.org/api/current/gbOpen/{i}/ADM1/"
UA = {"User-Agent": "geopolitics-game-b1/1.0 (data build)"}
TOL = 0.02          # درجه؛ ساده‌سازی نهایی DP
CAP_V = 5000        # سقف رأس در هر کشور؛ بالاتر → tolerance مضاعف
KEEP_TOP_ISLES = 4  # حفظ تا ۴ جزیرهٔ بزرگ هر استان مستقل از آستانهٔ حذف
NOISE_AREA = 1e-8   # مساحت زیر این (درجه²) = نویز نقشه‌برداری؛ همیشه حذف
SIMPLE_STATS = {"noise": 0, "small_dropped": 0}  # آمار حذفیاتِ آخرین استان
TINY_AREA = 2e-5    # درجه مربع؛ حذف جزیره‌های ریزتر از حد (بازچین‌نشدنی در Zoom بازی)
# نام فارسی رسمی استان‌های ایران — منبع: نام‌های رسمی کشور (تقسیمات کشوری)
FA_IRN_REAL = {
    "alborz": "البرز", "ardabil": "اردبیل", "azerbayjan-e east": "آذربایجان شرقی",
    "azerbayjan-e gharbi": "آذربایجان غربی", "bushehr": "بوشهر",
    "chaharmahal and bakhtiari": "چهارمحال و بختیاری", "fars": "فارس",
    "gilan": "گیلان", "golestan": "گلستان", "hamadan": "همدان",
    "hormozgan": "هرمزگان", "ilam": "ایلام", "isfahan": "اصفهان",
    "kerman": "کرمان", "kermanshah": "کرمانشاه", "khorasan-e junoubi": "خراسان جنوبی",
    "khorasan-e raqavi": "خراسان رضوی", "khorasan-e razavi": "خراسان رضوی",
    "razavi khorasan": "خراسان رضوی", "north khorasan": "خراسان شمالی",
    "south khorasan": "خراسان جنوبی", "khuzestan": "خوزستان",
    "west azerbaijan": "آذربایجان غربی", "east azerbaijan": "آذربایجان شرقی",
    "kohgiluyeh and boyer-ahmad": "کهگیلویه و بویراحمد",
    "kohgiluyeh and buyer ahmad": "کهگیلویه و بویراحمد",
    "sistan and baluchestan": "سیستان و بلوچستان", "sistan and balouchestan": "سیستان و بلوچستان",
    "kurdistan": "کردستان", "lorestan": "لرستان", "markazi": "مرکزی",
    "mazandaran": "مازندران", "qazvin": "قزوین", "qom": "قم",
    "semnan": "سمنان", "tehran": "تهران",
    "yazd": "یزد", "zanjan": "زنجان",
}

def jload(p):
    with open(p, "r", encoding="utf-8") as f: return json.load(f)

def jsave(p, o):
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, p)

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def fetch_json_cached(url, cache_path):
    if os.path.exists(cache_path):
        try: return jload(cache_path), True
        except Exception: pass
    data = fetch(url)
    obj = json.loads(data.decode("utf-8", "strict"))
    jsave(cache_path, obj)
    return obj, False

# ---------- ساده‌سازی (Douglas-Peucker تکراری، بدون recursion) ----------
def dp_ring(pts, tol):
    n = len(pts)
    if n <= 4: return list(pts)
    keep = [False] * n
    keep[0] = keep[-1] = True
    stack = [(0, n - 1)]
    def d(p, a, b):
        ax, ay = a; bx, by = b; px, py = p
        dx, dy = bx - ax, by - ay
        L = math.hypot(dx, dy)
        if L == 0: return math.hypot(px - ax, py - ay)
        return abs(dx * (ay - py) - (ax - px) * dy) / L
    while stack:
        i, j = stack.pop()
        if j <= i + 1: continue
        best, bi = -1.0, -1
        for k in range(i + 1, j):
            dd = d(pts[k], pts[i], pts[j])
            if dd > best: best, bi = dd, k
        if best > tol:
            keep[bi] = True
            stack.append((i, bi)); stack.append((bi, j))
    out = [pts[i] for i in range(n) if keep[i]]
    if out and out[0] != out[-1]:
        out = out + [out[0]]   # حلقهٔ خروجی همیشه بسته (GeoJSON استاندارد)
    if len(out) < 4:
        if n >= 7:
            # DP بیش از حد فرورفته — حلقهٔ بستهٔ حداقلی با دورترین نقطه از وتر
            bi, bd = 1, -1.0
            for k in range(1, n - 1):
                dd = d(pts[k], pts[0], pts[n - 1])
                if dd > bd: bd, bi = dd, k
            return [pts[0], pts[bi], pts[n - 1], pts[0]]
        return list(pts)       # رینگ ریز واقعی: بدون ساده‌سازی (بسته از ورودی)
    return out

def ring_area(ring):
    if len(ring) < 3: return 0.0
    ox, oy = ring[0]
    s = 0.0
    for i in range(1, len(ring) - 1):
        ax = ring[i][0] - ox; ay = ring[i][1] - oy
        bx = ring[i + 1][0] - ox; by = ring[i + 1][1] - oy
        s += ax * by - bx * ay
    return abs(s) / 2.0

def simplify_geom(geom, tol):
    """ساده‌سازی + حذف حلقه‌های بی‌ارزش؛ حفظ حداقل حلقه بزرگ هر استان."""
    t = geom.get("type")
    def parts_type(sub, tol):
        out = []
        noise = small_dropped = 0
        biggest_i, biggest_a = -1, -1.0
        floor_a = max(TINY_AREA, tol * tol)
        cands = []
        for idx, poly in enumerate(sub):
            outer = poly[0] if poly else []
            a = ring_area(outer)
            if a > biggest_a: biggest_a, biggest_i = a, idx
            new_poly = [dp_ring(outer, tol)]
            for hole in poly[1:]: new_poly.append(dp_ring(hole, tol))
            if a < NOISE_AREA:
                noise += 1  # نویز ریزفین نقشه — همیشه حذف
                continue
            cands.append((a, new_poly))
        keep = [(a, np) for a, np in cands if a >= floor_a]
        drop_small = len(cands) - len(keep)
        # حفظ جزایر important: تا KEEP_TOP_ISLES بزرگ‌ترینِ زیر آستانه
        sub_threshold = sorted(((a, np) for a, np in cands if a < floor_a), key=lambda t: -t[0])
        keep.extend(sub_threshold[:KEEP_TOP_ISLES])
        small_dropped = drop_small - len(sub_threshold[:KEEP_TOP_ISLES])
        if not keep and biggest_i >= 0:
            keep = [(biggest_a, sub[biggest_i])]
            simple_fix = 1
        out = keep
        SIMPLE_STATS["noise"] += noise
        SIMPLE_STATS["small_dropped"] += small_dropped
        return [p for _, p in out]
    if t == "Polygon":
        pl = parts_type([geom["coordinates"]], tol)
        if not pl: return None
        return {"type": "Polygon", "coordinates": pl[0]}
    if t == "MultiPolygon":
        pl = parts_type(geom["coordinates"], tol)
        if not pl: return None
        return {"type": "MultiPolygon", "coordinates": pl}
    return None

def clamp_geom(geom):
    """کلمپ خطی خلاف خطا روی نصف‌النهار ۱۸۰ (مثل فیجی)"""
    def rec(c):
        if isinstance(c[0], (int, float)):
            lon, lat = c[0], c[1]
            if lon > 180.0: lon = 180.0
            if lon < -180.0: lon = -180.0
            if lat > 90.0: lat = 90.0
            if lat < -90.0: lat = -90.0
            return [lon, lat]
        return [rec(x) for x in c]
    return {"type": geom["type"], "coordinates": rec(geom["coordinates"])}

# ---------- اعتبارسنجی هندسه ----------
def geom_bounds(geom):
    def walk(c, bb):
        if isinstance(c[0], (int, float)):
            bb[0] = min(bb[0], c[0]); bb[1] = min(bb[1], c[1])
            bb[2] = max(bb[2], c[0]); bb[3] = max(bb[3], c[1])
        else:
            for x in c: walk(x, bb)
    bb = [180.0, 90.0, -180.0, -90.0]
    walk(geom["coordinates"], bb)
    return bb

def walk_coords(geom):
    def rec(c):
        if isinstance(c[0], (int, float)): yield c
        else:
            for x in c:
                for p in rec(x): yield p
    for p in rec(geom["coordinates"]): yield p

def valid_geom(geom):
    t = geom.get("type")
    if t not in ("Polygon", "MultiPolygon"): return False
    for p in walk_coords(geom):
        if len(p) < 2: return False
        lon, lat = p[0], p[1]
        if not (-180.001 <= lon <= 180.001 and -90.001 <= lat <= 90.001): return False
    return True

# ---------- ساخت یک کشور ----------
def build_one(iso3, fa_country, log):
    os.makedirs(CACHE_META, exist_ok=True); os.makedirs(CACHE_RAW, exist_ok=True)
    try:
        meta, cached = fetch_json_cached(API.format(i=iso3), os.path.join(CACHE_META, iso3 + ".json"))
    except HTTPError as e:
        log("  %s: NO META (HTTP %s)" % (iso3, e.code)); return None, "no_adm1"
    except (URLError, OSError, ValueError) as e:
        log("  %s: NET FAIL %s" % (iso3, type(e).__name__)); return None, "net_fail"
    url = meta.get("simplifiedGeometryGeoJSON") or ""
    if not url:
        log("  %s: no simplified url" % iso3); return None, "no_url"
    try:
        gj, _ = fetch_json_cached(url, os.path.join(CACHE_RAW, iso3 + ".json"))
    except (HTTPError, URLError, OSError, ValueError) as e:
        log("  %s: DL FAIL %s" % (iso3, type(e).__name__)); return None, "dl_fail"
    feats = gj.get("features") or []
    SIMPLE_STATS["noise"] = 0; SIMPLE_STATS["small_dropped"] = 0
    seen, out, dropped = set(), [], 0
    tol = TOL
    n_try = 0
    while True:
        seen, out, dropped = set(), [], 0
        for f in feats:
            props = f.get("properties") or {}
            name_en = (props.get("shapeName") or "").strip()
            key = (name_en.lower())
            if key and key in seen: dropped += 1; continue
            if key: seen.add(key)
            g = simplify_geom(f.get("geometry") or {}, tol)
            if g is not None: g = clamp_geom(g)
            if g is None or not valid_geom(g): dropped += 1; continue
            sha_id = props.get("shapeID") or ("%s-%d" % (iso3, len(out)))
            iso = props.get("shapeISO") or ""
            if iso3 == "IRN":
                fa_name = FA_IRN_REAL.get(name_en.lower(), "")
            else:
                fa_name = ""
            # شناسه پایدار: shapeID در صورت نبود، ISO3+فهرست
            pid = sha_id if sha_id else "%s-%d" % (iso3, len(out))
            out.append({
                "type": "Feature",
                "properties": {
                    "id": pid, "iso": iso, "name_en": name_en,
                    "name_fa": fa_name, "country": iso3,
                },
                "geometry": g,
            })
        vtry = sum(1 for f in out for _ in walk_coords(f["geometry"]))
        if vtry <= CAP_V or n_try >= 6 or tol >= 0.32: break
        tol *= 2.0; n_try += 1
        log("  %s: v=%d > CAP → tol=%.3f" % (iso3, vtry, tol))
    if not out: return None, "empty"
    ids = set(); names = {}
    for f in out:
        p = f["properties"]
        if p["id"] in ids: log("  %s: DUP ID %s" % (iso3, p["id"]))
        ids.add(p["id"])
        names[p["name_en"]] = names.get(p["name_en"], 0) + 1
    bb = [180.0, 90.0, -180.0, -90.0]
    for f in out:
        b = geom_bounds(f["geometry"])
        bb = [min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3])]
    fc = {"type": "FeatureCollection", "features": out}
    jsave(os.path.join(PROV, iso3 + ".json"), fc)
    return {
        "fa": fa_country, "n": len(out),
        "bbox": [round(bb[0], 3), round(bb[1], 3), round(bb[2], 3), round(bb[3], 3)],
        "src": meta.get("boundaryID", ""), "year": meta.get("boundaryYearRepresented", ""),
        "license": meta.get("boundaryLicense", ""), "adm_count": meta.get("admUnitCount", ""),
        "vcount": vtry,
      }, ("dup=%d" % dropped if dropped else "ok")

# ---------- progress ----------
def load_progress():
    if os.path.exists(PROGRESS):
        try: return jload(PROGRESS)
        except Exception: pass
    return {"done": {}}

def load_nodata():
    if os.path.exists(CAP):
        try: return jload(CAP)
        except Exception: pass
    return {}

def country_list():
    cm = jload(os.path.join(ROOT, "phaseA", "data", "country_map.json"))
    out = []
    for fa, d in cm.items():
        out.append((d.get("iso3", ""), fa))
    return [x for x in out if x[0]]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iso", action="append", default=[])
    ap.add_argument("--budget", type=int, default=240)
    ap.add_argument("--index", action="store_true")
    ap.add_argument("--report", action="store_true")
    a = ap.parse_args()
    os.makedirs(PROV, exist_ok=True)
    if a.report:
        return report()
    if a.index:
        return rebuild_index()
    cl = country_list()
    todo = []
    if a.iso:
        todo = [c for c in cl if c[0] in a.iso]
    else:
        pr = load_progress()
        done = pr.get("done", {})
        todo = [c for c in cl if c[0] not in done]
    t0 = time.time()
    logf = open("/tmp/gb_build.log", "a", encoding="utf-8")
    def log(m):
        print(m); logf.write(m + "\n"); logf.flush()
    pr = load_progress(); nod = load_nodata()
    sprint = 0
    for iso3, fa in todo:
        if time.time() - t0 > a.budget:
            log("BUDGET Hit — (%d) مرجع مانده" % len(todo)); break
        log("[%d/%d] %s (%s)" % (sprint + 1, len(todo), iso3, fa))
        try:
            ent, status = build_one(iso3, fa, log)
        except Exception as e:
            ent, status = None, "exc:" + type(e).__name__
            log("  EXCEPTION %s" % e)
        if ent:
            pr["done"][iso3] = {"n": ent["n"], "vcount": ent["vcount"]}
            nod.pop(iso3, None)
            log("  OK n=%d v=%d (%s)" % (ent["n"], ent["vcount"], status))
        else:
            pr["done"][iso3] = {"n": 0}
            nod[iso3] = {"fa": fa, "status": status}
            log("  SKIP %s" % status)
        sprint += 1
        if sprint % 5 == 0:
            jsave(PROGRESS, pr); jsave(CAP, nod)
            rebuild_index(quiet=True)
    jsave(PROGRESS, pr); jsave(CAP, nod)
    rebuild_index(quiet=True)
    log("DONE %d in %.0fs" % (sprint, time.time() - t0))
    logf.close()

def rebuild_index(quiet=False):
    idx = {
        "version": "1.0", "built": time.strftime("%Y-%m-%d"),
        "source": "geoBoundaries gbOpen ADM1 (CC-BY 4.0 / سجله زیری ODbL)",
        "api": "https://www.geoboundaries.org/api/current/gbOpen/{ISO3}/ADM1/",
        "pinned_commit": "9469f09", "tol_deg": TOL,
        "countries": {},
    }
    total_n = total_v = 0
    for fn in sorted(os.listdir(PROV)):
        if not fn.endswith(".json") or fn == "index.json": continue
        iso3 = fn[:-5]
        d = jload(os.path.join(PROV, fn))
        feats = d.get("features", [])
        if not feats: continue
        bb = [180.0, 90.0, -180.0, -90.0]
        nv = 0
        for f in feats:
            b = geom_bounds(f["geometry"])
            bb = [min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3])]
            nv += sum(1 for _ in walk_coords(f["geometry"]))
        ent = {"n": len(feats), "bbox": [round(x, 3) for x in bb], "v": nv}
        p0 = feats[0]["properties"]
        if iso3 == "IRN": ent["license"] = "ODbL 1.0"
        idx["countries"][iso3] = ent
        total_n += len(feats); total_v += nv
    # کشورهای بدون داده
    nod = load_nodata()
    if nod: idx["no_data"] = nod
    idx["totals"] = {"files": len([f for f in idx["countries"]]), "features": total_n, "vertices": total_v}
    jsave(os.path.join(PROV, "index.json"), idx)
    if not quiet:
        print("index.json: %d countries, %d features, %d vertices" % (len(idx["countries"]), total_n, total_v))

def report():
    idx = jload(os.path.join(PROV, "index.json"))
    print("=== گزارش B1 ===")
    print("تعداد فایل کشور:", len(idx["countries"]), "| بدون داده:", len(idx.get("no_data", {})))
    print("مجموع استانهام:", idx["totals"])
    tot = 0
    for iso3, e in sorted(idx["countries"].items()):
        p = os.path.join(PROV, iso3 + ".json")
        sz = os.path.getsize(p); tot += sz
        print("%-4s n=%-4d v=%-7d %6.1fKB  bbox=%s" % (iso3, e["n"], e["v"], sz / 1024.0, e["bbox"]))
    print("حجم کل داده: %.2f MB" % (tot / 1048576.0))
    nd = idx.get("no_data", {})
    if nd:
        print("--- کشورهای بدون ADM1 ---")
        for k, v in sorted(nd.items()): print("  %-4s %s (%s)" % (k, v.get("fa", ""), v.get("status", "")))

if __name__ == "__main__":
    main()
