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
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<title>ژئوپلیتیک: رقابت قدرت‌ها</title>
<style>
  body{margin:0;font-family:Tahoma,'Segoe UI',sans-serif;background:#0d1521;color:#dfe8f2}
  header{background:#132a43;border-bottom:2px solid #2b4d77;padding:12px 18px}
  header h1{font-size:19px;margin:0 0 8px 0;color:#7fc4ff}
  .chip{display:inline-block;background:#16283f;border:1px solid #2b4d77;border-radius:14px;padding:4px 12px;font-size:12px;margin:2px}
  .chip b{color:#ffd54f}
  nav{padding:10px 14px;background:#0a1017;border-bottom:1px solid #1d2f4a}
  nav button{display:inline-block;background:#132a43;color:#bcd7f0;border:1px solid #2b4d77;border-radius:8px;padding:8px 14px;font-family:inherit;font-size:13px;cursor:pointer;margin:2px}
  nav button:hover{background:#1d3d5f;color:#fff}
  main{padding:14px 18px}
  #panel{background:#101b2b;border:1px solid #1d2f4a;border-radius:10px;padding:12px;margin-bottom:14px}
  #panel h3{margin:4px 0 10px;color:#7fc4ff;font-size:15px}
  .actions button{display:inline-block;background:#17350f;color:#c8f0b0;border:1px solid #3a6b28;border-radius:8px;padding:9px 14px;font-family:inherit;font-size:13px;cursor:pointer;margin:3px}
  .actions button:hover{background:#235017}
  .actions button.warn{background:#3a1b0f;border-color:#7c3a1d;color:#ffc9a3}
  .actions button.warn:hover{background:#542613}
  .rowline{margin:10px 0}
  select,input{background:#0d1725;color:#dfe8f2;border:1px solid #2b4d77;border-radius:8px;padding:8px;font-family:inherit;font-size:13px;margin:2px}
  #outwrap{background:#0a1017;border:1px solid #1d2f4a;border-radius:10px}
  #outwrap .ttl{padding:8px 14px;border-bottom:1px solid #1d2f4a;color:#7fc4ff;font-size:13px}
  #out{white-space:pre-wrap;padding:12px 14px;font-family:Tahoma;font-size:13.5px;line-height:1.9;min-height:220px;max-height:60vh;overflow:auto;margin:0}
  .hint{color:#8aa5c4;font-size:12px}
  .itemrow{display:block;border-bottom:1px dashed #1d2f4a;padding:6px 0;font-size:12.5px}
  .itemrow b{color:#ffd54f}
  .itemrow button{background:#17350f;color:#c8f0b0;border:1px solid #3a6b28;border-radius:6px;padding:3px 10px;cursor:pointer;font-family:inherit;margin-right:6px}
</style>
</head>
<body>
<header>
  <h1>⚔ ژئوپلیتیک: رقابت قدرت‌ها</h1><br>
  <span class="chip">کشور: <b id="h_player">—</b></span>
  <span class="chip">سال <b id="h_year">—</b> / روز <b id="h_day">—</b></span>
  <span class="chip">💰 خزانه: <b id="h_money">—</b></span>
  <span class="chip">🎖 نظامی: <b id="h_mil">—</b></span>
  <span class="chip">🏭 اقتصاد: <b id="h_eco">—</b></span>
  <span class="chip">🔬 فناوری: <b id="h_tech">—</b></span>
  <span class="chip">🕊 ثبات: <b id="h_stab">—</b></span>
  <span class="chip">☢ کلاهک: <b id="h_nukes">—</b></span>
</header>
<div id="tabs"></div>
<main>
  <div id="panel"><h3>در حال آماده‌سازی…</h3></div>
  <div id="outwrap"><div class="ttl">📰 گزارش بازی</div><div id="out">اول از دکمه‌های بالای صفحه استفاده کن — نتیجه‌ی هر کار اینجا نمایش داده می‌شود.</div></div>
</main>
<script>
var S = {countries:[], has_save:false};
var current = 0, lastPick = "";
function $(x){return document.getElementById(x);}
function show(t){var o=$("out");o.textContent=t;o.scrollTop=0;}
function getState(cb){
  var x=new XMLHttpRequest();
  x.open("GET","/api/state",true);
  x.onreadystatechange=function(){
    if(x.readyState!==4)return;
    try{S=JSON.parse(x.responseText);}catch(e){}
    cb();
  };
  x.send();
}
function apiPost(parts,cb){
  show("…در حال اجرا");
  var x=new XMLHttpRequest();
  x.open("POST","/api/cmd",true);
  x.setRequestHeader("Content-Type","application/json; charset=UTF-8");
  x.onreadystatechange=function(){
    if(x.readyState!==4)return;
    var j=null;
    try{j=JSON.parse(x.responseText);}catch(e){}
    if(j){S=j.state;header();if(cb)cb(j);}
    else{show("⚠ ارتباط با موتور بازی برقرار نشد. پنجره‌ی مشکی (cmd) را نبند و صفحه را با F5 رفرش کن.");}
  };
  x.send(JSON.stringify({cmd:parts}));
}
function runCmd(parts){
  apiPost(parts,function(j){
    show((j.text||"")+((j.err)?("\n⚠ "+j.err):""));
    tab(current);
  });
}
function header(){
  if(!S.has_save){$("h_player").textContent="بازی شروع نشده";return;}
  $("h_player").textContent=S.player;$("h_year").textContent=S.year;$("h_day").textContent=S.day;
  $("h_money").textContent=S.money;$("h_mil").textContent=S.mil;$("h_eco").textContent=S.eco;
  $("h_tech").textContent=S.tech;$("h_stab").textContent=S.stab;$("h_nukes").textContent=S.nukes;
}
function selField(){
  var s=$("countrysel");
  if(lastPick)return lastPick;
  if(!s)return "";
  if(s.selectedIndex>=0)return s.options[s.selectedIndex].value;
  return "";
}
function picker(p){
  var d=document.createElement("div"); d.className="rowline";
  var s=document.createElement("select"); s.id="countrysel";
  var cs=S.countries||[];
  for(var i=0;i<cs.length;i++){var o=document.createElement("option");o.value=cs[i];o.appendChild(document.createTextNode(cs[i]));s.appendChild(o);}
  s.onchange=function(){lastPick="";};
  var t=document.createElement("input"); t.type="text"; t.placeholder="یا اسم کشور…"; t.style.width="150px";
  t.onkeyup=function(){lastPick=t.value;};
  d.appendChild(s); d.appendChild(t); p.appendChild(d);
}
function grid(p, items, needCountry){
  var g=document.createElement("div"); g.className="actions";
  for(var i=0;i<items.length;i++){
    (function(it){
      var b=document.createElement("button"); b.appendChild(document.createTextNode(it[0]));
      if(needCountry)b.className="warn";
      b.onclick=function(){
        var c=it[1].slice(0);
        if(needCountry){var t=selField();if(!t){show("⚠ اول کشور را از منوی کشویی انتخاب کن.");return;}c.push(t);}
        runCmd(c);
      };
      g.appendChild(b);
    })(items[i]);
  }
  p.appendChild(g);
}
function sep(p){var d=document.createElement("div");d.style.height="14px";p.appendChild(d);}
function rowEnd(p){
  var d=document.createElement("div"); d.className="rowline";
  var b=document.createElement("button"); b.appendChild(document.createTextNode("🌙 پایان روز (زمان جلو می‌رود)"));
  b.onclick=function(){runCmd(["end"]);};
  d.appendChild(b); p.appendChild(d);
}
function market(p){
  p.appendChild(h3("🛒 بازار جهانی تجهیزات"));
  if(!S.has_save){hint(p,"اول بازی را شروع کن.");return;}
  var d=document.createElement("div"); d.className="rowline";
  var s=document.createElement("select");
  var cats=S.cats||[];
  for(var i=0;i<cats.length;i++){var o=document.createElement("option");o.value=cats[i];o.appendChild(document.createTextNode(cats[i]));s.appendChild(o);}
  d.appendChild(s); p.appendChild(d);
  var list=document.createElement("div"); list.id="mlist"; p.appendChild(list);
  listCat(s.value);
  s.onchange=function(){listCat(s.options[s.selectedIndex].value);};
  function listCat(cat){
    while(list.firstChild)list.removeChild(list.firstChild);
    var items=(S.equipment&&S.equipment[cat])||[];
    for(var i=0;i<items.length;i++){
      (function(e){
        var r=document.createElement("div"); r.className="itemrow";
        var lab=document.createElement("b"); lab.appendChild(document.createTextNode(e.n));
        r.appendChild(lab);
        r.appendChild(document.createTextNode(" — سازنده: "+e.mk+" | قیمت: "+e.pr+" | نظامی +"+e.m+" | تعداد: "));
        var q=document.createElement("input"); q.type="text"; q.value="1"; q.style.width="50px";
        var b=document.createElement("button"); b.appendChild(document.createTextNode("خرید"));
        b.onclick=function(){
          var n=parseInt(q.value,10); if(!(n>0))n=1;
          runCmd(["act","buy",e.n,String(n)]);
        };
        r.appendChild(q); r.appendChild(b); list.appendChild(r);
      })(items[i]);
    }
  }
}
function h3(t){var h=document.createElement("h3");h.appendChild(document.createTextNode(t));return h;}
function hint(p,t){var s=document.createElement("div");s.className="hint";s.appendChild(document.createTextNode(t));p.appendChild(s);}
var TABS = [
 ["🏠 خانه",function(p){
    p.appendChild(h3("مرکز فرماندهی"));
    grid(p,[["📋 وضعیت من",["status"]],["📚 راهنما",["help"]],["🏆 رتبه‌بندی جهانی",["rank"]],["🌆 فهرست ۱۷۴ کشور",["list"]]]);
    sep(p); rowEnd(p);
 }],
 ["📊 داشبورد",function(p){ p.appendChild(h3("داشبوردهای شش‌گانه"));
    grid(p,[["🏛 سیاست داخلی",["dash","dom"]],["🌍 دیپلماسی",["dash","dip"]],["🕵 عملیات",["dash","ops"]],["🛡 نظامی",["dash","mil"]],["💹 اقتصاد",["dash","eco"]],["🌐 نهادها",["dash","org"]]]); }],
 ["🤝 دیپلماسی",function(p){ p.appendChild(h3("دیپلماسی — کشور را از منوی زیر انتخاب کن")); picker(p);
    grid(p,[["💵 کمک اقتصادی",["act","aide"]],["🛒 قرارداد تجاری",["act","trade"]],["🕊 پیمان عدم تعارض",["act","pact"]],["⚔ اتحاد نظامی",["act","ally"]],["🚫 تحریم",["act","sanc"]],["🗣 محکومیت در ملل",["act","un"]]], true);
    sep(p); grid(p,[["✂ فسخ پیمان",["act","break"]]], true); }],
 ["🛡 ارتش و هسته‌ای",function(p){ p.appendChild(h3("ارتش و برنامه هسته‌ای"));
    grid(p,[["📈 بودجه نظامی",["act","mil"]],["🧪 پروژه فناوری",["act","tech"]],["☢ ساخت کلاهک",["act","nuke"]]]);
    sep(p); p.appendChild(h3("بازرسان آژانس")); grid(p,[["🔍 اعلام شفافیت",["act","iaea"]]]);
    sep(p); p.appendChild(h3("جنگ — کشور را انتخاب کن")); picker(p);
    grid(p,[["⚔ اعلام جنگ",["act","war"]]], true); }],
 ["🕵 عملیات پنهان",function(p){ p.appendChild(h3("عملیات پنهان — هدف را انتخاب کن")); picker(p);
    grid(p,[["🔑 جاسوسی",["act","spy"]],["💥 بی‌ثبات‌سازی",["act","covert"]],["🧨 خرابکاری",["act","sabotage"]],["🎯 ترور",["act","kill"]],["🕸 شبکه نیابتی",["act","proxy"]]], true); }],
 ["💰 اقتصاد",function(p){ p.appendChild(h3("اقتصاد"));
    grid(p,[["🏭 سرمایه‌گذاری کلان",["act","eco"]],["📣 کمپین تبلیغاتی",["act","propaganda"]]]); }],
 ["🛒 بازار",function(p){ market(p); }],
 ["🌐 نهادها",function(p){ p.appendChild(h3("نهادهای بین‌المللی"));
    grid(p,[["📊 وضعیت نهادها",["dash","org"]],["🔍 شفافیت به آژانس",["act","iaea"]]]);
    sep(p); p.appendChild(h3("مجمع عمومی ملل")); picker(p);
    grid(p,[["🗣 طرح محکومیت علیه کشوری",["act","un"]]], true);
    if(S.has_save){hint(p,"حرارت آژانس: "+S.heat+" — محکومیت‌های ملل: "+S.censures);} }],
 ["📁 پرونده کشور",function(p){ p.appendChild(h3("پرونده هر کشور — انتخاب کن")); picker(p);
    grid(p,[["📄 باز کردن پرونده",["status"]]], true); }],
];
function tabs(){
  var n=$("tabs");
  while(n.firstChild)n.removeChild(n.firstChild);
  for(var i=0;i<TABS.length;i++){
    (function(t,i2){
      var b=document.createElement("button"); b.appendChild(document.createTextNode(t[0]));
      b.onclick=function(){current=i2;tab(i2);};
      n.appendChild(b);
    })(TABS[i],i);
  }
}
function tab(i){
  lastPick = "";
  var p=$("panel");
  while(p.firstChild)p.removeChild(p.firstChild);
  TABS[i][1](p);
}
function boot(){
  getState(function(){
    header(); tabs(); tab(0);
    if(!S.has_save){
      var p=$("panel");
      while(p.firstChild)p.removeChild(p.firstChild);
      p.appendChild(h3("🎮 شروع بازی جدید"));
      hint(p,"کشورت را انتخاب کن و دکمه‌ی شروع را بزن:");
      picker(p);
      var b=document.createElement("button"); b.appendChild(document.createTextNode("شروع!"));
      b.onclick=function(){var c=selField();if(!c){show("⚠ کشور را انتخاب کن.");return;}runCmd(["init",c]);};
      p.appendChild(b);
      show("به بازی خوش آمدی! از پانل بالا کشور را انتخاب و «شروع!» را بزن.\n\nهیچ تایپی لازم نیست — همه‌چیز کلیکی است.");
    }
  });
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
