/* فاز A — کره سه‌بعدی ژئوپولیتیک (three.js r126 + globe.gl 2.21.0 — فقط WebGL 1)
   محدود سخت‌افزار: antialias خاموش، pixelRatio ≤ 1.5، بافت پیش‌فرض سبک تیره */
'use strict';

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
      if (f._fa == null) { flash('این سرزمین در بازی حضور ندارد.'); return; }
      selectCountry(f._fa);
    })
    .labelsData([])
    .labelLat(function (d) { return d.lat; })
    .labelLng(function (d) { return d.lon; })
    .labelText(function (d) { return d.fa; })
    .labelSize(0.45)
    .labelDotRadius(function (d) { return d.point ? 0.28 : 0; })
    .labelColor(function (d) { return (d.fa === SELECTED) ? '#ffd166' : '#e8eef8'; })
    .labelAltitude(0.012)
    .onLabelClick(function (d) { selectCountry(d.fa); });

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
  globe.polygonsData(FEATS.slice());   // ساخت مجدد برای اعمال رنگ‌بندی تازه
  globe.labelsData(labelsList());
}

function labelsList() {
  var out = [];
  if (!MAP) return out;
  for (var fa in MAP) {
    var m = MAP[fa];
    out.push({ fa: fa, lat: m.lat, lon: m.lon, point: !m.ne });
  }
  return out;
}

/* ---------- شبکه ---------- */
function getJSON(url, cb, errCb) {
  var x = new XMLHttpRequest();
  x.open('GET', url, true);
  x.onreadystatechange = function () {
    if (x.readyState !== 4) return;
    try {
      if (x.status >= 200 && x.status < 300) cb(JSON.parse(x.responseText));
      else if (errCb) errCb(x.status);
    } catch (e) { if (errCb) errCb(e); }
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
      else if (errCb) errCb(x.status);
    } catch (e) { if (errCb) errCb(e); }
  };
  x.send(JSON.stringify(obj));
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
  }, function () { flash('خطا در دریافت وضعیت بازی.'); });
}

/* ---------- پنل‌ها ---------- */
function el(id) { return document.getElementById(id); }

function flash(text) {
  var d = el('engineMsg');
  d.style.display = 'block';
  d.textContent = text;
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
  if (ST) { banner.style.display = 'none'; return; }
  banner.style.display = 'block';
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
}

function selectCountry(fa, silent) {
  SELECTED = fa;
  refreshPolygons();
  getJSON('api/country?name=' + encodeURIComponent(fa), function (r) {
    if (!r.ok) { flash(r.error || 'خطا'); return; }
    renderCountryPanel(r);
  }, function () { flash('خطا در دریافت اطلاعات کشور.'); });
  if (!silent) { /* آماده برای افکت‌های آینده */ }
}

function renderCountryPanel(r) {
  var box = el('countryInfo');
  el('idleInfo').style.display = 'none';
  box.style.display = 'block';
  var h = '';
  h += '<h2>' + r.name + '</h2>';
  h += '<div class="muted small">' + (r.en || '') + ' · ' + (r.iso3 || '') + '</div>';
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
  if (r.rel != null) {
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
  box.innerHTML = h;
}

/* ---------- اقدامات ---------- */
function endDay() {
  if (!ST) { flash('اول بازی را شروع کن.'); return; }
  postJSON('api/act', { argv: ['end'] }, function (r) {
    if (r.out) flash(r.out);
    loadState();
  }, function () { flash('خطا در پایان دور.'); });
}

function startGame() {
  var sel = el('startCountry');
  var c = sel.value;
  el('startErr').textContent = '';
  postJSON('api/init', { country: c }, function (r) {
    if (!r.ok) { el('startErr').textContent = r.error || 'خطا'; return; }
    flash(r.out || 'بازی آغاز شد!');
    SELECTED = null;
    el('countryInfo').style.display = 'none';
    el('idleInfo').style.display = 'block';
    loadState();
    if (ST && MAP[c] && MAP[c].lat != null) {
      globe.pointOfView({ lat: MAP[c].lat, lng: MAP[c].lon, altitude: 1.9 }, 900);
    }
  }, function () { el('startErr').textContent = 'خطای شبکه'; });
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
  el('btnStart').onclick = startGame;
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
