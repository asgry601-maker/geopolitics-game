#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""نسخه‌ی مرورگری بازی — فقط روی 127.0.0.1؛ بدون هیچ وابستگی خارجی."""
import io
import json
import os
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import geopolitics


def api_state():
    out = {
        "has_save": os.path.exists(geopolitics.STATE),
        "countries": list(geopolitics.COUNTRIES.keys()),
        "cats": list(geopolitics.EQUIP_CATS),
    }
    if out["has_save"]:
        s = geopolitics.load()
        P = s["player"]
        me = s["world"][P]
        out.update({
            "player": P,
            "year": s.get("year"),
            "day": s.get("day"),
            "money": round(me.get("money", 0)),
            "mil": round(me.get("mil", 0)),
            "eco": round(me.get("eco", 0)),
            "tech": round(me.get("tech", 0)),
            "stab": round(me.get("stab", 0)),
            "nukes": me.get("nukes", 0),
            "censures": s.get("un_censures", 0),
            "heat": s.get("iaea_heat", 0),
            "arsenal": s.get("arsenal", {}).get(P, {}),
            "equipment": geopolitics.EQUIPMENT,
        })
    return out


def run_cmd(parts):
    parts = [str(x) for x in parts]
    if not parts:
        return {"ok": False, "text": "", "err": "دستور خالی", "state": api_state()}
    if parts[0] in ("play", "بازی"):
        return {"ok": False, "text": "", "err": "این نسخه مرورگری است؛ نیازی به play نیست.", "state": api_state()}
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    err = ""
    ok = True
    try:
        geopolitics.main(parts)
    except SystemExit:
        pass
    except Exception as e:
        ok = False
        err = type(e).__name__ + ": " + str(e)
    finally:
        sys.stdout = old
    log = getattr(geopolitics, "LOG", None)
    return {"ok": ok, "text": buf.getvalue(), "err": err, "state": api_state()}


PAGE = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<title>ژئوپلیتیک: رقابت قدرت‌ها</title>
<style>
  *{box-sizing:border-box}
  body{margin:0;font-family:Tahoma,'Segoe UI',sans-serif;background:#0d1521;color:#dfe8f2}
  header{background:linear-gradient(135deg,#132a43,#0d1521);border-bottom:2px solid #2b4d77;padding:12px 18px;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
  header h1{font-size:19px;margin:0 0 0 18px;color:#7fc4ff}
  .chip{background:#16283f;border:1px solid #2b4d77;border-radius:14px;padding:4px 12px;font-size:12px}
  .chip b{color:#ffd54f}
  nav{display:flex;flex-wrap:wrap;gap:6px;padding:10px 18px;background:#0a1017;border-bottom:1px solid #1d2f4a}
  nav button{background:#132a43;color:#bcd7f0;border:1px solid #2b4d77;border-radius:8px;padding:8px 14px;font-family:inherit;font-size:13px;cursor:pointer}
  nav button:hover{background:#1d3d5f;color:#fff}
  main{display:flex;gap:14px;padding:14px 18px;align-items:flex-start}
  #panel{flex:1.2;background:#101b2b;border:1px solid #1d2f4a;border-radius:10px;padding:12px;min-height:300px}
  #panel h3{margin:4px 0 10px;color:#7fc4ff;font-size:15px}
  .actions{display:flex;flex-wrap:wrap;gap:8px}
  .actions button{background:#17350f;color:#c8f0b0;border:1px solid #3a6b28;border-radius:8px;padding:9px 14px;font-family:inherit;font-size:13px;cursor:pointer}
  .actions button:hover{background:#235017}
  .actions button.warn{background:#3a1b0f;border-color:#7c3a1d;color:#ffc9a3}
  .actions button.warn:hover{background:#542613}
  .rowline{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:10px 0}
  select,input[type=number],input[type=text]{background:#0d1725;color:#dfe8f2;border:1px solid #2b4d77;border-radius:8px;padding:8px;font-family:inherit;font-size:13px;min-width:180px}
  #outwrap{flex:1;background:#0a1017;border:1px solid #1d2f4a;border-radius:10px;padding:0;position:relative;min-height:300px;max-width:640px}
  #outwrap .ttl{padding:8px 14px;border-bottom:1px solid #1d2f4a;color:#7fc4ff;font-size:13px}
  #out{white-space:pre-wrap;padding:12px 14px;font-family:Tahoma;font-size:13.5px;line-height:1.9;max-height:70vh;overflow:auto;margin:0}
  small.hint{color:#8aa5c4}
  .itemrow{display:flex;flex-wrap:wrap;gap:6px;align-items:center;border-bottom:1px dashed #1d2f4a;padding:6px 0;font-size:12.5px}
  .itemrow b{color:#ffd54f}
  .itemrow button{background:#17350f;color:#c8f0b0;border:1px solid #3a6b28;border-radius:6px;padding:3px 10px;cursor:pointer;font-family:inherit}
  .load{color:#ffd54f;font-size:13px}
</style>
</head>
<body>
<header>
  <h1>⚔ ژئوپلیتیک: رقابت قدرت‌ها</h1>
  <div class="chip">کشور: <b id="h_player">—</b></div>
  <div class="chip">سال <b id="h_year">—</b> / روز <b id="h_day">—</b></div>
  <div class="chip">💰 خزانه: <b id="h_money">—</b></div>
  <div class="chip">🎖 نظامی: <b id="h_mil">—</b></div>
  <div class="chip">🏭 اقتصاد: <b id="h_eco">—</b></div>
  <div class="chip">🔬 فناوری: <b id="h_tech">—</b></div>
  <div class="chip">🕊 ثبات: <b id="h_stab">—</b></div>
  <div class="chip">☢ کلاهک: <b id="h_nukes">—</b></div>
</header>
<nav id="tabs"></nav>
<main>
  <div id="panel"><h3>در حال آماده‌سازی…</h3></div>
  <div id="outwrap"><div class="ttl">📰 متن بازی</div><div id="out">صدایم کن…</div></div>
</main>
<script>
var S = {countries:[], has_save:false};
function $(x){return document.getElementById(x)}
function show(t){var o=$('out');o.textContent=t;o.scrollTop=0;}
async function cmd(parts, silent){
  show('...در حال اجرا');
  var r = await fetch('/api/cmd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({cmd:parts})});
  var j = await r.json();
  S = j.state;
  header();
  show((j.text||'') + (j.err?('\n⚠ '+j.err):''));
  if(!silent) tab(current);
  return j;
}
function header(){
  if(!S.has_save){ $('h_player').textContent='بازی شروع نشده'; return; }
  $('h_player').textContent=S.player; $('h_year').textContent=S.year; $('h_day').textContent=S.day;
  $('h_money').textContent=S.money; $('h_mil').textContent=S.mil; $('h_eco').textContent=S.eco;
  $('h_tech').textContent=S.tech; $('h_stab').textContent=S.stab; $('h_nukes').textContent=S.nukes;
}
var TABS = [
 ['🏠 خانه', function(p){
    p.innerHTML='<h3>مرکز فرماندهی</h3>';
    grid(p,[['📋 وضعیت من',['status']],['📚 راهنما',['help']],['🏆 رتبه‌بندی جهانی',['rank']],['🌆 فهرست ۱۷۴ کشور',['list']]]);
    sep(p);
    row(p); // end of day button
 }],
 ['📊 داشبورد', function(p){ p.innerHTML='<h3>داشبوردهای شش‌گانه</h3>';
    grid(p,[['🏛 سیاست داخلی',['dash','dom']],['🌍 دیپلماسی',['dash','dip']],['🕵 عملیات',['dash','ops']],['🛡 نظامی',['dash','mil']],['💹 اقتصاد',['dash','eco']],['🌐 نهادها',['dash','org']]]); }],
 ['🤝 دیپلماسی', function(p){ p.innerHTML='<h3>دیپلماسی — کشور را انتخاب کن</h3>'; picker(p);
    grid(p,[['💵 کمک اقتصادی',['act','aide']],['🛒 قرارداد تجاری',['act','trade']],['🕊 پیمان عدم تعارض',['act','pact']],['⚔ اتحاد نظامی',['act','ally']],['🚫 تحریم',['act','sanc']],['🗣 محکومیت در ملل',['act','un']]], true);
    sep(p); grid(p,[['✂ فسخ پیمان',['act','break']]], true); }],
 ['🛡 ارتش و هسته‌ای', function(p){ p.innerHTML='<h3>ارتش و برنامه هسته‌ای</h3>';
    grid(p,[['📈 بودجه نظامی',['act','mil']],['🧪 پروژه فناوری',['act','tech']],['☢ کلاهک هسته‌ای',['act','nuke']],['🔍 شفافیت به آژانس',['act','iaea']]]);
    sep(p); picker(p); grid(p,[['⚔ اعلام جنگ',['act','war']]], true); }],
 ['🕵 عملیات پنهان', function(p){ p.innerHTML='<h3>عملیات پنهان — هدف را انتخاب کن</h3>'; picker(p);
    grid(p,[['🔑 جاسوسی',['act','spy']],['💥 بی‌ثبات‌سازی',['act','covert']],['🧨 خرابکاری',['act','sabotage']],['🎯 ترور',['act','kill']],['🕸 شبکه نیابتی',['act','proxy']]], true); }],
 ['💰 اقتصاد', function(p){ p.innerHTML='<h3>اقتصاد</h3>';
    grid(p,[['🏭 سرمایه‌گذاری کلان',['act','eco']],['📣 کمپین تبلیغاتی',['act','propaganda']]]); }],
 ['🛒 بازار تجهیزات', function(p){ market(p); }],
 ['🌐 نهادها', function(p){ p.innerHTML='<h3>نهادهای بین‌المللی</h3>';
    grid(p,[['📊 وضعیت نهادها',['dash','org']],['🔍 شفافیت به آژانس',['act','iaea']]]);
    sep(p); picker(p);
    grid(p,[['🗣 طرح محکومیت در مجمع',['act','un']]], true);
    if(S.has_save){ p.innerHTML += '<small class="hint">حرارت آژانس: '+S.heat+' / محکومیت‌های ملل: '+S.censures+'</small>'; } }],
 ['📁 پرونده کشور', function(p){ p.innerHTML='<h3>پرونده هر کشور — انتخاب کن</h3>'; picker(p);
    var b=document.createElement('button');b.textContent='افتح پرونده';b.className='';b.onclick=function(){cmd(['status',sel()]);};
    var g=p.querySelector('.actions')||document.createElement('div');g.className='actions';g.appendChild(b);p.appendChild(g); }],
];
var current = 0, lastPick = '';
function sel(){ return lastPick || $('countrysel').value || $('countrysel').options[0].value; }
function picker(p){
  var d=document.createElement('div'); d.className='rowline';
  var s=document.createElement('select'); s.id='countrysel';
  (S.countries||[]).forEach(function(c){var o=document.createElement('option');o.value=c;o.textContent=c;s.appendChild(o);});
  var t=document.createElement('input'); t.type='text'; t.placeholder='یا اسم بنویس…'; t.style.minWidth='140px';
  t.oninput=function(){ if(t.value) lastPick=t.value; };
  s.onchange=function(){ lastPick=s.value; };
  d.appendChild(s); d.appendChild(t); p.appendChild(d);
}
function grid(p, items, warn){
  var g=document.createElement('div'); g.className='actions';
  items.forEach(function(it){
    var b=document.createElement('button'); b.textContent=it[0];
    if(warn) b.className='warn';
    b.onclick=function(){ var c=it[1].slice(); if(warn) c.push(sel()); cmd(c); };
    g.appendChild(b);
  });
  p.appendChild(g);
}
function sep(p){ var d=document.createElement('div'); d.style.height='14px'; p.appendChild(d); }
function row(p){
  var d=document.createElement('div'); d.className='rowline';
  var b=document.createElement('button'); b.textContent='🌙 پایان روز (زمان جلو می‌رود)';
  b.onclick=function(){ cmd(['end']); };
  d.appendChild(b); p.appendChild(d);
}
function market(p){
  p.innerHTML='<h3>بازار جهانی تجهیزات</h3>';
  if(!S.has_save){ p.innerHTML+='<small class="hint">اول بازی را شروع کن.</small>'; return; }
  var d=document.createElement('div'); d.className='rowline';
  var s=document.createElement('select');
  S.cats.forEach(function(c){var o=document.createElement('option');o.value=c;o.textContent=c;s.appendChild(o);});
  s.onchange=function(){listCat(s.value);};
  d.appendChild(s); p.appendChild(d);
  var list=document.createElement('div'); list.id='mlist'; p.appendChild(list);
  listCat(S.cats[0]); s.value=S.cats[0];
  function listCat(cat){
    list.innerHTML='';
    (S.equipment[cat]||[]).forEach(function(e){
      var r=document.createElement('div'); r.className='itemrow';
      r.innerHTML='<b>'+e.n+'</b> — سازنده: '+e.mk+' | قیمت: '+e.pr+' | نظامی +'+e.m;
      var q=document.createElement('input'); q.type='number'; q.value='1'; q.min='1'; q.style.width='70px';
      var b=document.createElement('button'); b.textContent='خرید';
      b.onclick=function(){ cmd(['act','buy',e.n,String(q.value||'1')]); };
      r.appendChild(q); r.appendChild(b); list.appendChild(r);
    });
  }
}
function tabs(){
  var n=$('tabs'); n.innerHTML='';
  TABS.forEach(function(t,i){
    var b=document.createElement('button'); b.textContent=t[0];
    b.onclick=function(){ current=i; tab(i); };
    n.appendChild(b);
  });
}
function tab(i){ var p=$('panel'); p.innerHTML=''; TABS[i][1](p); }
async function boot(){
  var r=await fetch('/api/state'); S=await r.json(); header(); tabs(); tab(0);
  if(!S.has_save){
    var p=$('panel'); p.innerHTML='<h3>🎮 شروع بازی جدید</h3><p style="font-size:13px">کشورت را انتخاب کن و شروع کن (Enter لازم نیست، دکمه بزن):</p>';
    picker(p); var b=document.createElement('button'); b.textContent='شروع!'; b.style.marginTop='8px';
    b.onclick=function(){ var c=sel(); cmd(['init',c]); };
    p.appendChild(b);
  } else { cmd(['status'], true); }
  if(!S.has_save) show('به بازی خوش آمدی! از پنل کناری کشور را انتخاب و «شروع!» را بزن.\n\nهیچ تایپی لازم نیست — همه‌چیز کلیکی است.');
}
boot();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, ctype, data):
        body = data if isinstance(data, bytes) else data.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, "text/html; charset=utf-8", PAGE)
        elif self.path == "/api/state":
            self._send(200, "application/json; charset=utf-8",
                       json.dumps(api_state(), ensure_ascii=False))
        else:
            self._send(404, "text/plain; charset=utf-8", "not found")

    def do_POST(self):
        if self.path != "/api/cmd":
            self._send(404, "text/plain; charset=utf-8", "not found")
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
            req = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
            res = run_cmd(req.get("cmd", []))
            self._send(200, "application/json; charset=utf-8",
                       json.dumps(res, ensure_ascii=False))
        except Exception as e:
            self._send(200, "application/json; charset=utf-8",
                       json.dumps({"ok": False, "text": "", "err": str(e),
                                   "state": api_state()}, ensure_ascii=False))

    def log_message(self, fmt, *args):
        pass


def main():
    server = HTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    url = "http://127.0.0.1:%d" % port
    print("Server running on " + url + " (this window stays open; close it to stop the game)")
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
