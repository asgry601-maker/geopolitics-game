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
import re
import shutil
import sys
import threading
import webbrowser
import contextlib
import datetime
import traceback
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


def _log_exc(msg):
    """ثبت خطای کامل در stderr (کنسول سرور) با تاریخ و ساعت."""
    sys.stderr.write("[%s] %s\n%s" % (
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        msg, traceback.format_exc()))
    sys.stderr.flush()


def get_state(force=False):
    with _lock:
        try:
            mt = os.path.getmtime(STATE)
        except OSError:
            _cache["mtime"], _cache["state"] = -1.0, None
            return None
        if force or mt != _cache["mtime"] or _cache["state"] is None:
            try:
                _cache["state"] = G.load()
            except Exception:
                # ذخیره خراب/ناسازگار → سرور هرگز نمی‌میرد؛ state خالی گزارش می‌شود
                _cache["state"] = None
                _cache["mtime"] = mt
                _log_exc("خواندن game_state.json شکست خورد")
                return None
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


# ---------------------------------------------------------------- پرونده‌های پژوهش سیاسی (مرجع مستقل از شاخص‌های شبیه‌سازی موتور)
POLITICAL_PROFILES_PATH = os.path.join(HERE, "data", "political_profiles.json")
_POL_PROFILE_CACHE = {"mtime": -1.0, "countries": {}}


def political_profile(iso3):
    """پرونده پژوهش‌شده کشور را با کش mtime برمی‌گرداند؛ فقط خواندنی."""
    if not iso3:
        return None
    try:
        mt = os.path.getmtime(POLITICAL_PROFILES_PATH)
        if mt != _POL_PROFILE_CACHE["mtime"]:
            with open(POLITICAL_PROFILES_PATH, encoding="utf-8") as f:
                payload = json.load(f)
            _POL_PROFILE_CACHE["countries"] = payload.get("countries") or {}
            _POL_PROFILE_CACHE["mtime"] = mt
        profile = _POL_PROFILE_CACHE["countries"].get(iso3)
        return dict(profile) if isinstance(profile, dict) else None
    except (OSError, ValueError, TypeError):
        return None

# اطلاعات پایه کشورها؛ کش مستقل از شاخص‌های شبیه‌سازی
COUNTRY_PROFILES_PATH = os.path.join(HERE, "data", "country_profiles.json")
_COUNTRY_PROFILE_CACHE = {"mtime": -1.0, "countries": {}}

def country_profile(iso3):
    if not iso3:
        return None
    try:
        mt = os.path.getmtime(COUNTRY_PROFILES_PATH)
        if mt != _COUNTRY_PROFILE_CACHE['mtime']:
            with open(COUNTRY_PROFILES_PATH, encoding='utf-8') as f:
                payload = json.load(f)
            _COUNTRY_PROFILE_CACHE['countries'] = payload.get('countries') or {}
            _COUNTRY_PROFILE_CACHE['mtime'] = mt
        value = _COUNTRY_PROFILE_CACHE['countries'].get(iso3)
        return dict(value) if isinstance(value, dict) else None
    except (OSError, ValueError, TypeError):
        return None


# پرچم‌های SVG در بسته‌های JSON محلی؛ بدون نیاز به اینترنت در زمان اجرای بازی.
_FLAG_PARTS = ["flag_svgs_part_%d.json" % i for i in range(1, 13)]
_FLAG_CACHE = {"mtimes": None, "flags": {}}


def get_flag_svg(iso3):
    if not iso3 or not re.match(r"^[A-Z]{3}$", iso3):
        return None
    try:
        paths = [os.path.join(HERE, "data", name) for name in _FLAG_PARTS]
        mtimes = tuple(os.path.getmtime(path) if os.path.isfile(path) else None
                       for path in paths)
        if mtimes != _FLAG_CACHE["mtimes"]:
            flags = {}
            for path in paths:
                if os.path.isfile(path):
                    with open(path, encoding="utf-8") as f:
                        flags.update(json.load(f))
            _FLAG_CACHE["flags"] = flags
            _FLAG_CACHE["mtimes"] = mtimes
        return _FLAG_CACHE["flags"].get(iso3)
    except (OSError, ValueError, TypeError):
        return None


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
        day=s.get("day"), game_date=s.get("game_date"),
        hour=s.get("hour", 0), minute=s.get("minute", 0),
        ap=s.get("ap"), over=s.get("over", False),
        countries=countries, regions=regions,
        wars=wars, allies=list(s.get("allies", [])), pacts=list(s.get("pacts", [])),
        pact_records=(s.get("pact_records") or [])[-200:],
        alliance_records=(s.get("alliance_records") or [])[-150:],
        agreement_proposals=(s.get("agreement_proposals") or [])[-150:],
        agreement_history=(s.get("agreement_history") or [])[-100:],
        agreement_sequence=s.get("agreement_sequence", 0),
        player_sanctions=s.get("player_sanctions", {}),
        player_sanction_history=(s.get("player_sanction_history") or [])[-50:],
        inbox_messages=(s.get("inbox_messages") or [])[-100:],
        inbox_unread_count=sum(1 for item in (s.get("inbox_messages") or []) if isinstance(item, dict) and item.get("status") == "unread"),
        conversation_sessions=(s.get("conversation_sessions") or [])[-50:],
        conversation_sequence=s.get("conversation_sequence", 0),
        eliminated=list(s.get("eliminated", [])),
        iaea_heat=s.get("iaea_heat", 0), un_censures=s.get("un_censures", 0),
        iaea_out=bool(s.get("iaea_out", False)),
        log=(s.get("log") or [])[-6:],
        political_reform_proposals=(s.get("political_reform_proposals") or [])[-20:],
        social_groups=(s.get("social_groups") or {}).get(P, {}),
        legitimacy=s.get("legitimacy", 50.0),
        regime_crisis=s.get("regime_crisis"),
        game_events=(s.get("game_events") or [])[-50:],
        event_sequence=s.get("event_sequence", 0),
        political_history=(s.get("political_history") or [])[-10:],
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
    political_classification = (s.get("political_state") or {}).get(name)
    political_baseline = (s.get("political_baseline_state") or {}).get(name)
    friends, enemies = [], []
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
    # اقتصاد: فقط شاخص‌ها و فرمول‌های واقعاً موجود در موتور؛ بدون جعل GDP یا بودجه تفصیلی.
    income_daily = c.get("eco", 0) * G.INCOME_K * (0.5 if c.get("stab", 0) < 30 else 1.0)
    alive = [n for n in W if n not in s.get("eliminated", [])]
    eco_sorted = sorted(alive, key=lambda n: -W[n].get("eco", 0))
    eco_rank = eco_sorted.index(name) + 1 if name in eco_sorted else None
    economy_top = [dict(name=n, eco=round(W[n].get("eco", 0), 1)) for n in eco_sorted[:5]]
    return dict(
        ok=True, name=name, **meta,
        leader=G.leader(name), rank=G.rank_of(s, name),
        region=c.get("region", ""), trait=c.get("trait", ""),
        mil=round(c.get("mil", 0), 1), eco=round(c.get("eco", 0), 1),
        tech=round(c.get("tech", 0), 1), stab=round(c.get("stab", 0), 1),
        money=round(c.get("money", 0), 1), influence=round(c.get("influence", 0), 1),
        nukes=c.get("nukes", 0), rel=rel, tags=tags, war_with=war_with,
        income_daily=round(income_daily, 2), income_monthly_estimate=round(income_daily * 30, 1),
        economic_rank=eco_rank, economy_top=economy_top,
        arsenal=[("%s× %d" % (k, v)) for k, v in sorted(ars.items(), key=lambda x: -x[1])][:4],
        parties=dict((p, round(v, 1)) for p, v in (pol.get("parties") or {}).items()),
        political_profile=political_profile(meta.get("iso3")),
        political_classification=political_classification,
        political_baseline=political_baseline,
        country_profile=country_profile(meta.get("iso3")),
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


# تصاویر رهبران کشورها؛ نام فایل بر اساس ISO3 و بدون مسیر دلخواه کاربر.
LEADER_DIR = os.path.join(HERE, "assets", "leaders")
_LEADER_RE = re.compile(r"^assets/leaders/([A-Z]{3})\.(jpg|jpeg|png|webp)$")

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

# فاز B2 — سرو داده‌های استان‌ها (فقط نام‌های تحت الگوی سخت؛ مسیر traversal ممکن نیست)
PROV_DIR = os.path.join(HERE, "data", "provinces")
_PROV_RE = re.compile(r"^data/provinces/((?:index|LICENSES|[A-Z]{3})\.json)$")

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
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True
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

    def _serve_province(self, name):
        disk = os.path.join(PROV_DIR, name)
        try:
            with open(disk, "rb") as f:
                data = f.read()
        except OSError:
            self._json(dict(error="پرونده استان یافت نشد."), 404)
            return
        self._send(200, data, "application/json; charset=utf-8")

    def _do_get(self):
        u = urlparse(self.path)
        path = u.path.lstrip("/")
        if path == "api/state":
            self._json(api_state(get_state()))
        elif path == "api/events/catalog":
            self._json(dict(ok=True, activation=G.EVENT_TRIGGER_ACTIVATION,
                            categories=list(G.EVENT_CATEGORIES),
                            triggers=G.get_event_trigger_catalog()))
        elif path == "api/events":
            state = get_state()
            if state is None:
                self._json(dict(ok=False, error="بازی‌ای ساخته نشده."), 404)
                return
            query = parse_qs(u.query)
            try:
                limit = int((query.get("limit") or ["50"])[0])
            except (TypeError, ValueError):
                limit = 50
            limit = max(1, min(200, limit))
            include_closed = (query.get("include_closed") or ["0"])[0] in ("1", "true", "yes")
            events = G.get_prioritized_game_events(state, limit=200, include_closed=include_closed)
            category = (query.get("category") or [""])[0].strip()
            status = (query.get("status") or [""])[0].strip()
            country = (query.get("country") or [""])[0].strip()
            if category:
                events = [item for item in events if item.get("category") == category]
            if status:
                events = [item for item in events if item.get("status") == status]
            if country:
                events = [item for item in events if item.get("country") == country]
            self._json(dict(ok=True, count=len(events[:limit]), events=events[:limit],
                            event_sequence=state.get("event_sequence", 0)))
        elif path.startswith("api/events/chain/"):
            state = get_state()
            event_id = path[len("api/events/chain/"):]
            if state is None:
                self._json(dict(ok=False, error="بازی‌ای ساخته نشده."), 404)
            else:
                try:
                    self._json(dict(ok=True, chain=G.get_event_chain(state, event_id)))
                except ValueError as exc:
                    self._json(dict(ok=False, error=str(exc)), 404)
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
        elif _PROV_RE.match(path):
            self._serve_province(_PROV_RE.match(path).group(1))
        elif re.match(r"^assets/flags/[A-Z]{3}\.svg$", path):
            iso3 = path.rsplit("/", 1)[-1][:3]
            svg = get_flag_svg(iso3)
            if svg:
                self._send(200, svg.encode("utf-8"), "image/svg+xml; charset=utf-8")
            else:
                self._json(dict(error="پرچم این کشور در بسته محلی یافت نشد."), 404)
        elif _LEADER_RE.match(path):
            match = _LEADER_RE.match(path)
            disk = os.path.join(LEADER_DIR, match.group(1) + "." + match.group(2))
            if os.path.isfile(disk):
                ext = os.path.splitext(disk)[1].lower()
                ctype = {".jpg":"image/jpeg",".jpeg":"image/jpeg",".png":"image/png",".webp":"image/webp"}[ext]
                with open(disk, "rb") as f:
                    self._send(200, f.read(), ctype)
            else:
                self._json(dict(error="تصویر رهبر هنوز در بسته محلی ثبت نشده است."), 404)
        elif path in STATIC:
            self._serve_static(path)
        else:
            # صفحه اصلی — تجربی: مسیرهای دیگر به صفحه اصلی برمی‌گردند (SPA ساده)
            self._serve_static("")

    def _do_post(self):
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
            country = str(body.get("country", "")).strip()
            if not country:
                self._json(dict(ok=False, error="\u0646\u0627\u0645 \u06a9\u0634\u0648\u0631 \u0631\u0627 \u0628\u0641\u0631\u0633\u062a."))
                return
            if s is not None:
                # \u0628\u0627\u0632\u06cc \u0641\u0639\u0627\u0644 \u062f\u0627\u0631\u062f \u2014 \u0628\u062f\u0648\u0646 \u062a\u0623\u06cc\u06cc\u062f \u0635\u0631\u06cc\u062d \u06a9\u0627\u0631\u0628\u0631 \u0647\u06cc\u0686 reset \u0627\u0646\u062c\u0627\u0645 \u0646\u0645\u06cc\u200c\u0634\u0648\u062f
                if str(body.get("confirm", "")) != "\u0628\u0644\u0647":
                    self._json(dict(ok=False, needConfirm=True,
                                    error="\u0628\u0627\u0632\u06cc \u062f\u0631 \u062c\u0631\u06cc\u0627\u0646 \u0627\u0633\u062a. "
                                          "\u0628\u0631\u0627\u06cc \u0634\u0631\u0648\u0639 \u0628\u0627\u0632\u06cc \u062c\u062f\u06cc\u062f\u060c \u062f\u0631 \u067e\u0646\u062c\u0631\u0647 \u062a\u0623\u06cc\u06cc\u062f "
                                          "\u062f\u06a9\u0645\u0647 \u00ab\u0634\u0631\u0648\u0639 \u0628\u0627\u0632\u06cc \u062c\u062f\u06cc\u062f\u00bb \u0631\u0627 \u0628\u0632\u0646."))
                    return
                # \u062d\u0641\u0627\u0638 \u0627\u0632 \u0630\u062e\u06cc\u0631\u0647: \u067e\u0634\u062a\u06cc\u0628\u0627\u0646 game_state.json \u2190 .bak \u0642\u0628\u0644 \u0627\u0632 \u0647\u0631 reset
                bak = STATE + ".bak"
                try:
                    shutil.copyfile(STATE, bak)
                except OSError as e:
                    self._json(dict(ok=False,
                                    error="\u067e\u0634\u062a\u06cc\u0628\u0627\u0646\u200c\u06af\u06cc\u0631\u06cc \u0630\u062e\u06cc\u0631\u0647 \u0642\u0628\u0644\u06cc "
                                          "\u0646\u0627\u0645\u0648\u0641\u0642 \u0628\u0648\u062f\u061b reset \u0627\u0646\u062c\u0627\u0645 \u0646\u0634\u062f: %s" % e))
                    return
                res = run_engine(["reset", country])
                res["backup"] = bak
                res["out"] = ((res.get("out") or "") + "\n" if res.get("out") else "") + (
                    "\U0001f4be \u0627\u0632 \u0630\u062e\u06cc\u0631\u0647 \u06a9\u0646\u0648\u0646\u06cc "
                    "\u067e\u0634\u062a\u06cc\u0628\u0627\u0646 \u06af\u0631\u0641\u062a\u0647 \u0634\u062f: game_state.json.bak")
            else:
                # \u0628\u062f\u0648\u0646 \u0628\u0627\u0632\u06cc \u0641\u0639\u0627\u0644 \u2014 \u0634\u0631\u0648\u0639 \u0645\u0633\u062a\u0642\u06cc\u0645 \u0648 \u0628\u062f\u0648\u0646 \u062a\u0623\u06cc\u06cc\u062f \u0627\u0636\u0627\u0641\u06cc
                res = run_engine(["init", country])
            self._json(dict(res, state=api_state(get_state(True))))
            return
        elif path == "api/conversations/prepare":
            if s is None:
                self._json(dict(ok=False, error="بازی‌ای ساخته نشده."), 404)
                return
            try:
                with _lock:
                    current = G.load()
                    result = G.prepare_conversation_session(
                        current,
                        body.get("participants"),
                        topic=body.get("topic", "گفت‌وگوی دیپلماتیک"),
                        visibility_mode=body.get("visibility_mode", "public"),
                        negotiation_type=body.get("negotiation_type", "standard"),
                        source=body.get("source", "system"),
                        context=body.get("context"),
                        conversation_id=body.get("conversation_id"))
                    G.save(current)
                self._json(dict(result, state=api_state(get_state(True))))
            except ValueError as exc:
                self._json(dict(ok=False, error=str(exc)), 400)
            except Exception as exc:
                self._json(dict(ok=False, error="خطا در آماده‌سازی نشست گفت‌وگو: %s" % exc), 500)
        elif path == "api/inbox/read":
            if s is None:
                self._json(dict(ok=False, error="بازی‌ای ساخته نشده."), 404)
                return
            try:
                with _lock:
                    current = G.load()
                    item = G.mark_inbox_message_read(current, body.get("message_id"))
                    G.save(current)
                self._json(dict(ok=True, message=item, state=api_state(get_state(True))))
            except ValueError as exc:
                self._json(dict(ok=False, error=str(exc)), 404)
            except Exception as exc:
                self._json(dict(ok=False, error="خطا در به‌روزرسانی پیام: %s" % exc), 500)
        elif path == "api/events/source-review":
            if s is None:
                self._json(dict(ok=False, error="بازی‌ای ساخته نشده."), 404)
                return
            try:
                with _lock:
                    current = G.load()
                    result = G.review_game_event_source(
                        current, body.get("event_id"),
                        reviewer=body.get("reviewer", "player"),
                        status=body.get("status", "reviewed"),
                        note=body.get("note", ""))
                    G.save(current)
                self._json(dict(ok=True, source_info=result,
                                state=api_state(get_state(True))))
            except ValueError as exc:
                self._json(dict(ok=False, error=str(exc)), 400)
            except Exception as exc:
                self._json(dict(ok=False, error="خطا در بازبینی منشأ رویداد: %s" % exc), 500)
        elif path == "api/political/change":
            if s is None:
                self._json(dict(ok=False, error="بازی‌ای ساخته نشده."))
                return
            changes = body.get("changes")
            try:
                with _lock:
                    current = G.load()
                    result = G.apply_player_political_change(current, changes)
                self._json(dict(result, state=api_state(get_state(True))))
            except Exception as e:
                self._json(dict(ok=False, error="خطا در ثبت طرح اصلاحات: %s" % e), 500)
        elif path == "api/political/cancel":
            if s is None:
                self._json(dict(ok=False, error="بازی‌ای ساخته نشده."))
                return
            try:
                with _lock:
                    current = G.load()
                    result = G.cancel_player_political_reform(current, body.get("proposal_id"))
                self._json(dict(result, state=api_state(get_state(True))))
            except Exception as e:
                self._json(dict(ok=False, error="خطا در لغو طرح اصلاحات: %s" % e), 500)
        elif path == "api/political/review":
            if s is None:
                self._json(dict(ok=False, error="بازی‌ای ساخته نشده."))
                return
            try:
                with _lock:
                    current = G.load()
                    result = G.review_player_political_reform(current, body.get("proposal_id"))
                self._json(dict(result, state=api_state(get_state(True))))
            except Exception as e:
                self._json(dict(ok=False, error="خطا در ارزیابی طرح اصلاحات: %s" % e), 500)
        elif path == "api/political/decision":
            if s is None:
                self._json(dict(ok=False, error="بازی‌ای ساخته نشده."))
                return
            try:
                with _lock:
                    current = G.load()
                    result = G.decide_player_political_reform(
                        current, body.get("proposal_id"), body.get("decision"))
                self._json(dict(result, state=api_state(get_state(True))))
            except Exception as e:
                self._json(dict(ok=False, error="خطا در ثبت تصمیم طرح اصلاحات: %s" % e), 500)
        elif path == "api/time":
            if s is None:
                self._json(dict(ok=False, error="بازی‌ای در جریان نیست."))
                return
            minutes = body.get("minutes")
            if minutes not in (300, 1440):
                self._json(dict(ok=False, error="گام زمانی نامعتبر است."), 400)
                return
            try:
                with _lock:
                    current = G.load()
                    G.advance_time(current, minutes)
                state_now = get_state(True)
                self._json(dict(ok=True, out="زمان بازی جلو رفت.", state=api_state(state_now)))
            except Exception as e:
                self._json(dict(ok=False, error="خطا در جلو بردن زمان: %s" % e), 500)
        elif path == "api/sanctions/apply":
            if s is None:
                self._json(dict(ok=False, error="بازی‌ای ساخته نشده."), 404)
                return
            try:
                with _lock:
                    current = G.load()
                    result = G.apply_player_sanctions(
                        current, body.get("targets"), body.get("categories"))
                    G.save(current)
                self._json(dict(result, state=api_state(get_state(True))))
            except ValueError as exc:
                self._json(dict(ok=False, error=str(exc)), 400)
            except Exception as exc:
                self._json(dict(ok=False, error="خطا در ثبت تحریم‌ها: %s" % exc), 500)
        elif path == "api/sanctions/cancel":
            if s is None:
                self._json(dict(ok=False, error="بازی‌ای ساخته نشده."), 404)
                return
            try:
                with _lock:
                    current = G.load()
                    result = G.cancel_player_sanctions(current, body.get("targets"))
                    G.save(current)
                self._json(dict(result, state=api_state(get_state(True))))
            except ValueError as exc:
                self._json(dict(ok=False, error=str(exc)), 400)
            except Exception as exc:
                self._json(dict(ok=False, error="خطا در لغو تحریم‌ها: %s" % exc), 500)
        elif path == "api/agreements/propose":
            if s is None:
                self._json(dict(ok=False, error="بازی‌ای ساخته نشده."), 404)
                return
            try:
                with _lock:
                    current = G.load()
                    result = G.submit_agreement_proposal(
                        current, body.get("kind"), body.get("parties"),
                        body.get("pact_type", "non_aggression"),
                        body.get("alliance_name", ""), body.get("terms"),
                        body.get("conversation_id"))
                    G.save(current)
                self._json(dict(result, state=api_state(get_state(True))))
            except ValueError as exc:
                self._json(dict(ok=False, error=str(exc)), 400)
            except Exception as exc:
                self._json(dict(ok=False, error="خطا در ثبت پیشنهاد توافق: %s" % exc), 500)
        elif path == "api/agreements/decision":
            if s is None:
                self._json(dict(ok=False, error="بازی‌ای ساخته نشده."), 404)
                return
            try:
                with _lock:
                    current = G.load()
                    result = G.decide_agreement_proposal(
                        current, body.get("proposal_id"), body.get("decision"))
                    G.save(current)
                self._json(dict(result, state=api_state(get_state(True))))
            except ValueError as exc:
                self._json(dict(ok=False, error=str(exc)), 400)
            except Exception as exc:
                self._json(dict(ok=False, error="خطا در ثبت تصمیم توافق: %s" % exc), 500)
        elif path == "api/agreements/pact/cancel":
            if s is None:
                self._json(dict(ok=False, error="بازی‌ای ساخته نشده."), 404)
                return
            try:
                with _lock:
                    current = G.load()
                    result = G.cancel_pact_record(current, body.get("agreement_id"))
                    G.save(current)
                self._json(dict(result, state=api_state(get_state(True))))
            except ValueError as exc:
                self._json(dict(ok=False, error=str(exc)), 400)
            except Exception as exc:
                self._json(dict(ok=False, error="خطا در لغو پیمان: %s" % exc), 500)
        elif path == "api/agreements/alliance/leave":
            if s is None:
                self._json(dict(ok=False, error="بازی‌ای ساخته نشده."), 404)
                return
            try:
                with _lock:
                    current = G.load()
                    result = G.leave_alliance(current, body.get("agreement_id"))
                    G.save(current)
                self._json(dict(result, state=api_state(get_state(True))))
            except ValueError as exc:
                self._json(dict(ok=False, error=str(exc)), 400)
            except Exception as exc:
                self._json(dict(ok=False, error="خطا در خروج از اتحاد: %s" % exc), 500)
        elif path == "api/act":
            if s is None:
                self._json(dict(ok=False, error="بازی\u200cای ساخته نشده."))
                return
            argv = body.get("argv") or []
            if not argv or not isinstance(argv, list) or argv[0] not in CMD_WHITELIST:
                self._json(dict(ok=False, error="فرمان مجاز نیست."))
                return
            try:
                with _lock:
                    res = run_engine([str(a) for a in argv])
            except Exception as exc:
                self._json(dict(ok=False, error="خطا در اجرای فرمان: %s" % exc), 500)
                return
            self._json(dict(res, state=api_state(get_state(True))))
        elif path == "api/chat":
            self._json(api_chat(s, body))
        else:
            self._json(dict(ok=False, error="endpoint نامعتبر"), 404)

    # ---------------------------------------------------------------- catch-all:
    # هیچ استثنایی هرگز نباید اتصال را بدون پاسخ ببندد؛ وگرنه مرورگر status=0
    # می‌بیند و فقط «خطای شبکه» عمومی نمایش داده می‌شود.
    def do_GET(self):
        try:
            self._do_get()
        except Exception:  # noqa: BLE001
            self._fatal("GET")

    def do_POST(self):
        try:
            self._do_post()
        except Exception:  # noqa: BLE001
            self._fatal("POST")

    def _fatal(self, what):
        _log_exc("خطای داخلی سرور در " + what)
        try:
            self._json(dict(ok=False,
                            error="خطای داخلی سرور — جزئیات کامل در کنسول سرور ثبت شد"), 500)
        except Exception:  # noqa: BLE001 — پاسخ قبلاً ارسال شده؛ فقط لاگ
            pass


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
