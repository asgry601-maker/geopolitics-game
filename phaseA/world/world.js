/* فاز A — کره سه‌بعدی ژئوپولیتیک (three.js r126 + globe.gl 2.21.1 — فقط WebGL 1)
   محدود سخت‌افزار: antialias خاموش، pixelRatio ≤ 1.5، بافت پیش‌فرض سبک تیره */
'use strict';

/* ثبت سراسری خطاهای JS — نمایش علت واقعی به‌جای پیام خاموش (ES5) */
window.onerror = function (msg, src, line) {
  try {
    var d = document.getElementById('engineMsg');
    if (d) {
      d.style.display = 'block';
      d.textContent = 'خطای جاوااسکریپت: ' + String(msg) + ' — خط ' + line;
    }
  } catch (e) { /* محافظت */ }
};

/* ---------- حالت عمومی ---------- */
var MAP = null;       // fa -> {en, iso3, ne, lat, lon}
var FEATS = null;     // geojson features
var ST = null;        // آخرین /api/state
var MODE = 'geo';     // 'geo' | 'pol'
var SELECTED = null;  // نام فارسی کشور انتخابی
var TEX = 'img/earth-dark.jpg';
var ROT = true;
var globe = null;

/* ---------- رنگ‌ها ---------- */
var REGIONS = [
  'خاورمیانه و شمال آفریقا', 'اروپا', 'شرق آسیا', 'جنوب و جنوب\u200cشرق آسیا',
  'آفریقای جنوب صحرا', 'آمریکای شمالی', 'آمریکای لاتین و کارائیب',
  'اقیانوسیه', 'آسیای مرکزی و قفقاز'
];
var REGION_COLORS = {
  'خاورمیانه و شمال آفریقا': '#c98a4b',
  'اروپا': '#5a8fd4',
  'شرق آسیا': '#d45a7a',
  'جنوب و جنوب\u200cشرق آسیا': '#5ad4a2',
  'آفریقای جنوب صحرا': '#b9a13a',
  'آمریکای شمالی': '#7a5ad4',
  'آمریکای لاتین و کارائیب': '#4bb9c9',
  'اقیانوسیه': '#9c6bd6',
  'آسیای مرکزی و قفقاز': '#8fae4e'
};
var C_PLAYER = '#ffd166';      // کشور بازیکن
var C_ALLY = '#3fae6a';        // رابطه >= 40
var C_FRIEND = '#7fd08f';      // >= 10
var C_NEUTRAL = '#8d97a8';     // -10..10
var C_TENSE = '#d68f4b';       // <= -10
var C_ENEMY = '#c4453f';       // <= -40
var C_WAR = '#7a1420';         // جنگ با بازیکن
var C_ELIM = '#3c3f45';        // حذف‌شده
var C_ORPHAN = '#2b3038';      // بدون کشور در بازی
var C_SEL = '#ff9e2c';         // انتخاب‌شده

function polColor(fa) {
  if (!ST || !ST.countries) return C_NEUTRAL;
  var c = ST.countries[fa];
  if (!c) return C_ORPHAN;
  if (fa === ST.player) return C_PLAYER;
  if (ST.eliminated && ST.eliminated.indexOf(fa) >= 0) return C_ELIM;
  var inWar = false;
  for (var i = 0; i < (ST.wars || []).length; i++) {
    var w = ST.wars[i];
    if ((w[0] === fa && w[1] === ST.player) || (w[1] === fa && w[0] === ST.player)) inWar = true;
  }
  if (inWar) return C_WAR;
  var r = (c[8] == null ? 0 : c[8]);   /* فرم فشرده: اندیس 8 = رابطه با بازیکن */
  if (r >= 40) return C_ALLY;
  if (r >= 10) return C_FRIEND;
  if (r > -10) return C_NEUTRAL;
  if (r > -40) return C_TENSE;
  return C_ENEMY;
}

function geoColor(fa) {
  if (!ST || !ST.countries) return C_ORPHAN;
  var c = ST.countries[fa];
  if (!c) return C_ORPHAN;
  if (ST.eliminated && ST.eliminated.indexOf(fa) >= 0) return C_ELIM;
  var reg = (ST.regions && c[7] >= 0 && c[7] < ST.regions.length) ? ST.regions[c[7]] : '';
  return REGION_COLORS[reg] || '#6b7280';
}

function capColor(f) {
  if (f._fa == null) return C_ORPHAN;
  if (SELECTED && f._fa === SELECTED) return C_SEL;
  return (MODE === 'pol') ? polColor(f._fa) : geoColor(f._fa);
}

/* ---------- راه‌اندازی کره ---------- */
function initGlobe() {
  var el = document.getElementById('globe');
  globe = Globe({ animateIn: true })(el)
    .backgroundColor('rgba(0,0,0,0)')
    .globeImageUrl(TEX)
    .showAtmosphere(true)
    .atmosphereColor('#3a77d0')
    .atmosphereAltitude(0.16)
    .polygonsData([])
    .polygonCapColor(capColor)
    .polygonSideColor(function () { return 'rgba(20,28,45,0.85)'; })
    .polygonStrokeColor(function () { return '#0a0f1a'; })
    .polygonAltitude(function (f) {
      return (SELECTED && f._fa === SELECTED) ? 0.055 : 0.012;
    })
    .onPolygonClick(function (f) {
      if (PROV.taken && (Date.now() - PROV.taken) < 350) return;   /* کلیک متعلق به استان بود */
      if (f._fa == null) { flash('این سرزمین در بازی حضور ندارد.'); return; }
      selectCountry(f._fa);
    })
    .labelsData([])
    .labelLat(function (d) { return d.lat; })
    .labelLng(function (d) { return d.lon; })
    .labelText(function (d) { return d.en; })
    .labelSize(function (d) { return d.kind === 'prov' ? 0.32 : 0.45; })
    .labelDotRadius(function (d) { return d.kind === 'country' && d.point ? 0.28 : 0; })
    .labelColor(function (d) {
      if (d.kind === 'prov') return (PROV.sel === d.f) ? '#ffb347' : '#8ff0e5';
      return (d.fa === SELECTED) ? '#ffd166' : '#e8eef8';
    })
    .labelAltitude(function (d) { return d.kind === 'prov' ? 0.018 : 0.012; })
    .labelsTransitionDuration(0)
    .onLabelClick(function (d) {
      if (d.kind === 'prov') { PROV.taken = Date.now(); provSelect(d.f); }
      else { selectCountry(d.fa); }
    });

  var ctrl = globe.controls();
  ctrl.autoRotate = ROT;
  ctrl.autoRotateSpeed = 0.35;
  ctrl.minDistance = 140;
  ctrl.maxDistance = 500;
  globe.pointOfView({ lat: 27, lng: 48, altitude: 2.3 }, 0);
  globe.width(el.clientWidth);
  globe.height(el.clientHeight);
  window.addEventListener('resize', function () {
    globe.width(el.clientWidth);
    globe.height(el.clientHeight);
  });
}

function refreshPolygons() {
  if (!globe || !FEATS) return;
  globe.polygonsData(FEATS.slice());
  refreshLabels();
}
var LBL_COUNTRY = null, LBL_ALL = [], LBL_SIG = '', LBL_CACHE = {};
var PROV_LABELS_ENABLED = true;
function labelsList() {
  if (LBL_COUNTRY) return LBL_COUNTRY;
  var out = [];
  if (!MAP) return out;
  for (var fa in MAP) if (Object.prototype.hasOwnProperty.call(MAP, fa)) {
    var m = MAP[fa];
    out.push({ kind: 'country', fa: fa, en: m.en || fa, lat: m.lat, lon: m.lon, point: !m.ne });
  }
  LBL_COUNTRY = out;
  return out;
}
function refreshLabels() {
  if (!globe || !MAP) return;
  var countries = labelsList(), provinces = [];
  if (PROV_LABELS_ENABLED && PROV.on && PROV.iso && PROV.cache[PROV.iso]) provinces = provLabelsFor(PROV.iso);
  var sig = (PROV_LABELS_ENABLED && PROV.on ? (PROV.iso || '') : '') + ':' + provinces.length;
  if (sig === LBL_SIG && LBL_ALL.length === countries.length + provinces.length) return;
  LBL_SIG = sig; LBL_ALL = countries.concat(provinces); globe.labelsData(LBL_ALL);
}
function provRingCentroid(ring) {
  if (!ring || ring.length < 4) return null;
  var a2=0,cx=0,cy=0;
  for(var i=0;i<ring.length-1;i++){var j=i+1,x=ring[i][0],y=ring[i][1],xx=ring[j][0],yy=ring[j][1],cr=x*yy-xx*y;a2+=cr;cx+=(x+xx)*cr;cy+=(y+yy)*cr;}
  if(Math.abs(a2)<1e-10)return null;
  return {lon:cx/(3*a2),lat:cy/(3*a2),area:Math.abs(a2)/2};
}
function provLabelPoint(feature) {
  var g=feature&&feature.geometry;if(!g||!g.coordinates)return null;
  var polys=g.type==='Polygon'?[g.coordinates]:(g.type==='MultiPolygon'?g.coordinates:[]);
  var best=null,bestArea=-1;
  for(var p=0;p<polys.length;p++){var ring=polys[p]&&polys[p][0],c=provRingCentroid(ring);if(c&&c.area>bestArea){best=c;bestArea=c.area;}}
  if(!best)return null;
  if(!provHit(best.lat,best.lon,feature)){
    var coords=polys[0]&&polys[0][0],lat=0,lon=0,count=0;if(!coords||!coords.length)return null;
    for(var k=0;k<coords.length-1;k++){lon+=coords[k][0];lat+=coords[k][1];count++;}
    if(!count)return null;best={lon:lon/count,lat:lat/count};
    if(!provHit(best.lat,best.lon,feature)){
      var minLon=Infinity,maxLon=-Infinity,minLat=Infinity,maxLat=-Infinity;
      for(var q=0;q<coords.length;q++){minLon=Math.min(minLon,coords[q][0]);maxLon=Math.max(maxLon,coords[q][0]);minLat=Math.min(minLat,coords[q][1]);maxLat=Math.max(maxLat,coords[q][1]);}
      best={lon:(minLon+maxLon)/2,lat:(minLat+maxLat)/2};if(!provHit(best.lat,best.lon,feature))return null;
    }
  }
  return best;
}
function provLabelsFor(iso) {
  if(LBL_CACHE[iso])return LBL_CACHE[iso];
  var fs=(PROV.cache[iso]&&PROV.cache[iso].features)||[],candidates=[];
  for(var i=0;i<fs.length;i++){var f=fs[i],pp=(f&&f.properties)||{},pt=provLabelPoint(f),nm=pp.name_en||pp.name||pp.id;if(pt&&nm)candidates.push({f:f,en:String(nm),lat:pt.lat,lon:pt.lon,area:pt.area||0});}
  candidates.sort(function(a,b){return b.area-a.area;});
  var out=[],minSep=0.35,maxLabels=90;
  for(var c=0;c<candidates.length&&out.length<maxLabels;c++){
    var d=candidates[c],keep=true;
    for(var j=0;j<out.length;j++){var r1=d.lat*Math.PI/180,r2=out[j].lat*Math.PI/180,dl=(d.lon-out[j].lon)*Math.PI/180,dp=r1-r2,a=Math.sin(dp/2)*Math.sin(dp/2)+Math.cos(r1)*Math.cos(r2)*Math.sin(dl/2)*Math.sin(dl/2),dist=2*Math.atan2(Math.sqrt(a),Math.sqrt(Math.max(0,1-a)))*180/Math.PI;if(dist<minSep){keep=false;break;}}
    if(keep)out.push({kind:'prov',fa:SELECTED,iso3:iso,en:d.en,lat:d.lat,lon:d.lon,point:false,f:d.f});
  }
  LBL_CACHE[iso]=out;return out;
}

/* ---------- شبکه ---------- */
function getJSON(url, cb, errCb) {
  var x = new XMLHttpRequest();
  x.open('GET', url, true);
  x.onreadystatechange = function () {
    if (x.readyState !== 4) return;
    try {
      if (x.status >= 200 && x.status < 300) cb(JSON.parse(x.responseText));
      else if (errCb) errCb(x.status, x.responseText);
    } catch (e) { if (errCb) errCb(e && e.message ? e.message : String(e), null); }
  };
  x.send();
}

function postJSON(url, obj, cb, errCb) {
  var x = new XMLHttpRequest();
  x.open('POST', url, true);
  x.setRequestHeader('Content-Type', 'application/json');
  x.onreadystatechange = function () {
    if (x.readyState !== 4) return;
    try {
      if (x.status >= 200 && x.status < 300) cb(JSON.parse(x.responseText));
      else if (errCb) errCb(x.status, x.responseText);
    } catch (e) { if (errCb) errCb(e && e.message ? e.message : String(e), null); }
  };
  x.send(JSON.stringify(obj));
}

/* ---------- پیام خطای دقیق شبکه/سرور ---------- */
function netErrMsg(status, text) {
  if (text) {
    try {
      var r = JSON.parse(text);
      if (r && r.error) return '\u062e\u0637\u0627: ' + r.error;
    } catch (e) { /* پاسخ JSON نبود */ }
  }
  if (status && status > 0) return '\u062e\u0637\u0627\u06cc \u0633\u0631\u0648\u0631 (\u06a9\u062f ' + status + ')';
  return '\u0627\u0631\u062a\u0628\u0627\u0637 \u0628\u0627 \u0633\u0631\u0648\u0631 \u0628\u0631\u0642\u0631\u0627\u0631 \u0646\u0634\u062f (\u0627\u062d\u062a\u0645\u0627\u0644\u0627\u064b \u0633\u0631\u0648\u0631 \u0627\u062c\u0631\u0627 \u0646\u06cc\u0633\u062a \u06cc\u0627 \u067e\u0627\u0633\u062e \u0642\u0637\u0639 \u0634\u062f)';
}

/* ---------- بارگذاری داده ---------- */
function boot() {
  initGlobe();
  startFps();
  getJSON('data/country_map.json', function (m) {
    MAP = m;
    getJSON('data/countries.geojson', function (gj) {
      FEATS = gj.features;
      var neToFa = {};
      for (var fa in MAP) {
        if (MAP[fa].ne) neToFa[MAP[fa].ne] = fa;
      }
      for (var i = 0; i < FEATS.length; i++) {
        FEATS[i]._fa = neToFa[FEATS[i].properties.ADMIN] || null;
      }
      refreshPolygons();
      loadState();
    }, function () { flash('خطا: countries.geojson بارگذاری نشد.'); });
  }, function () { flash('خطا: country_map.json بارگذاری نشد.'); });
}

function loadState(after) {
  getJSON('api/state', function (s) {
    ST = (s && s.exists) ? s : null;
    renderWorldChips();
    renderStartWidget();
    refreshPolygons();
    if (ST && SELECTED) selectCountry(SELECTED, true);
    if (after) after();
  }, function (st, tx) { flash(netErrMsg(st, tx) + ' — وضعیت بازی دریافت نشد.'); });
}

/* ---------- پنل‌ها ---------- */
function el(id) { return document.getElementById(id); }

function flash(text) {
  var d = el('engineMsg');
  d.style.display = 'block';
  d.textContent = text;
}

/* ---------- پنل کشویی سمت راست (ES5) ---------- */
var PANEL_CLS = 'closed';

function panelIsClosed() {
  var pnl = el('panel');
  return !!pnl && (' ' + (pnl.className || '') + ' ').indexOf(' ' + PANEL_CLS + ' ') >= 0;
}

/* پس از تغییر عرض پنل، ابعاد کره تازه می‌شود (فضای بیشتر برای کره هنگام بسته بودن) */
function syncGlobeSize() {
  if (!globe) return;
  try {
    var a = el('mapArea');
    globe.width(a.clientWidth); globe.height(a.clientHeight);
  } catch (e) { /* محافظت */ }
}

/* باز/بسته کردن پنل + فلش جهت حرکت بعدی — انیمیشن فقط با CSS (سبک) */
function setPanel(open) {
  var pnl = el('panel'), b = el('panelToggle');
  if (!pnl) return;
  pnl.className = open ? '' : PANEL_CLS;
  if (b) {
    b.className = open ? '' : PANEL_CLS;
    b.textContent = open ? '\u276f' : '\u276e';
  }
  syncGlobeSize();
  setTimeout(syncGlobeSize, 340);   /* پس از پایان انیمیشن 0.3 ثانیه‌ای */
}

function openPanel() { setPanel(true); }
function togglePanel() { setPanel(panelIsClosed()); }

function barHtml(label, v, cls) {
  var w = Math.max(0, Math.min(100, v));
  return '<div class="row"><span class="muted">' + label + '</span><span>' + v.toFixed(1) + '</span></div>' +
    '<div class="bar ' + (cls || '') + '"><div style="width:' + w + '%"></div></div>';
}

function renderWorldChips() {
  var box = el('worldChips');
  if (!ST) { box.innerHTML = '<span class="muted">بازی\u200cای در جریان نیست.</span>'; return; }
  var wars = ST.wars.filter(function (w) {
    return w[0] === ST.player || w[1] === ST.player;
  }).length;
  box.innerHTML =
    '<span class="badge">🏳 ' + ST.player + '</span>' +
    '<span class="badge">📅 سال ' + ST.year + ' — دور ' + ST.turn + ' — روز ' + ST.day + '</span>' +
    '<span class="badge">⚡ AP ' + ST.ap + '</span>' +
    '<span class="badge">🤝 متحدان: ' + ST.allies.length + '</span>' +
    '<span class="badge">⚔ جنگ‌های شما: ' + wars + '</span>' +
    '<span class="badge">☢ گرمای آژانس: ' + ST.iaea_heat + '/3</span>' +
    '<span class="badge">🕊 تحریم شورای امنیت: ' + ST.un_censures + '</span>' +
    (ST.over ? '<span class="badge" style="color:#ffd166">🏁 بازی تمام شد</span>' : '');
}

function renderStartWidget() {
  var banner = el('banner');
  banner.style.display = 'block';   /* همیشه نمایان: هم شروع اول، هم شروع بازی جدید */
  var sel = el('startCountry');
  if (sel.options.length === 0 && MAP) {
    var names = Object.keys(MAP);
    names.sort(function (a, b) { return a.localeCompare(b, 'fa'); });
    for (var i = 0; i < names.length; i++) {
      var o = document.createElement('option');
      o.value = names[i];
      o.textContent = names[i];
      sel.appendChild(o);
    }
  }
  if (SELECTED && MAP && MAP[SELECTED]) sel.value = SELECTED;  /* سینک با انتخاب نقشه */
  /* اتصال دوطرفه: تغییر فهرست راست ← انتخاب روی نقشه + پنل */
  sel.onchange = function () { if (this.value) selectCountry(this.value); };
  /* توضیح بنر بسته به وضعیت بازی */
  var note = banner.querySelector('p');
  if (note) {
    if (ST) {
      note.textContent = '\u26a0\ufe0f \u0628\u0627\u0632\u06cc \u00ab' + ST.player +
        '\u00bb \u062f\u0631 \u062c\u0631\u06cc\u0627\u0646 \u0627\u0633\u062a. '
        + '\u0628\u0627\u0631\u0627\u06cc \u0634\u0631\u0648\u0639 \u0628\u0627\u0632\u06cc \u062c\u062f\u06cc\u062f\u060c \u06a9\u0634\u0648\u0631 \u0631\u0627 \u0627\u0646\u062a\u062e\u0627\u0628 \u06a9\u0646\u061b '
        + '\u067e\u06cc\u0634 \u0627\u0632 \u062d\u0630\u0641\u060c \u067e\u0634\u062a\u06cc\u0628\u0627\u0646\u06cc \u0627\u0632 \u0630\u062e\u06cc\u0631\u0647 \u0641\u0639\u0644\u06cc \u06af\u0631\u0641\u062a\u0647 \u0645\u06cc\u200c\u0634\u0648\u062f (game_state.json.bak).';
    } else {
      note.textContent = '\u0628\u0627\u0632\u06cc\u200c\u0627\u06cc \u062f\u0631 \u062c\u0631\u06cc\u0627\u0646 \u0646\u06cc\u0633\u062a. \u06a9\u0634\u0648\u0631 \u062e\u0648\u062f \u0631\u0627 \u0627\u0646\u062a\u062e\u0627\u0628 \u0648 \u0628\u0627\u0632\u06cc \u0631\u0627 \u0622\u063a\u0627\u0632 \u06a9\u0646.';
    }
  }
}

function selectCountry(fa, silent) {
  SELECTED = fa;
  provOnCountryChange();   /* B2: مرز استان‌های کشور جدید؛ playerCountry مستقل می‌ماند */
  openPanel();   /* کلیک کشور → پنل کشویی باز شود؛ playerCountry بدون تغییر می‌ماند */
  /* سینک یک‌طرفه نقشه ← پنل: دراپ‌داون راست روی همان کشور قرار می‌گیرد */
  var sel = el('startCountry');
  if (sel && MAP && MAP[fa]) sel.value = fa;
  refreshPolygons();   /* رنگ/ارتفاع نشانگر انتخابی روی نقشه */
  getJSON('api/country?name=' + encodeURIComponent(fa), function (r) {
    if (!r.ok) { flash(r.error || 'خطا'); return; }
    renderCountryPanel(r);
  }, function () { flash('خطا در دریافت اطلاعات کشور.'); });
  if (!silent) { /* آماده برای افکت‌های آینده */ }
}

function renderCountryPanel(r) {
  LAST_COUNTRY_R = r;   /* B2: برای رندر مجدد پنل پس از انتخاب استان */
  var box = el('countryInfo');
  el('idleInfo').style.display = 'none';
  box.style.display = 'block';
  var h = '';
  var isPlayer = !!(ST && ST.player === r.name);   /* playerCountry مستقل از SELECTED */
  h += '<h2>' + r.name + '</h2>';
  h += '<div class="muted small">' + (r.en || '') + ' · ' + (r.iso3 || '') + '</div>';
  h += '<div style="margin:4px 0">' + (isPlayer
      ? '<span class="badge" style="color:#ffd166">🏰 کشور شما — کنترل کامل</span>'
      : '<span class="badge">👥 حالت مشاهده — کشور شما: '
         + (ST ? ST.player : '—') + '</span>')
    + '</div>';
  h += '<div>';
  for (var i = 0; i < r.tags.length; i++) h += '<span class="badge">' + r.tags[i] + '</span>';
  h += '</div>';
  h += '<h3>👑 رهبری</h3>';
  h += '<div class="row"><span class="muted">رئیس دولت</span><span>' + r.leader + '</span></div>';
  if (r.rank) h += '<div class="row"><span class="muted">رتبه جهانی</span><span>#' + r.rank + '</span></div>';
  h += '<div class="row"><span class="muted">منطقه</span><span>' + r.region + '</span></div>';
  if (r.trait) h += '<div class="row"><span class="muted">ویژگی</span><span class="small">' + r.trait + '</span></div>';
  h += '<h3>📊 آمار ملی</h3>';
  h += barHtml('نیروی نظامی', r.mil, r.mil < 30 ? 'bad' : (r.mil < 55 ? 'warn' : ''));
  h += barHtml('اقتصاد', r.eco, r.eco < 30 ? 'bad' : (r.eco < 55 ? 'warn' : ''));
  h += barHtml('فناوری', r.tech, r.tech < 30 ? 'bad' : (r.tech < 55 ? 'warn' : ''));
  h += barHtml('ثبات داخلی', r.stab, r.stab < 30 ? 'bad' : (r.stab < 55 ? 'warn' : ''));
  h += '<div class="row"><span class="muted">خزانه</span><span>' + r.money.toFixed(0) + ' میلیارد</span></div>';
  h += '<div class="row"><span class="muted">نفوذ</span><span>' + r.influence.toFixed(0) + '</span></div>';
  h += '<div class="row"><span class="muted">کلاهک هسته\u200cای ☢</span><span>' + r.nukes + '</span></div>';
  if (r.rel != null && ST) {
    h += '<h3>🤝 رابطه با شما (' + ST.player + ')</h3>';
    h += barHtml('رابطه', r.rel, r.rel < 0 ? 'bad' : '');
  }
  if (r.war_with.length) {
    h += '<h3>⚔ در جنگ با</h3><div>';
    for (var w = 0; w < r.war_with.length; w++) h += '<span class="badge">' + r.war_with[w] + '</span>';
    h += '</div>';
  }
  if (r.arsenal.length) {
    h += '<h3>🛠 تجهیزات اصلی</h3>';
    for (var a = 0; a < r.arsenal.length; a++) h += '<div class="small">• ' + r.arsenal[a] + '</div>';
  }
  if (r.parties && Object.keys(r.parties).length) {
    h += '<h3>🏛 احزاب سیاسی</h3>';
    var ks = Object.keys(r.parties).sort(function (x, y) { return r.parties[y] - r.parties[x]; });
    for (var p = 0; p < ks.length; p++) {
      h += barHtml(ks[p], Math.min(100, r.parties[ks[p]]));
    }
  }
  if (r.friends && r.friends.length) {
    h += '<h3>💚 نزدیک\u200cترین دوستان</h3>';
    for (var f = 0; f < r.friends.length; f++)
      h += '<div class="row"><span>' + r.friends[f][0] + '</span><span class="muted">رابطه ' + r.friends[f][1].toFixed(0) + '</span></div>';
  }
  if (r.enemies && r.enemies.length) {
    h += '<h3>💢 دشمنان اصلی</h3>';
    for (var e = 0; e < r.enemies.length; e++)
      h += '<div class="row"><span>' + r.enemies[e][0] + '</span><span class="muted">رابطه ' + r.enemies[e][1].toFixed(0) + '</span></div>';
  }
  if (r.proxies && r.proxies.length) {
    h += '<h3>🗡 شبکه نیابتی شما اینجا</h3>';
    for (var x = 0; x < r.proxies.length; x++) h += '<div class="small">• ' + r.proxies[x] + '</div>';
  }
  if (r.press && r.press.length) {
    h += '<h3>📰 آخرین اخبار داخلی</h3>';
    for (var n = 0; n < r.press.length; n++) h += '<div class="press">' + r.press[n] + '</div>';
  }
  if (!isPlayer && ST) {
    h += '<div class="press" style="margin-top:10px">ℹ️ کنترل شما همچنان «'
      + ST.player + '» است؛ این پنل فقط اطلاعات «' + r.name
      + '» را نشان می‌دهد. برای تغییر کشور زیر کنترل از «شروع بازی جدید» استفاده کنید.</div>';
  }
  h += provPanelHtml();   /* B2: بخش استان (اگر استان‌ای انتخاب شده باشد) */
  box.innerHTML = h;
  provAfterPanel();       /* B2: اتصال دکمه رفع انتخاب استان */
}

/* ---------- فاز B2 — سیستم استان‌ها (سبک؛ بدون پردازش پرفریم) ---------- */
var LAST_COUNTRY_R = null;   /* آخرین داده پنل کشور — برای رندر مجدد پنل پس از انتخاب استان */
var PROV = {
  on: true, idx: null, cache: {}, iso: null, requestId: 0,           /* کشوری که مرز استان‌هایش هم‌اکنون روی کره است */
  sel: null,           /* استان انتخاب‌شده (یک feature) */
  layerObj: null,      /* گروه THREE الحاقی به صحنه (مرز انتخاب‌شده) */
  linesMesh: null, step: null, taken: 0
};

function provIso(fa) {
  if (!MAP || !MAP[fa] || !PROV.idx || !PROV.idx.countries) return null;
  var iso = MAP[fa].iso3;
  if (!iso || !PROV.idx.countries[iso]) return null;   /* بدون داده استان = بدون لایه */
  return iso;
}

function provName(p) {
  var pp = (p && p.properties) || p || {};
  return pp.name_en || pp.name || pp.name_fa || pp.id || '—';
}

/* حلقه‌های بیرونی استان‌ها (حفره‌ها رسم نمی‌شوند — خوانایی مرز) + undo آنتی‌مریدین */
function provRings(gj, wantTouched) {
  var rings = [];
  var fs = (gj && gj.features) || [];
  for (var i = 0; i < fs.length; i++) {
    var g = fs[i] && fs[i].geometry;
    if (!g || !g.coordinates) continue;
    var polys = (g.type === 'Polygon') ? [g.coordinates] :
                (g.type === 'MultiPolygon') ? g.coordinates : [];
    for (var p = 0; p < polys.length; p++) {
      var ring = polys[p] && polys[p][0];
      if (!ring || ring.length < 4) continue;
      /* انتقال پیوسته طول جغرافیایی (خط عرض جغرافیایی مورب روی خط تاریخ امن می‌شود) */
      var out = [], off = 0, prev = null;
      for (var k = 0; k < ring.length; k++) {
        var lng = ring[k][0], lat = ring[k][1];
        if (prev != null) {
          while (lng + off - prev > 180) off -= 360;
          while (lng + off - prev < -180) off += 360;
        }
        prev = lng + off;
        out.push([lat, lng + off]);
      }
      rings.push(out);
    }
  }
  return rings;
}

function provOneRings(f, wantTouched) { return provRings({ features: [f] }, wantTouched); }

/* PIP — آزمون نقطه‌درون استاندارد؛ حفره‌ها احترام می‌شود */
function pipRing(lat, lng, ring) {
  var inside = false;
  for (var i = 0, j = ring.length - 1; i < ring.length; j = i, i++) {
    var xi = ring[i][1], yi = ring[i][0], xj = ring[j][1], yj = ring[j][0];
    if (((xi > lat) !== (xj > lat)) && (lng < (yj - yi) * (lat - xi) / (xj - xi) + yi)) inside = !inside;
  }
  return inside;
}

function provHit(lat, lng, f) {
  var g = f && f.geometry;
  if (!g || !g.coordinates) return false;
  var polys = (g.type === 'Polygon') ? [g.coordinates] :
              (g.type === 'MultiPolygon') ? g.coordinates : [];
  for (var p = 0; p < polys.length; p++) {
    if (!polys[p] || !polys[p][0]) continue;
    if (!pipRing(lat, lng, polys[p][0])) continue;
    var hole = false;
    for (var hh = 1; hh < polys[p].length; hh++) {
      if (polys[p][hh] && pipRing(lat, lng, polys[p][hh])) { hole = true; break; }
    }
    if (!hole) return true;
  }
  return false;
}

/* مساحت کروی تقریبی (داده ساده‌شده) — تنها محاسبه مجاز؛ بدون سکوت داده جعلی */
function provAreaKm2(f) {
  var g = f && f.geometry;
  if (!g || !g.coordinates) return null;
  var polys = (g.type === 'Polygon') ? [g.coordinates] :
              (g.type === 'MultiPolygon') ? g.coordinates : [];
  var total = 0, R = 6371.0;
  for (var p = 0; p < polys.length; p++) {
    var ring = polys[p] && polys[p][0];
    if (!ring || ring.length < 4) continue;
    var s = 0;
    for (var i = 0; i < ring.length - 1; i++) {
      var l1 = ring[i][0] * Math.PI / 180, f1 = ring[i][1] * Math.PI / 180;
      var l2 = ring[i + 1][0] * Math.PI / 180, f2 = ring[i + 1][1] * Math.PI / 180;
      s += (l2 - l1) * (2 + Math.sin(f1) + Math.sin(f2));
    }
    total += Math.abs(s * R * R / 2);
  }
  return total > 0 ? total : null;
}

function provParts(f) {
  var g = f && f.geometry;
  if (!g || !g.coordinates) return 0;
  if (g.type === 'Polygon') return 1;
  if (g.type === 'MultiPolygon') return g.coordinates.length;
  return 0;
}

function provBuildAlt() {   /* کمی بالاتر از کپ کشوری؛ روی سطح کره نه شناور جدا */
  return (SELECTED ? 0.055 : 0.012) + 0.004;
}

function provMakeLines(rings, alt, hex, op) {
  var pos = [];
  for (var r = 0; r < rings.length; r++) {
    var ring = rings[r];
    for (var k = 0; k < ring.length - 1; k++) {
      var a = globe.getCoords(ring[k][0], ring[k][1], alt);
      var b = globe.getCoords(ring[k + 1][0], ring[k + 1][1], alt);
      pos.push(a.x, a.y, a.z, b.x, b.y, b.z);
    }
  }
  var geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(pos), 3));
  var mat = new THREE.LineBasicMaterial({ color: hex, transparent: true, opacity: op });
  return new THREE.LineSegments(geo, mat);
}

function provDisposeGroup() {
  var g = PROV.layerObj;
  if (!g) return;
  try { globe.scene().remove(g); } catch (e2) { /* محافظت */ }
  for (var i = 0; i < g.children.length; i++) {
    var c = g.children[i];
    if (c && c.geometry && c.geometry.dispose) c.geometry.dispose();
    if (c && c.material && c.material.dispose) c.material.dispose();
  }
  PROV.layerObj = null; PROV.linesMesh = null;
}

function provShow(iso, requestId) {
  if (!globe || !iso) return;
  provData(iso, function (gj) {
    if (!gj || iso !== PROV.iso || !PROV.on || requestId !== PROV.requestId) return;
    provDisposeGroup(); var rings=provRings(gj);
    if(rings.length){var grp=new THREE.Group(),seg=provMakeLines(rings,provBuildAlt(),0x2ee6d6,0.7);grp.add(seg);PROV.linesMesh=seg;PROV.layerObj=grp;try{globe.scene().add(grp);}catch(e3){}}
    refreshLabels();
  });
}

function provRefreshSelLine() {
  var g = PROV.layerObj;
  if (!g) return;
  if (PROV.selMesh) {
    g.remove(PROV.selMesh);
    PROV.selMesh.geometry.dispose();
    PROV.selMesh.material.dispose();
    PROV.selMesh = null;
  }
  if (!PROV.sel) return;
  var rings = provOneRings(PROV.sel);
  if (!rings.length) return;
  var sel = provMakeLines(rings, provBuildAlt() + 0.002, 0xff9e2c, 1.0);
  g.add(sel);
  PROV.selMesh = sel;
}

function provData(iso, cb) {       /* Lazy Loading + کش */
  if (PROV.cache[iso]) { cb(PROV.cache[iso]); return; }
  getJSON('data/provinces/' + iso + '.json', function (gj) {
    PROV.cache[iso] = gj;
    cb(gj);
  }, function (st, tx) { flash('خطای بارگذاری استان‌های ' + iso + ': ' + netErrMsg(st, tx)); cb(null); });
}

function provLoadIndex(cb) {
  if (PROV.idx) { cb(true); return; }
  getJSON('data/provinces/index.json', function (d) {
    PROV.idx = d;
    cb(true);
  }, function (st, tx) { flash('خطای بارگذاری فهرست استان‌ها: ' + netErrMsg(st, tx)); cb(false); });
}

function provOnCountryChange() {
  var requestId=++PROV.requestId;PROV.sel=null;provDisposeGroup();LBL_SIG='';
  if(!PROV.on){PROV.iso=null;refreshLabels();return;}
  PROV.iso=null;refreshLabels();
  provLoadIndex(function(ok){
    if(!ok||requestId!==PROV.requestId||!SELECTED)return;
    var iso=provIso(SELECTED);
    if(iso){PROV.iso=iso;provShow(iso,requestId);}
    else{provDisposeGroup();PROV.iso=null;refreshLabels();}
  });
}

function provSelect(ft) {
  if (ft === PROV.sel) return;
  PROV.sel = ft;
  provRefreshSelLine();
  provRenderPanel();
}

function provClear() {
  if (!PROV.sel) return;
  PROV.sel = null;
  provRefreshSelLine();
  provRenderPanel();
}

function provOff() {++PROV.requestId;PROV.sel=null;provDisposeGroup();PROV.iso=null;LBL_SIG='';refreshLabels();provRenderPanel();}

function provPanelHtml() {
  if (!PROV.sel) return '';
  var p = PROV.sel.properties || {};
  var h = '<h3>\ud83d\uddfa اطلاعات استان</h3>';
  h += '<div class="provBox small">';
  h += '<div class="row"><span class="muted">نام استان</span><span>' + provName(PROV.sel) + '</span></div>';
  h += '<div class="row"><span class="muted">کشور</span><span class="small">' + (p.country || SELECTED || '—') + '</span></div>';
  if (p.name_en && p.country === 'IRN') h += '<div class="row"><span class="muted">نام اصلی</span><span class="small">' + p.name_en + '</span></div>';
  h += '<div class="row"><span class="muted">شناسه استان</span><span class="small">' + (p.id || '—') + '</span></div>';
  if (p.iso) h += '<div class="row"><span class="muted">کد رسمی</span><span class="small">' + p.iso + '</span></div>';
  var parts = provParts(PROV.sel);
  if (parts > 1) h += '<div class="row"><span class="muted">بخش‌های جغرافیایی</span><span>' + parts + '</span></div>';
  var ar = provAreaKm2(PROV.sel);
  if (ar != null) {
    var arS = (ar >= 10000) ? (Math.round(ar / 1000) + ' هزارنkm²') : Math.round(ar) + ' km²';
    h += '<div class="row"><span class="muted">مساحت تقریبی</span><span>' + arS + '</span></div>';
  }
  h += '<div style="margin-top:6px"><button id="btnProvClear">✖ رفع انتخاب استان</button></div>';
  h += '</div>';
  return h;
}

function provRenderPanel() {
  if (LAST_COUNTRY_R) renderCountryPanel(LAST_COUNTRY_R);
}

function provAfterPanel() {
  var b = document.getElementById('btnProvClear');
  if (b) b.onclick = function () { provClear(); };
}

/* کلیک روی استان: raycast کره ساده + آزمون نقطه‌درون — تنها در pointerup کوتاه (غیر درگ) */
function provBindPointer() {
  if (!globe) return;
  var host = document.getElementById('globe');
  if (!host || !window.addEventListener) return;
  host.addEventListener('pointerdown', function (e) {
    PROV.step = { x: e.clientX, y: e.clientY, t: Date.now() };
  }, true);
  host.addEventListener('pointerup', function (e) {
    var s = PROV.step;
    PROV.step = null;
    if (!s) return;
    var drag = Math.abs(e.clientX - s.x) > 4 || Math.abs(e.clientY - s.y) > 4 || (Date.now() - s.t) > 700;
    if (drag) return;
    var hit = provPick(e, host);
    if (hit) {
      PROV.taken = Date.now();      /* کلیک متعلق به استان است، نه انتخاب کشور */
      provSelect(hit);
    } else if (PROV.sel) {
      provClear();                  /* کلیک بیرون استان‌ها = پاک شدن انتخاب */
    }
  }, true);
}

function provPick(e, host) {
  if (!PROV.iso || !globe || !globe.camera || !globe.renderer || !globe.toGeoCoords) return null;
  if (!PROV.cache[PROV.iso]) return null;
  var cv = globe.renderer().domElement;
  var w = cv ? cv.clientWidth : host.clientWidth;
  var hgt = cv ? cv.clientHeight : host.clientHeight;
  if (!w || !hgt) return null;
  var cam = globe.camera();
  var ndx = (e.clientX - host.getBoundingClientRect().left) / w * 2 - 1;
  var ndy = -((e.clientY - host.getBoundingClientRect().top) / hgt * 2 - 1);
  var v = new THREE.Vector3(ndx, ndy, 0.5).unproject(cam);
  var d3 = v.sub(cam.position);
  var len = Math.sqrt(d3.x * d3.x + d3.y * d3.y + d3.z * d3.z);
  if (!len) return null;
  var dx = d3.x / len, dy = d3.y / len, dz = d3.z / len;
  var ox = cam.position.x, oy = cam.position.y, oz = cam.position.z;
  var R = 100 * (1 + provBuildAlt());   /* شعاع کلیک ≈ سطح مرز استان */
  var b = 2 * (ox * dx + oy * dy + oz * dz);
  var c = (ox * ox + oy * oy + oz * oz) - R * R;
  var disc = b * b - 4 * c;
  if (disc <= 0) return null;
  var t = (-b - Math.sqrt(disc)) / 2;
  if (t <= 0) return null;
  var gc = globe.toGeoCoords({ x: ox + t * dx, y: oy + t * dy, z: oz + t * dz });
  var fs = PROV.cache[PROV.iso].features;
  for (var i = 0; i < fs.length; i++) {
    /* شماره‌گذاری طول جغرافیایی در حالت عبور از خط تاریخ: هر سه گزینه آزمون */
    for (var ww = -1; ww <= 1; ww++) {
      if (provHit(gc.lat, gc.lng + ww * 360, fs[i])) return fs[i];
    }
  }
  return null;
}

function provToggleBtn() {
  var bp = document.getElementById('btnProv');
  if (bp) bp.onclick = function () {
    PROV.on = !PROV.on;
    this.textContent = PROV.on ? '\ud83d\uddfa استان: روشن' : '\ud83d\uddfa استان: خاموش';
    if (PROV.on) { PROV.iso = null; provOnCountryChange(); }
    else { provOff(); }
  };
}

/* ---------- اقدامات ---------- */
function endDay() {
  if (!ST) { flash('اول بازی را شروع کن.'); return; }
  postJSON('api/act', { argv: ['end'] }, function (r) {
    if (r.out) flash(r.out);
    loadState();
  }, function () { flash('خطا در پایان دور.'); });
}

/* پنجره تأیید شروع بازی جدید — دو دکمه: «🆕 شروع بازی جدید» / «انصراف» */
function confirmBox(onYes) {
  var ovl = document.createElement('div');
  ovl.style.cssText = 'position:fixed;left:0;top:0;right:0;bottom:0;background:rgba(0,0,0,.6);'
    + 'z-index:50;display:flex;align-items:center;justify-content:center;direction:rtl;';
  var box = document.createElement('div');
  box.style.cssText = 'background:#0e1626;border:1px solid #3a77d0;border-radius:12px;'
    + 'padding:18px;max-width:420px;font-family:Tahoma;';
  box.innerHTML = '<b>🆕 شروع بازی جدید</b><p class="small" style="color:#ffd479;margin:8px 0"></p>'
    + '<div class="small muted" style="margin-bottom:10px">💾 از ذخیرهٔ کنونی پشتیبان گرفته می‌شود: game_state.json.bak</div>'
    + '<div style="display:flex;gap:8px">'
    + '<button class="warn" style="background:#7a2430;border-color:#a03a45">🆕 شروع بازی جدید</button>'
    + '<button style="background:#16233d;border-color:#2c3f66">انصراف</button></div>';
  box.querySelector('p').textContent = ST
    ? ('بازی «' + ST.player + '» در جریان است. با شروع بازی جدید، ذخیرهٔ کنونی حذف و با بازی جدید جایگزین می‌شود (پشتیبان .bak حفظ می‌شود).')
    : '';
  var btns = box.querySelectorAll('button');
  btns[1].onclick = function () { document.body.removeChild(ovl); };   /* انصراف — هیچی نمی‌کند */
  btns[0].onclick = function () { document.body.removeChild(ovl); onYes(); };
  ovl.appendChild(box);
  document.body.appendChild(ovl);
}

function startGame(confirmed) {
  var sel = el('startCountry');
  var c = sel.value;
  if (!c) { flash('برای شروع، ابتدا کشور را انتخاب کن.'); return; }
  el('startErr').textContent = '';
  /* بازی فعال = تأیید الزامی؛ بدون بازی فعال = شروع مستقیم بدون تأیید اضافی */
  if (confirmed !== true && ST) {
    confirmBox(function () { startGame(true); });
    return;
  }
  var payload = { country: c };
  if (confirmed === true) payload.confirm = 'بله';
  postJSON('api/init', payload, function (r) {
    if (!r.ok) {
      if (r.needConfirm) { confirmBox(function () { startGame(true); }); return; }
      el('startErr').textContent = r.error || 'خطا';
      return;
    }
    flash(r.out || 'بازی آغاز شد!');
    SELECTED = c;                      /* داشبورد کشور انتخاب‌شده پس از شروع */
    loadState();                       /* loadState خودش SELECTED را به پنل می‌راند */
    if (MAP[c] && MAP[c].lat != null) {
      globe.pointOfView({ lat: MAP[c].lat, lng: MAP[c].lon, altitude: 1.9 }, 900);
    }
  }, function (st, tx) { el('startErr').textContent = netErrMsg(st, tx); });
}

/* ---------- نوار بالا ---------- */
function bindToolbar() {
  el('btnMode').onclick = function () {
    MODE = (MODE === 'geo') ? 'pol' : 'geo';
    this.textContent = (MODE === 'geo') ? '🎨 رنگ: جغرافیایی' : '🎨 رنگ: سیاسی';
    refreshPolygons();
  };
  el('btnRot').onclick = function () {
    ROT = !ROT;
    globe.controls().autoRotate = ROT;
    this.textContent = ROT ? '🔄 چرخش: روشن' : '🔄 چرخش: خاموش';
  };
  el('btnZoomIn').onclick = function () {
    var v = globe.pointOfView();
    globe.pointOfView({ altitude: Math.max(1.15, v.altitude * 0.72) }, 350);
  };
  el('btnZoomOut').onclick = function () {
    var v = globe.pointOfView();
    globe.pointOfView({ altitude: Math.min(3.6, v.altitude * 1.35) }, 350);
  };
  el('btnHome').onclick = function () {
    globe.pointOfView({ lat: 27, lng: 48, altitude: 2.3 }, 700);
  };
  el('btnTex').onclick = function () {
    TEX = (TEX === 'img/earth-dark.jpg') ? 'img/earth-blue-marble.jpg' : 'img/earth-dark.jpg';
    globe.globeImageUrl(TEX);
    this.textContent = (TEX === 'img/earth-dark.jpg') ? '🖼 بافت: تیره' : '🖼 بافت: واقعی';
  };
  el('btnEnd').onclick = endDay;
  provToggleBtn();   /* B2: دکمه مرز استان‌ها (اگر در HTML باشد) */
  var tb = el('panelToggle');
  if (tb) tb.onclick = togglePanel;   /* فلش باز/بسته پنل */
  el('btnStart').onclick = function () { startGame(false); };
}

/* ---------- شمارنده FPS ---------- */
function startFps() {
  var last = performance.now(), frames = 0;
  var box = el('fps');
  (function tick(now) {
    frames++;
    if (now - last >= 1000) {
      box.textContent = 'FPS: ' + frames;
      frames = 0;
      last = now;
    }
    requestAnimationFrame(tick);
  })(last);
}

boot();
bindToolbar();
provBindPointer();   /* B2: کلیک استان — پس از ساخته شدن globe در boot */
setPanel(false);   /* پنل کشویی پیش‌فرض بسته است */
