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
    renderGameClock();
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

/* کلیدهای حالت مذاکرات؛ مستقل از هم و فعلاً فقط در رابط کاربری */
var EVENT_TALK_STATE = { confidential: false, alliance: false };
function renderEventTalkState() {
  var confidential = EVENT_TALK_STATE.confidential;
  var alliance = EVENT_TALK_STATE.alliance;
  var cb = el('btnConfidentialTalk'), ab = el('btnAllianceTalk');
  var cs = el('confidentialTalkState'), as = el('allianceTalkState');
  var title = el('eventStatementTitle'), note = el('eventContextNote');
  var targetBox = el('confidentialTargetBox');
  var confidentialOnly = confidential && !alliance;
  if (targetBox) targetBox.hidden = !confidentialOnly;
  if (confidentialOnly) renderConfidentialTargets();
  var feedBox = el('eventStatementFeed');
  var composerBox = el('eventStatementInput');
  var sendBox = el('eventStatementSend');
  if (feedBox) feedBox.style.display = confidentialOnly ? 'none' : '';
  if (composerBox && composerBox.parentNode) composerBox.parentNode.style.display = (confidential || alliance) ? 'none' : ''; 
  if (sendBox) sendBox.style.display = (confidential || alliance) ? 'none' : '';
  if (cb) { cb.className = 'eventNegotiationToggle' + (confidential ? ' active' : ''); cb.setAttribute('aria-pressed', confidential ? 'true' : 'false'); }
  if (ab) { ab.className = 'eventNegotiationToggle' + (alliance ? ' active' : ''); ab.setAttribute('aria-pressed', alliance ? 'true' : 'false'); }
  if (cs) cs.textContent = confidential ? 'روشن' : 'خاموش';
  if (as) as.textContent = alliance ? 'روشن' : 'خاموش';
  var context = [];
  if (confidential) context.push('مذاکره محرمانه');
  if (alliance) context.push('مذاکره با اتحاد');
  var feed = el('eventStatementFeed');
  if (!context.length) {
    if (title) title.textContent = 'پنجره بیانیه‌ها · حالت عمومی';
    if (note) note.textContent = 'حالت عمومی فعال است؛ مذاکره محرمانه در رسانه‌ها یا بیانیه عمومی نمایش داده نمی‌شود.';
    if (feed && feed.querySelector('.eventStatementEmpty')) feed.querySelector('.eventStatementEmpty').textContent = 'بیانیه‌ای برای نمایش وجود ندارد. پس از اتصال هوش مصنوعی زنده، بیانیه‌های عمومی کشورها در این قسمت نمایش داده می‌شوند.';
  } else if (confidential && alliance) {
    if (title) title.textContent = 'مذاکره محرمانه با اتحاد';
    if (note) note.textContent = 'این گفت‌وگو فقط میان بازیکن و هم‌پیمانان انجام می‌شود و کاملاً محرمانه است؛ هیچ محتوایی به مطبوعات یا بیانیه عمومی راه پیدا نمی‌کند، مگر اینکه بازیکن خودش آن را منتشر کند.';
    if (feed && feed.querySelector('.eventStatementEmpty')) feed.querySelector('.eventStatementEmpty').textContent = 'فضای گفت‌وگوی محرمانه با اتحاد آماده است. محتوای این مذاکره خصوصی باقی می‌ماند و به رسانه‌ها منتقل نمی‌شود.';
  } else if (confidential) {
    if (title) title.textContent = 'مذاکره محرمانه · انتخاب کشورها';
    if (note) note.textContent = 'کشورهای موردنظر را انتخاب و تأیید کن. این مذاکره خصوصی می‌ماند و به رسانه‌ها یا بیانیه عمومی منتقل نمی‌شود.';
  } else {
    if (title) title.textContent = 'پنجره مذاکرات با اتحاد';
    if (note) note.textContent = 'این بخش برای گفت‌وگو با اتحاد و هم‌پیمانان است. برای حالت محرمانه، گزینه مذاکره محرمانه را نیز روشن کن.';
  }
}
var EVENT_PANEL_VIEW = 'statements';
function setEventPanelView(view) {
  EVENT_PANEL_VIEW = (view === 'military' || view === 'sanctions') ? view : 'statements';
  var sv = el('eventStatementView'), mv = el('eventMilitaryView'), xv = el('eventSanctionsView');
  var sb = el('eventTabStatements'), mb = el('eventTabMilitary'), xb = el('eventTabSanctions');
  var isMilitary = EVENT_PANEL_VIEW === 'military', isSanctions = EVENT_PANEL_VIEW === 'sanctions';
  if (sv) sv.hidden = isMilitary || isSanctions;
  if (mv) mv.hidden = !isMilitary;
  if (xv) xv.hidden = !isSanctions;
  if (sb) { sb.className = 'eventPanelTab' + (!isMilitary && !isSanctions ? ' active' : ''); sb.setAttribute('aria-selected', (!isMilitary && !isSanctions) ? 'true' : 'false'); }
  if (mb) { mb.className = 'eventPanelTab' + (isMilitary ? ' active' : ''); mb.setAttribute('aria-selected', isMilitary ? 'true' : 'false'); }
  if (xb) { xb.className = 'eventPanelTab' + (isSanctions ? ' active' : ''); xb.setAttribute('aria-selected', isSanctions ? 'true' : 'false'); }
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
  var edit=el('confidentialEditCountries');
  if(!box || !list) return;
  if(CONFIDENTIAL_TARGETS.length) {
    list.hidden=true;
    if(edit) edit.hidden=false;
    if(summary) summary.textContent='مذاکره محرمانه با '+CONFIDENTIAL_TARGETS.join('، ');
  } else {
    list.hidden=false;
    if(edit) edit.hidden=true;
    renderCountryPicker('confidentialCountryList',CONFIDENTIAL_DRAFT,'conf');
    if(summary) summary.textContent='کشورهای موردنظر را انتخاب کن و تأیید را بزن. انتخاب چند کشور هم‌زمان امکان‌پذیر است.';
  }
}
function bindConfidentialTargetPicker() {
  var confirm=el('confidentialConfirmCountries'), cancel=el('confidentialCancelCountries'), edit=el('confidentialEditCountries');
  if(confirm) confirm.onclick=function(){ CONFIDENTIAL_DRAFT=readCountryPicker('confidentialCountryList'); CONFIDENTIAL_TARGETS=CONFIDENTIAL_DRAFT.slice(0); renderConfidentialTargets(); };
  if(cancel) cancel.onclick=function(){ CONFIDENTIAL_DRAFT=[]; CONFIDENTIAL_TARGETS=[]; renderConfidentialTargets(); };
  if(edit) edit.onclick=function(){ CONFIDENTIAL_DRAFT=CONFIDENTIAL_TARGETS.slice(0); renderCountryPicker('confidentialCountryList',CONFIDENTIAL_DRAFT,'conf'); el('confidentialCountryList').hidden=false; edit.hidden=true; };
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
    var cats=SANCTION_APPLIED[names[i]], labels=[];
    for(var k=0;k<SANCTION_CATEGORIES.length;k++) if(cats[SANCTION_CATEGORIES[k][0]]) labels.push(SANCTION_CATEGORIES[k][1]);
    out+='<div class="sanctionCard"><strong>'+names[i]+'</strong><div class="sanctionInfo">محدودیت‌هایی که فقط از طرف کشور بازیکن اعمال شده: '+(labels.join('، ')||'بدون تحریم فعال')+'</div></div>';
  }
  box.innerHTML=out;
}
function bindSanctionsUI() {
  var choose=el('sanctionChooseCountries'), confirm=el('sanctionConfirmCountries'), cancel=el('sanctionCancelCountries');
  if(choose) choose.onclick=function(){ SANCTION_DRAFT_COUNTRIES=SANCTION_TARGET_COUNTRIES.slice(0); renderCountryPicker('sanctionCountryList',SANCTION_DRAFT_COUNTRIES,'san'); el('sanctionCountryPicker').hidden=false; };
  if(confirm) confirm.onclick=function(){ SANCTION_DRAFT_COUNTRIES=readCountryPicker('sanctionCountryList'); SANCTION_TARGET_COUNTRIES=SANCTION_DRAFT_COUNTRIES.slice(0); el('sanctionCountryPicker').hidden=true; renderSanctionTargets(); };
  if(cancel) cancel.onclick=function(){ SANCTION_DRAFT_COUNTRIES=[]; SANCTION_TARGET_COUNTRIES=[]; el('sanctionCountryPicker').hidden=true; renderSanctionTargets(); };
  var apply=el('sanctionApply'), cancelAll=el('sanctionCancelAll');
  if(apply) apply.onclick=function(){
    var active={};
    for(var i=0;i<SANCTION_CATEGORIES.length;i++){ var key=SANCTION_CATEGORIES[i][0]; if(SANCTION_CATEGORY_STATE[key]) active[key]=true; }
    if(!SANCTION_TARGET_COUNTRIES.length){ var st2=el('sanctionActionStatus'); if(st2) st2.textContent='ابتدا کشورهای هدف را انتخاب کن.'; return; }
    for(var n=0;n<SANCTION_TARGET_COUNTRIES.length;n++) {
      var target=SANCTION_TARGET_COUNTRIES[n];
      if(Object.keys(active).length) SANCTION_APPLIED[target]=JSON.parse(JSON.stringify(active));
      else delete SANCTION_APPLIED[target];
    }
    var status=el('sanctionActionStatus'); if(status) status.textContent='وضعیت زمینه‌های انتخاب‌شده برای کشورهای هدف به‌روزرسانی شد؛ اثر اقتصادی هنوز به موتور اقتصاد متصل نیست.';
    renderAppliedSanctions();
  };
  if(cancelAll) cancelAll.onclick=function(){
    SANCTION_APPLIED={}; SANCTION_CATEGORY_STATE={}; renderSanctionCategories(); renderAppliedSanctions();
    var status=el('sanctionActionStatus'); if(status) status.textContent='تمام تحریم‌های ثبت‌شده در نمونه رابط کاربری لغو شدند.';
  };
  var imposed=el('sanctionTabImposed'), target=el('sanctionTabTarget');
  if(imposed) imposed.onclick=function(){ setSanctionInnerView('imposed'); };
  if(target) target.onclick=function(){ setSanctionInnerView('target'); };
  renderSanctionCategories(); renderAppliedSanctions(); renderSanctionTargets();
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
  if (sb) sb.onclick = function () { setEventPanelView('statements'); };
  if (mb) mb.onclick = function () { setEventPanelView('military'); };
  if (xb) xb.onclick = function () { setEventPanelView('sanctions'); };
  setEventPanelView('statements');
}
function bindEventTalkControls() {
  var cb = el('btnConfidentialTalk'), ab = el('btnAllianceTalk');
  if (cb) cb.onclick = function () { EVENT_TALK_STATE.confidential = !EVENT_TALK_STATE.confidential; renderEventTalkState(); };
  if (ab) ab.onclick = function () { EVENT_TALK_STATE.alliance = !EVENT_TALK_STATE.alliance; renderEventTalkState(); };
  bindConfidentialTargetPicker();
  renderEventTalkState();
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

var DASH_TAB = 'general';
var DASH_TABS = [
  ['general','اطلاعات عمومی'],['politics','سیاست داخلی'],['society','جمعیت و جامعه'],
  ['economy','اقتصاد و بودجه'],['resources','منابع طبیعی'],['industry','صنعت و زیرساخت'],
  ['military','وضعیت نظامی'],['relations','روابط خارجی'],['pacts','پیمان‌ها'],
  ['sanctions','تحریم‌ها'],['diplomacy','دیپلماسی'],['news','اخبار']
];

function dashEsc(v) {
  return String(v == null ? '—' : v).replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}
function dashMissing(title, detail) {
  return '<div class="dashNote"><b>⏳ ' + dashEsc(title) + '</b><br>' +
    dashEsc(detail || 'ساختار داده و منطق این قابلیت در ادامه فاز B طراحی و پیاده‌سازی می‌شود.') +
    '</div>';
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

function dashSectionHtml(r, isPlayer, tab) {
  var h = '', ks, i;
  if (tab === 'general') {
    h += '<h3>🌐 مشخصات کشور</h3><div class="dashGrid">';
    h += dashMetric('نام کشور',r.name) + dashMetric('نام انگلیسی',r.en || 'ثبت نشده');
    h += dashMetric('قاره / منطقه',r.region) + dashMetric('کد کشور',r.iso3 || 'ثبت نشده');
    h += dashMetric('رئیس کشور / دولت',r.leader) + dashMetric('رتبه جهانی',r.rank ? '#'+r.rank : '—');
    h += '</div>';
    var cp = r.country_profile || null;
    if (cp) {
      /* پرتره‌های تأییدشده از Wikimedia Commons؛ برای بقیه کشورها فایل محلی در صورت وجود استفاده می‌شود. */
      var leaderCommonsFiles = {
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
      var leaderPortrait = r.iso3 && leaderCommonsFiles[r.iso3]
        ? (leaderCommonsFiles[r.iso3].indexOf('https://') === 0
          ? leaderCommonsFiles[r.iso3]
          : 'https://commons.wikimedia.org/wiki/Special:FilePath/' + encodeURIComponent(leaderCommonsFiles[r.iso3]))
        : (r.iso3 ? 'assets/leaders/' + dashEsc(r.iso3) + '.jpg' : '');
      h += '<div class="dashCard countryIdentity"><div class="leaderPortraitWrap"><img class="leaderPortrait" src="'+leaderPortrait+'" alt="تصویر رهبر '+dashEsc(r.name)+'" onerror="this.style.display=\'none\';this.nextSibling.style.display=\'flex\';"><div class="leaderPortraitFallback" style="display:none">👤<small>تصویر ثبت نشده</small></div></div><div><b>'+dashEsc(r.leader || 'رهبر ثبت نشده')+'</b><div class="muted small">رهبر کشور / دولت</div><div class="muted small">'+dashEsc(r.name)+' · '+dashEsc(r.iso3 || '')+'</div></div></div>';
      h += '<h3>اطلاعات پایه کشور</h3><div class="dashGrid">';
      h += dashMetric('پایتخت',cp.capital || 'ثبت نشده');
      h += dashMetric('مساحت کل',cp.area_km2 == null ? 'ثبت نشده' : Number(cp.area_km2).toLocaleString('en-US')+' کیلومتر مربع');
      h += dashMetric('زبان‌های ثبت‌شده',(cp.languages || []).map(function(x){return x.name;}).join('، ') || 'ثبت نشده');
      h += dashMetric('واحد پول',(cp.currencies || []).map(function(x){return x.name+' ('+x.code+')';}).join('، ') || 'ثبت نشده');
      h += '</div><div class="dashNote">زبان‌ها و واحدهای پول از داده مرجع کشورها خوانده می‌شوند؛ در کشورهایی با چند زبان، همه موارد ثبت‌شده نمایش داده می‌شوند.</div>';
    } else h += dashMissing('اطلاعات پایه کشور','پرونده اطلاعات مرجع برای این کشور در دسترس نیست.');
  } else if (tab === 'politics') {
    var pp = r.political_profile || null, cur, keys2, item, fields, j, k, val;
    h += '<h3>🏛 ساختار سیاسی</h3>';
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
    h += '<h3>🛡 وضعیت نظامی</h3><div class="dashGrid">';
    h += dashMetric('قدرت نظامی',r.mil) + dashMetric('فناوری',r.tech);
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
    h += '<h3>📜 پیمان‌ها و اتحادها</h3>';
    h += '<div class="dashCard">'+(r.tags && r.tags.length ? r.tags.map(dashEsc).join(' · ') : 'پیمان اختصاصی ثبت‌شده‌ای در داده فعلی این پنل نیست.')+'</div>';
    h += dashMissing('فهرست کامل توافق‌ها','پیمان‌های نظامی و اقتصادی، توافق‌های تجاری، عدم تجاوز و عضویت سازمانی باید به ساختار مستقل و قابل مدیریت تبدیل شوند.');
  } else if (tab === 'sanctions') {
    h += '<h3>⛔ تحریم‌ها</h3>';
    h += dashMissing('وضعیت تحریم‌ها','کشورهای تحریم‌کننده، نوع و محدودیت تحریم، اثر اقتصادی و روند مذاکره برای رفع تحریم هنوز به شکل پنل تفصیلی پیاده‌سازی نشده‌اند.');
    if (ST && r.name === ST.player) h += '<div class="dashCard small">شاخص فعلی تحریم شورای امنیت در وضعیت جهان: '+dashEsc(ST.un_censures)+'</div>';
  } else if (tab === 'diplomacy') {
    h += '<h3>🕊 وضعیت دیپلماتیک</h3>';
    if (r.war_with && r.war_with.length) { h += '<div class="dashCard">در جنگ با: '+r.war_with.map(dashEsc).join('، ')+'</div>'; }
    h += dashMissing('مذاکرات و توافق‌ها','مذاکرات فعال، توافق‌های درحال بررسی، پیشنهادهای ارسالی/دریافتی، بحران‌ها و نشست‌های بین‌المللی نیازمند پنل مستقل هستند.');
  } else if (tab === 'news') {
    h += '<h3>📰 اخبار و رویدادها</h3>';
    if (r.press && r.press.length) for(i=0;i<r.press.length;i++) h += '<div class="press">'+dashEsc(r.press[i])+'</div>';
    else h += '<div class="dashNote">در حال حاضر خبر داخلی ثبت‌شده‌ای برای این کشور در داده موجود نیست.</div>';
    h += '<div class="dashNote">خبرها فعلاً عمدتاً از متن‌های ازپیش‌تعیین‌شده موتور می‌آیند. رسانه‌های پویا با کمک AI آنلاین در فاز F اضافه می‌شوند؛ رویداد واقعی بازی منبع حقیقت خبر خواهد بود.</div>';
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
    '<div class="muted small">' + dashEsc(r.en || '') + ' · ' + dashEsc(r.iso3 || '') + '</div></div>' +
    countryMiniBadgeHtml(r.iso3, r.name) + '</div>';
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
  var tb = el('panelToggle');
  if (tb) tb.onclick = togglePanel;   /* فلش باز/بسته پنل */
  var eb = el('eventPanelToggle');
  if (eb) eb.onclick = toggleEventPanel;
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
