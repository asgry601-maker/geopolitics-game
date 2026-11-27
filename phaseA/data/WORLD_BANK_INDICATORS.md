# شاخص‌های اقتصادی و جمعیتی بانک جهانی

این بخش شش شاخص سالانه را به پرونده محلی ۱۷۴ کشور اضافه می‌کند:

| کلید | شاخص | کد بانک جهانی |
|---|---|---|
| inflation_percent | تورم قیمت مصرف‌کننده، درصد سالانه | FP.CPI.TOTL.ZG |
| unemployment_percent | بیکاری، درصد نیروی کار (برآورد مدل‌سازی‌شده ILO) | SL.UEM.TOTL.ZS |
| gdp_growth_percent | رشد سالانه GDP واقعی، درصد | NY.GDP.MKTP.KD.ZG |
| population_growth_percent | رشد سالانه جمعیت، درصد | SP.POP.GROW |
| exports_gdp_percent | صادرات کالا و خدمات، درصد GDP | NE.EXP.GNFS.ZS |
| imports_gdp_percent | واردات کالا و خدمات، درصد GDP | NE.IMP.GNFS.ZS |

## به‌روزرسانی داده‌ها

در ریشه مخزن، با Python 3.8 یا جدیدتر اجرا کن:

```bash
python phaseA/tools/update_world_bank_indicators.py
```

این ابزار فقط از کتابخانه استاندارد پایتون استفاده می‌کند. برای اجرای همین دستور اتصال اینترنت لازم است؛ پس از دریافت داده‌ها، بازی در اجرای عادی کاملاً از JSON محلی استفاده می‌کند و به اینترنت وابسته نیست. پیش از جایگزینی فایل، نسخه پشتیبان `country_profiles.json.bak` ساخته می‌شود.

برای هر شاخص، جدیدترین مشاهده غیرخالی بانک جهانی ذخیره می‌شود و سال آن جداگانه ثبت می‌گردد. بنابراین سال تورم، رشد GDP و تجارت الزاماً یکسان نیست. داده‌های فاقد مقدار با `null` می‌مانند و هیچ مقدار حدسی تولید نمی‌شود.

## منبع و مجوز

منبع: World Bank, World Development Indicators, Indicators API v2:
https://api.worldbank.org/v2/

مستندات API:
https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api

داده‌های بانک جهانی عموماً تحت Creative Commons Attribution 4.0 International (CC BY 4.0) منتشر می‌شوند، مگر آن‌که فراداده یک مجموعه استثنا را مشخص کند. انتساب منبع و اعلام تغییرات داده ضروری است:
https://datacatalog.worldbank.org/public-licenses

این داده‌ها برآوردهای مرجع تاریخی هستند و نباید به‌عنوان خروجی زنده اقتصاد یا خزانه شبیه‌سازی تعبیر شوند.
