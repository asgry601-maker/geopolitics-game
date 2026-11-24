# -*- coding: utf-8 -*-
"""پل JSON بین موتور متن‌محور gameplay و بازی گرافیکی وب (فاز A + آماده‌سازی فاز F).

قوانین:
  * هیچ فایل اصلی پروژه تغییر نمی‌کند؛ این فایل فقط «می‌خواند» و از API بلندقوت
    موتور (load/save/main/init_game/negotiate/announce/...) استفاده می‌کند.
  * سرور فقط روی loopback (127.0.0.1) بالا می‌آید.
  * کلید API هوش مصنوعی فقط در فایل محلی api_key.local (خارج از گیت) می‌ماند
    و هرگز به مرورگر/JavaScript فرستاده نمی‌شود (استاب فاز F همین‌جا خوانده می‌شود).

اجرا:        python geopolitics_api.py
بدون مرورگر: python geopolitics_api.py --no-browser
"""
import io
import json
import os
import sys
import threading
import webbrowser
import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

# ---------------------------------------------------------------- کشف دایرکتوری موتور
HERE = os.path.dirname(os.path.abspath(__file__))


def _engine_dir():
    """ترتیب جستجو:
    1) متغیر محیطی GEO_ENGINE_DIR
    2) پوشه engine کنار همین فایل (ZIP مستقل)
    3) همین پوشه (API داخل پوشه بازی)
    4) پوشه بازی کنار همین فایل
    5) پوشه والد (ZIP داخل پوشه بازی استخراج شده)
    6) پوشه والد بازی github (نسخه سندباکس)
    7) پوشه home
    """
    env = os.environ.get("GEO_ENGINE_DIR")
    home = os.path.expanduser("~")
    parent = os.path.dirname(HERE)
    cands = [
        env,
        os.path.join(HERE, "engine"),
        HERE,
        os.path.join(HERE, "github__asgry601-maker__geopolitics-game"),
        parent,
        os.path.join(parent, "github__asgry601-maker__geopolitics-game"),
        os.path.join(home, "geopolitics-game"),
        home,
    ]
    for c in cands:
        if c and os.path.isfile(os.path.join(c, "geopolitics.py")):
            return os.path.abspath(c)
    return None

ENGINE_DIR = _engine_dir()
if ENGINE_DIR is None:
    sys.stderr.write("\u2717 پوشه بازی (حاوی geopolitics.py) پیدا نشد.\n")
    sys.stderr.write("  متغیر محیطی GEO_ENGINE_DIR را روی مسیر بازی تنظیم کن.\n")
    sys.exit(1)
sys.path.insert(0, ENGINE_DIR)

import geopolitics as G  # noqa: E402  (پس از اضافه شدن مسیر)

STATE = os.path.join(ENGINE_DIR, "game_state.json")

# ---------------------------------------------------------------- کش state بر اساس mtime
_cache = {"mtime": -1.0, "state": None}
_lock = threading.Lock()


def get_state(force=False):
    with _lock:
        try:
            mt = os.path.getmtime(STATE)
        except OSError:
            _cache["mtime"], _cache["state"] = -1.0, None
            return None
        if force or mt != _cache["mtime"] or _cache["state"] is None:
            _cache["state"] = G.load()
            _cache["mtime"] = mt
        return dict(_cache["state"])


# ---------------------------------------------------------------- نقشه کشورها
CMAP_PATH = os.path.join(HERE, "data", "country_map.json")
CMAP = {}
try:
    with open(CMAP_PATH, encoding="utf-8") as f:
        CMAP = json.load(f)
except OSError:
    pass


def fa_meta(fa_name):
    m = CMAP.get(fa_name) or {}
    return dict(
        en=m.get("en"), lat=m.get("lat"), lon=m.get("lon"), iso3=m.get("iso3"),
        point_only=(m.get("ne") is None),
    )


def mark(s):
    try:
        return os.path.getmtime(STATE)
    except OSError:
        return "none"


# ---------------------------------------------------------------- endpoints
CMD_WHITELIST = {"end", "act", "neg", "decide", "statement", "rank", "status",
                 "dash", "negos", "help"}


def run_engine(argv):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            G.main(argv)
        return dict(ok=True, out=buf.getvalue().strip())
    except SystemExit as e:
        return dict(ok=True, out=(buf.getvalue().strip() or str(e)))
    except Exception as e:  # noqa: BLE001 — گزارش امن، بدون کرش سرور
        return dict(ok=False, out=buf.getvalue().strip(),
                    error="%s: %s" % (type(e).__name__, e))


def api_state(s):
    if s is None:
        return dict(exists=False)
    W = s["world"]
    P = s.get("player", "")
    regions = list(G.REGIONS)
    ridx = dict((r, i) for i, r in enumerate(regions))
    countries = {}
    for n, c in W.items():
        rel = 0
        if n != P:
            try:
                rel = G.get_rel(s, P, n)
            except KeyError:
                rel = 0
        # فرم فشرده: [mil, eco, tech, stab, money, influence, nukes, regionIdx, rel]
        countries[n] = [
            round(c.get("mil", 0), 1), round(c.get("eco", 0), 1),
            round(c.get("tech", 0), 1), round(c.get("stab", 0), 1),
            round(c.get("money", 0), 1), round(c.get("influence", 0), 1),
            c.get("nukes", 0), ridx.get(c.get("region"), -1), rel,
        ]
    wars = [s["at_war"][i:i + 2] for i in range(0, len(s.get("at_war", [])) - 1, 2)]
    return dict(
        exists=True, mark=mark(s), player=P, year=s.get("year"), turn=s.get("turn"),
        day=s.get("day"), ap=s.get("ap"), over=s.get("over", False),
        countries=countries, regions=regions,
        wars=wars, allies=list(s.get("allies", [])), pacts=list(s.get("pacts", [])),
        eliminated=list(s.get("eliminated", [])),
        iaea_heat=s.get("iaea_heat", 0), un_censures=s.get("un_censures", 0),
        iaea_out=bool(s.get("iaea_out", False)),
        log=(s.get("log") or [])[-6:],
        hidden=True,
    )


def api_country(s, name):
    if s is None:
        return dict(ok=False, error="بازی\u200cای ساخته نشده.")
    if name not in s["world"]:
        found = G.find_name(s, name)
        if found is None:
            return dict(ok=False, error="کشور نامعلوم: " + name)
        name = found
    W = s["world"]; P = s["player"]; c = W[name]
    meta = fa_meta(name)
    rel = None if name == P else G.get_rel(s, P, name)
    tags = []
    if name == P:
        tags.append("کشور شما")
    if name in s.get("allies", []):
        tags.append("🤝 متحد")
    if name in s.get("pacts", []):
        tags.append("📜 عدم تجاوز")
    if name in s.get("at_war", []):
        tags.append("⚔ در جنگ با شما")
    if name in s.get("eliminated", []):
        tags.append("💀 حذف‌شده")
    wars = [s["at_war"][i:i + 2] for i in range(0, len(s.get("at_war", [])) - 1, 2)]
    war_with = sorted({a if b == name else b for a, b in wars if name in (a, b) and a != b})
    ars = s.get("arsenal", {}).get(name, {})
    pol = (s.get("politics") or {}).get(name) or {}
    friends, enemies = [], []
    if name != P:
        pairs = []
        for o in W:
            if o == name:
                continue
            pairs.append((o, G.get_rel(s, name, o)))
        pairs.sort(key=lambda x: -x[1])
        friends = [(o, r) for o, r in pairs if r > 0][:5]
        enemies = sorted(((o, r) for o, r in pairs if r < 0), key=lambda x: x[1])[:5]
    prx_mine = [px.get("name") or G.proxy_label(px["sponsor"], px["host"])
                for px in s.get("proxies", []) if px["host"] == name]
    return dict(
        ok=True, name=name, **meta,
        leader=G.leader(name), rank=G.rank_of(s, name),
        region=c.get("region", ""), trait=c.get("trait", ""),
        mil=round(c.get("mil", 0), 1), eco=round(c.get("eco", 0), 1),
        tech=round(c.get("tech", 0), 1), stab=round(c.get("stab", 0), 1),
        money=round(c.get("money", 0), 1), influence=round(c.get("influence", 0), 1),
        nukes=c.get("nukes", 0), rel=rel, tags=tags, war_with=war_with,
        arsenal=[("%s× %d" % (k, v)) for k, v in sorted(ars.items(), key=lambda x: -x[1])][:4],
        parties=dict((p, round(v, 1)) for p, v in (pol.get("parties") or {}).items()),
        press=(pol.get("press") or [])[-4:],
        proxies=prx_mine,
        friends=friends, enemies=enemies,
    )


def read_ai_key():
    """استاب فاز F — کلید فقط همین‌جا (سمت سرور) خوانده می‌شود."""
    path = os.path.join(HERE, "api_key.local")
    try:
        with open(path, encoding="utf-8") as f:
            k = json.load(f)
        return dict(provider=k.get("provider"), key=k.get("key"), model=k.get("model"))
    except OSError:
        return None


def api_chat(s, body):
    who = str(body.get("country", ""))
    text = str(body.get("message", ""))[:400]
    if s is None:
        return dict(ok=False, error="بازی\u200cای ساخته نشده.")
    if who not in s["world"] and G.find_name(s, who) is None:
        return dict(ok=False, error="کشور نامعلوم: " + who)
    cfg = read_ai_key()
    if not cfg or not cfg.get("key"):
        return dict(ok=True, online=False,
                    reply="[هوش مصنوعی آنلاین در فاز F فعال می‌شود] %s در مذاکره متنی "
                          "نسخه فعلی، از منوی «🤝 مذاکره» پاسخ می‌دهد." % who)
    # فاز F: فراخوانی Provider آنلاین با cfg["key"] — هرگز به مرورگر نمی‌رود.
    return dict(ok=True, online=True, reply="(فاز F — اتصال هنوز پیاده\u200cسازی نشده)")


# ---------------------------------------------------------------- HTTP Handler
STATIC = {}  # بسته آفلاین: مسیر نسبی -> فایل فیزیکی
for rel_path, disk in [
    ("", os.path.join(HERE, "world", "world.html")),
    ("world.html", os.path.join(HERE, "world", "world.html")),
    ("world.js", os.path.join(HERE, "world", "world.js")),
    ("lib/three.min.js", os.path.join(HERE, "lib", "three.min.js")),
    ("lib/globe.gl.min.js", os.path.join(HERE, "lib", "globe.gl.min.js")),
    ("data/countries.geojson", os.path.join(HERE, "data", "countries.geojson")),
    ("data/country_map.json", os.path.join(HERE, "data", "country_map.json")),
    ("img/earth-dark.jpg", os.path.join(HERE, "img", "earth-dark.jpg")),
    ("img/earth-blue-marble.jpg", os.path.join(HERE, "img", "earth-blue-marble.jpg")),
]:
    STATIC[rel_path] = disk

CTYPES = {
    ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8", ".geojson": "application/json; charset=utf-8",
    ".jpg": "image/jpeg", ".css": "text/css; charset=utf-8", ".ico": "image/x-icon",
}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *a):  # آرام‌سازی لاگ
        sys.stderr.write("  " + (fmt % a) + "\n")

    def _send(self, code, body=b"", ctype="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    def _serve_static(self, path):
        disk = STATIC.get(path)
        if not disk or not os.path.isfile(disk):
            self._json(dict(error="not found"), 404)
            return
        ext = os.path.splitext(disk)[1].lower()
        with open(disk, "rb") as f:
            data = f.read()
        self._send(200, data, CTYPES.get(ext, "application/octet-stream"))

    def do_GET(self):
        u = urlparse(self.path)
        path = u.path.lstrip("/")
        if path == "api/state":
            self._json(api_state(get_state()))
        elif path == "api/country":
            q = parse_qs(u.query)
            s = get_state()
            if s is None:
                self._json(dict(ok=False, error="بازی\u200cای ساخته نشده."))
            else:
                nm = (q.get("name") or [""])[0].strip()
                self._json(api_country(s, nm))
        elif path == "api/version":
            self._json(dict(ok=True, phase="A", engine=ENGINE_DIR, state=STATE))
        elif path in STATIC:
            self._serve_static(path)
        else:
            # صفحه اصلی — تجربی: مسیرهای دیگر به صفحه اصلی برمی‌گردند (SPA ساده)
            self._serve_static("")

    def do_POST(self):
        u = urlparse(self.path)
        path = u.path.lstrip("/")
        try:
            ln = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(ln) if ln else b"{}"
            body = json.loads(raw.decode("utf-8")) if raw else {}
        except (ValueError, UnicodeDecodeError):
            self._json(dict(ok=False, error="بدنه JSON نامعتبر"), 400)
            return
        s = get_state()
        if path == "api/init":
            if s is not None:
                self._json(dict(ok=False, error="بازی در جریان است. برای بازی جدید از نسخه وب متن استفاده کن."))
                return
            country = str(body.get("country", "")).strip()
            if not country:
                self._json(dict(ok=False, error="نام کشور را بفرست."))
                return
            res = run_engine(["init", country])
            self._json(dict(res, state=api_state(get_state(True))))
        elif path == "api/act":
            if s is None:
                self._json(dict(ok=False, error="بازی\u200cای ساخته نشده."))
                return
            argv = body.get("argv") or []
            if not argv or not isinstance(argv, list) or argv[0] not in CMD_WHITELIST:
                self._json(dict(ok=False, error="فرمان مجاز نیست."))
                return
            res = run_engine([str(a) for a in argv])
            self._json(dict(res, state=api_state(get_state(True))))
        elif path == "api/chat":
            self._json(api_chat(s, body))
        else:
            self._json(dict(ok=False, error="endpoint نامعتبر"), 404)


def main():
    port = int(os.environ.get("GEO_PORT", "8731")) if os.environ.get("GEO_PORT") else 8731
    srv = None
    while srv is None:
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        except OSError:
            port = 0  # پورت آزاد تصادفی
    if port == 0:
        port = srv.server_address[1]
    url = "http://127.0.0.1:%d/" % port
    print("\u2714 سرور بازی گرافیکی روی %s (loopback) \u2014 برای توقف: Ctrl+C" % url)
    print("  موتور: %s" % ENGINE_DIR)
    if "--no-browser" not in sys.argv:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n◼ سرور متوقف شد.")


if __name__ == "__main__":
    main()
