#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""نسخه‌ی ایمیل بازی — HTML خالص بدون جاوااسکریپت؛ فقط روی 127.0.0.1."""
import io as _io
import json
import os
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geopolitics

CSSL = """
body{margin:0;font-family:Tahoma,'Segoe UI',sans-serif;background:#0d1521;color:#dfe8f2}
header{background:#132a43;border-bottom:3px solid #2b4d77;padding:10px 16px}
h1{font-size:19px;color:#7fc4ff;margin:0 0 8px 0}
.chip{display:inline-block;background:#16283f;border:1px solid #2b4d77;border-radius:14px;padding:4px 12px;font-size:12px;margin:2px}
.chip b{color:#ffd54f}
section{background:#101b2b;border:1px solid #1d2f4a;border-radius:10px;padding:12px 14px;margin:12px 16px}
section h2{margin:0 0 10px 0;font-size:15px;color:#7fc4ff;border-bottom:1px solid #1d2f4a;padding-bottom:6px}
form.ib{display:inline-block;margin:2px}
input[type=submit]{background:#17350f;color:#c8f0b0;border:1px solid #3a6b28;border-radius:8px;padding:9px 14px;font-family:inherit;font-size:13px;cursor:pointer;margin:2px}
input[type=submit]:hover{background:#235017}
button{background:#1a3a5c;color:#dfe8f2;border:1px solid #2b4d77;border-radius:8px;padding:9px 14px;font-family:inherit;font-size:13px;cursor:pointer;margin:2px}
button:hover{background:#26496e}
button.big{background:#3a2c00;border-color:#8a6d00;color:#ffe08a;font-size:15px;padding:12px 22px}
.itemrow{border-bottom:1px solid #1d2f4a;padding:6px 2px;font-size:13px}
summary{cursor:pointer;color:#bfd6ee}
details{margin:2px 0}
input[type=submit].big{background:#3a2c00;border-color:#8a6d00;color:#ffe08a;font-size:15px;padding:12px 22px}
select,input[type=text]{background:#0d1725;color:#dfe8f2;border:1px solid #2b4d77;border-radius:8px;padding:7px 9px;font-family:inherit;font-size:13px;margin:2px;vertical-align:middle}
.out{background:#0a1017;border:1px solid #1d2f4a;border-radius:10px;margin:12px 16px;padding:0}
.out .ttl{padding:8px 14px;border-bottom:1px solid #1d2f4a;color:#7fc4ff;font-size:13px}
.out .txt{white-space:pre-wrap;padding:12px 14px;font-family:Tahoma;font-size:13.5px;line-height:1.9;min-height:120px;margin:0}
.hint{color:#8aa5c4;font-size:12px;margin:6px 0}
.footer{color:#5f7a99;font-size:11px;margin:18px 16px}
"""


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def btn(label, cmd, cls=""):
    c = ' class="%s"' % cls if cls else ""
    return ('<form class="ib" method="post" action="/">'
            '<button type="submit" name="cmd" value="%s"%s>%s</button></form>'
            % (esc(cmd), c, esc(label)))


def group(select_html, labels, cls=""):
    subs = "".join('<button type="submit" name="cmd" value="%s"%s>%s</button>'
                   % (esc(c), (' class="%s"' % cls if cls else ""), esc(lbl)) for lbl, c in labels)
    return ('<form method="post" action="/">' + select_html
            + '<div style="margin-top:6px">' + subs + "</div></form>")


def country_select(name, options, selected=""):
    opts = []
    for c in options:
        marker = ""
        if selected and c == selected:
            marker = " selected"
        opts.append('<option value="%s"%s>%s</option>' % (esc(c), marker, esc(c)))
    return '<select name="%s">%s</select>' % (name, "".join(opts))


def render(out_text="", chosen=None):
    has = os.path.exists(geopolitics.STATE)
    countries = list(geopolitics.COUNTRIES.keys())
    chips = ""
    s = None
    if has:
        s = geopolitics.load()
        P = s["player"]
        me = s["world"][P]
        stat = [
            ("کشور", P),
            ("سال", s.get("year")),
            ("روز", s.get("day")),
            ("💰 خزانه", round(me.get("money", 0))),
            ("🎖 نظامی", round(me.get("mil", 0))),
            ("🏭 اقتصاد", round(me.get("eco", 0))),
            ("🔬 فناوری", round(me.get("tech", 0))),
            ("🕊 ثبات", round(me.get("stab", 0))),
            ("☢ کلاهک", me.get("nukes", 0)),
        ]
        chips = " ".join('<span class="chip">%s: <b>%s</b></span>' % (esc(k), esc(v)) for k, v in stat)

    start = ""
    if not has:
        start = ('<section><h2>🎮 شروع بازی جدید</h2>'
                 '<div class="hint">کشورت را از فهرست انتخاب کن و «شروع» را بزن.</div>'
                 + group(country_select("start_country", countries, "ایران"),
                         [("شروع", "start")], "big")
                 + "</section>")

    sections = []
    sections.append('<section><h2>🏠 مرکز فرماندهی</h2>'
                    + btn("📋 وضعیت من", "status")
                    + btn("📚 راهنما", "help")
                    + btn("🏆 رتبه‌بندی جهانی", "rank")
                    + btn("🌆 فهرست ۱۷۴ کشور", "list")
                    + btn("🌙 پایان روز (زمان جلو می‌رود)", "end", "big")
                    + "</section>")

    dbs = [("سیاست داخلی", "dom"), ("دیپلماسی", "dip"), ("عملیات", "ops"),
           ("نظامی", "mil"), ("اقتصاد", "eco"), ("نهادها", "org")]
    body = "".join(btn("📊 " + n, "dash " + v) for n, v in dbs)
    sections.append('<section><h2>📊 داشبوردها</h2>' + body + "</section>")

    dip = [("💰 کمک اقتصادی", "act aide"), ("🛒 قرارداد تجاری", "act trade"), ("🕊️ پیمان عدم تعارض", "act pact"), ("⚔️ اتحاد نظامی", "act ally"), ("✂ فسخ پیمان", "act break"), ("⛔ تحریم", "act sanc"), ("🗣️ محکومیت در ملل", "act un")]
    body = ('<div class="hint">اول کشور را انتخاب کن، بعد دکمه را بزن:</div>'
            + group(country_select("target", countries), dip))
    sections.append('<section><h2>🤝 دیپلماسی</h2>' + body + "</section>")

    body = (btn("📈 بودجه نظامی", "act mil")
            + btn("🧪 پروژه فناوری", "act tech")
            + btn("☢ ساخت کلاهک هسته‌ای", "act nuke", "big")
            + btn("🔍 شفافیت به آژانس", "act iaea", "big"))
    body += ('<div class="hint">اعلام جنگ — کشور را انتخاب کن:</div>'
             + group(country_select("war_target", countries), [("⚔ اعلام جنگ", "act war")]))
    sections.append('<section><h2>🛡 ارتش و برنامه هسته‌ای</h2>' + body + "</section>")

    ops = [("🔑 جاسوسی", "act spy"), ("💥 بی‌ثبات‌سازی", "act covert"), ("🧨 خرابکاری", "act sabotage"), ("🎯 ترور", "act kill"), ("🕸 شبکه نیابتی", "act proxy")]
    body = ('<div class="hint">اول کشور هدف را انتخاب کن:</div>'
            + group(country_select("target", countries), ops))
    sections.append('<section><h2>🕵 عملیات پنهان</h2>' + body + "</section>")

    body = (btn("🏭 سرمایه‌گذاری کلان", "act eco", "big")
            + btn("📣 کمپین تبلیغاتی", "act propaganda"))
    sections.append('<section><h2>💰 اقتصاد</h2>' + body + "</section>")

    cats = list(geopolitics.EQUIP_CATS)
    body = ('<div class="hint">دسته را انتخاب کن و «نمایش دسته» را بزن:</div>'
            + group(country_select("cat", cats, cats[0]), [("📦 نمایش دسته", "show-cat")]))
    if chosen:
        cat, items = chosen
        rows = []
        for e in items:
            rows.append('<details class="itemrow"><summary><b>%s</b> \u2014 \u0633\u0627\u0632\u0646\u062f\u0647: %s | \u0642\u06cc\u0645\u062a: %s | \u0646\u0638\u0627\u0645\u06cc +%s </summary>'
                        '<form class="ib" method="post" action="/">'
                        '<input type="hidden" name="cat" value="%s">'
                        '<input type="hidden" name="item" value="%s">'
                        '<input type="text" name="qty" value="1" style="width:50px">'
                        '<button type="submit" name="cmd" value="act buy">\u062e\u0631\u06cc\u062f</button></form></details>'
                        % (esc(e["n"]), esc(e["mk"]), esc(e["pr"]), esc(e["m"]), esc(cat), esc(e["n"])))
        body += '<details style="margin-top:8px"><summary><b>\U0001f9fe \u0644\u06cc\u0633\u062a %s \u0622\u06cc\u062a\u0645 (%s)</b> \u2014 \u0628\u0627\u0632/\u0628\u0633\u062a\u0647 \u06a9\u0646\u062f</summary>%s</details>' % (len(items), esc(cat), "".join(rows))
    sections.append('<section><h2>🛒 بازار جهانی تجهیزات</h2>' + body + "</section>")

    body_stmt = ('<div class="hint">\u0628\u06cc\u0627\u0646\u06cc\u0647 \u0631\u0633\u0645\u06cc \u0645\u0646\u062a\u0634\u0631 \u06a9\u0646 \u2014 \u062f\u0631 \u06af\u0632\u0627\u0631\u0634 \u0628\u0627\u0632\u06cc \u0648 \u062f\u0627\u0634\u0628\u0648\u0631\u062f \u062b\u0628\u062a \u0645\u06cc\u200c\u0634\u0648\u062f:</div>'
                 '<form method="post" action="/">'
                 '<input type="text" name="statement" style="width:70%%" placeholder="\u0645\u062a\u0646 \u0628\u06cc\u0627\u0646\u06cc\u0647...">'
                 '<button type="submit" name="cmd" value="statement">\U0001f4e2 \u0627\u0646\u062a\u0634\u0627\u0631 \u0628\u06cc\u0627\u0646\u06cc\u0647</button></form>')
    if has and s is not None:
        stmts = s.get("statements") or []
        if stmts:
            body_stmt += '<div class="hint">\U0001f5e3 \u0622\u062e\u0631\u06cc\u0646 \u0628\u06cc\u0627\u0646\u06cc\u0647\u200c\u0647\u0627\u06cc \u06a9\u0634\u0648\u0631\u0647\u0627 \u0648 \u0631\u0647\u0628\u0631\u06cc:</div>'
            for stl in stmts[-8:]:
                body_stmt += '<div class="itemrow">\U0001f5e3 <b>%s</b>: %s</div>' % (esc(stl["who"]), esc(stl["text"]))
        else:
            body_stmt += '<div class="hint">\u0647\u0646\u0648\u0632 \u0628\u06cc\u0627\u0646\u06cc\u0647\u200c\u0627\u06cc \u0635\u0627\u062f\u0631 \u0646\u0634\u062f\u0647 \u0627\u0633\u062a.</div>'
    sections.append('<section><h2>\U0001f4e2 \u0628\u06cc\u0627\u0646\u06cc\u0647</h2>' + body_stmt + "</section>")

    orgs = (btn("📊 وضعیت نهادها", "dash org")
            + btn("🔍 شفافیت به آژانس", "act iaea", "big"))
    orgs += ('<div class="hint">مجمع عمومی ملل — کشور موردنظر:</div>'
             + group(country_select("target", countries), [("🗣 طرح محکومیت", "act un")]))
    if has and s is not None:
        orgs += '<div class="hint">حرارت آژانس: %s — محکومیت‌های ملل: %s</div>' % (
            esc(s.get("iaea_heat", 0)), esc(s.get("un_censures", 0)))
    sections.append('<section><h2>🌐 نهادهای بین‌المللی</h2>' + orgs + "</section>")

    body = group(country_select("target", countries), [("📄 باز کردن پرونده", "file")])
    sections.append('<section><h2>📁 پرونده کشور</h2>' + body + "</section>")

    if has:
        reset = ('<div class="hint">شروع از نو: کشور جدید را انتخاب کن و در کادر بنویس بله</div>'
                 '<form method="post" action="/">'
                 + country_select("reset_country", countries, "ایران")
                 + '<input type="text" name="reset_confirm" style="width:80px">'
                 + '<button type="submit" name="cmd" value="reset-game" class="big">بازی جدید (پاک شدن ذخیره!)</button>'
                 + "</form>")
        sections.append('<section><h2>♻ بازی جدید</h2>' + reset + "</section>")

    txt = out_text if out_text else "اول دکمه‌ای را بزن — نتیجه‌ی هر کار در همین کادر نمایش داده می‌شود."
    outbox = ('<div class="out"><div class="ttl">📰 گزارش بازی</div>'
              '<div class="txt">%s</div></div>' % esc(txt))

    page = ('<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="utf-8">'
            '<meta http-equiv="X-UA-Compatible" content="IE=edge">'
            "<title>ژئوپلیتیک: رقابت قدرت‌ها</title>"
            "<style>%s</style></head><body>"
            "<header><h1>⚔ ژئوپلیتیک: رقابت قدرت‌ها</h1><br>%s</header>"
            "%s%s%s"
            '<div class="footer">نسخه‌ی ایمیل ۵ — این صفحه کاملاً بدون جاوااسکریپت کار می‌کند؛ '
            "اگر این متن را می‌بینی یعنی نسخه‌ی درست داری.</div>"
            "</body></html>") % (CSSL, chips, start, outbox, "".join(sections))
    return page


def run_cmd(argv):
    buf = _io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    err = ""
    ok = True
    try:
        geopolitics.main(argv)
    except SystemExit:
        pass
    except Exception as e:
        ok = False
        err = type(e).__name__ + ": " + str(e)
    finally:
        sys.stdout = old
    text = buf.getvalue()
    if err:
        text += "\n⚠ " + err
    return text


def handle_post(form):
    get = lambda k, d="": form.get(k, [d])[0]
    cmd = get("cmd")
    target = get("target") or get("war_target") or get("reset_country")
    out = ""
    chosen = None
    if not cmd:
        return out, chosen
    if cmd == "statement":
        text = get("statement").strip()
        if not text:
            out = "\u26a0 \u0645\u062a\u0646 \u0628\u06cc\u0627\u0646\u06cc\u0647 \u062e\u0627\u0644\u06cc \u0628\u0648\u062f."
        else:
            out = run_cmd(["statement"] + text.split())
    elif cmd == "start":
        out = run_cmd(["init", get("start_country", "ایران")])
    elif cmd == "file":
        out = run_cmd(["status", target or "ایران"])
    elif cmd == "show-cat":
        cat = get("cat")
        chosen = (cat, geopolitics.EQUIPMENT.get(cat, []))
    elif cmd == "act buy":
        qty = get("qty", "1")
        item = get("item")
        if not item:
            out = "⚠ تجهیزی انتخاب نشده بود."
        else:
            out = run_cmd(["act", "buy", item, str(qty) if qty else "1"])
    elif cmd == "reset-game":
        if get("reset_confirm") == "بله":
            out = run_cmd(["reset", get("reset_country", "ایران")])
        else:
            out = "⚠ برای پاک شدن ذخیره باید در کادر، کلمه‌ی «بله» را بنویسی."
    else:
        argv = cmd.split()
        acted = ["mil", "tech", "nuke", "iaea", "eco", "propaganda"]
        if len(argv) >= 2 and argv[0] == "act":
            if target:
                argv.append(target)
            elif argv[1] not in acted:
                return ("⚠ اول کشور را از منوی کشویی همان بخش انتخاب کن.", None)
        out = run_cmd(argv)
    return out, chosen


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, ctype, data):
        body = data.encode("utf-8") if isinstance(data, str) else data
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._send(200, "text/html; charset=utf-8", render())

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
            form = parse_qs(self.rfile.read(n).decode("utf-8") or "")
            out, chosen = handle_post(form)
        except Exception as e:
            out, chosen = "⚠ خطا: " + str(e), None
        try:
            self._send(200, "text/html; charset=utf-8", render(out, chosen))
        except Exception:
            pass

    def log_message(self, fmt, *args):
        pass


def main():
    server = HTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    url = "http://127.0.0.1:%d" % port
    print("Server running on " + url + " (this window stays open; close it to stop the game)", flush=True)
    if os.name == "nt":
        try:
            os.startfile(url)
        except Exception:
            webbrowser.open(url)
    else:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    print("Server stopped.")


if __name__ == "__main__":
    main()
