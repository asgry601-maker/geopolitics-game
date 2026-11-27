(function () {
  'use strict';

  /* افزونه سبک شاخص‌های سالانه؛ داده از پرونده محلی API می‌آید و در مرورگر شبکه نمی‌خواهد. */
  var baseDashSectionHtml = window.dashSectionHtml;
  if (typeof baseDashSectionHtml !== 'function') return;

  function indicatorMetric(label, entry) {
    if (!entry || entry.value === null || entry.value === undefined || entry.year === null || entry.year === undefined) {
      return dashMetric(label, 'ثبت نشده');
    }
    var value = Number(entry.value);
    if (!isFinite(value)) return dashMetric(label, 'ثبت نشده');
    return dashMetric(label, value.toFixed(1) + '٪ · ' + String(entry.year));
  }

  window.dashSectionHtml = function (r, isPlayer, tab) {
    var html = baseDashSectionHtml.apply(this, arguments);
    var profile = r && r.country_profile;
    var data = profile && profile.indicators;
    if (!data) return html;

    if (tab === 'society') {
      html += '<h3>👷 بازار کار و رشد جمعیت</h3><div class="dashGrid">';
      html += indicatorMetric('رشد سالانه جمعیت', data.population_growth_percent);
      html += indicatorMetric('بیکاری (برآورد ILO)', data.unemployment_percent);
      html += '</div>';
      html += '<div class="dashNote">نرخ بیکاری بر پایه برآورد مدل‌سازی‌شده ILO در مجموعه داده بانک جهانی است. سال هر شاخص جداگانه کنار مقدار آن آمده است.</div>';
    } else if (tab === 'economy') {
      html += '<h3>🌍 شاخص‌های کلان اقتصادی و تجارت</h3><div class="dashGrid">';
      html += indicatorMetric('تورم سالانه مصرف‌کننده', data.inflation_percent);
      html += indicatorMetric('رشد واقعی GDP', data.gdp_growth_percent);
      html += indicatorMetric('صادرات کالا و خدمات (% GDP)', data.exports_gdp_percent);
      html += indicatorMetric('واردات کالا و خدمات (% GDP)', data.imports_gdp_percent);
      html += '</div>';
      html += '<div class="dashNote">صادرات و واردات به‌صورت درصدی از GDP نمایش داده می‌شوند، نه ارزش دلاری. سال داده‌ها ممکن است بین شاخص‌ها و کشورها متفاوت باشد؛ این ارقام تاریخی و مرجع‌اند و با خزانه یا درآمد شبیه‌سازی یکی نیستند.</div>';
    }
    return html;
  };
}());
