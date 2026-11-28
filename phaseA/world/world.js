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

var TRADE_SHIPS_ENABLED = true;
var TRADE_SHIP_DATA = [];
var TRADE_SHIP_TIMER = null;
var TRADE_SHIP_MAX = 12;

function tradeShipModel() {
  var g = new THREE.Group();
  var hullMat = new THREE.MeshPhongMaterial({ color: 0x263b52, shininess: 35 });
  var deckMat = new THREE.MeshPhongMaterial({ color: 0x9aa8b5 });
  var boxMats = [
    new THREE.MeshPhongMaterial({ color: 0xd28b45 }),
    new THREE.MeshPhongMaterial({ color: 0x4d8eaa }),
    new THREE.MeshPhongMaterial({ color: 0x718b68 })
  ];
  var hull = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.32, 0.68), hullMat);
  hull.position.y = 0;
  g.add(hull);
  var deck = new THREE.Mesh(new THREE.BoxGeometry(1.15, 0.12, 0.58), deckMat);
  deck.position.set(-0.08, 0.2, 0);
  g.add(deck);
  for (var i = 0; i < 3; i++) {
    var cargo = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.34, 0.48), boxMats[i]);
    cargo.position.set(-0.42 + i * 0.43, 0.42, 0);
    g.add(cargo);
  }
  var cabin = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.38, 0.42), deckMat);
  cabin.position.set(0.68, 0.34, 0);
  g.add(cabin);
  g.scale.set(0.19, 0.19, 0.19);
  g.rotation.y = Math.PI / 2;
  return g;
}

function tradeShipPosition(a, b, t) {
  var r = Math.PI / 180;
  var la = a.lat * r, loa = a.lon * r, lb = b.lat * r, lob = b.lon * r;
  var ax = Math.cos(la) * Math.cos(loa), ay = Math.cos(la) * Math.sin(loa), az = Math.sin(la);
  var bx = Math.cos(lb) * Math.cos(lob), by = Math.cos(lb) * Math.sin(lob), bz = Math.sin(lb);
  var dot = Math.max(-1, Math.min(1, ax * bx + ay * by + az * bz));
  var omega = Math.acos(dot), x, y, z;
  if (omega < 0.0001) {
    x = ax; y = ay; z = az;
  } else {
    var den = Math.sin(omega);
    var wa = Math.sin((1 - t) * omega) / den;
    var wb = Math.sin(t * omega) / den;
    x = wa * ax + wb * bx;
    y = wa * ay + wb * by;
    z = wa * az + wb * bz;
  }
  return {
    lat: Math.atan2(z, Math.sqrt(x * x + y * y)) / r,
    lon: Math.atan2(y, x) / r
  };
}

function refreshTradeShips() {
  if (!globe) return;
  var next = [], pacts = (ST && ST.pact_records) || [], i, j, members, a, b, ma, mb;
  if (TRADE_SHIPS_ENABLED && MAP) {
    for (i = 0; i < pacts.length && next.length < TRADE_SHIP_MAX; i++) {
      if (!pacts[i] || pacts[i].status !== 'active' || pacts[i].type !== 'trade') continue;
      members = pacts[i].members || [];
      if (members.length < 2) continue;
      ma = MAP[members[0]];
      if (!ma || ma.lat == null || ma.lon == null) continue;
      for (j = 1; j < members.length && next.length < TRADE_SHIP_MAX; j++) {
        mb = MAP[members[j]];
        if (!mb || mb.lat == null || mb.lon == null) continue;
        a = { lat: Number(ma.lat), lon: Number(ma.lon) };
        b = { lat: Number(mb.lat), lon: Number(mb.lon) };
        next.push({ id: String(pacts[i].id || i) + '-out-' + j, a: a, b: b, origin: members[0], destination: members[j], cargo: 'کالای عمومی', statusText: 'در حال حرکت', phase: (i * 0.17 + j * 0.11) % 1, period: 105 });
        if (next.length < TRADE_SHIP_MAX) {
          next.push({ id: String(pacts[i].id || i) + '-back-' + j, a: b, b: a, origin: members[j], destination: members[0], cargo: 'کالای عمومی', statusText: 'در حال حرکت', phase: (i * 0.23 + j * 0.19 + 0.5) % 1, period: 125 });
        }
      }
    }
  }
  TRADE_SHIP_DATA = next;
  updateTradeShips();
}

function updateTradeShips() {
  if (!globe) return;
  if (!TRADE_SHIPS_ENABLED || !TRADE_SHIP_DATA.length) {
    globe.objectsData([]);
    return;
  }
  var now = Date.now() / 1000;
  for (var i = 0; i < TRADE_SHIP_DATA.length; i++) {
    var d = TRADE_SHIP_DATA[i];
    var t = ((now / d.period + d.phase) % 1 + 1) % 1;
    var pos = tradeShipPosition(d.a, d.b, t);
    d.lat = pos.lat;
    d.lon = pos.lon;
  }
  globe.objectsData(TRADE_SHIP_DATA)
    .objectLat(function (d) { return d.lat; })
    .objectLng(function (d) { return d.lon; })
    .objectAltitude(0.018)
    .objectThreeObject(function (d) {
      if (!d.object) d.object = tradeShipModel();
      return d.object;
    })
    .onObjectHover(function (d) { showTradeShipInfo(d || null); });
}

function showTradeShipInfo(ship) {
  var box = el('tradeShipInfo');
  if (!box) return;
  if (!ship) {
    box.style.display = 'none';
    return;
  }
  var origin = ship.origin || ship.aName || 'مبدأ نامشخص';
  var destination = ship.destination || ship.bName || 'مقصد نامشخص';
  box.textContent = '🚢 کشتی تجاری\nمبدأ: ' + origin + '\nمقصد: ' + destination +
    '\nوضعیت: ' + (ship.statusText || 'در حال حرکت') +
    '\nبار: ' + (ship.cargo || 'کالای عمومی');
  box.style.display = 'block';
}

function bindTradeShipToggle() {
  var b = el('btnTradeShips');
  if (!b) return;
  b.onclick = function () {
    TRADE_SHIPS_ENABLED = !TRADE_SHIPS_ENABLED;
    this.textContent = TRADE_SHIPS_ENABLED ? '🚢 کشتی تجاری: روشن' : '🚢 کشتی تجاری: خاموش';
    if (TRADE_SHIPS_ENABLED) refreshTradeShips();
    else updateTradeShips();
  };
}

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
    .labelSize(function (d) { return d.kind === 'prov' ? (d.size || 0.18) : 0.45; })
    .labelDotRadius(function (d) { return d.kind === 'country' && d.point ? 0.28 : 0; })
    .labelColor(function (d) {
      if (d.kind === 'prov') return (PROV.sel === d.f) ? '#ffb347' : '#8ff0e5';
      return (d.fa === SELECTED) ? '#ffd166' : '#e8eef8';
    })
    .labelAltitude(function (d) { return d.kind === 'prov' ? 0.07 : 0.012; })
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
var LBL_COUNTRY = null, LBL_ALL = [], LBL_ACTIVE_ISO = null, LBL_ACTIVE_PROV = null, LBL_CACHE = {};
var LBL_EMPTY_PROV = [];
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
  var countries = labelsList(), provinces = LBL_EMPTY_PROV, iso = null;
  if (PROV_LABELS_ENABLED && PROV.on && PROV.iso && PROV.cache[PROV.iso]) {
    iso = PROV.iso;
    provinces = provLabelsFor(iso);
  }
  /* مقایسهٔ هویت آرایه‌ها، نه فقط تعداد؛ از بازسازی بی‌دلیل TextGeometry جلوگیری می‌کند. */
  if (countries === LBL_COUNTRY && provinces === LBL_ACTIVE_PROV && iso === LBL_ACTIVE_ISO) return;
  LBL_ACTIVE_ISO = iso;
  LBL_ACTIVE_PROV = provinces;
  /* وقتی استان فعالی نداریم، همان آرایهٔ ثابت کشورها را نگه می‌داریم. */
  LBL_ALL = provinces.length ? countries.concat(provinces) : countries;
  globe.labelsData(LBL_ALL);
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
  for(var i=0;i<fs.length;i++){var f=fs[i],pp=(f&&f.properties)||{},pt=provLabelPoint(f),nm=pp.name_en||pp.name||pp.id;if(pt&&nm)candidates.push({f:f,en:String(nm),lat:pt.lat,lon:pt.lon,area:(pt.area||0)*Math.max(0.15,Math.cos(pt.lat*Math.PI/180))});}
  candidates.sort(function(a,b){return b.area-a.area;});
  /* اندازه نوشته متناسب با مساحت واقعی تقریبی استان؛ تصحیح اثر عرض جغرافیایی */
  var areas=[];
  for(var ai=0;ai<candidates.length;ai++)areas.push(Math.max(0.000001,candidates[ai].area));
  areas.sort(function(a,b){return a-b;});
  var medianArea=areas.length?areas[Math.floor(areas.length/2)]:1;
  var out=[],minSep=0.35,maxLabels=90;
  for(var c=0;c<candidates.length&&out.length<maxLabels;c++){
    var d=candidates[c],keep=true;
    for(var j=0;j<out.length;j++){var r1=d.lat*Math.PI/180,r2=out[j].lat*Math.PI/180,dl=(d.lon-out[j].lon)*Math.PI/180,dp=r1-r2,a=Math.sin(dp/2)*Math.sin(dp/2)+Math.cos(r1)*Math.cos(r2)*Math.sin(dl/2)*Math.sin(dl/2),dist=2*Math.atan2(Math.sqrt(a),Math.sqrt(Math.max(0,1-a)))*180/Math.PI;if(dist<minSep){keep=false;break;}}
    if(keep){
      /* استان‌های کوچک، مخصوصاً در کشورهای پرتراکم، برچسب کوچک‌تری می‌گیرند. */
      var relative=Math.sqrt(Math.max(0.025,d.area/medianArea));
      var size=Math.max(0.055,Math.min(0.32,0.27*relative));
      var nameFactor=Math.min(1,Math.sqrt(14/Math.max(1,d.en.length)));
      size=Math.max(0.05,size*nameFactor);
      out.push({kind:'prov',iso3:iso,en:d.en,lat:d.lat,lon:d.lon,area:d.area,size:size,point:false,f:d.f});
    }
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
  if (TRADE_SHIP_TIMER) clearInterval(TRADE_SHIP_TIMER);
  TRADE_SHIP_TIMER = setInterval(updateTradeShips, 700);
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
    syncSanctionState();
    renderAppliedSanctions();
    renderInbox();
    renderGameClock();
    renderWorldChips();
    renderStartWidget();
    refreshPolygons();
    refreshTradeShips();
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

/* پنل رویدادها: پوسته بیانیه‌ها اکنون غیرفعال است؛ AI زنده در فاز F آن را فعال می‌کند. */
function setEventPanel(open) {
  var pnl = el('eventPanel'), btn = el('eventPanelToggle');
  if (!pnl || !btn) return;
  pnl.className = open ? 'open' : '';
  btn.className = open ? 'open' : '';
  btn.textContent = open ? '❮' : '❯';
  btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  pnl.setAttribute('aria-hidden', open ? 'false' : 'true');
}
function toggleEventPanel() {
  var pnl = el('eventPanel');
  setEventPanel(!pnl || pnl.className.indexOf('open') < 0);
}

/* حالت‌های مذاکره؛ اتصال به AI زنده در فاز F فعال می‌شود. */
var EVENT_TALK_STATE = { confidential: false, alliance: false, normal: false };
var PUBLIC_TARGETS = [], PUBLIC_DRAFT = [];
var NORMAL_TARGETS = [], NORMAL_DRAFT = [];
function renderPublicTargets() {
  var box=el('publicTargetBox'), list=el('publicCountryList'), summary=el('publicTargetSummary');
  var edit=el('publicEditCountries'), actions=box ? box.querySelector('.eventActionRow') : null;
  if(!box || !list) return;
  if(PUBLIC_TARGETS.length) {
    list.hidden=true; if(actions) actions.hidden=true; if(edit) edit.hidden=false;
    if(summary) summary.textContent='مذاکره عمومی با '+PUBLIC_TARGETS.join('، ')+' · فهرست کشورها بسته شد.';
  } else {
    list.hidden=false; if(actions) actions.hidden=false; if(edit) edit.hidden=true;
    renderCountryPicker('publicCountryList',PUBLIC_DRAFT,'pub');
    if(summary) summary.textContent='کشورهای شرکت‌کننده در مذاکره عمومی را انتخاب کن.';
  }
}
function bindPublicTargetPicker() {
  var confirm=el('publicConfirmCountries'), cancel=el('publicCancelCountries'), edit=el('publicEditCountries');
  if(confirm) confirm.onclick=function() {
    PUBLIC_DRAFT=readCountryPicker('publicCountryList');
    if(!PUBLIC_DRAFT.length) { flash('حداقل یک کشور را انتخاب کن.'); return; }
    PUBLIC_TARGETS=PUBLIC_DRAFT.slice(0); renderPublicTargets(); renderEventTalkState();
  };
  if(cancel) cancel.onclick=function() { PUBLIC_DRAFT=[]; PUBLIC_TARGETS=[]; renderPublicTargets(); renderEventTalkState(); };
  if(edit) edit.onclick=function() {
    PUBLIC_DRAFT=PUBLIC_TARGETS.slice(0);
    renderCountryPicker('publicCountryList',PUBLIC_DRAFT,'pub');
    el('publicCountryList').hidden=false;
    var box=el('publicTargetBox'), actions=box ? box.querySelector('.eventActionRow') : null;
    if(actions) actions.hidden=false; edit.hidden=true;
  };
}
function renderNormalTargets() {
  var box=el('normalTargetBox'), list=el('normalCountryList'), summary=el('normalTargetSummary');
  var edit=el('normalEditCountries'), actions=box ? box.querySelector('.eventActionRow') : null;
  if(!box || !list) return;
  if(NORMAL_TARGETS.length) {
    list.hidden=true; if(actions) actions.hidden=true; if(edit) edit.hidden=false;
    if(summary) summary.textContent='مذاکره عادی با '+NORMAL_TARGETS.join('، ')+' · فهرست کشورها بسته شد.';
  } else {
    list.hidden=false; if(actions) actions.hidden=false; if(edit) edit.hidden=true;
    renderCountryPicker('normalCountryList',NORMAL_DRAFT,'norm');
    if(summary) summary.textContent='کشورهای مذاکره را انتخاب کن؛ انتخاب چند کشور هم‌زمان ممکن است.';
  }
}
function bindNormalTargetPicker() {
  var confirm=el('normalConfirmCountries'), cancel=el('normalCancelCountries'), edit=el('normalEditCountries');
  if(confirm) confirm.onclick=function() {
    NORMAL_DRAFT=readCountryPicker('normalCountryList');
    if(!NORMAL_DRAFT.length) { flash('حداقل یک کشور را انتخاب کن.'); return; }
    NORMAL_TARGETS=NORMAL_DRAFT.slice(0); renderNormalTargets(); renderEventTalkState();
  };
  if(cancel) cancel.onclick=function() { NORMAL_DRAFT=[]; NORMAL_TARGETS=[]; renderNormalTargets(); renderEventTalkState(); };
  if(edit) edit.onclick=function() {
    NORMAL_DRAFT=NORMAL_TARGETS.slice(0);
    renderCountryPicker('normalCountryList',NORMAL_DRAFT,'norm');
    el('normalCountryList').hidden=false;
    var box=el('normalTargetBox'), actions=box ? box.querySelector('.eventActionRow') : null;
    if(actions) actions.hidden=false; edit.hidden=true;
  };
}
function renderEventTalkState() {
  var confidential=EVENT_TALK_STATE.confidential, alliance=EVENT_TALK_STATE.alliance, normal=EVENT_TALK_STATE.normal;
  var cb=el('btnConfidentialTalk'), ab=el('btnAllianceTalk'), nb=el('btnNormalTalk');
  var cs=el('confidentialTalkState'), as=el('allianceTalkState'), ns=el('normalTalkState');
  var title=el('eventStatementTitle'), note=el('eventContextNote');
  var cbox=el('confidentialTargetBox'), nbox=el('normalTargetBox');
  var pbox=el('publicTargetBox');
  var cReady=confidential && CONFIDENTIAL_TARGETS.length>0, nReady=normal && NORMAL_TARGETS.length>0;
  if(cbox) cbox.hidden=!confidential; if(nbox) nbox.hidden=!normal;
  if(pbox) pbox.hidden=!(!confidential && !normal);
  if(confidential) renderConfidentialTargets(); if(normal) renderNormalTargets();
  if(!confidential && !normal) renderPublicTargets();
  var ready=cReady||nReady, publicMode=!confidential&&!normal;
  var feed=el('eventStatementFeed'), input=el('eventStatementInput'), send=el('eventStatementSend');
  if(feed) feed.style.display=(ready||publicMode)?'':'none';
  if(input&&input.parentNode) input.parentNode.style.display=(ready||publicMode)?'':'none';
  if(input) {
    input.disabled=!cReady;
    input.placeholder=cReady?'پیش‌نویس پیام محرمانه؛ ارسال واقعی در فاز F فعال می‌شود.':
      (nReady?'متن مذاکره عادی؛ ارسال واقعی و پوشش رسانه‌ای در فاز F فعال می‌شود.':
      'گفت‌وگو پس از فعال‌سازی هوش مصنوعی زنده در دسترس قرار می‌گیرد.');
  }
  if(send) { send.style.display=(ready||publicMode)?'':'none'; send.disabled=!cReady; send.textContent=cReady?'ثبت پیش‌نویس محرمانه':'ارسال پس از فعال‌سازی هوش مصنوعی زنده'; }
  if(cb) { cb.className='eventNegotiationToggle'+(confidential?' active':''); cb.setAttribute('aria-pressed',confidential?'true':'false'); }
  if(ab) { ab.className='eventNegotiationToggle'+(alliance?' active':''); ab.setAttribute('aria-pressed',alliance?'true':'false'); }
  if(nb) { nb.className='eventNegotiationToggle'+(normal?' active':''); nb.setAttribute('aria-pressed',normal?'true':'false'); }
  if(cs) cs.textContent=confidential?'روشن':'خاموش'; if(as) as.textContent=alliance?'روشن':'خاموش'; if(ns) ns.textContent=normal?'روشن':'خاموش';
  if(publicMode) {
    if(title) title.textContent=alliance?'پنجره مذاکرات با اتحاد':'پنجره بیانیه‌ها · حالت عمومی';
    if(note) note.textContent=alliance?'مذاکره با اتحاد در حالت عمومی است؛ محتوا می‌تواند در بیانیه عمومی و رسانه‌ها بازتاب پیدا کند.':'حالت عمومی: محتوا برای انتشار در بیانیه عمومی و پوشش رسانه‌ای در نظر گرفته می‌شود.';
    if(feed&&feed.querySelector('.eventStatementEmpty')) feed.querySelector('.eventStatementEmpty').textContent=alliance?'فضای مذاکره عمومی با اتحاد آماده است؛ اتصال هوش مصنوعی زنده در فاز F فعال می‌شود.':'بیانیه‌ای برای نمایش وجود ندارد. پس از اتصال هوش مصنوعی زنده، بیانیه‌های عمومی کشورها در این قسمت نمایش داده می‌شوند.';
  } else if(confidential) {
    if(title) title.textContent=alliance?'مذاکره محرمانه با اتحاد':(CONFIDENTIAL_TARGETS.length?'مذاکره محرمانه · با '+CONFIDENTIAL_TARGETS.join('، '):'مذاکره محرمانه · انتخاب کشورها');
    if(note) note.textContent=CONFIDENTIAL_TARGETS.length?'محتوا فقط میان شرکت‌کنندگان می‌ماند؛ نه در بیانیه عمومی منتشر می‌شود و نه رسانه‌ها به آن دسترسی دارند.':'کشورهای مذاکره را انتخاب کن. این حالت از بیانیه عمومی و پوشش رسانه‌ای محرمانه است.';
    if(feed&&feed.querySelector('.eventStatementEmpty')) feed.querySelector('.eventStatementEmpty').textContent='فضای مذاکره محرمانه آماده است؛ اتصال واقعی در فاز F انجام می‌شود.';
  } else {
    if(title) title.textContent=alliance?'مذاکره عادی با اتحاد':(NORMAL_TARGETS.length?'مذاکره عادی · با '+NORMAL_TARGETS.join('، '):'مذاکره عادی · انتخاب کشورها');
    if(note) note.textContent=NORMAL_TARGETS.length?'این مذاکره در بیانیه عمومی درج نمی‌شود؛ اما محرمانه نیست و رسانه‌ها می‌توانند محتوای آن را پوشش دهند.':'کشورهای مذاکره را انتخاب کن. این حالت در بیانیه عمومی نمی‌آید، اما برای رسانه‌ها محرمانه نیست.';
    if(feed&&feed.querySelector('.eventStatementEmpty')) feed.querySelector('.eventStatementEmpty').textContent='فضای مذاکره عادی آماده است؛ محتوای آن در آینده برای پوشش رسانه‌ای قابل مشاهده خواهد بود.';
  }
}
var EVENT_PANEL_VIEW = 'statements';
var FACTORY_SUBVIEW = 'projects';
var TECHNOLOGY_SUBVIEW = 'level';
function renderTechnologyPanel() {
  var row = ST && ST.player && ST.countries ? ST.countries[ST.player] : null;
  var value = row ? Number(row[2]) : 0;
  var budget = row ? Number(row[4]) : 0;
  if (!isFinite(value)) value = 0;
  if (!isFinite(budget)) budget = 0;
  value = Math.max(0, Math.min(100, value));
  var cost = Math.round((1.0 + value * 0.05) * 100) / 100;
  var valueBox = el('technologyLevelValue'), bar = el('technologyLevelBar'), note = el('technologyLevelNote');
  var budgetBox = el('technologyBudgetValue'), costBox = el('technologyUpgradeCost'), button = el('technologyUpgradeButton');
  if (valueBox) valueBox.textContent = value.toFixed(1) + ' / ۱۰۰';
  if (bar) {
    bar.style.width = value + '%';
    bar.style.background = value >= 70 ? 'linear-gradient(90deg,#16794b,#46d18b)' : 'linear-gradient(90deg,#a66b12,#f0c343)';
  }
  if (note) note.textContent = ST && ST.player
    ? 'سطح فناوری فعلی کشور؛ برای ارتقا هر بار ۲ واحد افزایش اعمال می‌شود.'
    : 'برای نمایش سطح فناوری، ابتدا بازی را آغاز کن.';
  if (budgetBox) budgetBox.textContent = 'بودجه کشور: ' + budget.toFixed(2) + ' میلیارد';
  if (costBox) costBox.textContent = 'هزینه ارتقای بعدی: ' + cost.toFixed(2) + ' میلیارد';
  if (button) {
    button.disabled = !ST || !ST.player || value > 98 || budget < cost;
    button.textContent = value > 98 ? '✓ سقف فناوری تکمیل شده' : '＋ ارتقای فناوری · ۲ واحد';
  }
}
function setTechnologySubview(view) {
  TECHNOLOGY_SUBVIEW = view === 'exploitation' ? 'exploitation' : 'level';
  var lv = el('technologyLevelView'), ev = el('technologyExploitationView');
  var lb = el('technologyTabLevel'), eb = el('technologyTabExploitation');
  if (lv) lv.hidden = TECHNOLOGY_SUBVIEW !== 'level';
  if (ev) ev.hidden = TECHNOLOGY_SUBVIEW !== 'exploitation';
  if (lb) { lb.className = 'eventPanelTab' + (TECHNOLOGY_SUBVIEW === 'level' ? ' active' : ''); lb.setAttribute('aria-selected', TECHNOLOGY_SUBVIEW === 'level' ? 'true' : 'false'); }
  if (eb) { eb.className = 'eventPanelTab' + (TECHNOLOGY_SUBVIEW === 'exploitation' ? ' active' : ''); eb.setAttribute('aria-selected', TECHNOLOGY_SUBVIEW === 'exploitation' ? 'true' : 'false'); }
  if (TECHNOLOGY_SUBVIEW === 'level') renderTechnologyPanel();
}
function bindTechnologyActions() {
  var lb = el('technologyTabLevel'), eb = el('technologyTabExploitation'), up = el('technologyUpgradeButton');
  if (lb) lb.onclick = function () { setTechnologySubview('level'); };
  if (eb) eb.onclick = function () { setTechnologySubview('exploitation'); };
  if (up) up.onclick = function () {
    if (!ST || !ST.player) { flash('ابتدا یک بازی را آغاز کن.'); return; }
    if (!confirm('سطح فناوری ۲ واحد افزایش یابد و هزینه از بودجه کسر شود؟')) return;
    up.disabled = true;
    var status = el('technologyUpgradeStatus');
    if (status) status.textContent = 'در حال ثبت ارتقای فناوری...';
    postJSON('api/technology/upgrade', {}, function (res) {
      if (!res || !res.ok) {
        if (status) status.textContent = (res && res.error) || 'ارتقا انجام نشد.';
        renderTechnologyPanel();
        return;
      }
      loadState(function () {
        renderTechnologyPanel();
        if (status) status.textContent = 'فناوری ۲ واحد افزایش یافت؛ هزینه ' + Number(res.cost).toFixed(2) + ' میلیارد کسر شد.';
        flash('سطح فناوری کشور به‌روزرسانی شد.');
      });
    }, function (code, response) {
      renderTechnologyPanel();
      if (status) status.textContent = netErrMsg(code, response);
    });
  };
  setTechnologySubview(TECHNOLOGY_SUBVIEW);
}
function setFactorySubview(view) {
  FACTORY_SUBVIEW = view === 'production' ? 'production' : 'projects';
  var pv = el('factoryProjectsView'), rv = el('factoryProductionView');
  var pb = el('factoryTabProjects'), rb = el('factoryTabProduction');
  if (pv) pv.hidden = FACTORY_SUBVIEW !== 'projects';
  if (rv) rv.hidden = FACTORY_SUBVIEW !== 'production';
  if (pb) { pb.className = 'eventPanelTab' + (FACTORY_SUBVIEW === 'projects' ? ' active' : ''); pb.setAttribute('aria-selected', FACTORY_SUBVIEW === 'projects' ? 'true' : 'false'); }
  if (rb) { rb.className = 'eventPanelTab' + (FACTORY_SUBVIEW === 'production' ? ' active' : ''); rb.setAttribute('aria-selected', FACTORY_SUBVIEW === 'production' ? 'true' : 'false'); }
}
function bindFactoryInnerTabs() {
  var pb = el('factoryTabProjects'), rb = el('factoryTabProduction');
  if (pb) pb.onclick = function () { setFactorySubview('projects'); };
  if (rb) rb.onclick = function () { setFactorySubview('production'); };
  setFactorySubview(FACTORY_SUBVIEW);
}
function setEventPanelView(view) {
  var valid = ['statements','military','sanctions','technology','factory'];
  EVENT_PANEL_VIEW = valid.indexOf(view) >= 0 ? view : 'statements';
  var ids = ['statements','military','sanctions','technology','factory'];
  var panelIds = ['eventStatementView','eventMilitaryView','eventSanctionsView','eventTechnologyView','eventFactoryView'];
  var tabIds = ['eventTabStatements','eventTabMilitary','eventTabSanctions','eventTabTechnology','eventTabFactory'];
  for (var i=0;i<ids.length;i++) {
    var panel = el(panelIds[i]);
    var tab = el(tabIds[i]);
    var active = EVENT_PANEL_VIEW === ids[i];
    if (panel) panel.hidden = !active;
    if (tab) { tab.className = 'eventPanelTab' + (active ? ' active' : ''); tab.setAttribute('aria-selected', active ? 'true' : 'false'); }
  }
  if (EVENT_PANEL_VIEW === 'technology') bindTechnologyActions();
  if (EVENT_PANEL_VIEW === 'factory') bindFactoryInnerTabs();
}
var CONFIDENTIAL_DRAFT = [];
var CONFIDENTIAL_TARGETS = [];
var SANCTION_DRAFT_COUNTRIES = [];
var SANCTION_TARGET_COUNTRIES = [];
var SANCTION_APPLIED = {};
var SANCTION_CATEGORIES = [
  ['goods','کالا'], ['air','مرز هوایی و فرودگاه'], ['transit','ترانزیت'],
  ['land','بستن مرز زمینی'], ['bank','ارز و بانک'], ['energy','انرژی'],
  ['technology','فناوری'], ['sea','تجارت دریایی']
];
var SANCTION_CATEGORY_STATE = {};
function eventCountryNames() {
  var names = [];
  if (MAP) for (var fa in MAP) if (Object.prototype.hasOwnProperty.call(MAP, fa)) {
    if (!ST || fa !== ST.player) names.push(fa);
  }
  names.sort(function(a,b){ return a.localeCompare(b,'fa'); });
  return names;
}
function renderCountryPicker(containerId, selected, prefix) {
  var box = el(containerId);
  if (!box) return;
  var names = eventCountryNames(), out = '';
  for (var i=0;i<names.length;i++) {
    var safe = prefix + i;
    out += '<label class="eventCountryChoice"><input type="checkbox" data-country="' +
      names[i].replace(/&/g,'&amp;').replace(/"/g,'&quot;') + '"' +
      (selected.indexOf(names[i])>=0 ? ' checked' : '') + '> <span>' +
      names[i].replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;') + '</span></label>';
  }
  box.innerHTML = out || '<div class="sanctionInfo">فهرست کشورها بارگذاری نشده است.</div>';
}
function readCountryPicker(containerId) {
  var box=el(containerId), out=[];
  if (!box) return out;
  var inputs=box.getElementsByTagName('input');
  for(var i=0;i<inputs.length;i++) if(inputs[i].checked && inputs[i].getAttribute('data-country')) out.push(inputs[i].getAttribute('data-country'));
  return out;
}
function renderConfidentialTargets() {
  var box=el('confidentialTargetBox'), list=el('confidentialCountryList'), summary=el('confidentialTargetSummary');
  var edit=el('confidentialEditCountries'), actions=box ? box.querySelector('.eventActionRow') : null;
  if(!box || !list) return;
  if(CONFIDENTIAL_TARGETS.length) {
    list.hidden=true;
    if(actions) actions.hidden=true;
    if(edit) edit.hidden=false;
    if(summary) summary.textContent='مذاکره محرمانه با '+CONFIDENTIAL_TARGETS.join('، ')+' · فهرست کشورها بسته شد.';
  } else {
    list.hidden=false;
    if(actions) actions.hidden=false;
    if(edit) edit.hidden=true;
    renderCountryPicker('confidentialCountryList',CONFIDENTIAL_DRAFT,'conf');
    if(summary) summary.textContent='کشورهای موردنظر را انتخاب کن و تأیید را بزن. انتخاب چند کشور هم‌زمان امکان‌پذیر است.';
  }
}
function bindConfidentialTargetPicker() {
  var confirm=el('confidentialConfirmCountries'), cancel=el('confidentialCancelCountries'), edit=el('confidentialEditCountries');
  if(confirm) confirm.onclick=function(){
    CONFIDENTIAL_DRAFT=readCountryPicker('confidentialCountryList');
    if(!CONFIDENTIAL_DRAFT.length) { flash('حداقل یک کشور را انتخاب کن.'); return; }
    CONFIDENTIAL_TARGETS=CONFIDENTIAL_DRAFT.slice(0);
    renderConfidentialTargets();
    renderEventTalkState();
  };
  if(cancel) cancel.onclick=function(){ CONFIDENTIAL_DRAFT=[]; CONFIDENTIAL_TARGETS=[]; renderConfidentialTargets(); renderEventTalkState(); };
  if(edit) edit.onclick=function(){ CONFIDENTIAL_DRAFT=CONFIDENTIAL_TARGETS.slice(0); renderCountryPicker('confidentialCountryList',CONFIDENTIAL_DRAFT,'conf'); el('confidentialCountryList').hidden=false; var box=el('confidentialTargetBox'); var actions=box ? box.querySelector('.eventActionRow') : null; if(actions) actions.hidden=false; edit.hidden=true; };
}
function syncSanctionState() {
  SANCTION_APPLIED = {};
  var records = ST && ST.player_sanctions ? ST.player_sanctions : {};
  var names = Object.keys(records);
  for (var i=0;i<names.length;i++) {
    var categories = (records[names[i]] || {}).categories || [], flags = {};
    for (var k=0;k<categories.length;k++) flags[categories[k]] = true;
    SANCTION_APPLIED[names[i]] = flags;
  }
}
function loadSanctionCategorySelection() {
  SANCTION_CATEGORY_STATE = {};
  var records = ST && ST.player_sanctions ? ST.player_sanctions : {};
  for (var i=0;i<SANCTION_TARGET_COUNTRIES.length;i++) {
    var record = records[SANCTION_TARGET_COUNTRIES[i]] || {};
    var cats = record.categories || [];
    for (var k=0;k<cats.length;k++) SANCTION_CATEGORY_STATE[cats[k]] = true;
  }
}
function renderSanctionTargets() {
  var summary=el('sanctionTargetSummary'), card=el('sanctionCategoryCard');
  if(summary) summary.textContent=SANCTION_TARGET_COUNTRIES.length ? 'کشورهای انتخاب‌شده: '+SANCTION_TARGET_COUNTRIES.join('، ') : 'هنوز کشوری انتخاب نشده است.';
  if(card) card.hidden=!SANCTION_TARGET_COUNTRIES.length;
}
function renderSanctionCategories() {
  var box=el('sanctionCategoryList');
  if(!box) return;
  var out='';
  for(var i=0;i<SANCTION_CATEGORIES.length;i++) {
    var key=SANCTION_CATEGORIES[i][0], label=SANCTION_CATEGORIES[i][1], on=!!SANCTION_CATEGORY_STATE[key];
    out+='<button type="button" class="sanctionCategoryToggle'+(on?' active':'')+'" data-sanction-category="'+key+'" aria-pressed="'+(on?'true':'false')+'"><span>'+label+'</span><span class="eventToggleState">'+(on?'روشن':'خاموش')+'</span></button>';
  }
  box.innerHTML=out;
  var buttons=box.getElementsByTagName('button');
  for(var b=0;b<buttons.length;b++) buttons[b].onclick=function(){
    var key=this.getAttribute('data-sanction-category');
    SANCTION_CATEGORY_STATE[key]=!SANCTION_CATEGORY_STATE[key];
    renderSanctionCategories();
  };
}
function renderAppliedSanctions() {
  var box=el('sanctionPlayerAppliedList');
  if(!box) return;
  var names=Object.keys(SANCTION_APPLIED);
  if(!names.length) { box.textContent='هنوز تحریم یک‌جانبه‌ای از طرف بازیکن اعمال نشده است.'; return; }
  var out='';
  for(var i=0;i<names.length;i++) {
    var cats=SANCTION_APPLIED[names[i]], labels=[], record=(ST.player_sanctions || {})[names[i]] || {};
    for(var k=0;k<SANCTION_CATEGORIES.length;k++) if(cats[SANCTION_CATEGORIES[k][0]]) labels.push(SANCTION_CATEGORIES[k][1]);
    out+='<div class="sanctionCard"><strong>'+dashEsc(names[i])+'</strong><div class="sanctionInfo">زمینه‌ها: '+(labels.join('، ')||'ثبت نشده')+'</div><div class="sanctionInfo">تاریخ ثبت: '+dashEsc(record.imposed_date || 'نامشخص')+' · آخرین به‌روزرسانی: '+dashEsc(record.updated_date || 'نامشخص')+'</div></div>';
  }
  box.innerHTML=out;
}
function setSanctionActionStatus(message) {
  var status=el('sanctionActionStatus');
  if(status) status.textContent=message;
}
function bindSanctionsUI() {
  var choose=el('sanctionChooseCountries'), confirm=el('sanctionConfirmCountries'), cancel=el('sanctionCancelCountries');
  if(choose) choose.onclick=function(){
    SANCTION_DRAFT_COUNTRIES=SANCTION_TARGET_COUNTRIES.slice(0);
    renderCountryPicker('sanctionCountryList',SANCTION_DRAFT_COUNTRIES,'san');
    el('sanctionCountryPicker').hidden=false;
  };
  if(confirm) confirm.onclick=function(){
    SANCTION_DRAFT_COUNTRIES=readCountryPicker('sanctionCountryList');
    SANCTION_TARGET_COUNTRIES=SANCTION_DRAFT_COUNTRIES.slice(0);
    el('sanctionCountryPicker').hidden=true;
    loadSanctionCategorySelection();
    renderSanctionCategories();
    renderSanctionTargets();
  };
  if(cancel) cancel.onclick=function(){
    SANCTION_DRAFT_COUNTRIES=[];
    SANCTION_TARGET_COUNTRIES=[];
    el('sanctionCountryPicker').hidden=true;
    renderSanctionTargets();
  };
  var apply=el('sanctionApply'), cancelAll=el('sanctionCancelAll');
  if(apply) apply.onclick=function(){
    var active=[];
    for(var i=0;i<SANCTION_CATEGORIES.length;i++) {
      var key=SANCTION_CATEGORIES[i][0];
      if(SANCTION_CATEGORY_STATE[key]) active.push(key);
    }
    if(!SANCTION_TARGET_COUNTRIES.length) { setSanctionActionStatus('ابتدا کشورهای هدف را انتخاب کن.'); return; }
    if(!active.length) { setSanctionActionStatus('حداقل یک زمینه تحریم را روشن کن.'); return; }
    apply.disabled=true;
    postJSON('api/sanctions/apply',{targets:SANCTION_TARGET_COUNTRIES,categories:active},function(r){
      apply.disabled=false;
      if(!r || !r.ok) { setSanctionActionStatus((r && r.error) || 'ثبت تحریم انجام نشد.'); return; }
      loadState(function(){
        setSanctionActionStatus('تحریم‌ها در ذخیره بازی ثبت شدند. اثر اقتصادی دسته‌بندی‌شده پس از تکمیل موتور اقتصاد در فاز C فعال می‌شود.');
        renderAppliedSanctions();
      });
    },function(st,tx){
      apply.disabled=false;
      setSanctionActionStatus(netErrMsg(st,tx)+' — تحریم ثبت نشد.');
    });
  };
  if(cancelAll) cancelAll.onclick=function(){
    cancelAll.disabled=true;
    postJSON('api/sanctions/cancel',{},function(r){
      cancelAll.disabled=false;
      if(!r || !r.ok) { setSanctionActionStatus((r && r.error) || 'لغو تحریم‌ها انجام نشد.'); return; }
      SANCTION_CATEGORY_STATE={};
      SANCTION_TARGET_COUNTRIES=[];
      loadState(function(){
        renderSanctionCategories();
        renderSanctionTargets();
        renderAppliedSanctions();
        setSanctionActionStatus('تمام تحریم‌های یک‌جانبه ثبت‌شده از طرف کشور بازیکن لغو شدند.');
      });
    },function(st,tx){
      cancelAll.disabled=false;
      setSanctionActionStatus(netErrMsg(st,tx)+' — تحریم‌ها لغو نشدند.');
    });
  };
  var imposed=el('sanctionTabImposed'), target=el('sanctionTabTarget');
  if(imposed) imposed.onclick=function(){ setSanctionInnerView('imposed'); };
  if(target) target.onclick=function(){ setSanctionInnerView('target'); };
  syncSanctionState();
  renderSanctionCategories();
  renderAppliedSanctions();
  renderSanctionTargets();
}
function setSanctionInnerView(view) {
  var imp=view!=='target', iv=el('sanctionImposedView'), tv=el('sanctionTargetView');
  var ib=el('sanctionTabImposed'), tb=el('sanctionTabTarget');
  if(iv) iv.hidden=!imp; if(tv) tv.hidden=imp;
  if(ib){ib.className='eventPanelTab'+(imp?' active':'');ib.setAttribute('aria-selected',imp?'true':'false');}
  if(tb){tb.className='eventPanelTab'+(!imp?' active':'');tb.setAttribute('aria-selected',!imp?'true':'false');}
}
function bindEventPanelTabs() {
  var sb = el('eventTabStatements'), mb = el('eventTabMilitary'), xb = el('eventTabSanctions');
  var tb = el('eventTabTechnology'), fb = el('eventTabFactory');
  if (sb) sb.onclick = function () { setEventPanelView('statements'); };
  if (mb) mb.onclick = function () { setEventPanelView('military'); };
  if (xb) xb.onclick = function () { setEventPanelView('sanctions'); };
  if (tb) tb.onclick = function () { setEventPanelView('technology'); };
  if (fb) fb.onclick = function () { setEventPanelView('factory'); };
  setEventPanelView('statements');
}
function bindStatementConversationPrepare() {
  var button=el('statementPrepareConversation');
  var dateInput=el('statementMeetingDate');
  if(dateInput){dateInput.min=calendarNextDate();if(!dateInput.value)dateInput.value=calendarNextDate();}
  if(!button) return;
  button.onclick=function() {
    if(!ST || !ST.player) { flash('ابتدا یک بازی را آغاز کن.'); return; }
    var confidential=EVENT_TALK_STATE.confidential, normal=EVENT_TALK_STATE.normal;
    var participants=confidential ? CONFIDENTIAL_TARGETS.slice(0) : (normal ? NORMAL_TARGETS.slice(0) : PUBLIC_TARGETS.slice(0));
    if(!participants.length) { flash('ابتدا کشورهای شرکت‌کننده را انتخاب و تأیید کن.'); return; }
    if(participants.length>19) { flash('حداکثر ۱۹ کشور دیگر می‌توانند در نشست باشند.'); return; }
    var visibility=confidential?'confidential':(normal?'normal':'public');
    var meetingDate=el('statementMeetingDate');
    if(!meetingDate || !meetingDate.value || meetingDate.value < calendarNextDate()) { flash('تاریخ نشست باید از فردای روز فعلی بازی به بعد باشد.'); return; }
    var payload={
      participants:participants,
      meeting_date:meetingDate.value,
      topic:EVENT_TALK_STATE.alliance?'مذاکره با اتحاد':(confidential?'مذاکره محرمانه':(normal?'مذاکره عادی':'گفت‌وگوی عمومی')),
      visibility_mode:visibility,
      negotiation_type:EVENT_TALK_STATE.alliance?'alliance':'standard',
      source:'statement',
      context:{alliance_modifier:!!EVENT_TALK_STATE.alliance,statement_mode:visibility,requested_by_player:true}
    };
    button.disabled=true;
    var status=el('statementPrepareStatus');
    if(status) status.textContent='در حال ثبت پیشنهاد تاریخ نشست...';
    postJSON('api/conversations/prepare',payload,function(res) {
      button.disabled=false;
      if(!res || !res.ok || !res.session) {
        if(status) status.textContent=(res&&res.error)||'نشست ذخیره نشد.';
        return;
      }
      if(status) status.textContent='تاریخ نشست '+res.session.meeting_date+' پیشنهاد شد؛ تا پذیرش کشور مقابل در تقویم قطعی نمی‌شود.';
      loadState(function() {
        DASH_TAB='tribune';
        if(LAST_COUNTRY_R) renderCountryPanel(LAST_COUNTRY_R);
        flash('تاریخ نشست پیشنهاد شد؛ تریبون باز شد اما تا پذیرش طرف مقابل و رسیدن موعد، گفت‌وگو قفل است.');
      });
    },function(code,response) {
      button.disabled=false;
      if(status) status.textContent=netErrMsg(code,response)+' — نشست ذخیره نشد.';
    });
  };
}
function bindEventTalkControls() {
  var cb=el('btnConfidentialTalk'), ab=el('btnAllianceTalk'), nb=el('btnNormalTalk');
  var input=el('eventStatementInput'), send=el('eventStatementSend'), feed=el('eventStatementFeed');
  if(cb) cb.onclick=function() { EVENT_TALK_STATE.confidential=!EVENT_TALK_STATE.confidential; if(EVENT_TALK_STATE.confidential) EVENT_TALK_STATE.normal=false; renderEventTalkState(); };
  if(ab) ab.onclick=function() { EVENT_TALK_STATE.alliance=!EVENT_TALK_STATE.alliance; renderEventTalkState(); };
  if(nb) nb.onclick=function() { EVENT_TALK_STATE.normal=!EVENT_TALK_STATE.normal; if(EVENT_TALK_STATE.normal) EVENT_TALK_STATE.confidential=false; renderEventTalkState(); };
  if(send) send.onclick=function() {
    if(!EVENT_TALK_STATE.confidential || !CONFIDENTIAL_TARGETS.length || !input) return;
    var message=(input.value||'').replace(/^\s+|\s+$/g,'');
    if(!message) { flash('ابتدا متن پیش‌نویس را بنویس.'); return; }
    var empty=feed?feed.querySelector('.eventStatementEmpty'):null;
    if(empty) empty.parentNode.removeChild(empty);
    var item=document.createElement('div'); item.className='eventStatementEmpty';
    item.style.cssText='margin:7px 0;padding:9px;border:1px solid #31516e;border-radius:8px;background:#101a2e;white-space:pre-wrap;';
    item.textContent='بازیکن · پیش‌نویس محرمانه\n'+message;
    if(feed) feed.appendChild(item); input.value='';
    flash('پیش‌نویس فقط در همین پنجره ثبت شد و برای کشور مقابل ارسال نشده است.');
  };
  bindConfidentialTargetPicker(); bindNormalTargetPicker(); bindPublicTargetPicker(); bindStatementConversationPrepare(); renderEventTalkState();
}


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

function renderStartSelectionProfile(r) {
  var box = el('startCountryProfile');
  if (!box) return;
  if (!r) { box.innerHTML = '<div class="startProfileEmpty">برای مشاهده مشخصات، یک کشور را انتخاب کن.</div>'; return; }
  var pc = r.political_classification || r.political_baseline || {};
  var gov = classificationValueLabel('government_form',pc.government_form) + ' · ' + classificationValueLabel('government_subform',pc.government_subform);
  var ideologyLabels = {islamism:'اسلام‌گرایی',islamic_democracy:'دموکراسی اسلامی',political_islam_conservatism:'محافظه‌کاری اسلام‌گرا',nationalism:'ملی‌گرایی',liberalism:'لیبرالیسم',conservatism:'محافظه‌کاری',socialism:'سوسیالیسم',communism:'کمونیسم',marxism_leninism:'مارکسیسم–لنینیسم',social_democracy:'سوسیال‌دموکراسی',democratic_socialism:'سوسیالیسم دموکراتیک',secularism:'سکولاریسم',monarchism:'سلطنت‌طلبی',mixed_pragmatic:'ترکیبی / عمل‌گرایانه',not_officially_declared:'اعلام‌نشده',unknown:'نامشخص'};
  var ideolParts = pc.official_ideology || [], ideolText = [], i;
  for (i=0;i<ideolParts.length;i++) ideolText.push(ideologyLabels[ideolParts[i]] || String(ideolParts[i]).replace(/_/g,' '));
  box.innerHTML = '<div class="startProfileTop">'+countryMiniBadgeHtml(r.iso3,r.name)+'</div>'+
    '<img class="startLeaderPortrait" src="'+leaderPortraitUrlForCountry(r)+'" alt="" onerror="this.style.display=\'none\';this.nextSibling.style.display=\'flex\';">'+
    '<div class="startLeaderFallback" style="display:none">👤</div>'+
    '<b class="startProfileCountryName">'+dashEsc(r.name)+'</b>'+
    '<div class="startProfileLeaderName">'+dashEsc(r.leader || 'رهبر ثبت نشده')+'</div>'+
    '<div class="startProfileFacts"><div><span>ساختار حکومت</span><b>'+dashEsc(gov)+'</b></div><div><span>ایدئولوژی رسمی</span><b>'+dashEsc(ideolText.join('، ') || 'ثبت نشده')+'</b></div></div>';
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
    renderStartSelectionProfile(r);
  }, function () { flash('خطا در دریافت اطلاعات کشور.'); });
  if (!silent) { /* آماده برای افکت‌های آینده */ }
}

var DASH_TAB = 'general';
var DASH_TABS = [
  ['general','اطلاعات عمومی'],['politics','سیاست داخلی'],['society','جمعیت و جامعه'],
  ['economy','اقتصاد و بودجه'],['resources','منابع طبیعی'],['industry','صنعت و زیرساخت'],
  ['military','وضعیت نظامی'],['relations','روابط خارجی'],['pacts','پیمان‌ها'],
  ['diplomacy','دیپلماسی'],['news','اخبار'],['calendar','تقویم'],['tribune','تریبون']
];

function calendarDaysRemaining(dateText) {
  if (!dateText || !ST || !ST.game_date) return null;
  var a=String(ST.game_date).split('-'), b=String(dateText).split('-');
  if (a.length!==3 || b.length!==3) return null;
  var current=Date.UTC(Number(a[0]),Number(a[1])-1,Number(a[2]));
  var due=Date.UTC(Number(b[0]),Number(b[1])-1,Number(b[2]));
  if (!isFinite(current) || !isFinite(due)) return null;
  return Math.max(0,Math.round((due-current)/86400000));
}
function calendarNextDate() {
  var base=(ST && ST.game_date) ? ST.game_date : '2026-11-05';
  var p=base.split('-'), d=new Date(Date.UTC(Number(p[0]),Number(p[1])-1,Number(p[2])+1));
  return d.getUTCFullYear()+'-'+('0'+(d.getUTCMonth()+1)).slice(-2)+'-'+('0'+d.getUTCDate()).slice(-2);
}
function dashEsc(v) {
  return String(v == null ? '—' : v).replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}
function dashMissing(title, detail) {
  return '<div class="dashNote"><b>⏳ ' + dashEsc(title) + '</b><br>' +
    dashEsc(detail || 'ساختار داده و منطق این قابلیت در ادامه فاز B طراحی و پیاده‌سازی می‌شود.') +
    '</div>';
}
function dashPercentBar(label, value) {
  var n = Number(value);
  if (!isFinite(n)) n = 0;
  n = Math.max(0,Math.min(100,n));
  var tone = n < 30 ? 'bad' : (n <= 50 ? 'warn' : 'good');
  return '<div class="dashPercentRow"><div class="dashPercentLabel"><span>'+dashEsc(label)+'</span><b>'+dashEsc(value)+'٪</b></div><div class="dashPercentTrack '+tone+'"><div style="width:'+n+'%"></div></div></div>';
}
function dashMetric(label, value) {
  return '<div class="dashMetric"><span class="muted small">' + dashEsc(label) +
    '</span><b>' + dashEsc(value) + '</b></div>';
}
/* نشان پرچم مشترک: در آینده همین تابع در برچسب شناور کشتی‌های تجاری استفاده می‌شود. */
function countryMiniBadgeHtml(iso3, name) {
  if (!iso3 || !/^[A-Z]{3}$/.test(iso3)) return '';
  return '<span class="countryMiniBadge" title="'+dashEsc(name || iso3)+'"><img src="assets/flags/'+iso3+'.svg" alt=""><span>'+dashEsc(name || iso3)+'</span></span>';
}
function politicalFieldLabel(key) {
  var labels = {head_of_state:'رئیس کشور',supreme_leader:'رهبر عالی',head_of_government:'رئیس دولت',
    president:'رئیس‌جمهور',prime_minister:'نخست‌وزیر',parliament_speaker:'رئیس مجلس',
    monarch:'پادشاه / فرمانروا',foreign_minister:'وزیر امور خارجه',defense_minister:'وزیر دفاع',
    scenario_note:'توضیحات سناریو',note:'یادداشت'};
  return labels[key] || key.replace(/_/g,' ');
}
function politicalValueLabel(value) {
  var values = {PLAYER_CONTROLLED:'تحت کنترل بازیکن در سناریو',
    limited_managed_electoral_competition:'رقابت انتخاباتی محدود و مدیریت‌شده',
    competitive_electoral_democracy:'دموکراسی انتخاباتی رقابتی',
    electoral_authoritarianism:'اقتدارگرایی انتخاباتی',one_party_state:'حکومت تک‌حزبی',
    absolute_monarchy:'پادشاهی مطلقه',constitutional_monarchy:'پادشاهی مشروطه',
    presidential_republic:'جمهوری ریاستی',parliamentary_republic:'جمهوری پارلمانی',
    semi_presidential_republic:'جمهوری نیمه‌ریاستی'};
  return Object.prototype.hasOwnProperty.call(values,value) ? values[value] : value;
}


function classificationValueLabel(field, value) {
  var maps = {"government_form":{"emirate":"امارت","military_government":"حکومت نظامی","monarchy":"پادشاهی","republic":"جمهوری","sultanate":"سلطنت","transitional_government":"حکومت انتقالی"},"government_subform":{"absolute_monarchy":"پادشاهی مطلقه","constitutional_monarchy":"پادشاهی مشروطه","democratic_socialist_republic":"جمهوری سوسیالیست دموکراتیک","federal_constitutional_monarchy":"پادشاهی مشروطه فدرال","federal_directorial_republic":"جمهوری شورایی فدرال","federal_parliamentary_republic":"جمهوری پارلمانی فدرال","federal_republic":"جمهوری فدرال","federal_semi_presidential_republic":"جمهوری نیمه‌ریاستی فدرال","fragmented_transitional_republic":"جمهوری انتقالی با حاکمیت چندپاره","hereditary_emirate":"امارت موروثی","interim_self_governing_authority":"حاکمیت خودگردان موقت","islamic_emirate":"امارت اسلامی","islamic_republic":"جمهوری اسلامی","military_junta":"حکومت شورای نظامی","military_led_transitional_authority":"حاکمیت انتقالی با رهبری نظامی","parliamentary_republic":"جمهوری پارلمانی","presidential_republic":"جمهوری ریاستی","semi_presidential_republic":"جمهوری نیمه‌ریاستی","socialist_republic":"جمهوری سوسیالیستی","transitional_authority":"حاکمیت انتقالی","transitional_presidential_authority":"حاکمیت ریاستی انتقالی"},"executive_legislative_system":{"directorial":"شورایی / هیئتی","military_council":"شورای نظامی","mixed":"ترکیبی / ویژه","monarchical_executive":"قوه مجریه سلطنتی","no_functioning_national_legislature":"بدون مجلس ملی فعال","one_party":"نظام تک‌حزبی","parliamentary":"پارلمانی","presidential":"ریاستی","semi_presidential":"نیمه‌ریاستی","transitional":"انتقالی"},"territorial_structure":{"asymmetric_devolution":"واگذاری نامتقارن اختیارات","devolved_unitary":"دولت واحد با اختیارات واگذارشده","federal":"فدرال","occupied_or_fragmented":"اشغال‌شده یا چندپاره","transitional_or_disputed":"انتقالی یا مورد اختلاف","unitary":"دولت واحد"},"regime_character":{"closed_authoritarian":"اقتدارگرایی بسته","electoral_authoritarian":"اقتدارگرایی انتخاباتی","electoral_democracy":"دموکراسی انتخاباتی","flawed_or_limited_democracy":"دموکراسی محدود / ناقص","fragmented_authority":"حاکمیت چندپاره","hybrid_regime":"رژیم ترکیبی","liberal_democracy":"دموکراسی لیبرال","military_rule":"حکومت نظامی","one_party_authoritarian":"اقتدارگرایی تک‌حزبی","transitional_or_uncertain":"گذار سیاسی یا وضعیت نامطمئن"},"party_system":{"competitive_multi_party":"چندحزبی رقابتی","dominant_party_competitive":"حزب مسلط با رقابت","dominant_party_noncompetitive":"حزب مسلط بدون رقابت مؤثر","fragmented_or_uncertain":"چندپاره یا نامشخص","no_legal_party_system":"بدون نظام حزبی قانونی","nonpartisan":"غیرحزبی","one_party_legal":"تک‌حزبی قانونی","restricted_party_system":"نظام حزبی محدود","two_party_dominant":"دوحزبی غالب"}};
  if (value == null || value === '') return 'ثبت نشده';
  return maps[field] && maps[field][value] ? maps[field][value] : String(value).replace(/_/g,' ');
}
function classificationIdeologyHtml(title, values, missingText, ideologyNames) {
  var out = '<div class="dashCard"><div class="muted small">'+dashEsc(title)+'</div>';
  if (values && values.length) {
    for (var i=0;i<values.length;i++) {
      var id=values[i], label=ideologyNames[id] || String(id).replace(/_/g,' ');
      out += '<span class="badge">'+dashEsc(label)+'</span>';
    }
  } else {
    out += '<div class="muted">'+dashEsc(missingText)+'</div>';
  }
  return out + '</div>';
}

var POLITICAL_EDIT_OPTIONS = {
  government_form: [
    ["republic","جمهوری"],["monarchy","پادشاهی"],["emirate","امارت"],
    ["sultanate","سلطنت"],["theocracy","حکومت دینی"],["military_government","حکومت نظامی"],
    ["transitional_government","حکومت انتقالی"],["other","سایر"],["unknown","نامشخص"]
  ],
  government_subform: [
    ["absolute_monarchy","پادشاهی مطلقه"],["constitutional_monarchy","پادشاهی مشروطه"],
    ["parliamentary_monarchy","پادشاهی پارلمانی"],["federal_constitutional_monarchy","پادشاهی مشروطه فدرال"],
    ["hereditary_emirate","امارت موروثی"],["islamic_emirate","امارت اسلامی"],
    ["islamic_republic","جمهوری اسلامی"],["presidential_republic","جمهوری ریاستی"],
    ["parliamentary_republic","جمهوری پارلمانی"],["semi_presidential_republic","جمهوری نیمه‌ریاستی"],
    ["federal_republic","جمهوری فدرال"],["federal_parliamentary_republic","جمهوری پارلمانی فدرال"],
    ["federal_semi_presidential_republic","جمهوری نیمه‌ریاستی فدرال"],["socialist_republic","جمهوری سوسیالیستی"],
    ["democratic_socialist_republic","جمهوری سوسیالیستی دموکراتیک"],["federal_directorial_republic","جمهوری شورایی فدرال"],
    ["military_junta","شورای نظامی"],["military_led_transitional_authority","حکومت انتقالی با رهبری نظامی"],
    ["transitional_authority","حاکمیت انتقالی"],["transitional_presidential_authority","حاکمیت انتقالی ریاستی"],
    ["fragmented_transitional_republic","جمهوری انتقالی چندپاره"],["interim_self_governing_authority","حاکمیت خودگردان موقت"]
  ],
  executive_legislative_system: [
    ["presidential","ریاستی"],["semi_presidential","نیمه‌ریاستی"],["parliamentary","پارلمانی"],
    ["directorial","شورایی / هیئتی"],["monarchical_executive","اجرایی سلطنتی"],
    ["one_party","تک‌حزبی"],["military_council","شورای نظامی"],["transitional","انتقالی"],
    ["mixed","مختلط"],["no_functioning_national_legislature","بدون مجلس ملی فعال"],["unknown","نامشخص"]
  ],
  territorial_structure: [
    ["unitary","یکپارچه"],["federal","فدرال"],["confederal","کنفدرال"],
    ["devolved_unitary","یکپارچه با واگذاری اختیارات"],["asymmetric_devolution","واگذاری نامتقارن اختیارات"],
    ["occupied_or_fragmented","اشغالی یا چندپاره"],["transitional_or_disputed","انتقالی یا مورد اختلاف"],["unknown","نامشخص"]
  ],
  regime_character: [
    ["liberal_democracy","دموکراسی لیبرال"],["electoral_democracy","دموکراسی انتخاباتی"],
    ["flawed_or_limited_democracy","دموکراسی ناقص یا محدود"],["hybrid_regime","نظام ترکیبی"],
    ["electoral_authoritarian","اقتدارگرایی انتخاباتی"],["closed_authoritarian","اقتدارگرایی بسته"],
    ["one_party_authoritarian","اقتدارگرایی تک‌حزبی"],["military_rule","حکومت نظامی"],
    ["transitional_or_uncertain","انتقالی یا نامطمئن"],["fragmented_authority","حاکمیت چندپاره"],["unknown","نامشخص"]
  ],
  party_system: [
    ["competitive_multi_party","چندحزبی رقابتی"],["two_party_dominant","غلبه دو حزب"],
    ["dominant_party_competitive","حزب مسلط با رقابت"],["dominant_party_noncompetitive","حزب مسلط بدون رقابت مؤثر"],
    ["one_party_legal","تک‌حزبی قانونی"],["no_legal_party_system","بدون نظام حزبی قانونی"],
    ["restricted_party_system","نظام حزبی محدود"],["nonpartisan","غیرحزبی"],
    ["fragmented_or_uncertain","چندپاره یا نامطمئن"],["unknown","نامشخص"]
  ],
  official_ideology: [
    ["communism","کمونیسم"],["marxism_leninism","مارکسیسم–لنینیسم"],["socialism","سوسیالیسم"],
    ["democratic_socialism","سوسیالیسم دموکراتیک"],["social_democracy","سوسیال‌دموکراسی"],
    ["liberalism","لیبرالیسم"],["classical_liberalism","لیبرالیسم کلاسیک"],["conservatism","محافظه‌کاری"],
    ["liberal_conservatism","محافظه‌کاری لیبرال"],["national_conservatism","محافظه‌کاری ملی"],
    ["christian_democracy","دموکراسی مسیحی"],["nationalism","ملی‌گرایی"],["civic_nationalism","ملی‌گرایی مدنی"],
    ["ethnic_nationalism","ملی‌گرایی قومی"],["islamism","اسلام‌گرایی"],["islamic_democracy","دموکراسی اسلامی"],
    ["political_islam_conservatism","محافظه‌کاری اسلام‌گرا"],["secularism","سکولاریسم"],
    ["green_politics","سیاست سبز"],["libertarianism","لیبرتارینیسم"],["populism","پوپولیسم"],
    ["progressivism","ترقی‌خواهی"],["fascism","فاشیسم"],["far_right","راست افراطی"],
    ["anarchism","آنارشیسم"],["monarchism","سلطنت‌طلبی"],["baathism","بعث‌گرایی"],["juche","جوچه"],
    ["military_nationalism","ملی‌گرایی نظامی"],["mixed_pragmatic","ترکیبی / عمل‌گرایانه"],
    ["other","سایر"],["not_officially_declared","اعلام‌نشده"],["unknown","نامشخص"],
    ["social_liberalism","لیبرالیسم اجتماعی"]
  ]
};
POLITICAL_EDIT_OPTIONS.ruling_party_ideology = POLITICAL_EDIT_OPTIONS.official_ideology;
POLITICAL_EDIT_OPTIONS.ruling_coalition_ideology = POLITICAL_EDIT_OPTIONS.official_ideology;

function politicalEditSelect(field, label, current) {
  var opts = POLITICAL_EDIT_OPTIONS[field] || [], multi = field.indexOf("ideology") >= 0;
  var h = '<label style="display:block;margin:7px 0;color:#c8d6e8;font-size:11px">' + label;
  h += '<select id="politicalEdit_' + field + '"' + (multi ? ' multiple size="4"' : '') +
    ' style="display:block;width:100%;margin-top:4px;background:#101a2e;color:#e4edf8;border:1px solid #354b6d;border-radius:6px;padding:7px;font-family:Tahoma;font-size:11px">';
  if (!multi) h += '<option value="">بدون تغییر</option>';
  for (var i=0;i<opts.length;i++) {
    var selected = multi ? (current && current.indexOf(opts[i][0]) >= 0) : current === opts[i][0];
    h += '<option value="' + opts[i][0] + '"' + (selected ? ' selected' : '') + '>' + opts[i][1] + '</option>';
  }
  h += '</select></label>';
  return h;
}

function politicalChangeFormHtml(pc, isPlayer) {
  if (!isPlayer) return '<div class="dashNote">تغییر ساختار سایر کشورها از این پنل ممکن نیست. تصمیم‌گیری خودکار کشورها فقط پس از فعال‌شدن هوش مصنوعی زنده در آینده اضافه خواهد شد.</div>';
  pc = pc || {};
  var proposalList = (ST && ST.political_reform_proposals) || [];
  var activeProposal = null, terminalProposal = null, pi;
  for (pi=proposalList.length-1;pi>=0;pi--) {
    if (proposalList[pi].country !== (ST && ST.player)) continue;
    if (!terminalProposal && (proposalList[pi].status === 'completed' || proposalList[pi].status === 'failed')) terminalProposal = proposalList[pi];
    if (!activeProposal && ['pending','reviewed','approved','executing','paused_funds','paused_crisis'].indexOf(proposalList[pi].status) >= 0) activeProposal = proposalList[pi];
    if (activeProposal && terminalProposal) break;
  }
  var h = '<div class="dashCard" id="politicalChangeCard"><h3>📜 پیشنهاد اصلاح ساختار سیاسی</h3>';
  h += '<div class="dashNote">تغییرات ابتدا به‌صورت طرح ثبت و ارزیابی می‌شوند. پس از تصویب، اجرای مرحله‌ای از روز بعد آغاز می‌شود؛ هزینه در اقساط روزانه پرداخت خواهد شد و تغییر نهایی فقط پس از تکمیل موفق طرح اعمال می‌شود. هوش مصنوعی کشورها تا فعال‌شدن هوش مصنوعی زنده غیرفعال می‌ماند.</div>';
  if (terminalProposal) {
    var terminalOk = terminalProposal.status === 'completed';
    h += '<div class="reformOutcome '+(terminalOk ? 'success' : 'failure')+'"><b>'+(terminalOk ? '✅ طرح اصلاحات پذیرفته و اجرا شد' : '⚠️ طرح اصلاحات پذیرفته نشد')+'</b>';
    h += '<div>طرح شماره '+dashEsc(terminalProposal.id)+' · '+dashEsc(terminalProposal.completed_date || terminalProposal.last_update_date || '')+'</div>';
    h += '<div>'+(terminalOk ? 'تغییرات ثبت‌شده در ساختار سیاسی فعلی اعمال شده‌اند.' : 'تغییرات نهایی اعمال نشدند و ساختار قبلی حفظ شده است.')+'</div></div>';
  }
  if (activeProposal) {
    var statusLabel = {pending:'در انتظار بررسی',reviewed:'ارزیابی شده؛ منتظر تصمیم بازیکن',approved:'تصویب شده؛ آماده آغاز اجرا',executing:'در حال اجرا',paused_funds:'توقف موقت؛ بودجه کافی نیست',paused_crisis:'توقف موقت؛ بحران سیاسی'};
    h += '<div class="dashCard"><b>طرح شماره '+dashEsc(activeProposal.id)+'</b><div class="row"><span>وضعیت</span><b>'+dashEsc(statusLabel[activeProposal.status] || activeProposal.status)+'</b></div>';
    h += '<div class="row"><span>هزینه برآوردی</span><b>'+dashEsc(activeProposal.estimated_cost)+' میلیارد</b></div>';
    h += '<div class="row"><span>زمان برآوردی</span><b>'+dashEsc(activeProposal.estimated_days)+' روز</b></div>';
    h += '<div class="dashNote">'+(activeProposal.status === 'completed' ? 'اصلاحات با موفقیت اعمال شده‌اند.' : (activeProposal.status === 'failed' ? 'اجرای طرح ناموفق بود؛ تغییرات اعمال نشدند.' : 'تا پایان موفق اجرای طرح، ساختار فعلی کشور بدون تغییر می‌ماند.'))+'</div>';
    if (activeProposal.impact) {
      var impact = activeProposal.impact;
      h += '<div class="dashCard"><b>پیامدهای داخلی طرح</b>';
      if (impact.themes && impact.themes.length) h += '<div class="row"><span>محورهای اصلاحات</span><b>'+dashEsc(impact.themes.join('، '))+'</b></div>';
      if (impact.public_response && impact.public_response.length) {
        for (var ir=0;ir<impact.public_response.length;ir++) h += '<div class="dashNote">'+dashEsc(impact.public_response[ir])+'</div>';
      }
      if (impact.headlines && impact.headlines.length) {
        h += '<div class="muted small">آخرین واکنش رسانه‌ای</div>';
        h += '<div class="dashNote">'+dashEsc(impact.headlines[impact.headlines.length-1])+'</div>';
      }
      h += '<div class="dashNote">'+dashEsc(impact.risk_note || 'واکنش‌ها برآورد شبیه‌سازی بازی هستند.')+'</div></div>';
    }
    if (activeProposal.status === 'approved' || activeProposal.status === 'executing' || activeProposal.status === 'paused_funds' || activeProposal.status === 'paused_crisis') {
      h += '<div class="row"><span>پیشرفت اجرا</span><b>'+dashEsc(activeProposal.progress || 0)+'٪</b></div>';
      h += '<div class="row"><span>هزینه پرداخت‌شده</span><b>'+dashEsc(activeProposal.spent_cost || 0)+' از '+dashEsc(activeProposal.estimated_cost)+' میلیارد</b></div>';
      h += '<div class="dashNote">با گذشت هر روز بازی، یک مرحله از هزینه پرداخت و پیشرفت طرح ثبت می‌شود. در صورت کمبود بودجه، اجرا تا تأمین اعتبار متوقف می‌ماند.</div>';
    }
    if (activeProposal.status === 'pending') {
      h += '<button type="button" id="btnReviewPoliticalProposal" class="primary" data-proposal-id="'+dashEsc(activeProposal.id)+'">ارزیابی پیامدها</button> ';
    } else if (activeProposal.status === 'reviewed') {
      var rv=activeProposal.review || {};
      h += '<div class="dashCard"><b>نتیجه ارزیابی</b><div class="row"><span>امکان‌پذیری تقریبی</span><b>'+dashEsc(rv.feasibility)+' از ۱۰۰</b></div>';
      h += '<div class="row"><span>ثبات سیاسی</span><b>'+dashEsc(rv.stability)+'</b></div><div class="row"><span>توان مالی</span><b>'+dashEsc(rv.affordability)+'</b></div>';
      h += '<div class="row"><span>شاخص واکنش احزاب</span><b>'+dashEsc(rv.party_score)+'</b></div><div class="dashNote">'+dashEsc(rv.outlook || '')+'</div>';
      var rr=rv.party_reactions || {};
      for (var pn in rr) if (rr.hasOwnProperty(pn)) h += '<div class="row"><span>'+dashEsc(pn)+'</span><b>'+dashEsc(rr[pn].current)+'٪ ← '+dashEsc(rr[pn].projected)+'٪</b></div>';
      h += '<div class="row"><span>شاخص حمایت اجتماعی</span><b>'+dashEsc(rv.social_score)+' از ۱۰۰</b></div>';
      var sr=rv.social_reactions || {};
      h += '<div class="muted small">پیش‌بینی تغییر حمایت گروه‌های اجتماعی</div>';
      for (var sn in sr) if (sr.hasOwnProperty(sn)) h += '<div class="row"><span>'+dashEsc(sn)+'</span><b>'+dashEsc(sr[sn].current)+'٪ ← '+dashEsc(sr[sn].projected)+'٪</b></div>';
      h += '<div class="dashNote">'+dashEsc(rv.note || '')+'</div></div>';
      h += '<button type="button" id="btnApprovePoliticalProposal" class="primary" data-proposal-id="'+dashEsc(activeProposal.id)+'">تصویب و آماده‌سازی اجرا</button> ';
      h += '<button type="button" id="btnRejectPoliticalProposal" class="secondary" data-proposal-id="'+dashEsc(activeProposal.id)+'">رد طرح</button> ';
    }
    if (activeProposal.status === 'pending' || activeProposal.status === 'reviewed') h += '<button type="button" id="btnCancelPoliticalProposal" class="secondary" data-proposal-id="'+dashEsc(activeProposal.id)+'">لغو طرح</button>';
    h += '</div>';
  }

  var socialGroups = (ST && ST.social_groups) || {};
  h += '<div class="dashCard"><b>📊 مقبولیت گروه‌های اجتماعی</b><div class="dashNote">درصدها شاخص‌های شبیه‌سازی بازی هستند و داده واقعی نظرسنجی محسوب نمی‌شوند.</div>';
  for (var sg in socialGroups) if (socialGroups.hasOwnProperty(sg)) {
    h += dashPercentBar(sg,socialGroups[sg]);
  }
  h += '</div>';

  var politicalHistory = (ST && ST.political_history) || [];
  if (politicalHistory.length) {
    h += '<div class="dashCard"><b>📚 گزارش تاریخی اصلاحات سیاسی</b>';
    var historyStart = Math.max(0, politicalHistory.length - 3);
    for (var ph=historyStart;ph<politicalHistory.length;ph++) {
      var historyItem = politicalHistory[ph] || {};
      var historyImpact = historyItem.impact || {};
      h += '<div class="dashNote"><b>طرح شماره '+dashEsc(historyItem.proposal_id)+'</b> · '+dashEsc(historyItem.date || '')+' · '+dashEsc((historyImpact.themes || []).join('، '))+'</div>';
      var finalGroups = historyItem.social_groups_final || historyImpact.social_groups_final || {};
      for (var fg in finalGroups) if (finalGroups.hasOwnProperty(fg)) {
        h += '<div class="row"><span>'+dashEsc(fg)+'</span><b>'+dashEsc(finalGroups[fg])+'٪</b></div>';
      }
    }
    h += '</div>';
  }

  h += '<div class="dashGrid">';
  h += politicalEditSelect('government_form','نوع حکومت',pc.government_form);
  h += politicalEditSelect('government_subform','زیرنوع حکومت',pc.government_subform);
  h += politicalEditSelect('executive_legislative_system','مدل اجرایی و تقنینی',pc.executive_legislative_system);
  h += politicalEditSelect('territorial_structure','ساختار سرزمینی',pc.territorial_structure);
  h += politicalEditSelect('regime_character','ویژگی نظام سیاسی',pc.regime_character);
  h += politicalEditSelect('party_system','نظام حزبی',pc.party_system);
  h += '</div><h4 style="color:#ffd479;margin:10px 0 4px">ایدئولوژی‌ها · برای انتخاب چند مورد، Ctrl را نگه دار</h4>';
  h += politicalEditSelect('official_ideology','ایدئولوژی رسمی',pc.official_ideology);
  h += politicalEditSelect('ruling_party_ideology','گرایش حزب حاکم',pc.ruling_party_ideology);
  h += politicalEditSelect('ruling_coalition_ideology','گرایش ائتلاف حاکم',pc.ruling_coalition_ideology);
  if (!activeProposal) h += '<button type="button" id="btnApplyPoliticalChange" class="primary" style="width:100%;margin-top:8px">ارسال طرح اصلاحات</button>';
  h += '<div id="politicalChangeStatus" class="small muted" style="margin-top:7px" aria-live="polite"></div></div>';
  return h;
}

function bindPoliticalChangeForm(r) {
  var reviewBtn = el('btnReviewPoliticalProposal');
  if (reviewBtn) reviewBtn.onclick = function () {
    reviewBtn.disabled = true;
    postJSON('api/political/review', {proposal_id:reviewBtn.getAttribute('data-proposal-id')}, function(res) {
      if (!res.ok) { reviewBtn.disabled=false; flash(res.error || 'ارزیابی طرح ناموفق بود.'); return; }
      flash(res.out || 'ارزیابی انجام شد.');
      loadState(function () { if (SELECTED) selectCountry(SELECTED, true); });
    }, function(st,tx) { reviewBtn.disabled=false; flash(netErrMsg(st,tx)); });
  };
  function decidePoliticalProposal(button, decision) {
    if (!button) return;
    button.onclick = function () {
      var question = decision === 'approve' ? 'این طرح تصویب شود؟ اجرای مرحله‌ای آن از روز بعد آغاز می‌شود.' : 'این طرح رد شود؟';
      if (!window.confirm(question)) return;
      button.disabled = true;
      postJSON('api/political/decision', {proposal_id:button.getAttribute('data-proposal-id'), decision:decision}, function(res) {
        if (!res.ok) { button.disabled=false; flash(res.error || 'ثبت تصمیم ناموفق بود.'); return; }
        flash(res.out || 'تصمیم ثبت شد.');
        loadState(function () { if (SELECTED) selectCountry(SELECTED, true); });
      }, function(st,tx) { button.disabled=false; flash(netErrMsg(st,tx)); });
    };
  }
  decidePoliticalProposal(el('btnApprovePoliticalProposal'), 'approve');
  decidePoliticalProposal(el('btnRejectPoliticalProposal'), 'reject');
  var cancelBtn = el('btnCancelPoliticalProposal');
  if (cancelBtn) cancelBtn.onclick = function () {
    if (!window.confirm('طرح اصلاحات لغو شود؟')) return;
    cancelBtn.disabled = true;
    postJSON('api/political/cancel', {proposal_id:cancelBtn.getAttribute('data-proposal-id')}, function(res) {
      if (!res.ok) { cancelBtn.disabled=false; flash(res.error || 'لغو طرح ناموفق بود.'); return; }
      flash(res.out || 'طرح لغو شد.');
      loadState(function () { if (SELECTED) selectCountry(SELECTED, true); });
    }, function(st,tx) { cancelBtn.disabled=false; flash(netErrMsg(st,tx)); });
  };
  var btn = el('btnApplyPoliticalChange');
  if (!btn) return;
  btn.onclick = function () {
    var fields = ['government_form','government_subform','executive_legislative_system',
      'territorial_structure','regime_character','party_system'];
    var changes = {}, i, node;
    for (i=0;i<fields.length;i++) {
      node = el('politicalEdit_' + fields[i]);
      if (node && node.value) changes[fields[i]] = node.value;
    }
    var ideologies = ['official_ideology','ruling_party_ideology','ruling_coalition_ideology'];
    for (i=0;i<ideologies.length;i++) {
      node = el('politicalEdit_' + ideologies[i]);
      if (!node) continue;
      var selected = [], j;
      for (j=0;j<node.options.length;j++) if (node.options[j].selected) selected.push(node.options[j].value);
      if (selected.length) changes[ideologies[i]] = selected;
    }
    if (!Object.keys(changes).length) { flash('حداقل یک مورد را برای تغییر انتخاب کن.'); return; }
    btn.disabled = true;
    postJSON('api/political/change', {changes:changes}, function (res) {
      btn.disabled = false;
      var status = el('politicalChangeStatus');
      if (status) status.textContent = res.out || res.error || (res.ok ? 'ثبت شد.' : 'خطا');
      if (!res.ok) { flash(res.error || 'تغییر سیاسی ثبت نشد.'); return; }
      flash(res.out || 'طرح اصلاحات ثبت شد.');
      loadState(function () { if (SELECTED) selectCountry(SELECTED, true); });
    }, function (st, tx) {
      btn.disabled = false;
      flash(netErrMsg(st, tx) + ' — تغییر سیاسی ثبت نشد.');
    });
  };
}


function politicalCurrentStatusHtml(pc, baseline) {
  if (!pc) return dashMissing('وضعیت سیاسی فعلی','اطلاعات جاری سیاسی کشور در ذخیره بازی موجود نیست.');
  var fields = [
    ['government_form','نوع حکومت'],['government_subform','زیرنوع حکومت'],
    ['executive_legislative_system','مدل اجرایی و تقنینی'],
    ['territorial_structure','ساختار سرزمینی'],['regime_character','ویژگی نظام سیاسی'],
    ['party_system','نظام حزبی']
  ];
  var h = '<h3>📍 وضعیت سیاسی فعلی در بازی</h3><div class="dashCard">';
  var changed = false;
  for (var i=0;i<fields.length;i++) {
    var key=fields[i][0], value=pc[key];
    var isChanged = baseline && JSON.stringify(value) !== JSON.stringify(baseline[key]);
    if (isChanged) changed = true;
    h += '<div class="row"><span class="muted">'+dashEsc(fields[i][1])+'</span><b>'+dashEsc(classificationValueLabel(key,value))+'</b></div>';
  }
  h += '</div>';
  var ideologyNames = {communism:'کمونیسم',marxism_leninism:'مارکسیسم–لنینیسم',socialism:'سوسیالیسم',democratic_socialism:'سوسیالیسم دموکراتیک',social_democracy:'سوسیال‌دموکراسی',liberalism:'لیبرالیسم',classical_liberalism:'لیبرالیسم کلاسیک',conservatism:'محافظه‌کاری',liberal_conservatism:'محافظه‌کاری لیبرال',national_conservatism:'محافظه‌کاری ملی',christian_democracy:'دموکراسی مسیحی',nationalism:'ملی‌گرایی',civic_nationalism:'ملی‌گرایی مدنی',ethnic_nationalism:'ملی‌گرایی قومی',islamism:'اسلام‌گرایی',islamic_democracy:'دموکراسی اسلامی',political_islam_conservatism:'محافظه‌کاری اسلام‌گرا',secularism:'سکولاریسم',green_politics:'سیاست سبز',libertarianism:'لیبرتارینیسم',populism:'پوپولیسم',progressivism:'ترقی‌خواهی',fascism:'فاشیسم',far_right:'راست افراطی',anarchism:'آنارشیسم',monarchism:'سلطنت‌طلبی',baathism:'بعث‌گرایی',juche:'جوچه',military_nationalism:'ملی‌گرایی نظامی',mixed_pragmatic:'ترکیبی / عمل‌گرایانه',other:'سایر',not_officially_declared:'اعلام‌نشده',unknown:'نامشخص',social_liberalism:'لیبرالیسم اجتماعی'};
  h += classificationIdeologyHtml('ایدئولوژی رسمی فعلی حکومت',pc.official_ideology,'ایدئولوژی رسمی فعلی ثبت نشده است.',ideologyNames);
  if (changed) h += '<div class="dashNote">برخی محورهای ساختار سیاسی نسبت به baseline آغاز سناریو تغییر کرده‌اند؛ مرجع اولیه در بخش بعدی محفوظ است.</div>';
  else h += '<div class="dashNote">ساختار فعلی هنوز با طبقه‌بندی پایه آغاز سناریو یکسان است.</div>';
  return h;
}

function politicalClassificationHtml(pc) {
  if (!pc) return dashMissing('طبقه‌بندی سیاسی پایه','اطلاعات طبقه‌بندی ساختاریافته برای این کشور در ذخیره بازی موجود نیست.');
  var names = {"communism":"کمونیسم","marxism_leninism":"مارکسیسم–لنینیسم","socialism":"سوسیالیسم","democratic_socialism":"سوسیالیسم دموکراتیک","social_democracy":"سوسیال‌دموکراسی","liberalism":"لیبرالیسم","classical_liberalism":"لیبرالیسم کلاسیک","conservatism":"محافظه‌کاری","liberal_conservatism":"محافظه‌کاری لیبرال","national_conservatism":"محافظه‌کاری ملی","christian_democracy":"دموکراسی مسیحی","nationalism":"ملی‌گرایی","civic_nationalism":"ملی‌گرایی مدنی","ethnic_nationalism":"ملی‌گرایی قومی","islamism":"اسلام‌گرایی","islamic_democracy":"دموکراسی اسلامی","political_islam_conservatism":"محافظه‌کاری اسلام‌گرا","secularism":"سکولاریسم","green_politics":"سیاست سبز / محیط‌زیست‌گرایی","libertarianism":"لیبرتارینیسم","populism":"پوپولیسم","progressivism":"ترقی‌خواهی","fascism":"فاشیسم","far_right":"راست افراطی","anarchism":"آنارشیسم","monarchism":"سلطنت‌طلبی","baathism":"بعث‌گرایی","juche":"جوچه","military_nationalism":"ملی‌گرایی نظامی","mixed_pragmatic":"ترکیبی / عمل‌گرایانه","other":"سایر","not_officially_declared":"ایدئولوژی رسمی اعلام‌نشده","unknown":"نامشخص","social_liberalism":"لیبرالیسم اجتماعی"}, fields = [
    ['government_form','نوع حکومت'],['government_subform','زیرنوع حکومت'],
    ['executive_legislative_system','مدل رابطه قوه مجریه و مقننه'],
    ['territorial_structure','ساختار سرزمینی'],['regime_character','ویژگی رژیم سیاسی'],
    ['party_system','نظام حزبی']
  ];
  var out='<h3>🧭 طبقه‌بندی سیاسی پایه · آغاز سناریو</h3><div class="dashCard">';
  for(var i=0;i<fields.length;i++) {
    var key=fields[i][0], value=pc[key];
    out+='<div class="row"><span class="muted">'+dashEsc(fields[i][1])+'</span><b>'+dashEsc(classificationValueLabel(key,value))+'</b></div>';
  }
  out+='</div><h3>گرایش‌های ایدئولوژیک</h3>';
  out+=classificationIdeologyHtml('ایدئولوژی رسمی حکومت',pc.official_ideology,'ایدئولوژی رسمی جداگانه‌ای ثبت نشده است.',names);
  out+=classificationIdeologyHtml('گرایش حزب / جریان حاکم',pc.ruling_party_ideology,'حزب یا جریان حاکمِ قابل انتساب ثبت نشده است.',names);
  out+=classificationIdeologyHtml('گرایش ائتلاف حاکم',pc.ruling_coalition_ideology,'ائتلاف حاکمِ قابل طبقه‌بندی ثبت نشده است.',names);
  if(pc.ideology_notes) out+='<div class="dashNote">'+dashEsc(pc.ideology_notes)+'</div>';
  var quality=pc.data_quality || {};
  out+='<div class="dashNote">تاریخ مرجع سناریو: '+dashEsc(quality.scenario_snapshot_date || 'ثبت نشده')+
    ' · اطمینان طبقه‌بندی: '+dashEsc(pc.classification_confidence || 'نامشخص')+
    ' · منابع ثبت‌شده: '+dashEsc((pc.classification_sources || []).length)+'</div>';
  out+='<div class="dashNote">این بخش، baseline ثابت آغاز سناریو را نشان می‌دهد؛ با تغییرات آینده در سیاست داخلی بازی، مقدار پویا جداگانه به‌روزرسانی خواهد شد و این داده مرجع بازنویسی نمی‌شود.</div>';
  return out;
}

var LEADER_COMMONS_FILES = {
        IRN: 'Portrait of Mojtaba Khamenei.jpg',
        USA: 'January 2025 Official Presidential Portrait of Donald J. Trump.jpg',
        RUS: 'Vladimir Putin (2026 02 23).jpg',
        CHN: 'Xi Jinping - 2026 (55063342986) (cropped).jpg',
        GBR: 'Official portrait of Keir Starmer.jpg',
        DEU: 'Friedrich Merz 2025 (cropped).jpg',
        FRA: 'Emmanuel Macron portrait.jpg',
        TUR: 'Recep Tayyip Erdogan (2020-01-19) (cropped).jpg',
        SAU: 'الصورة الرسمية لخادم الحرمين الشريفين الملك سلمان بن عبدالعزيز آل سعود.jpg',
        ARE: 'Mohammed bin Zayed portrait.jpg',
        IRQ: "Mohammed Shia' Al Sudani in 2025 (cropped).jpg",
        SYR: 'Ahmed al-Sharaa in March 2026.jpg',
        JPN: 'Official portrait of Sanae Takaichi, Prime Minister of Japan (HD).jpg',
        IND: 'Official Photograph of Prime Minister Narendra Modi Portrait.png',
        KOR: 'President Lee Jae Myung.jpg',
        IDN: 'Prabowo Subianto 2024 official portrait.jpg',
        BRA: '09.07.2026 - Presidente Lula.jpg',
        AUS: 'Anthony Albanese Official Portrait.jpg',
        UKR: 'Volodymyr Zelensky Official portrait.jpg',
        CAN: 'Mark Carney im Bundeskanzleramt 2025 (cropped).jpg',
        ITA: 'Giorgia Meloni Official 2024 (cropped).jpg',
        POL: 'Donald Tusk 2025.jpg',
        ARG: 'Retrato oficial del Presidente Javier Milei.png',
        ZAF: 'Cyril Ramaphosa in 2026.jpg',
        MYS: 'Anwar Ibrahim June 2025.jpg',
        PAK: 'Shehbaz Sharif - 2025 (cropped).jpg',
        MEX: 'Claudia Sheinbaum en Noviembre 2025.jpg',
        LBN: 'Official Portrait of the President of the Republic of Lebanon.jpg',
        JOR: 'Abdullah II portrait at 10 Downing Street February 2026 (cropped).jpg',
        ISR: 'Israeli Prime Minister Benjamin Netanyahu 20260225.jpg',
        PSE: 'Mahmoud Abbas 2025-05-10 (cropped).jpg',
        QAT: 'Tamim bin Hamad Al Thani in October 2026.jpg',
        KWT: 'Emir of Kuwait Sheikh Mishal Al-Ahmad Al-Jaber Al-Sabah.jpg',
        BHR: 'Hamad-Bin-Isa-Al-Khalifa.jpg',
        OMN: 'Official portrait of Sultan Haitham bin Tariq (2021) (cropped).jpg',
        YEM: 'Rashad al-Alimi 2022 (cropped).jpg',
        EGY: 'Abdel Fattah el-Sisi - 2023.jpg',
        LBY: 'Mohamed al-Menfi Moscow 2026.jpg',
        MAR: 'King Mohammed VI (cropped).jpg',
        DZA: 'Abdelmadjid Tebboune (2023).jpg',
        TUN: 'President Kais Saïed.jpg',
        ETH: 'Prime Minister of Ethiopia Abiy Ahmed Ali (cropped).jpg',
        KEN: 'William Saomei Ruto official portrait.jpg',
        NGA: 'Bola Tinubu portrait (cropped).jpg',
        ESP: '100226-sanchez-biografia4.jpg',
        PRT: 'Luís Montenegro, 2025.06.26 (04) (cropped).jpg',
        NLD: 'Dick Schoof in 2025.jpg',
        SWE: 'Ulf Kristersson (cropped).jpg',
        DNK: 'Mette Frederiksen, 2025.06.26 (04) (cropped1).jpg',
        BEL: 'BartDeWever.jpg',
        NOR: 'Jonas Gahr Støre under åpningen av det nye regjeringskvartalet 130426 (cropped).jpg',
        FIN: 'Petteri Orpo 5.jpg',
        ISL: 'NYCW 2026 - Kristrún Frostadóttir 01.jpg',
        GRC: 'Kyriakos Mitsotakis 2026.jpg',
        HRV: 'Andrej Plenković (cropped).jpg',
        LUX: 'Luc Frieden 2025 (cropped).jpg',
        CHE: 'Karin Keller-Sutter (2025) (cropped).jpg',
        AUT: 'Christian Stocker, 2025.06.26 (01) (cropped).jpg',
        IRL: 'Taoiseach Micheál Martin.jpg',
        CZE: 'Czechia PM Petr Fiala 2025 portrait.jpg',
        SVK: 'Robert Fico portrait, 2025.jpg',
        ROU: 'Nicusor Dan in 2026.jpg',
        NZL: 'Christopher Luxon 2025 (mid cropped).jpg',
        HUN: 'Viktor Orbán, 2025.06.26 (04).jpg',
        BGR: 'Rosen Zhelyazkov 2025 (cropped).jpg',
        CYP: 'Nikos Christodoulides in 26 June 2025 (Cropped).png',
        SRB: 'Aleksandar Vučić 2025 (cropped).jpg',
        ALB: 'Albaania peaminister Edi Rama, 15.05.2026 (55271492269)(cropped).jpg',
        SVN: 'Robert Golob v Dražgošah.jpg',
        BIH: 'Denis Bećirović (cropped).jpg',
        MNE: 'Milojko Spajić (2023-12-20).jpg',
        MDA: 'Maia Sandu, September 2025 (cropped).jpg',
        GEO: 'Georgian Prime Minister Irakli Kobakhidze in 2025.jpg',
        ARM: 'Nikol Pashinyan 2026-04-01.png',
        MKD: 'Hristijan Mickoski official portrait 2024 (cropped).jpg',
        BLR: 'Александр Лукашенко (29-04-2025) (cropped).jpg',
        LVA: 'Andris Kulbergs 2026 (cropped).png',
        LTU: 'Mindaugas Sinkevičius in August 2026.jpg',
        EST: 'Euroopa päev Narvas 9. mai 2026. (12) Kristen Michal, Eesti poliitik.jpg',
        MLT: 'Robert Abela, 2025.06.26 (03) (cropped).jpg',
        PRK: 'Kim Jong-un (2025) (cropped).jpg',
        TWN: 'President Lai Ching-te 2024-10-01.jpg',
        MNG: 'Sandagiin Byambatsogt, official portrait as Chairman of the State Great Khural.jpg',
        BGD: 'Prime minister Tarique Rahman1.jpg',
        LKA: 'Anura Kumara Dissanayake in 2025.jpg',
        NPL: 'Prime Minister of Nepal Balen Shah.jpg',
        KHM: 'Hun Manet on May 30, 2025 (cropped 2).jpg',
        BTN: 'Dasho Tshering Tobgay.jpg',
        MDV: 'Dr Mohamed Muizzu portrait.jpg',
        MMR: 'Min Aung Hlaing at the Kremlin on March 4, 2025 (cropped).jpg',
        THA: 'Anutin Charnvirakul September 2026 (cropped).jpg',
        VNM: 'President of Vietnam, Mr. Tô Lâm (cropped).jpg',
        UGA: 'Yoweri K. Museveni (portrait, 2018).jpg',
        GHA: 'John Mahama.png',
        SEN: 'Président Diomaye Faye.jpg',
        TZA: 'Samia Suluhu at the XXIX St Petersburg International Economic Forum - 2026 (cropped).jpg',
        RWA: 'Kagame Paul.jpg',
        CIV: 'Alassane Ouattara - 2024 (cropped).jpg',
        CMR: 'Paul Biya in December 14th, 2022.jpg',
        ZWE: 'Emmerson Mnangagwa Official Portrait.jpg',
        ZMB: 'Inauguration of Hakainde Hichilema 2026 9.jpg',
        MOZ: 'Daniel Chapo, November 2025.jpg',
        AGO: 'President of Angola João Lourenço during a bilateral exchange at the Angola presidential palace in Luanda, Angola, September 27, 2023 - 230927-D-PM193-1914 (cropped).jpg',
        NAM: 'Netumbo Nandi-Ndaitwah 2025.jpg',
        SDN: 'Abdel Fattah al-Burhan in April 2025 (cropped).jpg',
        SSD: 'Salva Kiir at the Kremlin (2026-10-30) (cropped).jpg',
        TCD: 'Mahamat Idriss Déby in 2022.jpg',
        MLI: 'Assimi Goita at the Kremlin (2026-10-30) (cropped).jpg',
        MRT: 'Mohamed Ould Ghazouani 2025.png',
        GAB: 'Brice Oligui Nguema on November 26, 2024 (cropped).jpg',
        SGP: 'Lawrence Wong, August 2026 (cropped).jpg',
        PHL: 'Ferdinand "Bongbong" Marcos Jr. 2025 SONA Portrait (cropped).jpg',
        LAO: 'Portrait of Thongloun Sisoulith.jpg',
        BRN: 'Sultan Hassanal Bolkiah - 53857993945(cropped).jpg',
        TLS: 'Portrait of Jose Ramos-Horta.jpg',
        NER: 'Tiani (cropped).jpg',
        BFA: 'Ibrahim Traoré portrait.jpg',
        GIN: 'Mamady Doumbouya.png',
        SLE: 'Julius Maada Bio - 2020 (cropped).jpg',
        LBR: 'Joseph Boakai in Yokohama (cropped).jpg',
        TGO: 'President of Togo Faure Gnassingbé on November 13, 2024 (cropped).jpg',
        BEN: 'Romuald Wadagni in June 2026.jpg',
        COG: 'Denis Sassou Nguesso on April 29, 2026 (cropped).jpg',
        COD: 'Felix Tshisekedi, President of the Democratic Republic of the Congo (55078564106) (cropped).jpg',
        CAF: 'Faustin Archange Touadera.jpg',
        ERI: 'Isaias Afewerki (2026-10-30).jpg',
        DJI: 'Ismail Omar Guelleh, the President of Djibouti meets with Shinzō Abe, the Prime Minister of Japan.jpg',
        SOM: 'His Excellency President Hassan Sheikh Mohamud (cropped).jpg',
        CHL: 'Retrato presidencial de José Antonio Kast Rist (2026) (cropped).jpg',
        COL: 'Abelardo de la Espriella agosto de 2026.jpg',
        PER: 'Pdta. Keiko Fujimori.jpg',
        ECU: 'Daniel Noboa.jpg',
        BOL: 'President Rodrigo Paz Pereira 2025.jpg',
        VEN: 'Delcy Rodríguez portrait.jpg',
        KGZ: 'Official Photo of the President of the Kyrgyz Republic H.E. Mr. Sadyr Zhaparov.jpg',
        TJK: 'Emomali Rahmon in 2026.jpg',
        AZE: 'President of Azerbaijan Ilham Aliyev in 2025.jpg',
        GUY: '2025 Irfaan Ali (cropped).jpg',
        SUR: 'Jennifer Geerlings-Simons, November 2025.jpg',
        URY: 'Yamandú Orsi en agosto de 2026 (cropped).jpg',
        GNQ: 'Teodoro Obiang Nguema Mbasogo on September 26, 2024 (cropped).jpg',
        KAZ: 'Kassym-Jomart Tokayev 카슴조마르트 토카예프 20260916.jpg',
        UZB: 'Shavkat Mirziyoyev official portrait.jpg',
        TKM: 'Serdar Berdimuhamedow.jpg',
        FJI: '2025 Sitiveni Rabuka (cropped).jpg',
        PNG: 'Papua New Guinea Prime Minister James Marape in Port Moresby, Papua New Guinea on July 27, 2023 - 230727-D-TT977-0140 (cropped).jpg',
        MDG: 'Michael Randrianirina in February 2026.jpg',
        MUS: 'Navin Ramgoolam, 2025.jpg',
        CPV: 'José Maria Neves, 2023.jpg',
        LSO: 'Sam Matekane candidate (cropped).jpg',
        SWZ: 'Mswati III 20261010.jpg',
        GMB: 'President Adama Barrow Republic of The Gambia.jpg',
        AFG: 'Hasan Akhund 2026.jpg',
        BWA: 'Duma Boko 2025 (cropped).jpg',
        GNB: 'Le Tchad célèbre ce mardi 11 août 2026 le 66ᵉ anniversaire 101 (cropped).jpg',
        PRY: 'Santiago Peña mayo 2026 (cropped).jpg',
        CUB: 'Miguel Díaz-Canel 2025.jpg',
        HTI: '2026 Alix Didier Fils-Aimé (cropped).jpg',
        DOM: 'Luis Abinader en 2025.jpg',
        JAM: 'Holness March 2025 (cropped).jpg',
        TTO: '2025 Kamla Persad-Bissessar (cropped).jpg',
        CRI: 'Laura Fernandez Delgado presidential inauguration 20260508 0515 (cropped).jpg',
        PAN: 'José Raúl Mulino 2025.jpg',
        GTM: 'Retrato oficial de Presidente Bernardo Arévalo (cropped).jpg',
        WSM: 'Laʻauli Leuatea Schmidt in 2023.jpg',
        TON: 'Fatafehi Fakafānua January 2026.jpg',
        VUT: 'https://pmo.gov.vu/images/Hon.%20Jotham%20Napat.png',
        SLB: 'Matthew Wale in 2026 (cropped).jpg',
        HND: 'Nasry Asfura in January 2026.jpg',
        SLV: 'Presidente Bukele.jpg',
        NIC: 'Daniel Ortega on July 20, 2024 (cropped).jpg',
        BLZ: 'Johnny Briceño (52135383761) (cropped).jpg',
        BHS: 'Philip "Brave" Davis (profile).jpg',
        BRB: 'Foreign Secretary Yvette Cooper meets with Barbados Prime Minister - 5535661749 (cropped).jpg'
      };
function leaderPortraitUrlForCountry(r) {
  var iso = r && r.iso3, file = iso && LEADER_COMMONS_FILES[iso];
  if (file) return file.indexOf('https://') === 0 ? file : 'https://commons.wikimedia.org/wiki/Special:FilePath/' + encodeURIComponent(file);
  return iso ? 'assets/leaders/' + dashEsc(iso) + '.jpg' : '';
}

/* ---------- آماده‌سازی نشست مشترک دیپلماسی؛ چت واقعی فقط در فاز F ---------- */
function conversationShortcutHtml(source, canManage) {
  if (!canManage || !ST || !ST.player) return '';
  var names = ST && ST.countries ? Object.keys(ST.countries) : [];
  names.sort();
  var suffix = source === 'pacts' ? 'pacts' : 'diplomacy';
  var h = '<div class="dashCard" style="margin:10px 0"><b>💬 آماده‌سازی گفت‌وگو با کشورهای منتخب</b>';
  h += '<div class="muted small">کشورها را انتخاب کن تا نشست مشترک در بازی ذخیره شود. این کار پیام ارسال نمی‌کند و پاسخ هوش مصنوعی نمی‌سازد؛ گفت‌وگوی زنده تا فاز F قفل است.</div>';
  h += '<label>کشورها <select id="convTargets_'+suffix+'" multiple size="6" style="width:100%;min-height:120px">';
  for (var i=0;i<names.length;i++) {
    if (names[i] !== ST.player && (!ST.eliminated || ST.eliminated.indexOf(names[i]) < 0)) {
      h += '<option value="'+dashEsc(names[i])+'">'+dashEsc(names[i])+'</option>';
    }
  }
  h += '</select></label><div class="muted small">برای انتخاب چند کشور، کلید Ctrl را نگه دار؛ حداکثر ۱۹ کشور دیگر.</div>';
  h += '<label>موضوع نشست <input id="convTopic_'+suffix+'" type="text" maxlength="120" value="'+(source === 'pacts' ? 'مذاکره درباره پیمان یا اتحاد' : 'گفت‌وگوی دیپلماتیک')+'" style="width:100%"></label>';
  h += '<label>نوع مذاکره <select id="convType_'+suffix+'" style="width:100%">';
  h += '<option value="'+(source === 'pacts' ? 'pact' : 'diplomacy')+'">'+(source === 'pacts' ? 'پیمان / اتحاد' : 'دیپلماسی عمومی')+'</option>';
  h += '<option value="alliance">اتحاد</option><option value="pact">پیمان</option><option value="trade">تجارت</option><option value="ceasefire">آتش‌بس</option><option value="diplomacy">دیپلماسی</option><option value="standard">گفت‌وگوی عادی</option><option value="other">سایر</option></select></label>';
  h += '<label>حالت انتشار <select id="convVisibility_'+suffix+'" style="width:100%"><option value="public">عمومی و قابل پوشش رسانه‌ای</option><option value="normal">غیرعمومی، اما قابل پوشش رسانه‌ای</option><option value="confidential">محرمانه و بدون پوشش رسانه‌ای</option></select></label>';
  h += '<label>تاریخ پیشنهادی نشست <input type="date" id="convMeetingDate_'+suffix+'" min="'+dashEsc(calendarNextDate())+'" value="'+dashEsc(calendarNextDate())+'" style="width:100%"></label>';
  h += '<button type="button" data-conversation-prepare="'+suffix+'">پیشنهاد تاریخ نشست و رفتن به تریبون</button>';
  h += '<div class="muted small" id="convStatus_'+suffix+'">نشست پس از ثبت، در تریبون نمایش داده می‌شود؛ چت همچنان قفل خواهد بود.</div></div>';
  return h;
}
function bindConversationShortcuts() {
  var box = el('dashSection');
  if (!box) return;
  var buttons = box.querySelectorAll('[data-conversation-prepare]');
  for (var i=0;i<buttons.length;i++) buttons[i].onclick = function() {
    var source = this.getAttribute('data-conversation-prepare');
    var suffix = source === 'pacts' ? 'pacts' : 'diplomacy';
    var select = el('convTargets_'+suffix), participants = [], j;
    if (select) for (j=0;j<select.options.length;j++) if (select.options[j].selected) participants.push(select.options[j].value);
    var status = el('convStatus_'+suffix);
    if (!participants.length) { if(status) status.textContent='حداقل یک کشور را انتخاب کن.'; return; }
    if (participants.length > 19) { if(status) status.textContent='حداکثر ۱۹ کشور دیگر را می‌توان انتخاب کرد.'; return; }
    var topic = el('convTopic_'+suffix), type = el('convType_'+suffix), visibility = el('convVisibility_'+suffix), meetingDate=el('convMeetingDate_'+suffix);
    if (!meetingDate || !meetingDate.value || meetingDate.value < calendarNextDate()) { if(status) status.textContent='تاریخ نشست باید از فردای روز فعلی بازی به بعد باشد.'; return; }
    var payload = {
      participants: participants,
      topic: topic ? topic.value : 'گفت‌وگوی دیپلماتیک',
      negotiation_type: type ? type.value : (source === 'pacts' ? 'pact' : 'diplomacy'),
      visibility_mode: visibility ? visibility.value : 'public',
      meeting_date: meetingDate.value,
      source: source,
      context: {origin_tab:source, selected_country:ST ? ST.player : null, requested_by_player:true}
    };
    var btn = this;
    btn.disabled = true;
    if(status) status.textContent='در حال ذخیره نشست...';
    postJSON('api/conversations/prepare',payload,function(res) {
      btn.disabled = false;
      if (!res || !res.ok || !res.session) {
        if(status) status.textContent=(res&&res.error)||'نشست ذخیره نشد.';
        return;
      }
      loadState(function() {
        DASH_TAB = 'tribune';
        if (LAST_COUNTRY_R) renderCountryPanel(LAST_COUNTRY_R);
        flash('تاریخ نشست '+res.session.meeting_date+' پیشنهاد شد؛ تا پذیرش کشور مقابل و رسیدن موعد، گفت‌وگو قفل می‌ماند.');
      });
    },function(code,response) {
      btn.disabled = false;
      if(status) status.textContent=netErrMsg(code,response)+' — نشست ذخیره نشد.';
    });
  };
}

function agreementSessionOptionsHtml(selectId) {
  var sessions = ST && ST.conversation_sessions ? ST.conversation_sessions : [];
  var h = '<label>نشست مرتبط (اختیاری) <select id="' + selectId + '" style="width:100%"><option value="">بدون اتصال به نشست</option>';
  for (var i=sessions.length-1;i>=0;i--) {
    var item=sessions[i] || {};
    h += '<option value="' + dashEsc(item.id || '') + '">' + dashEsc((item.id || '') + ' · ' + (item.topic || 'گفت‌وگوی دیپلماتیک') + ' · ' + (item.participants || []).join('، ')) + '</option>';
  }
  return h + '</select></label>';
}
function agreementSessionMatches(conversationId, parties) {
  if (!conversationId) return true;
  var sessions = ST && ST.conversation_sessions ? ST.conversation_sessions : [], session=null;
  for (var i=0;i<sessions.length;i++) if (sessions[i] && sessions[i].id === conversationId) { session=sessions[i]; break; }
  if (!session) return false;
  var a=(session.participants || []).slice(0).sort(), b=parties.slice(0).sort();
  if (a.length !== b.length) return false;
  for (var j=0;j<a.length;j++) if (a[j] !== b[j]) return false;
  return true;
}

/* ---------- پیمان‌های فعال: نمایش از داده پایدار موتور ---------- */
function pactTypeLabel(type) {
  var labels = {
    non_aggression: 'عدم تجاوز',
    trade: 'تجاری',
    defense: 'دفاعی',
    cooperation: 'همکاری',
    transit: 'ترانزیت',
    economic: 'اقتصادی',
    other: 'سایر'
  };
  return labels[type] || 'نوع ثبت‌نشده (' + String(type || '—') + ')';
}
function pactPanelHtml(countryName, canManage) {
  var records = ST && ST.pact_records ? ST.pact_records : [];
  var active = [], i, rec, members, partners;
  for (i=0;i<records.length;i++) {
    rec = records[i] || {};
    members = rec.members || [];
    if (rec.status === 'active' && members.indexOf(countryName) >= 0) active.push(rec);
  }
  var h = '<h3>📜 پیمان‌های در جریان</h3>';
  h += '<div class="dashNote">فقط پیمان‌هایی نمایش داده می‌شوند که در وضعیت فعال و در میان اعضای آن‌ها کشور انتخاب‌شده حضور دارد. لغو پیمان از طرف بازیکن یک‌جانبه است و در تاریخچه بازی ثبت می‌شود.</div>';
  h += conversationShortcutHtml('pacts', canManage);
  if (canManage) {
    h += '<h4>ثبت پیشنهاد پیمان</h4><div class="dashCard">';
    h += '<label>کشورهای طرف پیمان <select id="pactProposalCountries" multiple size="6" style="width:100%;min-height:110px">';
    var pactNames=ST && ST.countries ? Object.keys(ST.countries) : []; pactNames.sort();
    for (i=0;i<pactNames.length;i++) if (pactNames[i] !== ST.player && (!ST.eliminated || ST.eliminated.indexOf(pactNames[i]) < 0)) h += '<option value="' + dashEsc(pactNames[i]) + '">' + dashEsc(pactNames[i]) + '</option>';
    h += '</select></label><label>نوع پیمان <select id="pactProposalType" style="width:100%"><option value="non_aggression">عدم تجاوز</option><option value="trade">تجاری</option><option value="defense">دفاعی</option><option value="cooperation">همکاری</option><option value="transit">ترانزیت</option><option value="economic">اقتصادی</option><option value="other">سایر</option></select></label>';
    h += agreementSessionOptionsHtml('pactProposalSession');
    h += '<button type="button" id="pactProposalSubmit">ثبت پیشنهاد پیمان</button><div id="pactProposalStatus" class="dashNote">پیمان تا پذیرش همه طرف‌ها فعال نمی‌شود. نشست مرتبط باید دقیقاً همین اعضا را داشته باشد.</div></div>';
  }
  var pactProposals=ST && ST.agreement_proposals ? ST.agreement_proposals : [], pendingPacts=0;
  for(i=0;i<pactProposals.length;i++) {
    rec=pactProposals[i] || {};
    if(rec.kind!=='pact' || rec.status!=='pending' || (rec.parties || []).indexOf(ST ? ST.player : '')<0) continue;
    pendingPacts++;
    var incomingPact = rec.initiator !== (ST ? ST.player : '');
    var acceptedPact = rec.accepted_by || [];
    h += '<div class="dashCard"><b>'+(incomingPact?'پیشنهاد پیمان دریافتی':'پیشنهاد پیمان ارسالی')+' · '+dashEsc(pactTypeLabel(rec.pact_type))+'</b>';
    h += '<div>طرف‌ها: '+dashEsc((rec.parties || []).join('، '))+'</div>';
    h += '<div>پذیرفته‌اند: '+dashEsc(acceptedPact.join('، ') || 'هنوز مشخص نیست')+'</div>';
    if(rec.conversation_id) h += '<div class="muted small">نشست مرتبط: '+dashEsc(rec.conversation_id)+'</div>';
    if(incomingPact && acceptedPact.indexOf(ST.player)<0) {
      h += '<div class="row" style="gap:8px;margin-top:8px"><button type="button" data-agreement-decision="accept" data-proposal-id="'+dashEsc(rec.id)+'">پذیرش پیشنهاد پیمان</button><button type="button" class="warn" data-agreement-decision="reject" data-proposal-id="'+dashEsc(rec.id)+'">رد پیشنهاد</button></div>';
    } else if(incomingPact) {
      h += '<div class="muted small">پیشنهاد را پذیرفته‌ای؛ پیمان تا پذیرش همه طرف‌ها فعال نمی‌شود.</div>';
    } else {
      h += '<div class="muted small">پیشنهاد ارسالی شما در انتظار پاسخ طرف‌های دیگر است؛ پاسخ خودکار از طرف هوش مصنوعی ساخته نمی‌شود.</div>';
    }
    h += '</div>';
  }
  if (!active.length && !pendingPacts) h += '<div class="dashCard">در حال حاضر پیمان فعال یا پیشنهاد در انتظار ثبت‌شده‌ای برای این کشور وجود ندارد.</div>';
  for (i=0;i<active.length;i++) {
    rec = active[i];
    members = rec.members || [];
    partners = [];
    for (var j=0;j<members.length;j++) if (members[j] !== countryName) partners.push(members[j]);
    h += '<div class="dashCard">';
    h += '<div class="row"><b>' + dashEsc(rec.name || pactTypeLabel(rec.type)) + '</b><span class="badge">فعال</span></div>';
    h += '<div class="row"><span class="muted">نوع پیمان</span><b>' + dashEsc(pactTypeLabel(rec.type)) + '</b></div>';
    h += '<div class="row"><span class="muted">طرف‌های دیگر</span><span>' + dashEsc(partners.join('، ') || '—') + '</span></div>';
    h += '<div class="row"><span class="muted">تاریخ ثبت</span><span>' + dashEsc(rec.created_date || '—') + '</span></div>';
    if (rec.legacy) h += '<div class="muted small">این پیمان از داده‌های نسخه قدیمی بازی مهاجرت داده شده است.</div>';
    if (rec.terms && Object.keys(rec.terms).length) h += '<div class="muted small">شرایط ثبت‌شده: ' + dashEsc(JSON.stringify(rec.terms)) + '</div>';
    if (canManage) h += '<button type="button" class="warn" data-pact-cancel="' + dashEsc(rec.id) + '">لغو یک‌جانبه پیمان</button>';
    h += '</div>';
  }
  if (!canManage) h += '<div class="dashNote">این کشور در حالت مشاهده است؛ مدیریت پیمان‌ها فقط از کشور تحت کنترل بازیکن انجام می‌شود.</div>';
  return h;
}
function bindAgreementDecisionActions() {
  var box = el('dashSection');
  if (!box) return;
  var buttons = box.querySelectorAll('[data-agreement-decision]');
  for (var i=0;i<buttons.length;i++) buttons[i].onclick=function() {
    var button=this;
    var proposalId=button.getAttribute('data-proposal-id');
    var decision=button.getAttribute('data-agreement-decision');
    if(!proposalId || (decision!=='accept' && decision!=='reject')) return;
    if(window.confirm && !window.confirm(decision==='accept'?'این پیشنهاد را می‌پذیری؟':'این پیشنهاد را رد می‌کنی؟')) return;
    button.disabled=true;
    postJSON('api/agreements/decision',{proposal_id:proposalId,decision:decision},function(res) {
      if(!res || !res.ok) {
        button.disabled=false;
        flash((res&&res.error)||'ثبت تصمیم درباره پیشنهاد ناموفق بود.');
        return;
      }
      loadState(function() {
        if(LAST_COUNTRY_R) renderCountryPanel(LAST_COUNTRY_R);
        flash(decision==='accept'?'پذیرش شما ثبت شد؛ توافق فقط پس از پذیرش همه طرف‌ها فعال می‌شود.':'رد پیشنهاد ثبت شد.');
      });
    },function(st,tx) {
      button.disabled=false;
      flash(netErrMsg(st,tx)+' — تصمیم ثبت نشد.');
    });
  };
}

function bindPactActions() {
  var box = el('dashSection');
  if (!box) return;
  bindAgreementDecisionActions();
  var create=el('pactProposalSubmit');
  if(create) create.onclick=function(){
    var select=el('pactProposalCountries'), parties=[], j;
    if(select) for(j=0;j<select.options.length;j++) if(select.options[j].selected) parties.push(select.options[j].value);
    if(!parties.length){var st=el('pactProposalStatus');if(st)st.textContent='حداقل یک کشور را انتخاب کن.';return;}
    parties.unshift(ST.player);
    var session=el('pactProposalSession'), conversationId=session?session.value:'';
    var status=el('pactProposalStatus');
    if(conversationId && !agreementSessionMatches(conversationId,parties)){if(status)status.textContent='اعضای نشست انتخاب‌شده با طرف‌های پیمان یکسان نیستند.';return;}
    var type=el('pactProposalType'); create.disabled=true;
    postJSON('api/agreements/propose',{kind:'pact',parties:parties,pact_type:type?type.value:'non_aggression',conversation_id:conversationId||null},function(res){
      create.disabled=false;
      if(!res||!res.ok){if(status)status.textContent=(res&&res.error)||'پیشنهاد پیمان ثبت نشد.';return;}
      loadState(function(){if(LAST_COUNTRY_R)renderCountryPanel(LAST_COUNTRY_R);flash('پیشنهاد پیمان ثبت شد؛ تا پذیرش همه طرف‌ها فعال نمی‌شود.');});
    },function(code,response){create.disabled=false;if(status)status.textContent=netErrMsg(code,response)+' — پیشنهاد ثبت نشد.';});
  };
  var buttons = box.querySelectorAll('[data-pact-cancel]');
  for (var i=0;i<buttons.length;i++) {
    buttons[i].onclick = function() {
      var id = this.getAttribute('data-pact-cancel');
      if (!id) return;
      if (window.confirm && !window.confirm('آیا از لغو یک‌جانبه این پیمان مطمئن هستی؟')) return;
      this.disabled = true;
      postJSON('api/agreements/pact/cancel', {agreement_id:id}, function(result) {
        if (!result || !result.ok) {
          flash((result && result.error) || 'لغو پیمان انجام نشد.');
          if (LAST_COUNTRY_R) renderCountryPanel(LAST_COUNTRY_R);
          return;
        }
        loadState(function() {
          if (LAST_COUNTRY_R) renderCountryPanel(LAST_COUNTRY_R);
          flash('پیمان لغو شد و تغییر آن در ذخیره و تاریخچه بازی ثبت شد.');
        });
      }, function(status, response) {
        flash(netErrMsg(status, response) + ' — پیمان لغو نشد.');
        if (LAST_COUNTRY_R) renderCountryPanel(LAST_COUNTRY_R);
      });
    };
  }
}


/* ---------- مدیریت اتحادها و درخواست عضویت ---------- */
function alliancePanelHtml(countryName, canManage) {
  var records = ST && ST.alliance_records ? ST.alliance_records : [];
  var proposals = ST && ST.agreement_proposals ? ST.agreement_proposals : [];
  var joinRequests = ST && ST.alliance_join_requests ? ST.alliance_join_requests : [];
  var current = [], world = [], i, rec, members, h = '<h3>🤝 مدیریت اتحادها</h3>';
  for (i=0;i<records.length;i++) {
    rec = records[i] || {};
    if (rec.status !== 'active') continue;
    members = rec.members || [];
    if (members.indexOf(countryName) >= 0) current.push(rec);
    if (members.indexOf(ST ? ST.player : '') < 0) world.push(rec);
  }
  h += '<h4>اتحادهای کشور انتخاب‌شده</h4>';
  if (!current.length) h += '<div class="dashCard">این کشور در حال حاضر عضو هیچ اتحاد فعالی نیست.</div>';
  for (i=0;i<current.length;i++) {
    rec=current[i]; members=rec.members || [];
    h += '<div class="dashCard"><div class="row"><b>'+dashEsc(rec.name || 'اتحاد ثبت‌شده')+'</b><span class="badge">فعال</span></div>';
    h += '<div class="row"><span class="muted">نوع اتحاد</span><b>'+dashEsc(rec.type || 'ثبت‌نشده')+'</b></div>';
    h += '<div class="row"><span class="muted">اعضا</span><span>'+dashEsc(members.join('، '))+'</span></div>';
    h += '<div class="row"><span class="muted">تاریخ تشکیل</span><span>'+dashEsc(rec.created_date || '—')+'</span></div>';
    if (rec.legacy) h += '<div class="muted small">این سابقه از اطلاعات نسخه قبلی منتقل شده است.</div>';
    if (canManage) h += '<button type="button" class="warn" data-alliance-leave="'+dashEsc(rec.id)+'">خروج یک‌جانبه از اتحاد</button>';
    h += '</div>';
  }
  if (!canManage) h += '<div class="dashNote">مدیریت اتحادها فقط برای کشور تحت کنترل بازیکن فعال است.</div>';
  if (canManage) {
    h += '<h4>ایجاد اتحاد جدید</h4><div class="dashCard">';
    h += '<label>نام اتحاد <input id="allianceNewName" type="text" maxlength="100" placeholder="مثلاً اتحاد همکاری منطقه‌ای"></label>';
    h += '<label>کشورهای دعوت‌شونده <select id="allianceNewCountries" multiple size="8" style="width:100%;min-height:150px">';
    var names = ST && ST.countries ? Object.keys(ST.countries) : [];
    names.sort();
    for (i=0;i<names.length;i++) if (names[i] !== ST.player && (!ST.eliminated || ST.eliminated.indexOf(names[i]) < 0)) {
      h += '<option value="'+dashEsc(names[i])+'">'+dashEsc(names[i])+'</option>';
    }
    h += '</select></label><div class="muted small">برای انتخاب چند کشور، کلید Ctrl را نگه دار. اتحاد فقط پس از پذیرش همه اعضای دعوت‌شده تشکیل می‌شود.</div>';
    h += agreementSessionOptionsHtml('allianceProposalSession');
    h += '<button type="button" id="allianceCreateSubmit">ارسال پیشنهاد تشکیل اتحاد</button><div id="allianceActionStatus" class="dashNote">نشست مرتبط اختیاری است و باید دقیقاً شامل همین اعضا باشد. هیچ دعوتی بدون تأیید همه اعضا فعال نمی‌شود.</div></div>';
  }
  h += '<h4>اتحادهای دیگر کشورهای جهان</h4>';
  if (!world.length) h += '<div class="dashCard">در داده فعلی، اتحاد فعال مستقلی برای نمایش ثبت نشده است. اتحادهای فرضی یا تأییدنشده نمایش داده نمی‌شوند.</div>';
  for (i=0;i<world.length;i++) {
    rec=world[i]; members=rec.members || [];
    h += '<div class="dashCard"><div class="row"><b>'+dashEsc(rec.name || 'اتحاد ثبت‌شده')+'</b><span class="badge">فعال</span></div>';
    h += '<div class="row"><span class="muted">نوع</span><span>'+dashEsc(rec.type || 'ثبت‌نشده')+'</span></div>';
    h += '<div class="row"><span class="muted">اعضا</span><span>'+dashEsc(members.join('، '))+'</span></div>';
    if (canManage) h += '<button type="button" data-alliance-join="'+dashEsc(rec.id)+'">درخواست عضویت در این اتحاد</button>';
    h += '</div>';
  }
  if (canManage) {
    h += '<h4>پیشنهادها و درخواست‌های در انتظار</h4>';
    var pending = 0;
    for (i=0;i<proposals.length;i++) {
      rec=proposals[i] || {};
      if (rec.kind !== 'alliance' || rec.status !== 'pending' ||
          (rec.initiator !== ST.player && (rec.parties || []).indexOf(ST.player)<0)) continue;
      pending++;
      var incomingAlliance = rec.initiator !== ST.player;
      var acceptedAlliance = rec.accepted_by || [];
      h += '<div class="dashCard"><b>'+(incomingAlliance?'دعوت دریافتی برای عضویت در اتحاد':'پیشنهاد تشکیل اتحاد')+'</b>';
      h += '<div>نام اتحاد: '+dashEsc(rec.name || 'اتحاد جدید')+'</div><div>طرف‌ها: '+dashEsc((rec.parties || []).join('، '))+'</div>';
      h += '<div>پذیرفته‌اند: '+dashEsc(acceptedAlliance.join('، ') || 'هنوز مشخص نیست')+'</div>';
      if(rec.conversation_id) h += '<div class="muted small">نشست مذاکره مرتبط: '+dashEsc(rec.conversation_id)+'</div>';
      if (incomingAlliance && acceptedAlliance.indexOf(ST.player)<0) {
        h += '<div class="row" style="gap:8px;margin-top:8px"><button type="button" data-agreement-decision="accept" data-proposal-id="'+dashEsc(rec.id)+'">پذیرش دعوت</button><button type="button" class="warn" data-agreement-decision="reject" data-proposal-id="'+dashEsc(rec.id)+'">رد دعوت</button></div>';
      } else if (incomingAlliance) {
        h += '<div class="muted small">دعوت را پذیرفته‌ای؛ تشکیل اتحاد تا پذیرش همه طرف‌ها معلق می‌ماند.</div>';
      } else {
        h += '<div class="muted small">پیشنهاد ارسالی شما در انتظار پاسخ طرف‌های دیگر است؛ پاسخ خودکار از طرف هوش مصنوعی ساخته نمی‌شود.</div>';
      }
      h += '</div>';
    }
    for (i=0;i<joinRequests.length;i++) {
      rec=joinRequests[i] || {};
      if (rec.requester === ST.player && rec.status === 'pending') {
        pending++;
        h += '<div class="dashCard"><b>درخواست عضویت در '+dashEsc(rec.alliance_name || 'اتحاد')+'</b><div>وضعیت: در انتظار بررسی اعضا</div><div class="muted small">درخواست ثبت شده، اما عضویت هنوز فعال نیست؛ بررسی زنده در فاز F انجام می‌شود.</div></div>';
      }
    }
    if (!pending) h += '<div class="dashCard">پیشنهاد یا درخواست در انتظاری وجود ندارد.</div>';
  }
  return h;
}
function bindAllianceActions() {
  var box=el('dashSection');
  if (!box || !ST) return;
  bindAgreementDecisionActions();
  var leave=box.querySelectorAll('[data-alliance-leave]');
  for (var i=0;i<leave.length;i++) leave[i].onclick=function(){
    var id=this.getAttribute('data-alliance-leave');
    if (!id || (window.confirm && !window.confirm('از خروج یک‌جانبه از این اتحاد مطمئنی؟'))) return;
    this.disabled=true;
    postJSON('api/agreements/alliance/leave',{agreement_id:id},function(res){
      if(!res || !res.ok){flash((res&&res.error)||'خروج از اتحاد انجام نشد.');return;}
      loadState(function(){if(LAST_COUNTRY_R)renderCountryPanel(LAST_COUNTRY_R);flash('خروج از اتحاد ثبت شد.');});
    },function(st,tx){flash(netErrMsg(st,tx)+' — خروج از اتحاد انجام نشد.');});
  };
  var join=box.querySelectorAll('[data-alliance-join]');
  for (i=0;i<join.length;i++) join[i].onclick=function(){
    var id=this.getAttribute('data-alliance-join');
    if(!id)return;
    this.disabled=true;
    postJSON('api/agreements/alliance/join-request',{alliance_id:id},function(res){
      if(!res||!res.ok){flash((res&&res.error)||'درخواست عضویت ثبت نشد.');if(LAST_COUNTRY_R)renderCountryPanel(LAST_COUNTRY_R);return;}
      loadState(function(){if(LAST_COUNTRY_R)renderCountryPanel(LAST_COUNTRY_R);flash('درخواست عضویت ثبت شد؛ تا پذیرش اعضا عضو اتحاد محسوب نمی‌شوی.');});
    },function(st,tx){flash(netErrMsg(st,tx)+' — درخواست عضویت ثبت نشد.');});
  };
  var create=el('allianceCreateSubmit');
  if(create)create.onclick=function(){
    var select=el('allianceNewCountries'), name=el('allianceNewName'), parties=[], j;
    if(select)for(j=0;j<select.options.length;j++)if(select.options[j].selected)parties.push(select.options[j].value);
    if(!parties.length){var status=el('allianceActionStatus');if(status)status.textContent='حداقل یک کشور برای دعوت انتخاب کن.';return;}
    parties.unshift(ST.player);
    var linked=el('allianceProposalSession'), conversationId=linked?linked.value:'';
    var statusBox=el('allianceActionStatus');
    if(conversationId && !agreementSessionMatches(conversationId,parties)){if(statusBox)statusBox.textContent='اعضای نشست انتخاب‌شده با اعضای اتحاد یکسان نیستند.';return;}
    create.disabled=true;
    postJSON('api/agreements/propose',{kind:'alliance',parties:parties,alliance_name:name?name.value:'',conversation_id:conversationId||null},function(res){
      create.disabled=false;
      if(!res||!res.ok){var status=el('allianceActionStatus');if(status)status.textContent=(res&&res.error)||'پیشنهاد ثبت نشد.';return;}
      loadState(function(){if(LAST_COUNTRY_R)renderCountryPanel(LAST_COUNTRY_R);flash('پیشنهاد تشکیل اتحاد ثبت شد؛ تا پذیرش همه کشورها اتحاد فعال نمی‌شود.');});
    },function(st,tx){create.disabled=false;var status=el('allianceActionStatus');if(status)status.textContent=netErrMsg(st,tx)+' — پیشنهاد ثبت نشد.';});
  };
}


/* ---------- پنل اقدامات دیپلماتیک بازیکن ---------- */
function diplomacyPanelHtml(country, isPlayer) {
  var h = '<h3>🕊 وضعیت و مدیریت دیپلماسی</h3>';
  var wars = country.war_with || [];
  h += '<div class="dashCard"><b>وضعیت جنگ کشور انتخاب‌شده</b><div>' +
    (wars.length ? 'در جنگ با: ' + wars.map(dashEsc).join('، ') : 'در حال حاضر جنگ فعالی با کشور دیگری ثبت نشده است.') +
    '</div></div>';
  if (!isPlayer) {
    h += '<div class="dashNote">این کشور در حالت مشاهده است. اقدامات دیپلماتیک فقط از پنل کشور تحت کنترل بازیکن انجام می‌شوند.</div>';
    return h;
  }
  h += conversationShortcutHtml('diplomacy', true);
  var names = ST && ST.countries ? Object.keys(ST.countries) : [];
  names.sort();
  h += '<div class="dashCard"><b>اقدام دیپلماتیک مستقیم</b>';
  h += '<label>کشورها <select id="diplomacyTargets" multiple size="9" style="width:100%;min-height:160px">';
  for (var i=0;i<names.length;i++) {
    if (names[i] !== ST.player && (!ST.eliminated || ST.eliminated.indexOf(names[i]) < 0)) {
      h += '<option value="'+dashEsc(names[i])+'">'+dashEsc(names[i])+'</option>';
    }
  }
  h += '</select></label><div class="muted small">برای انتخاب چند کشور، کلید Ctrl را نگه دار. نتیجه هر کشور جداگانه اعتبارسنجی می‌شود.</div>';
  h += '<div class="row" style="flex-wrap:wrap;gap:6px;margin-top:10px">';
  h += '<button type="button" data-diplomacy-action="improve_relations">بهبود روابط</button>';
  h += '<button type="button" data-diplomacy-action="reduce_relations">کاهش روابط</button>';
  h += '<button type="button" data-diplomacy-action="declare_war" class="warn">اعلام جنگ</button>';
  h += '<button type="button" data-diplomacy-action="unilateral_ceasefire">اعلام آتش‌بس یک‌جانبه</button>';
  h += '</div><div id="diplomacyActionStatus" class="dashNote">ابتدا یک یا چند کشور را انتخاب کن.</div></div>';
  h += '<h4>تاریخچه اقدامات دیپلماتیک</h4>';
  var history = ST && ST.diplomatic_history ? ST.diplomatic_history : [];
  if (!history.length) h += '<div class="dashCard">هنوز اقدام دیپلماتیکی ثبت نشده است.</div>';
  for (i=history.length-1;i>=0 && i>=history.length-20;i--) {
    var item = history[i] || {};
    var labels = {improve_relations:'بهبود روابط',reduce_relations:'کاهش روابط',declare_war:'اعلام جنگ',unilateral_ceasefire:'آتش‌بس یک‌جانبه'};
    h += '<div class="dashCard"><div class="row"><b>'+dashEsc(labels[item.action] || item.action || 'اقدام دیپلماتیک')+'</b><span class="muted small">'+dashEsc(item.date || '—')+'</span></div>';
    h += '<div>کشور: '+dashEsc(item.country || '—')+'</div><div>'+dashEsc(item.detail || '—')+'</div>';
    h += '<div class="muted small">روابط: '+dashEsc(item.relation_before)+' ← '+dashEsc(item.relation_after)+'</div></div>';
  }
  h += '<div class="dashNote">گفت‌وگوی زنده، پیشنهاد شروط و تصمیم‌گیری مستقل کشورهای هوش مصنوعی در فاز F فعال می‌شود؛ این پنل فعلاً فقط اقدامات مستقیم و قطعی بازیکن را ثبت می‌کند.</div>';
  return h;
}
function bindDiplomacyActions() {
  var box = el('dashSection');
  if (!box || !ST || !ST.player || ST.player !== (LAST_COUNTRY_R && LAST_COUNTRY_R.name)) return;
  var buttons = box.querySelectorAll('[data-diplomacy-action]');
  for (var i=0;i<buttons.length;i++) buttons[i].onclick = function() {
    var action = this.getAttribute('data-diplomacy-action');
    var select = el('diplomacyTargets'), targets = [], j;
    if (select) for (j=0;j<select.options.length;j++) if (select.options[j].selected) targets.push(select.options[j].value);
    var status = el('diplomacyActionStatus');
    if (!targets.length) { if(status) status.textContent='حداقل یک کشور را انتخاب کن.'; return; }
    var labels = {improve_relations:'بهبود روابط',reduce_relations:'کاهش روابط',declare_war:'اعلام جنگ',unilateral_ceasefire:'آتش‌بس یک‌جانبه'};
    if (action === 'declare_war' && window.confirm && !window.confirm('اعلام وضعیت جنگ با '+targets.join('، ')+' ثبت شود؟')) return;
    if (action === 'unilateral_ceasefire' && window.confirm && !window.confirm('وضعیت جنگ با کشورهای انتخاب‌شده پایان یابد؟')) return;
    var btn = this;
    btn.disabled = true;
    if(status) status.textContent='در حال ثبت اقدام دیپلماتیک...';
    postJSON('api/diplomacy/action',{action:action,targets:targets},function(res) {
      btn.disabled = false;
      if (!res || !res.ok) { if(status) status.textContent=(res&&res.error)||'اقدام انجام نشد.'; return; }
      var lines = [];
      for (var k=0;k<(res.results||[]).length;k++) {
        var result=res.results[k]||{};
        lines.push((result.ok?'✓ ':'✗ ')+result.country+': '+(result.detail||result.reason||'ثبت شد.'));
      }
      loadState(function() {
        if (LAST_COUNTRY_R) renderCountryPanel(LAST_COUNTRY_R);
        flash(labels[action]+'؛ موفق: '+res.success_count+'، ناموفق: '+res.failed_count);
      });
      if(status) status.textContent=lines.join(' | ') || 'نتیجه‌ای دریافت نشد.';
    },function(code,response) {
      btn.disabled = false;
      if(status) status.textContent=netErrMsg(code,response)+' — اقدام ثبت نشد.';
    });
  };
}

function dashSectionHtml(r, isPlayer, tab) {
  var h = '', ks, i;
  if (tab === 'calendar') {
    var events=(ST && ST.calendar_events)||[], pending=(ST && ST.conversation_sessions)||[];
    h += '<h3>📅 تقویم و روزشمار</h3><div class="dashNote">موعدهای قطعی پس از پذیرش طرف‌ها در اینجا ثبت می‌شوند. شمارش روزها با گذر زمان بازی به‌روزرسانی می‌شود؛ نشست‌ها پیش از موعد و پیش از فعال‌شدن هوش مصنوعی زنده قابل گفت‌وگو نیستند.</div>';
    if (!events.length) h += '<div class="dashCard">هنوز موعد قطعی در تقویم ثبت نشده است.</div>';
    for (var ci=events.length-1;ci>=0;ci--) {
      var ce=events[ci]||{}, dueText=ce.due_date||'—', left=calendarDaysRemaining(dueText), status=left===0?'موعد فرارسیده':('باقی‌مانده: '+left+' روز');
      h += '<div class="dashCard"><div class="row"><b>'+dashEsc(ce.title||'رویداد زمان‌بندی‌شده')+'</b><span class="badge">'+dashEsc(status)+'</span></div>';
      h += '<div>تاریخ: '+dashEsc(dueText)+' · دسته: '+dashEsc(ce.category||'عمومی')+'</div>';
      if (ce.participants && ce.participants.length) h += '<div class="muted small">طرف‌ها: '+dashEsc(ce.participants.join('، '))+'</div>';
      if (ce.linked_session_id) h += '<div class="muted small">نشست مرتبط: '+dashEsc(ce.linked_session_id)+'</div>';
      h += '</div>';
    }
    var waiting=0;
    for (var pi=pending.length-1;pi>=0;pi--) {
      var ps=pending[pi]||{};
      if (ps.meeting_status==='pending_ai_acceptance' || ps.meeting_status==='pending_player_acceptance') {
        waiting++;
        h += '<div class="dashCard"><div class="row"><b>پیشنهاد نشست · '+dashEsc(ps.id||'')+'</b><span class="badge">در انتظار پاسخ</span></div>';
        var pendingLeft=ps.meeting_date?calendarDaysRemaining(ps.meeting_date):null;
        h += '<div>'+dashEsc(ps.topic||'نشست دیپلماتیک')+' · تاریخ پیشنهادی: '+dashEsc(ps.meeting_date||'—')+'</div>';
        if(pendingLeft!==null) h += '<div class="muted small">'+(pendingLeft===0?'تاریخ پیشنهادی فرا رسیده است':'تا تاریخ پیشنهادی: '+pendingLeft+' روز')+'</div>';
        h += '<div class="muted small">'+dashEsc((ps.participants||[]).join('، '))+' · تا پذیرش همه طرف‌ها در تقویم قطعی نمی‌شود.</div></div>';
      }
    }
    if (!waiting) h += '<div class="muted small">پیشنهاد نشستِ در انتظار پاسخ وجود ندارد.</div>';
    h += '<div class="dashNote">زیرساخت تقویم برای موعدهای سیاسی، اقتصادی، تجاری، دیپلماتیک، نظامی و پروژه‌ها آماده است؛ با اضافه‌شدن هر فرایند زمان‌دار، موعد آن از طریق موتور بازی به همین فهرست متصل می‌شود.</div>';
  } else if (tab === 'general') {
    h += '<h3>🌐 مشخصات کشور</h3><div class="dashGrid">';
    h += dashMetric('نام کشور',r.name) + dashMetric('نام انگلیسی',r.en || 'ثبت نشده');
    h += dashMetric('قاره / منطقه',r.region) + dashMetric('کد کشور',r.iso3 || 'ثبت نشده');
    h += dashMetric('رئیس کشور / دولت',r.leader) + dashMetric('رتبه جهانی',r.rank ? '#'+r.rank : '—');
    h += '</div>';
    var cp = r.country_profile || null;
    if (cp) {
      h += '<h3>اطلاعات پایه کشور</h3><div class="dashGrid">';
      h += dashMetric('پایتخت',cp.capital || 'ثبت نشده');
      h += dashMetric('مساحت کل',cp.area_km2 == null ? 'ثبت نشده' : Number(cp.area_km2).toLocaleString('en-US')+' کیلومتر مربع');
      h += dashMetric('زبان‌های ثبت‌شده',(cp.languages || []).map(function(x){return x.name;}).join('، ') || 'ثبت نشده');
      h += dashMetric('واحد پول',(cp.currencies || []).map(function(x){return x.name+' ('+x.code+')';}).join('، ') || 'ثبت نشده');
      h += '</div><div class="dashNote">زبان‌ها و واحدهای پول از داده مرجع کشورها خوانده می‌شوند؛ در کشورهایی با چند زبان، همه موارد ثبت‌شده نمایش داده می‌شوند.</div>';
    } else h += dashMissing('اطلاعات پایه کشور','پرونده اطلاعات مرجع برای این کشور در دسترس نیست.');
  } else if (tab === 'politics') {
    var pp = r.political_profile || null, pc = r.political_classification || null;
    var baselinePc = r.political_baseline || null, cur, keys2, item, fields, j, k, val;
    h += '<h3>🏛 ساختار سیاسی</h3>';
    h += politicalCurrentStatusHtml(pc, baselinePc);
    h += politicalClassificationHtml(baselinePc);
    h += politicalChangeFormHtml(pc, isPlayer);
    h += '<div class="dashCard"><div class="row"><span class="muted">رئیس کشور / دولت در موتور بازی</span><b>'+dashEsc(r.leader)+'</b></div>';
    h += '<div class="row"><span class="muted">ثبات سیاسی شبیه‌سازی</span><b>'+dashEsc(r.stab)+'/100</b></div></div>';
    if (pp) {
      h += '<h3>نوع نظام و مدل حکومت</h3><div class="dashCard">';
      h += '<div class="row"><span class="muted">نوع نظام سیاسی</span><b>'+dashEsc(politicalValueLabel(pp.system_type || 'ثبت نشده'))+'</b></div>';
      h += '<div class="muted">'+dashEsc(politicalValueLabel(pp.government_model || 'توضیح مدل حکومت ثبت نشده'))+'</div></div>';
      if (pp.current_government) {
        h += '<h3>ساختار دولت در تاریخ شروع سناریو</h3><div class="dashCard">';
        cur = pp.current_government;
        keys2 = Object.keys(cur);
        for (j=0;j<keys2.length;j++) {
          k=keys2[j]; val=cur[k];
          if (val == null || typeof val === 'object') continue;
          if (k === 'scenario_note' || k === 'note') {
            h += '<div class="muted">'+dashEsc(val)+'</div>';
          } else if (val === 'PLAYER_CONTROLLED') {
            if (!cur._playerControlShown) {
              h += '<div class="row"><span class="muted">کنترل سناریو</span><b>بازیکن</b></div>';
              cur._playerControlShown = true;
            }
          } else {
            h += '<div class="row"><span class="muted">'+dashEsc(politicalFieldLabel(k))+'</span><b>'+dashEsc(politicalValueLabel(val))+'</b></div>';
          }
        }
        h += '</div>';
      }
      if (pp.parties && pp.parties.length) {
        h += '<h3>احزاب واقعی ثبت‌شده</h3>';
        for (j=0;j<pp.parties.length;j++) {
          item=pp.parties[j] || {};
          h += '<div class="dashCard"><b>'+dashEsc(item.name_fa || item.name_en || 'حزب بدون نام')+'</b>';
          if (item.name_en) h += '<div class="muted small">'+dashEsc(item.name_en)+'</div>';
          if (item.political_role) h += '<div>'+dashEsc(item.political_role)+'</div>';
          if (item.ideological_profile) h += '<div class="muted">'+dashEsc(item.ideological_profile)+'</div>';
          h += '<div class="muted small">نوع: '+dashEsc(item.entity_type || 'party')+' · وضعیت: '+dashEsc(item.legal_status || 'ثبت نشده')+' · اطمینان: '+dashEsc(item.confidence || 'نامشخص')+'</div></div>';
        }
      } else {
        h += '<div class="dashNote">در پرونده پژوهشی، حزب رقابتی رسمی ثبت نشده است؛ ساختار سیاسی این کشور از طریق جریان‌ها یا نهادهای قدرت توصیف می‌شود.</div>';
      }
      if (pp.factions && pp.factions.length) {
        h += '<h3>جریان‌ها و جناح‌های سیاسی واقعی</h3>';
        for (j=0;j<pp.factions.length;j++) {
          item=pp.factions[j] || {};
          h += '<div class="dashCard"><b>'+dashEsc(item.name_fa || item.name_en || 'جریان بدون نام')+'</b>';
          if (item.name_en) h += '<div class="muted small">'+dashEsc(item.name_en)+'</div>';
          if (item.entity_type) h += '<div class="muted small">ماهیت: '+dashEsc(item.entity_type)+'</div>';
          fields=item.policy_positions || {};
          keys2=Object.keys(fields);
          for(k=0;k<keys2.length;k++) h += '<div class="muted">'+dashEsc(keys2[k])+': '+dashEsc(fields[keys2[k]])+'</div>';
          h += '<div class="muted small">اطمینان پژوهش: '+dashEsc(item.confidence || 'نامشخص')+'</div></div>';
        }
      }
      if (pp.power_centers && pp.power_centers.length) {
        h += '<h3>مراکز واقعی قدرت</h3>';
        for (j=0;j<pp.power_centers.length;j++) {
          item=pp.power_centers[j] || {};
          h += '<div class="dashCard"><b>'+dashEsc(item.name_fa || item.name_en || 'مرکز قدرت')+'</b>';
          if (item.role) h += '<div class="muted">'+dashEsc(item.role)+'</div>';
          h += '<div class="muted small">اطمینان: '+dashEsc(item.confidence || 'نامشخص')+'</div></div>';
        }
      }
      if (pp.parliamentary_groups && pp.parliamentary_groups.length) {
        h += '<h3>فراکسیون‌ها و گروه‌های پارلمانی</h3>';
        for (j=0;j<pp.parliamentary_groups.length;j++) {
          item=pp.parliamentary_groups[j] || {};
          h += '<div class="dashCard small">'+dashEsc(item.name_fa || item.name_en || item.id || 'گروه پارلمانی')+'</div>';
        }
      }
      h += '<div class="dashNote">منبع داده: پرونده پژوهشی سیاسی کشور · وضعیت پژوهش: '+dashEsc(pp.research_status || 'نامشخص')+' · میزان اطمینان کلی: '+dashEsc((pp.data_quality || {}).confidence || 'نامشخص')+' · تاریخ بررسی: '+dashEsc((pp.data_quality || {}).last_verified || 'نامشخص')+'</div>';
      if (pp.data_quality && pp.data_quality.notes) h += '<div class="dashNote">'+dashEsc(pp.data_quality.notes)+'</div>';
    } else {
      h += dashMissing('پرونده سیاسی پژوهش‌شده','برای این کشور پرونده ساختاریافته در داده مرجع پیدا نشد؛ هیچ حزب یا جناحی به‌صورت حدسی نمایش داده نمی‌شود.');
    }
    if (r.press && r.press.length) {
      h += '<h3>آخرین اخبار و مطبوعات داخل شبیه‌سازی</h3>';
      for(i=0;i<r.press.length;i++) h += '<div class="dashCard small">'+dashEsc(r.press[i])+'</div>';
    }
    h += '<div class="dashNote">احزاب، جریان‌ها و مراکز قدرت بالا از پرونده پژوهشی کشور خوانده می‌شوند و با شاخص‌های عددی شبیه‌سازی موتور یکی نیستند. انتخابات، محبوبیت دولت و اعتراضات فقط پس از طراحی مکانیک مستقل به‌عنوان داده پویا نمایش داده خواهند شد.</div>';
    if (!isPlayer) h += '<div class="dashNote">این کشور در حالت مشاهده است؛ کنترل سیاسی فقط برای کشور تحت مدیریت بازیکن فعال خواهد بود.</div>';
  } else if (tab === 'society') {
    h += '<h3>👥 جمعیت و جامعه</h3>';
    var sp = r.country_profile || null;
    if (sp) {
      h += '<div class="dashGrid">';
      h += dashMetric('جمعیت کل',sp.population == null ? 'ثبت نشده' : Number(sp.population).toLocaleString('en-US'));
      h += dashMetric('سال آمار جمعیت',sp.population_year || '—');
      h += dashMetric('تراکم جمعیت',sp.population_density == null ? 'ثبت نشده' : sp.population_density+' نفر در کیلومتر مربع');
      h += dashMetric('رشد سالانه جمعیت',sp.population_growth_percent == null ? 'ثبت نشده' : Number(sp.population_growth_percent).toLocaleString('en-US')+'٪ · '+(sp.population_growth_year || 'سال نامشخص'));
      h += dashMetric('مساحت خشکی',sp.land_area_km2 == null ? 'ثبت نشده' : Number(sp.land_area_km2).toLocaleString('en-US')+' کیلومتر مربع');
      h += '</div>';
      h += '<div class="dashNote">جمعیت از شاخص World Bank SP.POP.TOTL گرفته شده است. سال هر مقدار کنار همان شاخص نمایش داده می‌شود. آمار مهاجرت، رشد طبیعی، ساختار سنی و نیروی کار هنوز به داده‌های مستقل نیاز دارند.</div>';
    } else h += dashMissing('اطلاعات جمعیتی','داده مرجع جمعیت برای این کشور موجود نیست.');
  } else if (tab === 'economy') {
    h += '<h3>📈 اقتصاد و بودجه</h3><div class="dashGrid">';
    h += dashMetric('شاخص اقتصاد بازی',r.eco) + dashMetric('رتبه اقتصادی جهان',r.economic_rank ? '#'+r.economic_rank : '—');
    h += dashMetric('خزانه فعلی',Number(r.money).toFixed(1)+' میلیارد') +
      dashMetric('درآمد روزانه موتور',Number(r.income_daily || 0).toFixed(2)+' میلیارد');
    h += dashMetric('برآورد ۳۰روزه درآمد',Number(r.income_monthly_estimate || 0).toFixed(1)+' میلیارد');
    h += '</div>';
    h += '<div class="dashNote">درآمد روزانه از فرمول فعلی موتور محاسبه می‌شود؛ اگر ثبات کشور کمتر از ۳۰ باشد، نصف می‌شود. برآورد ۳۰روزه صرفاً تخمین است. شاخص اقتصاد و خزانه، GDP و بودجه تفصیلی واقعی نیستند.</div>';
    if (r.economy_top && r.economy_top.length) {
      h += '<h3>🏆 پنج اقتصاد برتر جهان در بازی</h3>';
      for (i=0;i<r.economy_top.length;i++) {
        h += '<div class="row"><span>'+dashEsc((i+1)+'. '+r.economy_top[i].name)+'</span><b>'+dashEsc(r.economy_top[i].eco)+'</b></div>';
      }
    }
    var ep = r.country_profile || null;
    if (ep) {
      function refMetric(value, suffix, decimals) {
        if (value == null || !isFinite(Number(value))) return 'ثبت نشده';
        return Number(value).toLocaleString('en-US', {maximumFractionDigits: decimals == null ? 2 : decimals}) + (suffix || '');
      }
      function refYear(key) { return ep[key] ? ' · ' + ep[key] : ''; }
      h += '<h3>اقتصاد واقعی — داده مرجع</h3><div class="dashGrid">';
      h += dashMetric('تولید ناخالص داخلی اسمی (GDP)', refMetric(ep.gdp_usd, ' دلار') + refYear('gdp_year'));
      h += dashMetric('GDP سرانه اسمی', refMetric(ep.gdp_per_capita_usd, ' دلار') + refYear('gdp_year'));
      h += dashMetric('رشد اقتصادی سالانه', refMetric(ep.gdp_growth_percent, '٪') + refYear('gdp_growth_year'));
      h += dashMetric('تورم سالانه مصرف‌کننده', refMetric(ep.inflation_percent, '٪') + refYear('inflation_year'));
      h += dashMetric('بیکاری (برآورد ILO)', refMetric(ep.unemployment_percent, '٪') + refYear('unemployment_year'));
      h += dashMetric('صادرات کالا و خدمات', refMetric(ep.exports_usd, ' دلار') + refYear('exports_year'));
      h += dashMetric('واردات کالا و خدمات', refMetric(ep.imports_usd, ' دلار') + refYear('imports_year'));
      h += dashMetric('تراز تجاری کالا و خدمات', refMetric(ep.trade_balance_usd, ' دلار') + refYear('trade_balance_year'));
      h += '</div>';
      h += '<div class="dashNote">شاخص‌های تکمیلی از World Bank، پایگاه World Development Indicators هستند. سال هر شاخص مستقل نمایش داده می‌شود؛ بنابراین سال داده‌ها ممکن است بین کشورها و حتی بین شاخص‌های یک کشور متفاوت باشد. مقادیر خالی به معنی نبود داده معتبر در بازه انتخاب‌شده است، نه صفر.</div>';
    } else h += dashMissing('داده اقتصادی مرجع','پرونده اطلاعات پایه این کشور در دسترس نیست.');
  } else if (tab === 'resources') {
    h += '<h3>⛏ منابع طبیعی</h3>';
    h += dashMissing('منابع کشور و استان‌ها','ذخایر نفت، گاز، زغال‌سنگ، اورانیوم، آهن، طلا و سایر منابع هنوز داده‌گذاری نشده‌اند. در فاز C باید روی نقشه نیز به شکل مدل سه‌بعدی سبک دیده شوند.');
  } else if (tab === 'industry') {
    h += '<h3>🏭 صنعت و زیرساخت</h3>';
    h += dashMissing('زیرساخت‌های کشور','نیروگاه، پالایشگاه، فرودگاه، بندر، مراکز صنعتی و ظرفیت تولید هنوز پیاده‌سازی نشده‌اند. هر تأسیسات در فاز C شناسه مستقل، استان، ظرفیت، تولید و نوار سلامت خواهد داشت.');
    if (PROV.sel) h += provPanelHtml();
    else h += '<div class="dashNote">برای مشاهده اطلاعات جغرافیایی پایه، یک استان از روی کره انتخاب کن. داده زیرساختی استان در مرحله بعد اضافه می‌شود.</div>';
  } else if (tab === 'military') {
    h += '<h3>🛡 وضعیت نظامی</h3><div class="dashCard">';
    h += dashPercentBar('قدرت نظامی',r.mil);
    h += dashPercentBar('فناوری',r.tech);
    h += '</div><div class="dashGrid">';
    h += dashMetric('کلاهک هسته‌ای (شاخص فعلی)',r.nukes) + dashMetric('تجهیزات ثبت‌شده',r.arsenal.length);
    h += '</div>';
    if (r.arsenal.length) { h += '<h3>تجهیزات ثبت‌شده فعلی</h3>'; for(i=0;i<r.arsenal.length;i++) h += '<div class="dashCard small">'+dashEsc(r.arsenal[i])+'</div>'; }
    h += dashMissing('فرماندهی نظامی تفصیلی','تفکیک نیروهای زمینی، هوایی، دریایی، پدافند، موجودی و آمادگی در مراحل بعد طراحی می‌شود. پنجره فرماندهی مستقل در فاز D ساخته خواهد شد.');
  } else if (tab === 'relations') {
    h += '<h3>🤝 روابط خارجی</h3>';
    if (ST && r.name === ST.player) {
      h += '<div class="dashNote">نمای کلی روابط کشور تحت مدیریت شما؛ اطلاعات زیر از وضعیت فعلی موتور بازی خوانده می‌شود.</div>';
      var allyList = ST.allies || [], pactList = ST.pacts || [], warList = ST.wars || [], opponents = [];
      for (i=0;i<warList.length;i++) {
        if (warList[i] && warList[i].length === 2) {
          if (warList[i][0] === r.name) opponents.push(warList[i][1]);
          else if (warList[i][1] === r.name) opponents.push(warList[i][0]);
        }
      }
      h += '<h3>متحدان ثبت‌شده</h3>';
      h += allyList.length ? allyList.map(function(n){return '<div class="row"><span>'+dashEsc(n)+'</span><span class="muted">اتحاد</span></div>';}).join('') : '<div class="dashNote">در حال حاضر متحدی در فهرست موتور ثبت نشده است.</div>';
      h += '<h3>پیمان‌های عدم تجاوز</h3>';
      h += pactList.length ? pactList.map(function(n){return '<div class="row"><span>'+dashEsc(n)+'</span><span class="muted">عدم تجاوز</span></div>';}).join('') : '<div class="dashNote">پیمان عدم تجاوز ثبت‌شده‌ای وجود ندارد.</div>';
      h += '<h3>وضعیت جنگ</h3>';
      h += opponents.length ? '<div class="dashCard">در جنگ با: '+opponents.map(dashEsc).join('، ')+'</div>' : '<div class="dashNote">کشور شما در حال حاضر در جنگ ثبت‌شده‌ای نیست.</div>';
    } else {
      var relTags = r.tags || [];
      var isPlayerAlly = relTags.indexOf('🤝 متحد') !== -1;
      var hasPlayerPact = relTags.indexOf('📜 عدم تجاوز') !== -1;
      if (r.rel != null && ST) h += '<h3>رابطه با کشور بازیکن ('+dashEsc(ST.player)+')</h3>'+barHtml('شاخص رابطه',r.rel,r.rel<0?'bad':'');
      h += '<h3>وضعیت اتحاد با کشور بازیکن</h3>';
      h += isPlayerAlly ? '<div class="dashCard">🤝 این کشور در فهرست متحدان کشور بازیکن ثبت شده است.</div>' : '<div class="dashNote">اتحاد ثبت‌شده‌ای با کشور بازیکن وجود ندارد.</div>';
      h += '<h3>پیمان عدم تجاوز با کشور بازیکن</h3>';
      h += hasPlayerPact ? '<div class="dashCard">📜 پیمان عدم تجاوز با کشور بازیکن ثبت شده است.</div>' : '<div class="dashNote">پیمان عدم تجاوزی با کشور بازیکن ثبت نشده است.</div>';
      h += '<h3>وضعیت جنگ</h3>';
      h += r.war_with && r.war_with.length ? '<div class="dashCard">در جنگ با: '+r.war_with.map(dashEsc).join('، ')+'</div>' : '<div class="dashNote">در حال حاضر جنگ ثبت‌شده‌ای برای این کشور وجود ندارد.</div>';
      h += '<div class="dashNote">اتحادها و پیمان‌های این کشور با سایر کشورهای جهان هنوز در موتور به‌صورت شبکهٔ مستقل ثبت نشده‌اند؛ اینجا فقط وضعیت آن در برابر کشور بازیکن نمایش داده می‌شود.</div>';
    }
    if (r.friends && r.friends.length) {
      h += '<h3>کشورهای نزدیک</h3>';
      for (i=0;i<r.friends.length;i++) h += '<div class="row"><span>'+dashEsc(r.friends[i][0])+'</span><span class="muted">'+dashEsc(r.friends[i][1])+'</span></div>';
    }
    if (r.enemies && r.enemies.length) {
      h += '<h3>روابط پرتنش</h3>';
      for (i=0;i<r.enemies.length;i++) h += '<div class="row"><span>'+dashEsc(r.enemies[i][0])+'</span><span class="muted">'+dashEsc(r.enemies[i][1])+'</span></div>';
    }
    h += dashMissing('روابط تجاری و نفوذ بین‌المللی','آمار تجارت، روابط دیپلماتیک تفصیلی و نفوذ بین‌المللی هنوز طراحی نشده‌اند.');
  } else if (tab === 'pacts') {
    h += pactPanelHtml(r.name, isPlayer);
    h += alliancePanelHtml(r.name, isPlayer);
  } else if (tab === 'sanctions') {
    h += '<h3>⛔ تحریم‌ها</h3>';
    h += dashMissing('وضعیت تحریم‌ها','کشورهای تحریم‌کننده، نوع و محدودیت تحریم، اثر اقتصادی و روند مذاکره برای رفع تحریم هنوز به شکل پنل تفصیلی پیاده‌سازی نشده‌اند.');
    if (ST && r.name === ST.player) h += '<div class="dashCard small">شاخص فعلی تحریم شورای امنیت در وضعیت جهان: '+dashEsc(ST.un_censures)+'</div>';
  } else if (tab === 'diplomacy') {
    h += diplomacyPanelHtml(r, isPlayer);
  } else if (tab === 'news') {
    h += '<h3>📰 اخبار و رویدادها</h3>';
    if (r.press && r.press.length) for(i=0;i<r.press.length;i++) h += '<div class="press">'+dashEsc(r.press[i])+'</div>';
    else h += '<div class="dashNote">در حال حاضر خبر داخلی ثبت‌شده‌ای برای این کشور در داده موجود نیست.</div>';
    h += '<div class="dashNote">خبرها فعلاً عمدتاً از متن‌های ازپیش‌تعیین‌شده موتور می‌آیند. رسانه‌های پویا با کمک AI آنلاین در فاز F اضافه می‌شوند؛ رویداد واقعی بازی منبع حقیقت خبر خواهد بود.</div>';
  }
  if (tab === 'tribune') {
    h += '<h3>🏛 تریبون ملی</h3>';
    var preparedSessions = ST && ST.conversation_sessions ? ST.conversation_sessions : [];
    if (isPlayer && preparedSessions.length) {
      h += '<h4>نشست‌های آماده‌شده</h4>';
      h += '<div class="dashNote">این نشست‌ها ذخیره شده‌اند و زمینه مشترک آن‌ها حفظ می‌شود؛ هیچ پیام یا پاسخ هوش مصنوعی تولید نشده و چت تا فاز F غیرفعال است.</div>';
      for (var si=preparedSessions.length-1, shown=0;si>=0 && shown<10;si--,shown++) {
        var session = preparedSessions[si] || {};
        var visibilityLabels = {public:'عمومی',normal:'غیرعمومی با پوشش رسانه‌ای',confidential:'محرمانه'};
        var typeLabels = {standard:'عادی',alliance:'اتحاد',pact:'پیمان',diplomacy:'دیپلماسی',ceasefire:'آتش‌بس',trade:'تجارت',other:'سایر'};
        var meetingLeft=session.meeting_date?calendarDaysRemaining(session.meeting_date):null;
        var meetingStatus=session.meeting_status==='pending_ai_acceptance'?'در انتظار پذیرش کشور مقابل':(session.meeting_status==='pending_player_acceptance'?'در انتظار پاسخ بازیکن':(session.meeting_status==='rejected'?'رد شده':(session.meeting_status==='due'?'موعد فرارسیده':(session.meeting_status==='confirmed'?'تأیید شده':'بدون زمان‌بندی'))));
        h += '<div class="dashCard"><div class="row"><b>'+dashEsc(session.id || 'نشست')+'</b><span class="badge">'+dashEsc(meetingStatus)+' · چت قفل</span></div>';
        h += '<div>موضوع: '+dashEsc(session.topic || 'گفت‌وگوی دیپلماتیک')+'</div>';
        h += '<div>کشورها: '+dashEsc((session.participants || []).join('، '))+'</div>';
        h += '<div class="muted small">نوع: '+dashEsc(typeLabels[session.negotiation_type] || session.negotiation_type || '—')+' · انتشار: '+dashEsc(visibilityLabels[session.visibility_mode] || session.visibility_mode || '—')+' · تاریخ پیشنهادی: '+dashEsc(session.meeting_date || '—')+'</div>';
        if(session.meeting_date && meetingLeft!==null) h += '<div class="muted small">'+(meetingLeft===0?'موعد فرا رسیده':'باقی‌مانده تا نشست: '+meetingLeft+' روز')+'</div>';
        h += '<div class="muted small">گفت‌وگو تا رسیدن موعد و فعال‌شدن رسمی هوش مصنوعی زنده قفل می‌ماند.</div></div>';
      }
    }
    if (isPlayer && ST && ST.regime_crisis) {
      var crisis = ST.regime_crisis;
      var crisisLabel = crisis.kind === 'coup_crisis' ? 'بحران کودتا' : (crisis.kind === 'revolution_crisis' ? 'بحران انقلاب' : (crisis.kind === 'revolution' ? 'انقلاب' : 'کودتا'));
      h += '<div class="tribuneLocked"><b>⚠️ بحران تغییر حکومت: '+dashEsc(crisisLabel)+'</b><br>';
      h += 'تاریخ رخداد: '+dashEsc(crisis.date || '—')+'<br>';
      h += 'مشروعیت فعلی حکومت: <b>'+dashEsc(ST.legitimacy)+'٪</b><br>';
      h += 'ثبات هنگام رخداد: '+dashEsc(crisis.stability_at_event)+'٪<br>';
      if (crisis.kind === 'coup_crisis' || crisis.kind === 'revolution_crisis') {
        h += 'میانگین حمایت اجتماعی هنگام رخداد: '+dashEsc(crisis.social_support_average)+'٪<br>';
        h += 'قدرت نظامی هنگام رخداد: '+dashEsc(crisis.military_strength_at_event)+'٪<br>';
      }
      if (crisis.institution) {
        h += '<hr><b>نهاد سیاسی متناظر با ساختار کشور</b><br>';
        h += dashEsc(crisis.institution.name || 'نامشخص')+'<br>';
        h += '<span class="muted small">مبنای تشخیص: '+dashEsc(crisis.institution.basis || 'نامشخص')+'</span><br>';
        h += dashEsc(crisis.institution.focus || '')+'<br>';
      }
      h += 'وضعیت: در انتظار فعال‌سازی هوش مصنوعی زنده؛ هیچ گفت‌وگوی ساختگی اجرا نمی‌شود.</div>';
    } else {
      h += '<div class="tribuneLocked"><b>این بخش هنوز فعال نشده است.</b><br>گفت‌وگوی زنده با شورای ملی / کنگره و مردم فقط پس از فعال‌سازی رسمی هوش مصنوعی زنده در بازی در دسترس قرار می‌گیرد. در حال حاضر هیچ گفت‌وگوی شبیه‌سازی‌شده یا پاسخ از پیش‌نوشته‌شده‌ای جایگزین هوش مصنوعی زنده نمی‌شود.</div>';
    }
  }
  return h;
}
function dashSelectTab(id) {
  DASH_TAB = id;
  if (LAST_COUNTRY_R) renderCountryPanel(LAST_COUNTRY_R);
}
function renderCountryPanel(r) {
  LAST_COUNTRY_R = r;
  var box = el('countryInfo');
  el('idleInfo').style.display = 'none';
  box.style.display = 'block';
  var isPlayer = !!(ST && ST.player === r.name), h = '';
  h += '<div class="countryHeader"><div class="countryHeaderText"><h2>' + dashEsc(r.name) + '</h2>' +
    '<div class="muted small">' + dashEsc(r.en || '') + ' · ' + dashEsc(r.iso3 || '') + '</div></div></div>';
  h += '<div style="margin:4px 0">' + (isPlayer
      ? '<span class="badge" style="color:#ffd166">🏰 کشور شما — کنترل کامل</span>'
      : '<span class="badge">👥 حالت مشاهده — کشور شما: '+dashEsc(ST ? ST.player : '—')+'</span>') + '</div>';
  h += '<div>'+(r.tags || []).map(function(t){return '<span class="badge">'+dashEsc(t)+'</span>';}).join('')+'</div>';
  h += '<div class="dashTabs">';
  for(var t=0;t<DASH_TABS.length;t++){
    h += '<button type="button" class="dashTab'+(DASH_TAB===DASH_TABS[t][0]?' active':'')+
      '" data-dash-tab="'+DASH_TABS[t][0]+'">'+DASH_TABS[t][1]+'</button>';
  }
  h += '</div><div id="dashSection">'+dashSectionHtml(r,isPlayer,DASH_TAB)+'</div>';
  if (DASH_TAB !== 'industry' && PROV.sel) h += provPanelHtml();
  if (!isPlayer && ST) h += '<div class="dashNote">کشور انتخاب‌شده فقط در حالت مشاهده است؛ کشور تحت مدیریت شما همچنان «'+dashEsc(ST.player)+'» است.</div>';
  box.innerHTML = h;
  var btns = box.querySelectorAll('[data-dash-tab]');
  for (var b=0;b<btns.length;b++) btns[b].onclick = (function(id){return function(){dashSelectTab(id);};})(btns[b].getAttribute('data-dash-tab'));
  provAfterPanel();
  bindPoliticalChangeForm(r);
  if (DASH_TAB === 'pacts') bindPactActions();
  if (DASH_TAB === 'pacts') bindAllianceActions();
  if (DASH_TAB === 'diplomacy' && isPlayer) bindDiplomacyActions();
  if ((DASH_TAB === 'pacts' || DASH_TAB === 'diplomacy') && isPlayer) bindConversationShortcuts();
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
  var requestId=++PROV.requestId;PROV.sel=null;provDisposeGroup();if(!PROV.on){PROV.iso=null;refreshLabels();return;}
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

function provOff() {++PROV.requestId;PROV.sel=null;provDisposeGroup();PROV.iso=null;refreshLabels();provRenderPanel();}

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
function renderGameClock() {
  var box = el('gameClockText');
  if (!box) return;
  if (!ST) { box.textContent = '📅 — | 🕒 —'; return; }
  var parts = String(ST.game_date || '').split('-');
  var dateText = parts.length === 3 ? parts[2] + '/' + parts[1] + '/' + parts[0] : String(ST.year || '—');
  var hh = ('0' + (ST.hour || 0)).slice(-2);
  var mm = ('0' + (ST.minute || 0)).slice(-2);
  box.textContent = '📅 ' + dateText + '  |  🕒 ' + hh + ':' + mm;
}

function advanceGameTime(minutes) {
  if (!ST) { flash('اول بازی را شروع کن.'); return; }
  var five = el('btn5h'), day = el('btnEnd');
  if (five) five.disabled = true;
  if (day) day.disabled = true;
  postJSON('api/time', { minutes: minutes }, function (r) {
    if (r.out) flash(r.out);
    else if (!r.ok && r.error) flash(r.error);
    loadState(function () {
      if (five) five.disabled = false;
      if (day) day.disabled = false;
    });
  }, function (st, tx) {
    flash(netErrMsg(st, tx) + ' — زمان جلو نرفت.');
    if (five) five.disabled = false;
    if (day) day.disabled = false;
  });
}

function endDay() { advanceGameTime(1440); }

/* صندوق پیام‌ها؛ محتوای واقعی AI زنده فقط در فاز F وارد این فهرست می‌شود. */
function renderInbox() {
  var list = el("inboxList"), count = el("inboxUnreadCount");
  var messages = (ST && ST.inbox_messages) || [], unread = 0, html = "";
  for (var i=0;i<messages.length;i++) if (messages[i] && messages[i].status === "unread") unread++;
  if (count) { count.textContent = unread ? String(unread) : ""; count.style.display = unread ? "inline-block" : "none"; }
  if (!list) return;
  if (!messages.length) {
    list.innerHTML = '<div class="inboxEmpty">📭 هنوز پیام یا درخواستی از کشورهای تحت کنترل هوش مصنوعی زنده دریافت نشده است.<br>پس از فعال‌شدن هوش مصنوعی زنده در فاز F، درخواست‌ها، پیشنهاد پیمان‌ها و پیام‌های گفت‌وگو در این قسمت نمایش داده می‌شوند.</div>';
    return;
  }
  for (var j=messages.length-1;j>=0;j--) {
    var m=messages[j] || {}, id=String(m.id || ""), safeId=id.replace(/&/g,"&amp;").replace(/"/g,"&quot;"), linkedSessionDate='';
    if(m.conversation_id) { var ss=(ST&&ST.conversation_sessions)||[]; for(var si=0;si<ss.length;si++) if(ss[si]&&ss[si].id===m.conversation_id){linkedSessionDate=ss[si].meeting_date||'';break;} }
    html += '<div class="inboxCard"><div class="inboxCardHead"><b>'+dashEsc(m.sender_country || "کشور نامشخص")+'</b><span>'+(m.status==="unread"?"● خوانده‌نشده":"خوانده‌شده")+'</span></div>';
    html += '<div class="inboxCardTitle">'+dashEsc(m.title || "پیام جدید")+'</div><button type="button" class="inboxShowBtn" data-message-id="'+safeId+'">نمایش</button>';
    html += '<div class="inboxMessageBody" id="inboxBody_'+dashEsc(id)+'" hidden><div>'+dashEsc(m.body || "جزئیات پیام ثبت نشده است.")+'</div><small>'+dashEsc(m.date || "")+' · نوع: '+dashEsc(m.message_type || "message")+'</small>';
    if (m.conversation_id) html += '<div class="inboxFutureNote">این پیام به یک زمینه گفت‌وگو متصل است؛ پاسخ زنده پس از فعال‌شدن فاز F در دسترس قرار می‌گیرد.</div>';
    if (m.message_type === 'meeting_request' && m.conversation_id) {
      html += '<div class="inboxFutureNote">تاریخ پیشنهادی نشست: '+dashEsc(m.metadata && m.metadata.meeting_date ? m.metadata.meeting_date : 'ثبت‌شده در نشست')+'</div>';
      html += '<button type="button" class="inboxMeetingDecision" data-message-id="'+safeId+'" data-meeting-decision="accept">پذیرش تاریخ نشست</button> <button type="button" class="inboxMeetingDecision" data-message-id="'+safeId+'" data-meeting-decision="reject">رد درخواست</button>';
    } else if (m.response_allowed || m.conversation_id) html += '<label>تاریخ پیشنهادی پاسخ <input type="date" class="inboxMeetingDate" data-message-date="'+safeId+'" min="'+dashEsc(calendarNextDate())+'" value="'+dashEsc(linkedSessionDate||calendarNextDate())+'"></label><button type="button" class="inboxReplyBtn" data-message-id="' + safeId + '">پیشنهاد نشست و رفتن به تریبون</button><div class="inboxFutureNote">تاریخ ابتدا به طرف مقابل پیشنهاد می‌شود؛ تا پذیرش آن، نشست در تقویم قطعی و قابل گفت‌وگو نیست.</div>';
    html += '</div></div>';
  }
  list.innerHTML = html;
  var buttons=list.querySelectorAll(".inboxShowBtn");
  for (var k=0;k<buttons.length;k++) buttons[k].onclick=function(){
    var mid=this.getAttribute("data-message-id"), body=el("inboxBody_"+mid);
    if (body) body.hidden=!body.hidden;
    this.textContent=(body && !body.hidden)?"بستن":"نمایش";
    if (ST) postJSON("api/inbox/read",{message_id:mid},function(r){if(r.ok){loadState();}},function(){});
  };
  var decisionButtons=list.querySelectorAll('.inboxMeetingDecision');
  for (var z=0;z<decisionButtons.length;z++) decisionButtons[z].onclick=function(){
    var mid=this.getAttribute('data-message-id'), decision=this.getAttribute('data-meeting-decision'), message=null, msgs=(ST&&ST.inbox_messages)||[];
    for(var mi=0;mi<msgs.length;mi++) if(String(msgs[mi].id||'')===mid){message=msgs[mi];break;}
    var linkedId=message && message.conversation_id;
    if(!linkedId){flash('نشست مرتبط با درخواست پیدا نشد.');return;}
    var btn=this;btn.disabled=true;
    postJSON('api/conversations/meeting/decision',{conversation_id:linkedId,decision:decision},function(res){
      if(!res||!res.ok){btn.disabled=false;flash((res&&res.error)||'تصمیم نشست ثبت نشد.');return;}
      loadState(function(){setInboxOpen(true);flash(decision==='accept'?(res.confirmed?'تاریخ نشست با پذیرش همه طرف‌ها به تقویم اضافه شد.':'پاسخ شما ثبت شد؛ پس از پذیرش همه کشورهای شرکت‌کننده، موعد وارد تقویم می‌شود.'):'درخواست نشست رد شد.');});
    },function(code,response){btn.disabled=false;flash(netErrMsg(code,response)+' — تصمیم نشست ثبت نشد.');});
  };
  var replyButtons=list.querySelectorAll(".inboxReplyBtn");
  for (var q=0;q<replyButtons.length;q++) replyButtons[q].onclick=function(){
    var mid=this.getAttribute("data-message-id"), message=null, i, sessions=(ST && ST.conversation_sessions)||[], linked=null;
    var messages=(ST && ST.inbox_messages)||[];
    for(i=0;i<messages.length;i++) if(String(messages[i].id||"")===mid) { message=messages[i]; break; }
    if(!message || (!message.response_allowed && !message.conversation_id)) { flash("برای این پیام امکان آماده‌سازی پاسخ ثبت نشده است."); return; }
    if(message.conversation_id) for(i=0;i<sessions.length;i++) if(sessions[i].id===message.conversation_id) { linked=sessions[i]; break; }
    if(message.conversation_id && !linked) { flash("نشست مرتبط با این پیام پیدا نشد؛ تاریخچه حفظ نشده و نشست تازه‌ای ساخته نمی‌شود."); return; }
    var payload={
      participants: linked ? (linked.participants||[]) : [message.sender_country],
      topic: linked ? (linked.topic||message.title||"پاسخ به پیام ورودی") : (message.title||"پاسخ به پیام ورودی"),
      visibility_mode: linked ? (linked.visibility_mode||"public") : "public",
      negotiation_type: linked ? (linked.negotiation_type||"standard") : (message.message_type==="treaty_offer"?"pact":(message.message_type==="alliance_invite"?"alliance":"standard")),
      source:"inbox",
      context:{inbox_message_id:mid,sender_country:message.sender_country,message_type:message.message_type||"message",response_to_incoming:true},
      conversation_id:message.conversation_id||null,
      meeting_date:(function(){var d=list.querySelector('[data-message-date="'+mid+'"]');return d?d.value:null;})()
    };
    var btn=this; btn.disabled=true;
    postJSON("api/conversations/prepare",payload,function(res){
      btn.disabled=false;
      if(!res || !res.ok || !res.session) { flash((res&&res.error)||"نشست پاسخ آماده نشد."); return; }
      loadState(function(){ DASH_TAB="tribune"; if(LAST_COUNTRY_R) renderCountryPanel(LAST_COUNTRY_R); flash("تاریخ نشست پاسخ پیشنهاد شد؛ تا پذیرش کشور مقابل و رسیدن موعد، گفت‌وگو قفل است."); });
    },function(code,response){ btn.disabled=false; flash(netErrMsg(code,response)+" — نشست پاسخ ذخیره نشد."); });
  };
}
function setInboxOpen(open) {
  var box=el("inboxPanel"), btn=el("btnInbox");
  if (!box || !btn) return;
  box.hidden=!open;
  btn.setAttribute("aria-expanded",open?"true":"false");
  if (open) renderInbox();
}
function advanceFiveHours() { advanceGameTime(300); }

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
  /* دکمه شروع مستقل از خطاهای احتمالی اتصال سایر کنترل‌ها */
  var startBtn = el('btnStart');
  if (startBtn) startBtn.onclick = function () { startGame(false); };
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
  el('btn5h').onclick = advanceFiveHours;
  provToggleBtn();   /* B2: دکمه مرز استان‌ها (اگر در HTML باشد) */
  bindTradeShipToggle();
  var tb = el('panelToggle');
  if (tb) tb.onclick = togglePanel;   /* فلش باز/بسته پنل */
  var eb = el('eventPanelToggle');
  if (eb) eb.onclick = toggleEventPanel;
  var inboxBtn=el("btnInbox"), inboxClose=el("btnInboxClose");
  if (inboxBtn) inboxBtn.onclick=function(){setInboxOpen(true);};
  if (inboxClose) inboxClose.onclick=function(){setInboxOpen(false);};
  bindEventTalkControls();
  bindEventPanelTabs();
  bindSanctionsUI();

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
