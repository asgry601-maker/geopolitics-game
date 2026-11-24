/* تست تشخیصی مستقل WebGL1 — ۵ مرحله ایزوله؛ گزارش روی صفحه */
'use strict';

var ERRS = [];
function showErrs() {
  var box = document.getElementById('errlog');
  box.textContent = ERRS.length ? ERRS.join('\n') : '(هنوز خطایی ثبت نشده)';
}
window.onerror = function (m, src, line, col) {
  ERRS.push('خطا: ' + m + ' — ' + (src || '').split('/').pop() + ' سطر ' + line + ':' + col);
  showErrs();
  return false;
};

function step(n, title, cb) {
  var host = document.getElementById('steps');
  var d = document.createElement('div');
  d.className = 'step';
  d.innerHTML = '<div class="t">مرحله ' + n + ' — ' + title + '</div><div class="body inf">در حال اجرا…</div>';
  host.appendChild(d);
  var body = d.querySelector('.body');
  var t0 = (window.performance && performance.now()) ? performance.now() : Date.now();
  var out = [];
  function log(s, cls) { out.push('<div class="' + (cls || 'inf') + '">' + s + '</div>'); }
  try {
    var ok = cb(log);
    var ms = Math.round(((window.performance && performance.now) ? performance.now() : Date.now()) - t0);
    d.className = 'step ' + (ok ? 'pass' : 'fail');
    body.innerHTML = out.join('') + '<div class="' + (ok ? 'ok' : 'bad') + '"><b>' +
      (ok ? '✔ نتیجه: OK' : '✘ نتیجه: مشکل در این مرحله') + '</b> <span class="mut">(' + ms + 'ms)</span></div>';
    return ok;
  } catch (e) {
    var ms2 = Math.round(((window.performance && performance.now) ? performance.now() : Date.now()) - t0);
    d.className = 'step fail';
    body.innerHTML = out.join('') + '<div class="bad"><b>✘ خطا: ' + (e && e.message ? e.message : e) +
      '</b> <span class="mut">(' + ms2 + 'ms)</span></div>';
    ERRS.push('مرحله ' + n + ': ' + ((e && e.message) ? e.message : e));
    showErrs();
    return false;
  }
}

/* --- ابزار پیکسل‌خوانی --- */
function readCenter(gl, cw, ch) {
  var px = new Uint8Array(4);
  var fb = gl.canvas.width;
  gl.flush();
  gl.readPixels(Math.floor(gl.drawingBufferWidth / 2), Math.floor(gl.drawingBufferHeight / 2), 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
  return px;
}

var S = {};

/* مرحله ۱ — WebGL 1 خام (بدون کتابخانه): مشکل از مرورگر/کارت گرافیک است؟ */
S.a = step('۱', 'WebGL 1 خام (بدون کتابخانه) + رسم مثلث', function (log) {
  var c = document.createElement('canvas');
  c.width = 320; c.height = 200;
  var gl = c.getContext('webgl', { antialias: false, preserveDrawingBuffer: true }) ||
           c.getContext('experimental-webgl', { antialias: false, preserveDrawingBuffer: true });
  if (!gl) { log('✘ WebGL context ساخته نشد.', 'bad'); return false; }
  log('◉ context: ' + gl.getParameter(gl.VERSION));
  log('◉ کارت گرافیک: ' + gl.getParameter(gl.RENDERER));
  log('◉ درایور: ' + gl.getParameter(gl.SHADING_LANGUAGE_VERSION));
  log('◉ حداکثر اندازه بافت: ' + gl.getParameter(gl.MAX_TEXTURE_SIZE) + ' | ' +
      gl.getSupportedExtensions().length + ' extension');
  document.getElementById('steps').appendChild(c);
  var vs = gl.createShader(gl.VERTEX_SHADER);
  gl.shaderSource(vs, 'attribute vec2 p; void main(){ gl_Position = vec4(p, 0.0, 1.0); }');
  gl.compileShader(vs);
  if (!gl.getShaderParameter(vs, gl.COMPILE_STATUS)) { log('شیدر: ' + gl.getShaderInfoLog(vs), 'bad'); return false; }
  var fs = gl.createShader(gl.FRAGMENT_SHADER);
  gl.shaderSource(fs, 'void main(){ gl_FragColor = vec4(1.0, 0.6, 0.2, 1.0); }');
  gl.compileShader(fs);
  var pr = gl.createProgram();
  gl.attachShader(pr, vs); gl.attachShader(pr, fs); gl.linkProgram(pr);
  if (!gl.getProgramParameter(pr, gl.LINK_STATUS)) { log('لینک: ' + gl.getProgramInfoLog(pr), 'bad'); return false; }
  gl.useProgram(pr);
  var buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([0, 0.7, -0.7, -0.7, 0.7, -0.7]), gl.STATIC_DRAW);
  var loc = gl.getAttribLocation(pr, 'p');
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  gl.viewport(0, 0, c.width, c.height);
  gl.clearColor(0.04, 0.07, 0.12, 1);
  gl.clear(gl.COLOR_BUFFER_BIT);
  gl.drawArrays(gl.TRIANGLES, 0, 3);
  var px = readCenter(gl);
  var hit = px[0] > 100;
  log((hit ? '✔ ' : '✘ ') + 'پس‌زمینه خوانده شد: ' + px[0] + ',' + px[1] + ',' + px[2], hit ? 'ok' : 'bad');
  return hit;
});

/* مرحله ۲ — three.js r126 کتابخانه‌ای */
S.b = step('۲', 'three.js r126 (WebGLRenderer + مکعب)', function (log) {
  if (typeof THREE === 'undefined') { log('✘ THREE بارگذاری نشد — فایل lib/three.min.js سالم کنار صفحه نیست.', 'bad'); return false; }
  log('◉ THREE نسخه ' + THREE.REVISION + ' موجود است.', 'ok');
  var c = document.createElement('canvas');
  c.width = 320; c.height = 200;
  document.getElementById('steps').appendChild(c);
  var r = new THREE.WebGLRenderer({ canvas: c, antialias: false, preserveDrawingBuffer: true });
  var sc = new THREE.Scene();
  var cam = new THREE.PerspectiveCamera(50, 1.6, 0.1, 100);
  cam.position.z = 3;
  var m = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshBasicMaterial({ color: 0xff9e2c }));
  sc.add(m);
  r.render(sc, cam);
  var gl = c.getContext('webgl');
  var px = readCenter(gl);
  var hit = (px[0] > 100 || px[1] > 100);
  log((hit ? '✔ ' : '✘ ') + 'پیکسل مرکز: ' + px[0] + ',' + px[1] + ',' + px[2], hit ? 'ok' : 'bad');
  return hit;
});

/* مرحله ۳ — globe.gl کره خالی (بدون داده) */
S.c = step('۳', 'globe.gl 2.21 — ساخت کره خالی', function (log) {
  if (typeof Globe === 'undefined') { log('✘ Globe بارگذاری نشد — فایل lib/globe.gl.min.js کنار صفحه نیست یا خراب است.', 'bad'); return false; }
  var host = document.createElement('div');
  host.style.cssText = 'width:320px;height:200px;';
  document.getElementById('steps').appendChild(host);
  var g = Globe({ animateIn: false, rendererConfig: { antialias: false, failIfMajorPerformanceCaveat: false } })(host);
  g.backgroundColor('rgba(3,8,20,0.85)').showAtmosphere(false);
  g.width(320); g.height(200);
  g.pointOfView({ lat: 0, lng: 0, altitude: 2.5 }, 0);
  log('✔ کره خالی بدون خطا ساخته شد (متدها: width/height/pointOfView OK).', 'ok');
  return true;
});

/* مرحله ۴ — globe.gl + یک چندضلعی و یک برچسب (بخش اصلی بازی) */
S.d = step('۴', 'globe.gl — چندضلعی + برچسب (شبیه کد بازی)', function (log) {
  var host = document.createElement('div');
  host.style.cssText = 'width:320px;height:200px;';
  document.getElementById('steps').appendChild(host);
  var g = Globe({ animateIn: false, rendererConfig: { antialias: false, failIfMajorPerformanceCaveat: false } })(host);
  g.backgroundColor('rgba(3,8,20,0.85)').showAtmosphere(false);
  g.width(320); g.height(200);
  var feat = {
    type: 'Feature', properties: {},
    geometry: { type: 'Polygon', coordinates: [[[46, 32], [52, 32], [52, 38], [46, 38], [46, 32]]] }
  };
  g.polygonsData([feat])
    .polygonCapColor(function () { return '#c98a4b'; })
    .polygonSideColor(function () { return 'rgba(20,28,45,0.85)'; })
    .polygonStrokeColor(function () { return '#0a0f1a'; })
    .polygonAltitude(0.012)
    .onPolygonClick(function () { });
  g.labelsData([{ fa: 'ایران', lat: 32.5, lon: 51, point: false }])
    .labelLat(function (d) { return d.lat; })
    .labelLng(function (d) { return d.lon; })
    .labelText(function (d) { return d.fa; })
    .labelSize(0.6)
    .labelDotRadius(function (d) { return d.point ? 0.3 : 0; })
    .labelColor(function () { return '#ffffff'; })
    .labelAltitude(0.012)
    .onLabelClick(function () { });
  log('✔ polygonsData + labelsData بدون خطا پذیرفته شد.', 'ok');
  return true;
});

/* مرحله ۵ — بارگذاری بافت (data URI، مستقل از سرور) */
S.e = step('۵', 'بارگذاری بافت (THREE.TextureLoader + data-URI)', function (log) {
  if (typeof THREE === 'undefined') return false;
  var done = false;
  var dataURI = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAYAAABytg0kAAAAFElEQVR4nGNkYPj/n4GBgYmRjY0NAAK1AQNfwcO1AAAAAElFTkSuQmCC';
  var loader = new THREE.TextureLoader();
  loader.load(dataURI,
    function (t) { done = true; log('✔ بافت منتقل شد (رفرنس ' + (t.image ? 'دارد' : 'ندارد') + ').', 'ok'); var d = document.querySelector('#steps .step:last-child .body'); if (d) d.innerHTML += '<div class="ok">✔ نتیجه: OK (async)</div>'; },
    undefined,
    function () { log('✘ بافت لود نشد.', 'bad'); });
  return true;
});

/* جمع‌بندی */
window.addEventListener('load', function () {
  setTimeout(function () {
    var allOk = S.a && S.b && S.c && S.d;
    var verdict = document.createElement('div');
    verdict.className = 'step ' + (allOk ? 'pass' : 'fail');
    var txt = allOk
      ? '<b class="ok">✔ همه مراحل کلیدی OK</b><br><span class="inf">پس مشکل از مرورگر/کارت گرافیک نیست؛ باید خطای داخل کد بازی (world.js) را از گزارش «کپی گزارش» بفهمیم. مرورگر اصلی لعنتی را F12 بزن → تب Console → متن خطای قرمز را بفرست.</span>'
      : '<b class="bad">✘ اولین مرحله مشکل‌دار را برای من بفرست.</b><br><span class="inf">با دکمه «کپی گزارش» کل نتیجه را بردار.</span>';
    verdict.innerHTML = '<div class="t">🧭 جمع‌بندی</div>' + txt;
    document.getElementById('steps').appendChild(verdict);
  }, 800);
});

document.getElementById('copyBtn').onclick = function () {
  var lines = ['گزارش تست WebGL — فاز A'];
  var steps = document.querySelectorAll('#steps .step');
  for (var i = 0; i < steps.length; i++) {
    lines.push('---\n' + steps[i].textContent.replace(/\s+/g, ' ').trim());
  }
  lines.push('---\nخطاها:\n' + (ERRS.join('\n') || '(خطایی ثبت نشد)'));
  var report = lines.join('\n');
  try {
    var ta = document.createElement('textarea');
    ta.value = report; document.body.appendChild(ta); ta.select();
    document.execCommand('copy'); document.body.removeChild(ta);
    document.getElementById('copyDone').textContent = 'کپی شد ✔';
  } catch (e) {
    document.getElementById('copyDone').textContent = 'کپی دستی لازم';
    window.prompt('متن گزارش:', report);
  }
};
