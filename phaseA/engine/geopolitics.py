#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""بازی استراتژیک ژئوپلیتیک متنی — ثبت وضعیت در game_state.json"""
import json, os, random, sys, datetime


STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game_state.json")

START_YEAR = 2026
FINAL_YEAR = 2040
START_DATE = datetime.date(2026, 11, 5)
INCOME_K = 0.15      # درآمد روزانه = اقتصاد × این ضریب


# آمار تقریبی بر پایه داده‌های ۲۰۲۴ — اقتصاد (PPP-نسبی)، ارتش، فناوری، ثبات، خزانه آزاد
REGIONS = [
    "خاورمیانه و شمال آفریقا", "اروپا", "شرق آسیا", "جنوب و جنوب‌شرق آسیا",
    "آفریقای جنوب صحرا", "آمریکای شمالی", "آمریکای لاتین و کارائیب",
    "اقیانوسیه", "آسیای مرکزی و قفقاز",
]

TIER = {
    1: dict(mil=88, eco=90, tech=88, stab=70, money=450, aggr=0.45),
    2: dict(mil=62, eco=62, tech=68, stab=62, money=180, aggr=0.35),
    3: dict(mil=38, eco=42, tech=48, stab=55, money=90,  aggr=0.30),
    4: dict(mil=20, eco=22, tech=20, stab=46, money=45,  aggr=0.22),
    5: dict(mil=11, eco=13, tech=12, stab=40, money=25,  aggr=0.12),
}

# نام:منطقه:سطح‌اقتدار — بیش از ۱۷۰ کشور عضو سازمان ملل
_TABLE = (
    "آمریکا:6:1;کانادا:6:2;مکزیک:7:3;"
    "ایران:1:2;عراق:1:4;سوریه:1:4;لبنان:1:4;اردن:1:4;اسرائیل:1:3;فلسطین:1:5;"
    "عربستان:1:2;امارات:1:3;قطر:1:4;کویت:1:4;بحرین:1:5;عمان:1:4;یمن:1:5;ترکیه:1:2;"
    "مصر:1:3;لیبی:1:4;تونس:1:4;الجزایر:1:3;مراکش:1:4;"
    "روسیه:2:1;آلمان:2:2;فرانسه:2:2;بریتانیا:2:2;ایتالیا:2:2;اسپانیا:2:3;پرتغال:2:3;"
    "هلند:2:3;بلژیک:2:3;سوئیس:2:3;اتریش:2:3;سوئد:2:3;نروژ:2:3;دانمارک:2:3;فنلاند:2:3;"
    "ایسلند:2:4;ایرلند:2:3;لهستان:2:3;چک:2:3;اسلواکی:2:4;مجارستان:2:4;رومانی:2:4;"
    "بلغارستان:2:4;یونان:2:3;صربستان:2:4;کرواسی:2:4;بوسنی:2:5;آلبانی:2:5;"
    "مقدونیه شمالی:2:5;اسلوونی:2:4;مونته‌نگرو:2:5;اوکراین:2:3;بلاروس:2:4;مولداوی:2:5;"
    "لتونی:2:4;لیتوانی:2:4;استونی:2:4;لوکزامبورگ:2:5;قبرس:2:4;مالت:2:5;"
    "چین:3:1;ژاپن:3:2;کره جنوبی:3:2;کره شمالی:3:3;تایوان:3:3;مغولستان:3:4;"
    "هند:4:2;پاکستان:4:3;بنگلادش:4:4;سری‌لانکا:4:4;نپال:4:5;بوتان:4:5;مالدیو:4:5;"
    "افغانستان:4:5;اندونزی:4:3;مالزی:4:3;سنگاپور:4:3;تایلند:4:3;ویتنام:4:3;"
    "فیلیپین:4:3;میانمار:4:4;کامبوج:4:5;لائوس:4:5;برونئی:4:5;تیمور شرقی:4:5;"
    "نیجریه:5:3;آفریقای جنوبی:5:3;اتیوپی:5:4;کنیا:5:4;غنا:5:4;سنگال:5:4;"
    "ساحل عاج:5:4;کامرون:5:4;اوگاندا:5:4;تانزانیا:5:4;رواندا:5:5;زیمبابوه:5:4;"
    "زامبیا:5:5;موزامبیک:5:5;آنگولا:5:4;نامیبیا:5:5;بوتسوانا:5:4;سودان:5:4;"
    "سودان جنوبی:5:5;چاد:5:5;نیجر:5:5;مالی:5:5;موریتانی:5:5;بورکینافاسو:5:5;"
    "گینه:5:5;سیرالئون:5:5;لیبریا:5:5;توگو:5:5;بنین:5:5;گابن:5:5;کنگو:5:5;"
    "کنگو دموکراتیک:5:5;آفریقای مرکزی:5:5;اریتره:5:5;جیبوتی:5:5;سومالی:5:5;"
    "ماداگاسکار:5:5;موریس:5:5;لسوتو:5:5;اسواتینی:5:5;گامبیا:5:5;گینه بیسائو:5:5;"
    "گینه استوایی:5:5;کیپ‌ورد:5:5;"
    "برزیل:7:2;آرژانتین:7:3;شیلی:7:3;کلمبیا:7:3;پرو:7:4;ونزوئلا:7:4;اکوادور:7:4;"
    "بولیوی:7:5;پاراگوئه:7:5;اوروگوئه:7:4;گویان:7:5;سورینام:7:5;کوبا:7:4;"
    "هائیتی:7:5;دومینیکن:7:4;جامائیکا:7:5;ترینیداد و توباگو:7:5;کاستاریکا:7:4;"
    "پاناما:7:4;گواتمالا:7:4;هندوراس:7:5;السالوادور:7:5;نیکاراگوئه:7:5;بلیز:7:5;"
    "باهاماس:7:5;باربادوس:7:5;"
    "استرالیا:8:2;نیوزیلند:8:3;پاپوآ گینه نو:8:4;فیجی:8:5;ساموآ:8:5;"
    "تونگا:8:5;وانواتو:8:5;جزایر سلیمان:8:5;"
    "قزاقستان:9:3;ازبکستان:9:4;ترکمنستان:9:4;تاجیکستان:9:5;قرقیزستان:9:5;"
    "آذربایجان:9:4;ارمنستان:9:4;گرجستان:9:4;"
)

# آمار اختصاصی قابل‌اعتماد برای قدرت‌های شاخص (بقیه از سطح قلمرو گرفته می‌شوند)
SPECIAL = {
    "آمریکا":    dict(mil=95, eco=95, tech=95, stab=70, money=500, aggr=0.45, trait="اَبَرقدرت فعلی، ۵ کلاهک (نماد منور ۵۰۰۰+)"),
    "چین":       dict(mil=88, eco=88, tech=82, stab=80, money=420, aggr=0.35, trait="اَبَرقدرت نوظهور، نخستین اقتصاد دوم جهان"),
    "روسیه":     dict(mil=82, eco=55, tech=72, stab=62, money=180, aggr=0.60, trait="بازیگر خطرپذیر، انبار سلاح هسته‌ای"),
    "هند":       dict(mil=68, eco=62, tech=62, stab=58, money=200, aggr=0.30, trait="قدرت رو به رشد با جمعیت عظیم"),
    "آلمان":     dict(mil=52, eco=73, tech=85, stab=78, money=280, aggr=0.15, trait="قلب اقتصادی اروپا، صلح‌طلب"),
    "ژاپن":      dict(mil=55, eco=72, tech=88, stab=80, money=260, aggr=0.15, trait="فناوری پیشرفته، دفاعی"),
    "فرانسه":    dict(mil=64, eco=64, tech=80, stab=66, money=190, aggr=0.30, trait="قدرت هسته‌ای اروپایی، مداخله‌گر سابق"),
    "بریتانیا":  dict(mil=63, eco=63, tech=80, stab=68, money=180, aggr=0.40, trait="پیمان ویژه با آمریکا"),
    "ایران":     dict(mil=50, eco=45, tech=48, stab=45, money=70,  aggr=0.50, trait="تحت تحریم، منطقه‌ای و پرتحرک (حالت سخت)"),
    "اسرائیل":   dict(mil=62, eco=60, tech=85, stab=55, money=160, aggr=0.50, trait="برتری هوایی و اطلاعاتی منطقه"),
    "پاکستان":   dict(mil=48, eco=30, tech=42, stab=38, money=60,  aggr=0.55, trait="رقیب دیرینه هند، هسته‌ای"),
    "کره شمالی": dict(mil=45, eco=12, tech=30, stab=75, money=30,  aggr=0.75, trait="منزوی، آزمون‌های موشکی مداوم"),
    "عربستان":   dict(mil=58, eco=68, tech=55, stab=60, money=320, aggr=0.40, trait="قلب جهانی نفت، رقیب منطقه‌ای ایران"),
    "ترکیه":     dict(mil=55, eco=48, tech=55, stab=50, money=120, aggr=0.55, trait="پل دو قاره، توسعه‌طلب منطقه‌ای"),
    "اوکراین":   dict(mil=52, eco=25, tech=45, stab=35, money=40,  aggr=0.35, trait="درگیر جنگ با روسیه"),
    "سنگاپور":   dict(mil=25, eco=65, tech=78, stab=82, money=140, aggr=0.08, trait="شهر-دولت مالی پُرجذابیت"),
    "سوئیس":     dict(mil=20, eco=72, tech=75, stab=85, money=200, aggr=0.05, trait="بی‌طرف، محافظ سرمایه‌های جهان"),
    "امارات":    dict(mil=30, eco=62, tech=60, stab=72, money=220, aggr=0.30, trait="قطب تجاری و لجستیکی خلیج فارس"),
    "قطر":       dict(mil=18, eco=60, tech=58, stab=70, money=180, aggr=0.20, trait="گاز جهانی، دیپلماسی فعال"),
    "برزیل":     dict(mil=48, eco=58, tech=52, stab=55, money=150, aggr=0.25, trait="غول لاتین، بزرگ‌ترین اقتصاد منطقه"),
    "استرالیا":  dict(mil=45, eco=60, tech=72, stab=80, money=220, aggr=0.20, trait="متحد ژرف آمریکا، معادن راهبردی"),
}

# درآمد کلاهک هسته‌ای اولیه کشورها
NUKES0 = {"آمریکا": 5, "روسیه": 5, "چین": 3, "فرانسه": 1, "بریتانیا": 1,
          "هند": 1, "پاکستان": 1, "کره شمالی": 1, "اسرائیل": 1}

# کینه‌های تاریخی (درجه خصومت اولیه)
ENMITY = {
    frozenset(("هند", "پاکستان")): -65,
    frozenset(("کره شمالی", "کره جنوبی")): -80,
    frozenset(("چین", "تایوان")): -55,
    frozenset(("اسرائیل", "ایران")): -85,
    frozenset(("اسرائیل", "سوریه")): -70,
    frozenset(("اسرائیل", "لبنان")): -65,
    frozenset(("اسرائیل", "فلسطین")): -90,
    frozenset(("عربستان", "ایران")): -55,
    frozenset(("عربستان", "یمن")): -45,
    frozenset(("روسیه", "اوکراین")): -90,
    frozenset(("ارمنستان", "آذربایجان")): -60,
    frozenset(("یونان", "ترکیه")): -40,
    frozenset(("الجزایر", "مراکش")): -40,
    frozenset(("آمریکا", "کره شمالی")): -75,
    frozenset(("آمریکا", "ونزوئلا")): -55,
    frozenset(("ترکیه", "سوریه")): -40,
    frozenset(("مصر", "اتیوپی")): -25,
    frozenset(("پاکستان", "افغانستان")): -35,
    frozenset(("تایلند", "کامبوج")): -20,
    frozenset(("رواندا", "کنگو دموکراتیک")): -35,
}

# دوستی‌های راهبردی اولیه
FRIEND = {
    frozenset(("چین", "پاکستان")): 65,
    frozenset(("ترکیه", "پاکستان")): 55,
    frozenset(("عربستان", "مصر")): 55,
    frozenset(("عربستان", "امارات")): 70,
    frozenset(("آمریکا", "اسرائیل")): 80,
    frozenset(("روسیه", "سوریه")): 45,
    frozenset(("روسیه", "بلاروس")): 85,
    frozenset(("ایران", "سوریه")): 60,
    frozenset(("ایران", "عراق")): 25,
    frozenset(("ایران", "لبنان")): 45,
    frozenset(("ایران", "ونزوئلا")): 30,
    frozenset(("آمریکا", "کانادا")): 75,
    frozenset(("برزیل", "آرژانتین")): 55,
    frozenset(("سوئد", "فنلاند")): 75,
    frozenset(("استرالیا", "نیوزیلند")): 80,
    frozenset(("آلمان", "اتریش")): 70,
}

# اعضای ناتو
NATO = ["آمریکا", "کانادا", "بریتانیا", "فرانسه", "آلمان", "ایتالیا", "اسپانیا",
        "پرتغال", "هلند", "بلژیک", "لوکزامبورگ", "نروژ", "دانمارک", "ایسلند",
        "فنلاند", "سوئد", "لهستان", "چک", "اسلواکی", "مجارستان", "رومانی",
        "بلغارستان", "یونان", "آلبانی", "مقدونیه شمالی", "اسلوونی", "مونته‌نگرو",
        "کرواسی", "ترکیه"]

# متفدهای غیرناتوی آمریکا
US_PACT = ["ژاپن", "کره جنوبی", "استرالیا", "نیوزیلند", "فیلیپین", "تایلند"]

def _build_countries():
    out = {}
    for i, ent in enumerate(_TABLE.split(";")):
        if not ent.strip(): continue
        name, reg, tier = ent.strip().rsplit(":", 2)
        base = dict(TIER[int(tier)])
        j = ((i * 37) % 11) - 5
        for k in ("mil", "eco", "tech"):
            base[k] = max(8, base[k] + j)
        base["stab"] = max(15, min(90, base["stab"] + (((i * 17) % 13) - 6)))
        base["money"] = max(10, base["money"] + j * 2)
        base["aggr"] = min(0.75, max(0.05, base["aggr"] + (((i * 7) % 10) - 4) * 0.03))
        base["trait"] = ""
        base["nukes"] = 0
        out[name] = dict(region=REGIONS[int(reg) - 1], **base)
    for name, over in SPECIAL.items():
        out[name].update(over)
    for name, n in NUKES0.items():
        out[name]["nukes"] = n
    return out

COUNTRIES = _build_countries()

# ---------- تجهیزات نظامی (نام‌های واقعی: سازنده، قیمت میلیارد، اثر نظامی، فناوری-برتر) ----------
EQUIPMENT = {
    "جنگنده": [
        dict(n="F-35A Lightning II", mk="آمریکا", pr=10.0, m=3.5, hi=1),
        dict(n="F-16C Fighting Falcon", mk="آمریکا", pr=3.0, m=2.0, hi=1),
        dict(n="F/A-18E Super Hornet", mk="آمریکا", pr=5.5, m=2.6, hi=1),
        dict(n="F-15E Strike Eagle", mk="آمریکا", pr=5.5, m=2.7, hi=1),
        dict(n="داسو رافال", mk="فرانسه", pr=7.5, m=3.0, hi=1),
        dict(n="یوروفایتر تایفون", mk="بریتانیا", pr=7.0, m=3.0, hi=1),
        dict(n="سو-35S", mk="روسیه", pr=5.5, m=2.8, hi=1),
        dict(n="سو-57 فلون", mk="روسیه", pr=9.0, m=3.6, hi=1),
        dict(n="میگ-29M", mk="روسیه", pr=2.8, m=1.8, hi=0),
        dict(n="چنگدو J-20", mk="چین", pr=8.5, m=3.4, hi=1),
        dict(n="JF-17 تاندر", mk="پاکستان", pr=1.6, m=1.2, hi=0),
        dict(n="JAS 39 گریپن", mk="سوئد", pr=4.5, m=2.2, hi=1),
    ],
    "تانک": [
        dict(n="M1A2 آبرامز", mk="آمریکا", pr=0.9, m=1.0, hi=1),
        dict(n="لئوپارد 2A7", mk="آلمان", pr=0.9, m=1.0, hi=1),
        dict(n="T-90M", mk="روسیه", pr=0.45, m=0.9, hi=0),
        dict(n="تایپ 99A", mk="چین", pr=0.4, m=0.9, hi=0),
        dict(n="مرکاوا 4", mk="اسرائیل", pr=0.8, m=1.0, hi=0),
        dict(n="K2 Black Panther", mk="کره جنوبی", pr=0.75, m=0.95, hi=1),
        dict(n="آرجون Mk1A", mk="هند", pr=0.55, m=0.8, hi=0),
        dict(n="آل‌خالد-I", mk="پاکستان", pr=0.3, m=0.7, hi=0),
        dict(n="زلفیقار-3", mk="ایران", pr=0.25, m=0.6, hi=0),
        dict(n="لوکلرک", mk="فرانسه", pr=0.9, m=1.0, hi=1),
    ],
    "پهپاد": [
        dict(n="MQ-9 ریپر", mk="آمریکا", pr=3.0, m=1.2, hi=1),
        dict(n="بایراکتار TB2", mk="ترکیه", pr=0.5, m=0.5, hi=0),
        dict(n="شهید-136", mk="ایران", pr=0.02, m=0.15, hi=0),
        dict(n="IAI هرمس 900", mk="اسرائیل", pr=1.0, m=0.5, hi=0),
        dict(n="TAI آنکا-S", mk="ترکیه", pr=0.8, m=0.45, hi=0),
        dict(n="CH-4 رینبو", mk="چین", pr=1.0, m=0.5, hi=0),
    ],
    "پدافند و موشک": [
        dict(n="پاتریوت PAC-3", mk="آمریکا", pr=5.0, m=2.0, hi=1),
        dict(n="S-400 تریومف", mk="روسیه", pr=4.5, m=2.0, hi=1),
        dict(n="S-500 پرومته", mk="روسیه", pr=7.0, m=2.6, hi=1),
        dict(n="گنبد آهنین", mk="اسرائیل", pr=2.5, m=1.2, hi=0),
        dict(n="باراک-8", mk="هند", pr=1.5, m=0.9, hi=0),
        dict(n="HQ-9", mk="چین", pr=3.0, m=1.4, hi=0),
        dict(n="اسکاد-D", mk="کره شمالی", pr=0.4, m=0.6, hi=0),
        dict(n="ایسکندر-M", mk="روسیه", pr=1.8, m=1.1, hi=0),
        dict(n="باور-373", mk="ایران", pr=0.3, m=0.7, hi=0),
    ],
    "نیروی دریایی": [
        dict(n="ناو هواپیمابر جرالد فورد", mk="آمریکا", pr=35.0, m=8.0, hi=1),
        dict(n="ناوشکن ارلی برک", mk="آمریکا", pr=5.0, m=1.6, hi=1),
        dict(n="ناوشکن دییرینگ", mk="بریتانیا", pr=4.5, m=1.5, hi=1),
        dict(n="زیردریایی آستیوت", mk="بریتانیا", pr=9.0, m=2.5, hi=1),
        dict(n="زیردریایی کلاس کیلو", mk="روسیه", pr=1.5, m=1.0, hi=0),
        dict(n="ناو بالگردنشین میسترال", mk="فرانسه", pr=2.8, m=0.9, hi=0),
        dict(n="ناوچه MEKO-200", mk="آلمان", pr=1.2, m=0.5, hi=0),
        dict(n="زیردریایی تایپ 093", mk="چین", pr=3.5, m=1.6, hi=1),
    ],
}
ARSENAL_ITEMS = {e["n"]: e for items in EQUIPMENT.values() for e in items}
EQUIP_CATS = list(EQUIPMENT)

# انبار ویژه چند کشور معروف (سهم واقع‌گرایانه)
ARSENALS = {
    "آمریکا": {"F-35A Lightning II": 60, "F-16C Fighting Falcon": 900, "F/A-18E Super Hornet": 500,
               "F-15E Strike Eagle": 220, "M1A2 آبرامز": 2500, "MQ-9 ریپر": 100, "پاتریوت PAC-3": 60,
               "ناو هواپیمابر جرالد فورد": 11, "ناوشکن ارلی برک": 70},
    "روسیه": {"سو-35S": 100, "سو-57 فلون": 20, "میگ-29M": 120, "T-90M": 700,
              "S-400 تریومف": 57, "S-500 پرومته": 10, "ایسکندر-M": 150, "زیردریایی کلاس کیلو": 24},
    "چین": {"چنگدو J-20": 150, "تایپ 99A": 800, "HQ-9": 300, "زیردریایی تایپ 093": 9, "CH-4 رینبو": 200},
    "هند": {"داسو رافال": 36, "آرجون Mk1A": 120, "باراک-8": 5, "T-90M": 600, "IAI هرمس 900": 10},
    "ایران": {"زلفیقار-3": 150, "شهید-136": 3000, "باور-373": 200},
    "اسرائیل": {"F-35A Lightning II": 39, "مرکاوا 4": 400, "گنبد آهنین": 15, "IAI هرمس 900": 60},
    "ترکیه": {"F-16C Fighting Falcon": 240, "بایراکتار TB2": 120, "لئوپارد 2A7": 300, "TAI آنکا-S": 40},
    "عربستان": {"F-15E Strike Eagle": 210, "M1A2 آبرامز": 370, "پاتریوت PAC-3": 30, "MQ-9 ریپر": 8},
    "کره جنوبی": {"K2 Black Panther": 600, "F-35A Lightning II": 40, "F-16C Fighting Falcon": 130},
    "آلمان": {"لئوپارد 2A7": 320, "یوروفایتر تایفون": 140, "ناوچه MEKO-200": 5},
    "بریتانیا": {"یوروفایتر تایفون": 110, "F-35A Lightning II": 34, "ناوشکن دییرینگ": 6, "زیردریایی آستیوت": 6},
    "ژاپن": {"F-35A Lightning II": 105},
    "فرانسه": {"داسو رافال": 140, "لوکلرک": 200, "ناو بالگردنشین میسترال": 3},
    "پاکستان": {"F-16C Fighting Falcon": 85, "JF-17 تاندر": 150, "آل‌خالد-I": 400},
    "اوکراین": {"بایراکتار TB2": 40, "پاتریوت PAC-3": 5},
}

def _default_arsenal(rel_map):
    """انبار اولیه برای کشورهای دیگر بر اساس سطح قدرت و روابط با سازندگان"""
    budgets = {1: 90, 2: 55, 3: 30, 4: 16, 5: 8}
    out = {}
    for name, c in COUNTRIES.items():
        if name in ARSENALS:
            out[name] = dict(ARSENALS[name])
            continue
        budget = budgets[c.get("tier", 3)]
        inventory = {}
        for cat in EQUIP_CATS:
            for e in EQUIPMENT[cat]:
                if e["hi"] and c["tech"] < e["pr"] * 8:
                    continue
                rel = rel_map.get(rel_key(name, e["mk"]), 0)
                need = 30 if e["hi"] else 0
                if name == e["mk"] or rel >= need:
                    qty = max(0, int(budget / max(e["m"], 0.2) * (0.06 if rel < 60 else 0.12)))
                    if qty:
                        inventory[e["n"]] = inventory.get(e["n"], 0) + qty
                        budget -= 1
                if budget <= 0:
                    break
            if budget <= 0:
                break
        out[name] = inventory
    return out

def arsenal_bonus(c, arsenal):
    try:
        return min(12.0, sum(ARSENAL_ITEMS[i]["m"] * n for i, n in arsenal.items()) * 0.5)
    except Exception:
        return 0.0

def find_item(query):
    query = str(query).strip().casefold()
    best = None
    for key in ARSENAL_ITEMS:
        k = key.casefold()
        if query == k or (query and (query in k or k in query)):
            return key
        pre = min(len(query), len(k), 10)
        if pre >= 3 and query[:pre] == k[:pre] and (best is None or pre > best[0]):
            best = (pre, key)
    return best[1] if best else None


DEFAULT_REL = {
    frozenset(("آمریکا", "روسیه")): -60,
    frozenset(("آمریکا", "چین")): -40,
    frozenset(("آمریکا", "فرانسه")): 65,
    frozenset(("آمریکا", "بریتانیا")): 80,
    frozenset(("آمریکا", "آلمان")): 70,
    frozenset(("آمریکا", "ژاپن")): 80,
    frozenset(("آمریکا", "هند")): 45,
    frozenset(("آمریکا", "ایران")): -75,
    frozenset(("چین", "روسیه")): 55,
    frozenset(("چین", "ایران")): 50,
    frozenset(("چین", "هند")): -35,
    frozenset(("چین", "ژاپن")): -25,
    frozenset(("چین", "بریتانیا")): -20,
    frozenset(("چین", "فرانسه")): 5,
    frozenset(("چین", "آلمان")): 10,
    frozenset(("روسیه", "ایران")): 55,
    frozenset(("روسیه", "هند")): 45,
    frozenset(("روسیه", "ژاپن")): -20,
    frozenset(("روسیه", "آلمان")): -30,
    frozenset(("روسیه", "بریتانیا")): -55,
    frozenset(("روسیه", "فرانسه")): -25,
    frozenset(("هند", "ژاپن")): 50,
    frozenset(("هند", "بریتانیا")): 60,
    frozenset(("هند", "فرانسه")): 55,
    frozenset(("هند", "آلمان")): 50,
    frozenset(("ایران", "بریتانیا")): -40,
    frozenset(("ایران", "فرانسه")): -30,
    frozenset(("ایران", "آلمان")): -10,
    frozenset(("ایران", "ژاپن")): 0,
    frozenset(("ایران", "هند")): 20,
    frozenset(("آلمان", "فرانسه")): 80,
    frozenset(("آلمان", "بریتانیا")): 65,
    frozenset(("آلمان", "ژاپن")): 50,
    frozenset(("فرانسه", "بریتانیا")): 70,
    frozenset(("فرانسه", "ژاپن")): 45,
    frozenset(("بریتانیا", "ژاپن")): 55,
}

HELP = """
راهنمای سریع — «ژئوپلیتیک: رقابت قدرت‌ها»
زمان: تقویم میلادی از ۵ نوامبر ۲۰۲۶؛ ساعت بازی با گام‌های ۵ یا ۲۴ ساعت جلو می‌رود.

فرمان‌ها (در منوی تعاملی هم همان کارها با شماره‌ها انجام می‌شود):
  init <کشور>| reset <کشور>| list| status [کشور]| rank| help

  act eco        سرمایه‌گذاری اقتصادی (4م)      act mil        بودجه نظامی (5م)
  act tech       فناوری (4م)                    act nuke       کلاهک هسته‌ای (12م؛ فناوری≥70)
  act iaea       شفافیت به آژانس انرژی اتمی (3م — فشار پرونده صفر)
  act buy <تجهیز> [تعداد]     خرید از بازار جهانی (نمونه: act buy F-16C 5)
  act sell <تجهیز> <کشور>     فروش تجهیز به کشور دوست (روابط>20)
  act spy <کشور>        جاسوسی (2م)            act covert <کشور>   بی‌ثبات‌سازی (5م)
  act sabotage <کشور>   خرابکاری (5م)          act kill <کشور>     ترور (8م)
  act proxy <کشور>      شبکه نیابتی (6م؛ تقویت 4م)
  act aide <کشور> کمک اقتصادی (3م)             act trade <کشور> تجارت (2م)
  act pact <کشور> پیمان عدم تعارض (1م)         act ally <کشور> اتحاد نظامی (3م)
  act break <کشور> فسخ پیمان                   act sanc <کشور> تحریم اقتصادی
  act un <کشور>        طرح محکومیت در مجمع عمومی سازمان ملل
  act war <کشور>       اعلان جنگ (حواست به ماده ۵ ناتو و محکومیت ملل باشد!)
  neg <\u0646\u0648\u0639> <\u06a9\u0634\u0648\u0631> [s]   \u0645\u0630\u0627\u06a9\u0631\u0647 \u0639\u0644\u0646\u06cc/\u0645\u062d\u0631\u0645\u0627\u0646\u0647 \u2014 `negos` \u0641\u0647\u0631\u0633\u062a \u0627\u0646\u0648\u0627\u0639
  decide <\u0646\u0648\u0639>        \u062a\u0635\u0645\u06cc\u0645 \u0627\u0639\u0644\u0627\u0645\u06cc \u0631\u0647\u0628\u0631\u06cc: exit_iaea|freeze|resume|neutrality
  rank mil|eco|tech|stab|nukes   \u0631\u062a\u0628\u0647\u200c\u0628\u0646\u062f\u06cc \u067e\u0648\u06cc\u0627 \u062f\u0631 \u0647\u0631 \u0634\u0627\u062e\u0647
داشبورد: dash dom|dip|ops|mil|eco|org (یا فارسی: سیاست/دیپلماسی/عملیات/نظامی/اقتصاد/نهاد)
پایان دور: end  → یک روز جلو می‌رود؛ ظاهر گزارش: احزاب، مطبوعات، جنگ‌ها، بازار سلاح.
"""

def load_political_baseline():
    """بارگذاری baseline سیاسی از داده‌های ثابت و ساخت نسخه مستقل برای هر ذخیره."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    classifications_path = os.path.join(data_dir, "political_classifications.json")
    country_map_path = os.path.join(data_dir, "country_map.json")
    with open(classifications_path, encoding="utf-8") as f:
        payload = json.load(f)
    with open(country_map_path, encoding="utf-8") as f:
        country_map = json.load(f)
    records = payload.get("countries") or {}
    runtime = {}
    missing = []
    # نام داخلی موتور در این مورد با نام نقشه تفاوت املایی دارد.
    name_aliases = {"دومینیکن": "دومینیکان"}
    for name in COUNTRIES:
        meta = country_map.get(name) or country_map.get(name_aliases.get(name, "")) or {}
        iso3 = meta.get("iso3")
        record = records.get(iso3) if iso3 else None
        if not isinstance(record, dict):
            missing.append("%s (%s)" % (name, iso3 or "بدون ISO3"))
        else:
            runtime[name] = record
    if missing:
        raise ValueError("طبقه‌بندی سیاسی برای کشورها ناقص است: " + "، ".join(missing[:12]))
    expected = int(payload.get("coverage", {}).get("expected_countries", len(runtime)))
    if expected != len(runtime):
        raise ValueError("تعداد کشورهای baseline با موتور یکسان نیست: %d در برابر %d" %
                         (expected, len(runtime)))
    meta = {
        "schema_version": payload.get("schema_version", "unknown"),
        "scenario_reference_date": payload.get("scenario_reference_date", ""),
        "source_file": "data/political_classifications.json",
        "country_count": len(runtime),
    }
    return runtime, meta



def apply_player_political_change(s, changes):
    """اعمال تغییرات ساختار سیاسی فقط برای کشور تحت کنترل بازیکن؛ AI عمداً در این مسیر نیست."""
    if s.get("over"):
        return dict(ok=False, error="بازی پایان یافته است.")
    player = s.get("player")
    if not player or player not in (s.get("political_state") or {}):
        return dict(ok=False, error="وضعیت سیاسی کشور بازیکن در دسترس نیست.")
    if not isinstance(changes, dict) or not changes:
        return dict(ok=False, error="حداقل یک تغییر معتبر انتخاب کن.")

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    taxonomy_path = os.path.join(data_dir, "political_taxonomy.json")
    with open(taxonomy_path, encoding="utf-8") as f:
        taxonomy = json.load(f)
    fields = taxonomy.get("runtime_change_policy", {}).get("mutable_fields", [])
    allowed = {}
    profile_fields = taxonomy.get("country_profile_fields", {})
    for field in fields:
        spec = profile_fields.get(field) or {}
        if isinstance(spec.get("allowed"), list):
            allowed[field] = set(spec["allowed"])
    subforms = set((profile_fields.get("government_subform") or {}).get("examples", []))
    for record in (s.get("political_state") or {}).values():
        value = record.get("government_subform") if isinstance(record, dict) else None
        if value:
            subforms.add(value)
    allowed["government_subform"] = subforms
    ideology_ids = set(x.get("id") for x in taxonomy.get("ideology_families", []) if x.get("id"))
    ideology_fields = set(["official_ideology", "ruling_party_ideology", "ruling_coalition_ideology"])
    current = s["political_state"][player]
    updated = {}
    for field, value in changes.items():
        if field not in fields:
            return dict(ok=False, error="فیلد غیرمجاز برای تغییر: " + str(field))
        if field in ideology_fields:
            if not isinstance(value, list):
                return dict(ok=False, error="ایدئولوژی باید به‌صورت فهرست انتخاب شود: " + field)
            clean = []
            for item in value:
                item = str(item)
                if item not in ideology_ids:
                    return dict(ok=False, error="شناسه ایدئولوژی نامعتبر است: " + item)
                if item not in clean:
                    clean.append(item)
            if not clean:
                continue
            normalized = clean
        else:
            normalized = str(value)
            if normalized not in allowed.get(field, set()):
                return dict(ok=False, error="مقدار انتخاب‌شده برای «%s» معتبر نیست." % field)
        if current.get(field) != normalized:
            updated[field] = dict(old=current.get(field), new=normalized)
    if not updated:
        return dict(ok=False, error="هیچ تغییری نسبت به ساختار فعلی انتخاب نشده است.")

    # جلوگیری از ترکیب‌های نامعتبر میان نوع حکومت و زیرنوع آن.
    candidate_form = updated.get("government_form", {}).get("new", current.get("government_form"))
    candidate_subform = updated.get("government_subform", {}).get("new", current.get("government_subform"))
    compatible_subforms = {
        "republic": set(["democratic_socialist_republic", "federal_directorial_republic",
            "federal_parliamentary_republic", "federal_republic", "federal_semi_presidential_republic",
            "fragmented_transitional_republic", "islamic_republic", "parliamentary_republic",
            "presidential_republic", "semi_presidential_republic", "socialist_republic", "transitional_authority"]),
        "monarchy": set(["absolute_monarchy", "constitutional_monarchy", "federal_constitutional_monarchy"]),
        "emirate": set(["hereditary_emirate", "islamic_emirate"]),
        "military_government": set(["military_junta"]),
        "sultanate": set(["absolute_monarchy"]),
        "transitional_government": set(["interim_self_governing_authority", "military_junta",
            "military_led_transitional_authority", "transitional_authority", "transitional_presidential_authority"]),
    }
    if ("government_form" in updated or "government_subform" in updated):
        valid_subforms = compatible_subforms.get(candidate_form)
        if valid_subforms and candidate_subform not in valid_subforms:
            return dict(ok=False, error="نوع حکومت و زیرنوع انتخاب‌شده با هم سازگار نیستند؛ هر دو را به شکل هماهنگ انتخاب کن.")

    proposals = s.setdefault("political_reform_proposals", [])
    active_reform_statuses = set([
        "pending", "reviewed", "approved", "executing",
        "paused_funds", "paused_crisis"
    ])
    if any(isinstance(p, dict) and p.get("country") == player
           and p.get("status") in active_reform_statuses for p in proposals):
        return dict(ok=False, error="یک طرح اصلاحات فعال داری؛ ابتدا آن را لغو کن، رد کن یا منتظر پایان اجرای آن بمان.")
    # برآورد اولیه؛ در این بسته فقط طرح ثبت می‌شود و هنوز پولی کسر یا تغییری اعمال نمی‌شود.
    weights = {
        "government_form": 12, "government_subform": 8,
        "executive_legislative_system": 7, "territorial_structure": 15,
        "regime_character": 10, "party_system": 7,
        "official_ideology": 6, "ruling_party_ideology": 4,
        "ruling_coalition_ideology": 4
    }
    complexity = sum(weights.get(k, 5) for k in updated)
    estimated_cost = round(2.0 + complexity * 0.65, 1)
    estimated_days = 7 + complexity * 2
    proposal_id = 1 + max([int(p.get("id", 0)) for p in proposals] or [0])
    proposal = dict(
        id=proposal_id, country=player, actor="player",
        submitted_date=s.get("game_date", ""), changes=updated,
        estimated_cost=estimated_cost, estimated_days=estimated_days,
        elapsed_days=0, progress=0, status="pending",
        note="برآورد اولیه؛ هزینه و زمان‌بندی اجرایی در بسته بعدی فعال می‌شود."
    )
    proposals.append(proposal)
    if len(proposals) > 100:
        del proposals[:-100]
    s.setdefault("log", []).append("📜 طرح اصلاحات سیاسی شماره %s برای %s ثبت شد؛ هنوز تغییری در ساختار اعمال نشده است." % (proposal_id, player))
    save(s)
    return dict(ok=True, out="طرح اصلاحات ثبت شد؛ وضعیت فعلی کشور تا تصویب و اجرای نهایی بدون تغییر می‌ماند.",
                proposal=proposal, current_unchanged=True)



def cancel_player_political_reform(s, proposal_id):
    """لغو طرح در انتظار؛ این مسیر فقط برای کشور بازیکن است."""
    player = s.get("player")
    proposals = s.setdefault("political_reform_proposals", [])
    for proposal in reversed(proposals):
        if int(proposal.get("id", -1)) == int(proposal_id) and proposal.get("country") == player:
            if proposal.get("status") != "pending":
                return dict(ok=False, error="فقط طرحی که هنوز در انتظار است قابل لغو است.")
            proposal["status"] = "cancelled"
            proposal["cancelled_date"] = s.get("game_date", "")
            s.setdefault("log", []).append("🗑 طرح اصلاحات سیاسی شماره %s لغو شد." % proposal.get("id"))
            save(s)
            return dict(ok=True, out="طرح اصلاحات لغو شد؛ ساختار فعلی کشور تغییری نکرد.")
    return dict(ok=False, error="طرح در انتظار معتبری با این شناسه پیدا نشد.")

def review_player_political_reform(s, proposal_id):
    """ارزیابی شفاف و شبیه‌سازی‌شده؛ بدون کسر پول یا اعمال تغییر سیاسی."""
    player = s.get("player")
    proposals = s.setdefault("political_reform_proposals", [])
    proposal = next((p for p in reversed(proposals)
                     if int(p.get("id", -1)) == int(proposal_id) and p.get("country") == player), None)
    if not proposal or proposal.get("status") != "pending":
        return dict(ok=False, error="طرحِ در انتظار معتبری برای ارزیابی پیدا نشد.")
    country = (s.get("world") or {}).get(player) or {}
    politics = (s.get("politics") or {}).get(player) or {}
    parties = politics.get("parties") or {}
    changes = proposal.get("changes") or {}
    fields = set(changes)
    stability = max(0.0, min(100.0, float(country.get("stab", 0))))
    money = max(0.0, float(country.get("money", 0)))
    cost = max(0.1, float(proposal.get("estimated_cost", 0)))
    affordability = max(0.0, min(100.0, (money / cost) * 50.0))
    # واکنش‌ها فرض‌های شبیه‌سازی بازی‌اند، نه ادعایی درباره مواضع واقعی احزاب.
    reactions = {}
    for party, support in parties.items():
        delta = 0
        if party == "اصلاح‌طلبان":
            delta += 2 if fields.intersection(set(["executive_legislative_system", "party_system", "regime_character"])) else 0
            delta -= 2 if "government_form" in fields else 0
        elif party == "جبهه انقلاب":
            delta -= 2 if fields.intersection(set(["government_form", "official_ideology", "regime_character"])) else 0
            delta += 1 if "ruling_party_ideology" in fields else 0
        elif party == "ملی‌گرایان":
            territory_change = changes.get("territorial_structure")
            territory_value = territory_change.get("new") if isinstance(territory_change, dict) else territory_change
            delta -= 2 if territory_value in ("federal", "federal_state", "confederation") else 0
            delta += 1 if "official_ideology" in fields else 0
        elif party == "تکنوکرات‌ها":
            delta += 2 if fields.intersection(set(["executive_legislative_system", "party_system"])) else 0
            delta -= 1 if "territorial_structure" in fields else 0
        reactions[party] = dict(current=round(float(support), 1), projected_change=delta,
                                projected=round(max(0.0, min(100.0, float(support) + delta)), 1))
    party_score = 50.0
    if reactions:
        total = sum(max(0.0, float(v.get("current", 0))) for v in reactions.values())
        if total > 0:
            party_score = sum(v["projected"] * v["current"] for v in reactions.values()) / total

    social_groups = s.setdefault("social_groups", {}).setdefault(player, dict(SOCIAL_GROUP_BASE))
    social_reactions = {}
    for group_name, support in social_groups.items():
        delta = 0
        if group_name == "کارگران و مزدبگیران":
            delta += 2 if fields.intersection(set(["executive_legislative_system", "party_system"])) else 0
            delta -= 1 if "official_ideology" in fields else 0
        elif group_name == "کسب‌وکار و بازرگانان":
            delta += 2 if fields.intersection(set(["executive_legislative_system", "party_system"])) else 0
            delta -= 2 if "official_ideology" in fields else 0
        elif group_name == "کارمندان و خدمات عمومی":
            delta += 2 if fields.intersection(set(["government_form", "government_subform", "executive_legislative_system"])) else 0
            delta -= 1 if "regime_character" in fields else 0
        elif group_name == "دانشجویان و جوانان":
            delta += 2 if fields.intersection(set(["party_system", "executive_legislative_system"])) else 0
            delta -= 1 if "official_ideology" in fields else 0
        elif group_name == "کشاورزان و مناطق روستایی":
            territory_change = changes.get("territorial_structure")
            territory_value = territory_change.get("new") if isinstance(territory_change, dict) else territory_change
            delta += 3 if territory_value in ("federal", "federal_state", "confederation") else 0
            delta -= 2 if territory_value in ("unitary", "centralized") else 0
        elif group_name == "متخصصان و طبقه متوسط":
            delta += 2 if fields.intersection(set(["executive_legislative_system", "party_system"])) else 0
            delta -= 1 if "government_form" in fields else 0
        social_reactions[group_name] = dict(
            current=round(float(support), 1), projected_change=delta,
            projected=round(max(0.0, min(100.0, float(support) + delta)), 1))
    social_score = 50.0
    if social_reactions:
        social_score = sum(v["projected"] for v in social_reactions.values()) / float(len(social_reactions))

    scope = sum(1 for _ in changes)
    complexity_penalty = min(20.0, scope * 2.5)
    feasibility = max(0.0, min(100.0,
        stability * 0.35 + affordability * 0.25 +
        party_score * 0.20 + social_score * 0.20 - complexity_penalty))
    if stability < 20:
        outlook = "پرریسک؛ ثبات داخلی پایین است"
    elif affordability < 25:
        outlook = "پرریسک؛ توان مالی برای برآورد طرح محدود است"
    elif feasibility >= 65:
        outlook = "مساعد؛ امکان پیشبرد طرح در شبیه‌سازی بیشتر است"
    elif feasibility >= 45:
        outlook = "میانه؛ نیازمند توافق و مدیریت پیامدها"
    else:
        outlook = "دشوار؛ احتمال مخالفت و ناکامی بالاتر است"
    proposal["review"] = dict(
        reviewed_date=s.get("game_date", ""), stability=round(stability, 1),
        affordability=round(affordability, 1), party_score=round(party_score, 1),
        social_score=round(social_score, 1),
        complexity_penalty=round(complexity_penalty, 1),
        feasibility=round(feasibility, 1), outlook=outlook,
        party_reactions=reactions, social_reactions=social_reactions,
        note="ارزیابی تقریبیِ مدل بازی؛ نتیجه قطعی نیست و هیچ هزینه یا تغییری اعمال نشده است."
    )
    proposal["status"] = "reviewed"
    save(s)
    return dict(ok=True, out="ارزیابی طرح انجام شد؛ هنوز باید درباره تصویب یا رد آن تصمیم بگیری.", proposal=proposal)


def decide_player_political_reform(s, proposal_id, decision):
    """ثبت تصمیم بازیکن پس از ارزیابی؛ اجرا در بسته بعدی انجام می‌شود."""
    player = s.get("player")
    proposals = s.setdefault("political_reform_proposals", [])
    proposal = next((p for p in reversed(proposals)
                     if int(p.get("id", -1)) == int(proposal_id) and p.get("country") == player), None)
    if not proposal or proposal.get("status") != "reviewed" or not proposal.get("review"):
        return dict(ok=False, error="ابتدا باید طرح را ارزیابی کنی.")
    if decision == "approve":
        proposal["status"] = "approved"
        proposal["decision_date"] = s.get("game_date", "")
        out = "طرح تصویب شد و برای اجرای مرحله‌ای در بسته بعدی آماده است؛ هنوز تغییری اعمال نشده."
    elif decision == "reject":
        proposal["status"] = "rejected"
        proposal["decision_date"] = s.get("game_date", "")
        out = "طرح رد شد؛ هیچ هزینه‌ای کسر و هیچ تغییری اعمال نشد."
    else:
        return dict(ok=False, error="تصمیم نامعتبر است.")
    s.setdefault("log", []).append("📜 طرح اصلاحات سیاسی شماره %s: %s." %
                                   (proposal.get("id"), "تصویب شد" if decision == "approve" else "رد شد"))
    save(s)
    return dict(ok=True, out=out, proposal=proposal)


def load():
    with open(STATE, encoding="utf-8") as f:
        s = json.load(f)
    # مهاجرت ذخیره‌های قدیمی به تقویم میلادی؛ روزهای سپری‌شده حفظ می‌شوند.
    if not s.get("game_date"):
        legacy_year = int(s.get("year", 2025))
        legacy_day = int(s.get("day", 1))
        elapsed = max(0, (legacy_year - 2025) * 30 + legacy_day - 1)
        migrated = START_DATE + datetime.timedelta(days=elapsed)
        s["game_date"] = migrated.isoformat()
        s["elapsed_days"] = elapsed
        s["hour"] = 0
        s["minute"] = 0
    try:
        current_date = datetime.date.fromisoformat(s["game_date"])
    except (TypeError, ValueError):
        current_date = START_DATE
        s["game_date"] = current_date.isoformat()
    s["year"] = current_date.year
    s["day"] = current_date.day
    s.setdefault("hour", 0)
    s.setdefault("minute", 0)
    s.setdefault("elapsed_days", 0)
    # مهاجرت ذخیره‌های قدیمی: ساخت نسخه runtime مستقل از baseline ثابت سیاسی
    political_state = s.get("political_state")
    if not isinstance(political_state, dict):
        political_state = {}
        s["political_state"] = political_state
    missing_political = [n for n in s.get("world", {}) if n not in political_state]
    needs_political_save = False
    if missing_political or not isinstance(s.get("political_baseline"), dict) or not isinstance(s.get("political_baseline_state"), dict):
        baseline, baseline_meta = load_political_baseline()
        for n in missing_political:
            political_state[n] = json.loads(json.dumps(baseline[n]))
        if not isinstance(s.get("political_baseline_state"), dict):
            # baseline جداگانه و مستقل نگهداری می‌شود تا تغییر runtime هرگز آن را تغییر ندهد.
            s["political_baseline_state"] = json.loads(json.dumps(baseline))
        s["political_baseline"] = baseline_meta
        needs_political_save = True
    if needs_political_save:
        save(s)
    # مهاجرت ذخیره‌های قدیمی به ساختار politics سراسری
    if "politics" not in s:
        p = s.get("player", "")
        pol = {}
        for n in s.get("world", {}):
            if n == p:
                pol[n] = dict(parties=s.get("parties") or dict(PARTY_BASE), press=s.get("press") or [])
            else:
                pol[n] = dict(parties=dict(AI_PARTY_BASE), press=[])
        s["politics"] = pol
    if not isinstance(s.get("social_groups"), dict):
        s["social_groups"] = {}
    player_name = s.get("player")
    if player_name:
        groups = s["social_groups"].get(player_name)
        if not isinstance(groups, dict) or not groups:
            s["social_groups"][player_name] = dict(SOCIAL_GROUP_BASE)
        else:
            for group_name, default_value in SOCIAL_GROUP_BASE.items():
                groups.setdefault(group_name, default_value)
            s["social_groups"][player_name] = dict(
                (k, round(max(0.0, min(100.0, float(v))), 1))
                for k, v in groups.items())
    if not isinstance(s.get("political_history"), list):
        s["political_history"] = []
    if not isinstance(s.get("turn_events"), dict):
        s["turn_events"] = {}
    # مهاجرت سازگار رویدادها برای ذخیره‌های قدیمی و نسخه‌های میانی سیستم مرکزی
    raw_events = s.get("game_events")
    if not isinstance(raw_events, list):
        raw_events = []
        s["game_events"] = raw_events
        needs_event_save = True
    else:
        needs_event_save = False

    normalized_events = []
    max_event_number = 0
    for event in raw_events:
        if not isinstance(event, dict):
            needs_event_save = True
            continue
        if not isinstance(event.get("metadata"), dict):
            event["metadata"] = {}
            needs_event_save = True
        if not isinstance(event.get("impact_targets"), list):
            event["impact_targets"] = list(EVENT_IMPACT_ROUTES.get(event.get("category"), []))
            needs_event_save = True
        if not isinstance(event.get("impact_plan"), list):
            event["impact_plan"] = []
            needs_event_save = True
        defaults = {
            "status": "recorded",
            "effects_applied": False,
            "impact_status": "pending_design",
            "parent_event_id": None,
            "child_event_ids": [],
            "chain_depth": 0
        }
        for key, value in defaults.items():
            if key not in event:
                event[key] = value
                needs_event_save = True
        if not isinstance(event.get("child_event_ids"), list):
            event["child_event_ids"] = []
            needs_event_save = True
        try:
            severity = max(1, min(5, int(event.get("severity", 1))))
        except (TypeError, ValueError):
            severity = 1
        if event.get("severity") != severity:
            event["severity"] = severity
            needs_event_save = True
        priority = get_event_priority(severity)
        for key, value in (("priority", priority["key"]),
                           ("priority_rank", priority["rank"]),
                           ("priority_label", priority["label"])):
            if event.get(key) != value:
                event[key] = value
                needs_event_save = True
        if "status_updated_date" not in event:
            event["status_updated_date"] = event.get("date") or s.get("game_date", "")
            needs_event_save = True
        try:
            event["chain_depth"] = max(0, int(event.get("chain_depth", 0)))
        except (TypeError, ValueError):
            event["chain_depth"] = 0
            needs_event_save = True
        if not isinstance(event.get("status_history"), list):
            event["status_history"] = [{
                "date": event.get("date") or s.get("game_date", ""),
                "from": None,
                "to": event.get("status", "recorded"),
                "actor": "migration",
                "note": "سوابق وضعیت در مهاجرت ذخیره تکمیل شد."
            }]
            needs_event_save = True
        if not isinstance(event.get("source_info"), dict):
            event["source_info"] = _normalize_event_source(event.get("source", "system"))
            needs_event_save = True
        else:
            source_info = event["source_info"]
            source_defaults = {
                "source_system": str(event.get("source") or "system"),
                "source_record_id": "",
                "signal": "",
                "recorded_by": "system",
                "evidence_refs": [],
                "review_status": "pending",
                "reviewed_by": "",
                "review_note": ""
            }
            for key, value in source_defaults.items():
                if key not in source_info:
                    source_info[key] = value
                    needs_event_save = True
            if not isinstance(source_info.get("evidence_refs"), list):
                source_info["evidence_refs"] = []
                needs_event_save = True
        event_id = str(event.get("id") or "")
        if not event_id:
            event["id"] = "EV-LEGACY-%06d" % (len(normalized_events) + 1)
            event_id = event["id"]
            needs_event_save = True
        if not event.get("chain_id"):
            event["chain_id"] = event_id
            needs_event_save = True
        if event_id.startswith("EV-"):
            try:
                max_event_number = max(max_event_number, int(event_id[3:]))
            except (TypeError, ValueError):
                pass
        normalized_events.append(event)

    if normalized_events != raw_events:
        s["game_events"] = normalized_events
        needs_event_save = True
    try:
        saved_event_sequence = max(0, int(s.get("event_sequence", 0)))
    except (TypeError, ValueError):
        saved_event_sequence = 0
        needs_event_save = True
    safe_event_sequence = max(saved_event_sequence, max_event_number)
    if s.get("event_sequence") != safe_event_sequence:
        s["event_sequence"] = safe_event_sequence
        needs_event_save = True
    if needs_event_save:
        save(s)
    if not isinstance(s.get("diplomatic_history"), list):
        s["diplomatic_history"] = []
        save(s)
    else:
        s["diplomatic_history"] = [x for x in s["diplomatic_history"][-300:] if isinstance(x, dict)]

    s.setdefault("proxies", [])
    s.setdefault("day", 1)
    s.setdefault("iaea_heat", 0)
    s.setdefault("un_censures", 0)
    s.setdefault("statements", [])
    s.setdefault("iaea_out", False)
    s.setdefault("arsenal", {})
    rel = s.get("relations", {})
    fresh = None
    for name in s.get("world", {}):
        if name not in s["arsenal"]:
            if fresh is None:
                fresh = _default_arsenal(rel)
            s["arsenal"][name] = dict(fresh.get(name, {}))
        s["world"][name].setdefault("_arsenal", s["arsenal"][name])

    # مهاجرت و اعتبارسنجی تحریم‌های بازیکن برای ذخیره‌های قدیمی
    sanction_save_needed = False
    raw_sanctions = s.get("player_sanctions")
    if not isinstance(raw_sanctions, dict):
        raw_sanctions = {}
        sanction_save_needed = True
    normalized_sanctions = {}
    for target, record in raw_sanctions.items():
        if target not in s.get("world", {}) or target == s.get("player") or not isinstance(record, dict):
            sanction_save_needed = True
            continue
        cats = record.get("categories")
        if not isinstance(cats, list):
            cats = []
            sanction_save_needed = True
        cats = [x for x in cats if isinstance(x, str) and x in PLAYER_SANCTION_CATEGORIES]
        if not cats:
            sanction_save_needed = True
            continue
        normalized_sanctions[target] = {
            "country": target, "actor": "player", "categories": sorted(set(cats)),
            "status": "active",
            "imposed_date": str(record.get("imposed_date") or s.get("game_date", "")),
            "updated_date": str(record.get("updated_date") or record.get("imposed_date") or s.get("game_date", ""))
        }
        if normalized_sanctions[target] != record:
            sanction_save_needed = True
    if normalized_sanctions != raw_sanctions:
        s["player_sanctions"] = normalized_sanctions
        sanction_save_needed = True
    raw_sanction_history = s.get("player_sanction_history")
    if not isinstance(raw_sanction_history, list):
        s["player_sanction_history"] = []
        sanction_save_needed = True
    else:
        clean_history = [x for x in raw_sanction_history[-200:] if isinstance(x, dict)]
        if clean_history != raw_sanction_history:
            s["player_sanction_history"] = clean_history
            sanction_save_needed = True
    if sanction_save_needed:
        save(s)

    # صندوق پیام‌ها؛ آماده دریافت درخواست‌ها و پیام‌های آینده هوش مصنوعی زنده
    inbox_save_needed = False
    raw_inbox = s.get("inbox_messages")
    if not isinstance(raw_inbox, list):
        raw_inbox = []
        s["inbox_messages"] = raw_inbox
        inbox_save_needed = True
    clean_inbox = []
    max_inbox_number = 0
    for item in raw_inbox:
        if not isinstance(item, dict):
            inbox_save_needed = True
            continue
        if not item.get("id"):
            inbox_save_needed = True
            continue
        item.setdefault("sender_country", "")
        item.setdefault("message_type", "message")
        item.setdefault("title", "پیام جدید")
        item.setdefault("body", "")
        item.setdefault("date", s.get("game_date", ""))
        item.setdefault("status", "unread")
        item.setdefault("conversation_id", None)
        item.setdefault("response_allowed", False)
        item.setdefault("metadata", {})
        if not isinstance(item.get("metadata"), dict):
            item["metadata"] = {}
            inbox_save_needed = True
        if item.get("status") not in ("unread", "read", "answered", "archived"):
            item["status"] = "unread"
            inbox_save_needed = True
        if not isinstance(item.get("response_allowed"), bool):
            item["response_allowed"] = False
            inbox_save_needed = True
        try:
            number = int(str(item.get("id", "")).split("-")[-1])
            max_inbox_number = max(max_inbox_number, number)
        except (TypeError, ValueError):
            pass
        clean_inbox.append(item)
    if clean_inbox != raw_inbox:
        s["inbox_messages"] = clean_inbox[-300:]
        inbox_save_needed = True
    try:
        seq = max(0, int(s.get("inbox_sequence", 0)))
    except (TypeError, ValueError):
        seq = 0
        inbox_save_needed = True
    if seq < max_inbox_number:
        seq = max_inbox_number
        inbox_save_needed = True
    if s.get("inbox_sequence") != seq:
        s["inbox_sequence"] = seq
        inbox_save_needed = True
    if inbox_save_needed:
        save(s)

    # نشست‌های مشترک مذاکره؛ بدون تولید پیام یا فعال‌سازی AI تا فاز F
    conversation_save_needed = False
    raw_sessions = s.get("conversation_sessions")
    if not isinstance(raw_sessions, list):
        raw_sessions = []
        s["conversation_sessions"] = raw_sessions
        conversation_save_needed = True
    clean_sessions = []
    max_conversation_number = 0
    valid_modes = ("public", "normal", "confidential")
    valid_types = ("standard", "alliance", "pact", "diplomacy", "ceasefire", "trade", "other")
    valid_sources = ("statement", "diplomacy", "pacts", "inbox", "system")
    valid_statuses = ("prepared", "active", "completed", "cancelled")
    for session in raw_sessions:
        if not isinstance(session, dict) or not session.get("id"):
            conversation_save_needed = True
            continue
        participants = session.get("participants")
        if not isinstance(participants, list):
            participants = []
            conversation_save_needed = True
        original_participants = list(participants)
        participants = [n for n in participants if isinstance(n, str) and n in s.get("world", {})]
        if s.get("player") in s.get("world", {}) and s.get("player") not in participants:
            participants.insert(0, s.get("player"))
        normalized_participants = list(dict.fromkeys(participants))
        if normalized_participants != original_participants:
            conversation_save_needed = True
        session["participants"] = normalized_participants
        if session.get("visibility_mode") not in valid_modes:
            session["visibility_mode"] = "public"
            conversation_save_needed = True
        if session.get("negotiation_type") not in valid_types:
            session["negotiation_type"] = "standard"
            conversation_save_needed = True
        if session.get("source") not in valid_sources:
            session["source"] = "system"
            conversation_save_needed = True
        if session.get("status") not in valid_statuses:
            session["status"] = "prepared"
            conversation_save_needed = True
        if not isinstance(session.get("context"), dict):
            session["context"] = {}
            conversation_save_needed = True
        if not isinstance(session.get("messages"), list):
            session["messages"] = []
            conversation_save_needed = True
        if not isinstance(session.get("linked_records"), list):
            session["linked_records"] = []
            conversation_save_needed = True
        defaults = {
            "topic": "گفت‌وگوی دیپلماتیک",
            "initiator": s.get("player", ""),
            "created_date": s.get("game_date", ""),
            "updated_date": session.get("created_date", s.get("game_date", ""))
        }
        for key, value in defaults.items():
            if key not in session:
                session[key] = value
                conversation_save_needed = True
        for key, value in (("meeting_status", "unscheduled"),
                           ("meeting_date", None),
                           ("meeting_request_id", None),
                           ("live_ai_required", True)):
            if key not in session:
                session[key] = value
                conversation_save_needed = True
        try:
            meeting_due = bool(session.get("meeting_date") and
                               datetime.date.fromisoformat(str(session.get("meeting_date"))) <=
                               datetime.date.fromisoformat(str(s.get("game_date", ""))))
        except (TypeError, ValueError):
            meeting_due = False
        chat_enabled = bool(s.get("live_ai_active") and meeting_due and
                            session.get("meeting_status") in ("confirmed", "due"))
        live_status = "ready" if chat_enabled else (
            "locked_until_phase_f" if not s.get("live_ai_active") else "locked_until_meeting_date")
        if session.get("live_ai_required") is not True:
            session["live_ai_required"] = True
            conversation_save_needed = True
        if session.get("chat_enabled") != chat_enabled:
            session["chat_enabled"] = chat_enabled
            conversation_save_needed = True
        if session.get("live_ai_status") != live_status:
            session["live_ai_status"] = live_status
            conversation_save_needed = True
        try:
            number = int(str(session.get("id", "")).split("-")[-1])
            max_conversation_number = max(max_conversation_number, number)
        except (TypeError, ValueError):
            pass
        clean_sessions.append(session)
    if clean_sessions != raw_sessions:
        s["conversation_sessions"] = clean_sessions[-200:]
        conversation_save_needed = True
    try:
        conversation_seq = max(0, int(s.get("conversation_sequence", 0)))
    except (TypeError, ValueError):
        conversation_seq = 0
        conversation_save_needed = True
    if conversation_seq < max_conversation_number:
        conversation_seq = max_conversation_number
        conversation_save_needed = True
    if s.get("conversation_sequence") != conversation_seq:
        s["conversation_sequence"] = conversation_seq
        conversation_save_needed = True
    if conversation_save_needed:
        save(s)

    calendar_save_needed = False
    if not isinstance(s.get("calendar_events"), list):
        s["calendar_events"] = []
        calendar_save_needed = True
    try:
        calendar_seq = max(0, int(s.get("calendar_sequence", 0)))
    except (TypeError, ValueError):
        calendar_seq = 0
        calendar_save_needed = True
    for item in s["calendar_events"]:
        if isinstance(item, dict):
            try:
                calendar_seq = max(calendar_seq, int(str(item.get("id", "")).split("-")[-1]))
            except (TypeError, ValueError):
                pass
    if s.get("calendar_sequence") != calendar_seq:
        s["calendar_sequence"] = calendar_seq
        calendar_save_needed = True
    if not isinstance(s.get("live_ai_active"), bool):
        s["live_ai_active"] = False
        calendar_save_needed = True
    if calendar_save_needed:
        save(s)

    # قرارداد پایدار پیمان‌ها و اتحادها؛ مهاجرت داده‌های قدیمی بدون پذیرش ساختگی
    agreement_save_needed = False
    for key in ("pact_records", "alliance_records", "agreement_proposals", "agreement_history", "alliance_join_requests"):
        if not isinstance(s.get(key), list):
            s[key] = []
            agreement_save_needed = True
    pact_types = ("non_aggression", "trade", "defense", "cooperation", "transit", "economic", "other")
    clean_pacts = []
    seen_pact_ids = set()
    max_agreement_number = 0
    for record in s.get("pact_records", []):
        if not isinstance(record, dict):
            agreement_save_needed = True
            continue
        rid = str(record.get("id") or "")
        parties = record.get("members")
        if not isinstance(parties, list):
            parties = record.get("parties") if isinstance(record.get("parties"), list) else []
        parties = list(dict.fromkeys([n for n in parties if isinstance(n, str) and n in s.get("world", {})]))
        if len(parties) < 2 or record.get("type") not in pact_types or record.get("status") not in ("active", "cancelled", "expired"):
            agreement_save_needed = True
            continue
        if not rid:
            max_agreement_number += 1
            rid = "PACT-LEGACY-%06d" % max_agreement_number
            agreement_save_needed = True
        if rid in seen_pact_ids:
            agreement_save_needed = True
            continue
        seen_pact_ids.add(rid)
        record.update({
            "id": rid, "type": record.get("type", "non_aggression"),
            "members": parties, "status": record.get("status", "active"),
            "created_date": str(record.get("created_date") or s.get("game_date", "")),
            "updated_date": str(record.get("updated_date") or record.get("created_date") or s.get("game_date", "")),
            "legacy": bool(record.get("legacy", False))
        })
        clean_pacts.append(record)
    s["pact_records"] = clean_pacts[-500:]

    clean_alliances = []
    seen_alliance_ids = set()
    for record in s.get("alliance_records", []):
        if not isinstance(record, dict):
            agreement_save_needed = True
            continue
        rid = str(record.get("id") or "")
        members = record.get("members")
        if not isinstance(members, list):
            members = []
        members = list(dict.fromkeys([n for n in members if isinstance(n, str) and n in s.get("world", {})]))
        if len(members) < 2 or record.get("status") not in ("active", "dissolved"):
            agreement_save_needed = True
            continue
        if not rid:
            max_agreement_number += 1
            rid = "ALLY-LEGACY-%06d" % max_agreement_number
            agreement_save_needed = True
        if rid in seen_alliance_ids:
            agreement_save_needed = True
            continue
        seen_alliance_ids.add(rid)
        record.update({
            "id": rid, "name": str(record.get("name") or "اتحاد ثبت‌شده"),
            "type": str(record.get("type") or "military"),
            "members": members, "status": record.get("status", "active"),
            "created_date": str(record.get("created_date") or s.get("game_date", "")),
            "updated_date": str(record.get("updated_date") or record.get("created_date") or s.get("game_date", "")),
            "legacy": bool(record.get("legacy", False))
        })
        clean_alliances.append(record)
    s["alliance_records"] = clean_alliances[-300:]

    # تبدیل فهرست‌های قدیمی به پرونده‌های دوجانبه؛ شبکه جهانیِ حدس‌زده ساخته نمی‌شود
    player_name = s.get("player")
    known_pact_pairs = set(tuple(sorted(x.get("members", []))) for x in s["pact_records"] if x.get("status") == "active")
    for partner in s.get("pacts", []):
        if isinstance(partner, str) and partner in s.get("world", {}) and partner != player_name:
            pair = tuple(sorted([player_name, partner]))
            if pair not in known_pact_pairs:
                max_agreement_number += 1
                s["pact_records"].append({
                    "id": "PACT-LEGACY-%06d" % max_agreement_number,
                    "type": "non_aggression", "name": "پیمان عدم تجاوز (داده قدیمی)",
                    "members": [player_name, partner], "status": "active",
                    "created_date": str(s.get("game_date", "")),
                    "updated_date": str(s.get("game_date", "")),
                    "terms": {}, "legacy": True
                })
                known_pact_pairs.add(pair)
                agreement_save_needed = True
    known_alliance_pairs = set(tuple(sorted(x.get("members", []))) for x in s["alliance_records"] if x.get("status") == "active" and x.get("legacy"))
    for partner in s.get("allies", []):
        if isinstance(partner, str) and partner in s.get("world", {}) and partner != player_name:
            pair = tuple(sorted([player_name, partner]))
            if pair not in known_alliance_pairs:
                max_agreement_number += 1
                s["alliance_records"].append({
                    "id": "ALLY-LEGACY-%06d" % max_agreement_number,
                    "name": "اتحاد دوجانبه ثبت‌شده (داده قدیمی)",
                    "type": "military", "members": [player_name, partner],
                    "status": "active", "created_date": str(s.get("game_date", "")),
                    "updated_date": str(s.get("game_date", "")),
                    "terms": {}, "legacy": True
                })
                known_alliance_pairs.add(pair)
                agreement_save_needed = True

    clean_proposals = []
    valid_proposal_statuses = ("pending", "accepted", "rejected", "cancelled", "completed")
    for proposal in s.get("agreement_proposals", []):
        if not isinstance(proposal, dict) or not proposal.get("id"):
            agreement_save_needed = True
            continue
        parties = proposal.get("parties")
        if not isinstance(parties, list):
            parties = []
        parties = list(dict.fromkeys([n for n in parties if isinstance(n, str) and n in s.get("world", {})]))
        if len(parties) < 2 or proposal.get("kind") not in ("pact", "alliance") or proposal.get("status") not in valid_proposal_statuses:
            agreement_save_needed = True
            continue
        proposal["parties"] = parties
        proposal.setdefault("accepted_by", [])
        proposal.setdefault("rejected_by", [])
        proposal.setdefault("created_date", s.get("game_date", ""))
        proposal.setdefault("updated_date", proposal.get("created_date", ""))
        proposal.setdefault("terms", {})
        proposal.setdefault("conversation_id", None)
        clean_proposals.append(proposal)
        try:
            max_agreement_number = max(max_agreement_number, int(str(proposal.get("id", "")).split("-")[-1]))
        except (TypeError, ValueError):
            pass
    if clean_proposals != s.get("agreement_proposals"):
        agreement_save_needed = True
    s["agreement_proposals"] = clean_proposals[-300:]
    try:
        agreement_seq = max(0, int(s.get("agreement_sequence", 0)))
    except (TypeError, ValueError):
        agreement_seq = 0
        agreement_save_needed = True
    if agreement_seq < max_agreement_number:
        agreement_seq = max_agreement_number
        agreement_save_needed = True
    if s.get("agreement_sequence") != agreement_seq:
        s["agreement_sequence"] = agreement_seq
        agreement_save_needed = True
    s["agreement_history"] = [x for x in s.get("agreement_history", []) if isinstance(x, dict)][-500:]
    if agreement_save_needed:
        save(s)
    return s


def register_inbox_message(s, sender_country, message_type="message", title="", body="",
                           conversation_id=None, response_allowed=False, metadata=None):
    """ثبت پیام ورودی؛ تولیدکننده AI زنده در فاز F به این قرارداد متصل می‌شود."""
    if sender_country not in (s.get("world") or {}) or sender_country == s.get("player"):
        raise ValueError("فرستنده پیام باید یک کشور دیگر در جهان بازی باشد.")
    allowed_types = ("request", "treaty_offer", "alliance_invite", "meeting_request", "conversation", "message")
    if message_type not in allowed_types:
        raise ValueError("نوع پیام ورودی نامعتبر است.")
    sequence = int(s.get("inbox_sequence", 0)) + 1
    s["inbox_sequence"] = sequence
    item = {
        "id": "MSG-%06d" % sequence, "sender_country": sender_country,
        "message_type": message_type, "title": str(title or "پیام جدید"),
        "body": str(body or ""), "date": s.get("game_date", ""),
        "status": "unread", "conversation_id": conversation_id,
        "response_allowed": bool(response_allowed),
        "metadata": metadata if isinstance(metadata, dict) else {}
    }
    messages = s.setdefault("inbox_messages", [])
    messages.append(item)
    if len(messages) > 300:
        del messages[:-300]
    return item


def mark_inbox_message_read(s, message_id):
    for item in s.get("inbox_messages") or []:
        if isinstance(item, dict) and item.get("id") == message_id:
            if item.get("status") == "unread":
                item["status"] = "read"
            return item
    raise ValueError("پیام موردنظر پیدا نشد.")

def prepare_conversation_session(s, participants, topic="گفت‌وگوی دیپلماتیک",
                                  visibility_mode="public", negotiation_type="standard",
                                  source="system", context=None, conversation_id=None,
                                  meeting_date=None):
    """نشست مشترک و پایدار برای ورودی‌های دیپلماسی؛ گفت‌وگوی واقعی فقط در فاز F."""
    if not isinstance(participants, list):
        raise ValueError("فهرست کشورهای گفت‌وگو نامعتبر است.")
    player = s.get("player")
    if player not in (s.get("world") or {}):
        raise ValueError("کشور بازیکن در وضعیت بازی معتبر نیست.")
    selected = []
    for name in participants:
        if not isinstance(name, str) or name not in s.get("world", {}):
            raise ValueError("یکی از کشورهای انتخاب‌شده در جهان بازی وجود ندارد.")
        if name in (s.get("eliminated") or []):
            raise ValueError("کشور حذف‌شده نمی‌تواند در نشست جدید شرکت کند.")
        if name not in selected:
            selected.append(name)
    if player not in selected:
        selected.insert(0, player)
    if len(selected) < 2:
        raise ValueError("برای تشکیل نشست، دست‌کم یک کشور دیگر را انتخاب کن.")
    if len(selected) > 20:
        raise ValueError("حداکثر ۲۰ کشور می‌توانند در یک نشست شرکت کنند.")
    if visibility_mode not in ("public", "normal", "confidential"):
        raise ValueError("حالت انتشار نشست نامعتبر است.")
    if negotiation_type not in ("standard", "alliance", "pact", "diplomacy", "ceasefire", "trade", "other"):
        raise ValueError("نوع مذاکره نامعتبر است.")
    if source not in ("statement", "diplomacy", "pacts", "inbox", "system"):
        raise ValueError("مبدأ نشست نامعتبر است.")
    topic = str(topic or "گفت‌وگوی دیپلماتیک").strip()[:120]
    if not topic:
        topic = "گفت‌وگوی دیپلماتیک"
    if not isinstance(context, dict):
        context = {}
    try:
        safe_context = json.loads(json.dumps(context, ensure_ascii=False))
    except (TypeError, ValueError):
        raise ValueError("زمینه نشست باید داده قابل ذخیره باشد.")
    if len(json.dumps(safe_context, ensure_ascii=False)) > 12000:
        raise ValueError("اطلاعات زمینه نشست بیش از حد مجاز است.")

    sessions = s.setdefault("conversation_sessions", [])
    existing = None
    if conversation_id:
        for item in sessions:
            if isinstance(item, dict) and item.get("id") == conversation_id:
                existing = item
                break
        if existing is None:
            raise ValueError("نشست گفت‌وگوی درخواستی پیدا نشد.")
        if set(existing.get("participants") or []) != set(selected):
            raise ValueError("اعضای نشست موجود با کشورهای انتخاب‌شده مطابقت ندارند.")
        old_date = existing.get("meeting_date")
        if old_date:
            if meeting_date and str(meeting_date) != old_date:
                raise ValueError("این نشست از قبل تاریخ مشخصی دارد؛ برای تغییر تاریخ باید درخواست جداگانه ثبت شود.")
            existing["updated_date"] = s.get("game_date", "")
            return dict(ok=True, created=False, session=existing,
                        note="نشست قبلی بازیابی شد؛ تاریخ و وضعیت فعلی آن حفظ شده است.")
    if not meeting_date:
        raise ValueError("برای نشست باید تاریخ پیشنهادی مشخص شود.")
    try:
        requested_date = datetime.date.fromisoformat(str(meeting_date))
        current_date = datetime.date.fromisoformat(str(s.get("game_date", "")))
    except (TypeError, ValueError):
        raise ValueError("تاریخ نشست معتبر نیست.")
    if requested_date <= current_date:
        raise ValueError("تاریخ نشست باید بعد از تاریخ فعلی بازی باشد.")
    if existing:
        existing["meeting_date"] = requested_date.isoformat()
        existing["meeting_status"] = "pending_ai_acceptance"
        existing["meeting_initiator"] = player
        existing["meeting_proposed_by"] = player
        existing["meeting_accepted_by"] = [player]
        existing["meeting_request_id"] = "MR-" + existing["id"]
        existing["updated_date"] = s.get("game_date", "")
        return dict(ok=True, created=False, session=existing,
                    note="تاریخ پیشنهادی به نشست قبلی افزوده شد؛ تا پذیرش طرف مقابل قفل می‌ماند.")

    sequence = int(s.get("conversation_sequence", 0)) + 1
    s["conversation_sequence"] = sequence
    session = {
        "id": "CONV-%06d" % sequence,
        "participants": selected,
        "initiator": player,
        "topic": topic,
        "visibility_mode": visibility_mode,
        "negotiation_type": negotiation_type,
        "source": source,
        "context": safe_context,
        "status": "prepared",
        "created_date": s.get("game_date", ""),
        "updated_date": s.get("game_date", ""),
        "meeting_date": requested_date.isoformat(),
        "meeting_status": "pending_ai_acceptance",
        "meeting_initiator": player,
        "meeting_proposed_by": player,
        "meeting_accepted_by": [player],
        "meeting_request_id": "MR-CONV-%06d" % sequence,
        "calendar_event_id": None,
        "messages": [],
        "linked_records": [],
        "live_ai_required": True,
        "live_ai_status": "locked_until_phase_f",
        "chat_enabled": False
    }
    sessions.append(session)
    if len(sessions) > 200:
        del sessions[:-200]
    msg(s, "پیشنهاد نشست %s برای %s در تاریخ %s ثبت شد؛ تا پذیرش کشور مقابل در تقویم قطعی نمی‌شود." %
        (session["id"], "، ".join(selected[1:]), session["meeting_date"]))
    return dict(ok=True, created=True, session=session,
                note="تاریخ به طرف مقابل پیشنهاد شد؛ پذیرش و ثبت قطعی در تقویم فقط با هوش مصنوعی زنده در فاز F انجام می‌شود.")


def _calendar_parse_date(value):
    try:
        return datetime.date.fromisoformat(str(value))
    except (TypeError, ValueError):
        raise ValueError("تاریخ تقویم معتبر نیست.")


def register_calendar_item(s, title, due_date, category="general", source="system",
                           linked_session_id=None, participants=None, details=None):
    """ثبت موعد قطعی برای نشست‌ها و فرایندهای زمان‌دار آینده."""
    current = _calendar_parse_date(s.get("game_date", ""))
    due = _calendar_parse_date(due_date)
    if due < current:
        raise ValueError("موعد نمی‌تواند قبل از تاریخ فعلی بازی باشد.")
    if category not in ("meeting", "political", "economic", "trade", "diplomatic",
                        "military", "social", "project", "other", "general"):
        raise ValueError("دسته‌بندی موعد معتبر نیست.")
    safe_details = json.loads(json.dumps(details if isinstance(details, dict) else {}, ensure_ascii=False))
    if len(json.dumps(safe_details, ensure_ascii=False)) > 8000:
        raise ValueError("جزئیات رویداد تقویم بیش از حد مجاز است.")
    events = s.setdefault("calendar_events", [])
    if linked_session_id:
        for event in events:
            if isinstance(event, dict) and event.get("linked_session_id") == linked_session_id and event.get("status") != "cancelled":
                return event
    seq = int(s.get("calendar_sequence", 0)) + 1
    s["calendar_sequence"] = seq
    item = {"id":"CAL-%06d" % seq, "title":str(title or "رویداد زمان‌بندی‌شده")[:140],
            "category":category, "source":str(source or "system")[:40],
            "due_date":due.isoformat(), "created_date":current.isoformat(),
            "status":"due" if due == current else "scheduled",
            "days_remaining":max(0, (due - current).days),
            "linked_session_id":linked_session_id, "participants":list(participants or []),
            "details":safe_details}
    events.append(item)
    if len(events) > 500:
        del events[:-500]
    return item


def _refresh_calendar(s):
    current = _calendar_parse_date(s.get("game_date", ""))
    for event in s.get("calendar_events") or []:
        if not isinstance(event, dict) or event.get("status") == "cancelled":
            continue
        try:
            due = _calendar_parse_date(event.get("due_date"))
        except ValueError:
            event["status"] = "invalid"
            continue
        event["status"] = "due" if due <= current else "scheduled"
        event["days_remaining"] = max(0, (due - current).days)
        linked = get_conversation_session(s, event.get("linked_session_id")) if event.get("linked_session_id") else None
        if linked:
            linked["meeting_status"] = "due" if due <= current else "confirmed"
            linked["chat_enabled"] = bool(s.get("live_ai_active") and due <= current)
            linked["live_ai_status"] = "ready" if linked["chat_enabled"] else "locked_until_phase_f"


def decide_conversation_meeting(s, conversation_id, decision, actor_country=None):
    """تصمیم طرف مقابل روی پیشنهاد نشست؛ تصمیم AI فقط از فاز F فراخوانی می‌شود."""
    if decision not in ("accept", "reject"):
        raise ValueError("تصمیم نشست نامعتبر است.")
    session = get_conversation_session(s, conversation_id)
    if not session:
        raise ValueError("نشست موردنظر پیدا نشد.")
    player = s.get("player")
    actor = actor_country or player
    status = session.get("meeting_status")
    if status == "pending_ai_acceptance":
        if not s.get("live_ai_active") or actor == player or actor not in (session.get("participants") or []):
            raise ValueError("پاسخ کشور مقابل فقط از مسیر هوش مصنوعی زنده در فاز F مجاز است.")
    elif status == "pending_player_acceptance":
        if actor != player:
            raise ValueError("فقط بازیکن می‌تواند دعوت نشست دریافتی را پاسخ دهد.")
    else:
        raise ValueError("این پیشنهاد نشست دیگر در انتظار پاسخ نیست.")
    if decision == "reject":
        session["meeting_status"] = "rejected"
        session["updated_date"] = s.get("game_date", "")
        msg(s, "پیشنهاد نشست %s رد شد." % session.get("id"))
        return dict(ok=True, session=session, calendar_event=None)
    accepted = session.setdefault("meeting_accepted_by", [])
    if actor not in accepted:
        accepted.append(actor)
    required_parties = set(session.get("participants") or [])
    if set(accepted) != required_parties:
        if session.get("meeting_proposed_by") == player:
            session["meeting_status"] = "pending_ai_acceptance"
        else:
            session["meeting_status"] = "pending_player_acceptance" if player not in accepted else "pending_ai_acceptance"
        session["updated_date"] = s.get("game_date", "")
        return dict(ok=True, confirmed=False, session=session, calendar_event=None,
                    note="پاسخ ثبت شد؛ تا تأیید همه کشورهای شرکت‌کننده، موعد به تقویم قطعی اضافه نمی‌شود.")
    session["meeting_status"] = "confirmed"
    event = register_calendar_item(
        s, "نشست: " + str(session.get("topic") or "گفت‌وگوی دیپلماتیک"),
        session.get("meeting_date"), category="meeting", source="conversation",
        linked_session_id=session.get("id"), participants=session.get("participants"),
        details={"visibility_mode":session.get("visibility_mode"),"negotiation_type":session.get("negotiation_type")})
    session["calendar_event_id"] = event.get("id")
    session["updated_date"] = s.get("game_date", "")
    session["chat_enabled"] = False
    session["live_ai_status"] = "locked_until_phase_f"
    msg(s, "نشست %s برای تاریخ %s در تقویم قطعی شد." % (session.get("id"), session.get("meeting_date")))
    return dict(ok=True, confirmed=True, session=session, calendar_event=event)


def register_ai_meeting_proposal(s, initiator_country, participants, meeting_date,
                                 topic="نشست دیپلماتیک", visibility_mode="public",
                                 negotiation_type="standard", source="inbox", context=None):
    """قرارداد درخواست نشست از سوی کشور AI؛ فقط در فاز F مجاز است."""
    if not s.get("live_ai_active"):
        raise ValueError("کشورهای هوش مصنوعی تا فعال‌سازی فاز F نمی‌توانند نشست پیشنهاد دهند.")
    if initiator_country == s.get("player") or initiator_country not in (s.get("world") or {}):
        raise ValueError("کشور آغازگر نشست معتبر نیست.")
    if not isinstance(participants, list) or s.get("player") not in participants or initiator_country not in participants:
        raise ValueError("درخواست نشست باید شامل بازیکن و کشور آغازگر باشد.")
    prepared = prepare_conversation_session(s, participants, topic=topic, visibility_mode=visibility_mode,
        negotiation_type=negotiation_type, source=source, context=context, meeting_date=meeting_date)
    session = prepared["session"]
    session["initiator"] = initiator_country
    session["meeting_status"] = "pending_player_acceptance"
    session["meeting_initiator"] = initiator_country
    session["meeting_proposed_by"] = initiator_country
    session["meeting_accepted_by"] = [initiator_country]
    session["meeting_request_id"] = "MR-" + session["id"]
    register_inbox_message(s, initiator_country, message_type="meeting_request",
        title="پیشنهاد نشست دیپلماتیک",
        body="کشور %s درخواست نشست در تاریخ %s را دارد." % (initiator_country, session["meeting_date"]),
        conversation_id=session["id"], response_allowed=True,
        metadata={"meeting_date":session["meeting_date"],"meeting_request":True})
    return dict(ok=True, session=session, note="درخواست نشست کشور هوش مصنوعی برای تصمیم بازیکن ثبت شد.")


def get_conversation_session(s, conversation_id):
    for session in s.get("conversation_sessions") or []:
        if isinstance(session, dict) and session.get("id") == conversation_id:
            return session
    return None


def save(s):
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, STATE)

def bar(v, width=10):
    filled = max(0, min(width, int(round(v / 100 * width))))
    return "█" * filled + "░" * (width - filled)

def power(c):
    base = c["mil"] * (1 + c["tech"] / 200) * (1.1 if c["nukes"] else 1.0) * (0.8 if c["stab"] < 40 else 1.0)
    base += arsenal_bonus(c, c.get("_arsenal") or {})
    return base

def dominance(c, allies_count, influence):
    return c["mil"] * 0.25 + c["eco"] * 0.25 + c["tech"] * 0.15 + influence * 0.5 + c["nukes"] * 3 + allies_count * 6

def log_take(s, n=4):
    msgs = s.get("log", [])
    out = msgs[-n:]
    s["log"] = msgs
    return out

def msg(s, text):
    s.setdefault("log", []).append(text)

def find_name(s, query):
    query = query.strip()
    for name in s["world"]:
        if query == name or name.startswith(query) or query.startswith(name[:3]):
            return name
    return None

def rel_key(a, b):
    return "|".join(sorted((a, b)))

def get_rel(s, a, b):
    return s["relations"][rel_key(a, b)]

def set_rel(s, a, b, val):
    s["relations"][rel_key(a, b)] = max(-100, min(100, val))

def add_rel(s, a, b, delta):
    set_rel(s, a, b, get_rel(s, a, b) + delta)


# ---------- اقدامات مستقیم دیپلماتیک بازیکن ----------
DIPLOMACY_ACTIONS = ("improve_relations", "reduce_relations",
                     "declare_war", "unilateral_ceasefire")


def apply_diplomacy_action(s, action, targets):
    """اجرای اقدام دیپلماتیک بازیکن؛ بدون پاسخ ساختگی از سوی AI."""
    if action not in DIPLOMACY_ACTIONS:
        raise ValueError("نوع اقدام دیپلماتیک نامعتبر است.")
    if s.get("over"):
        raise ValueError("بازی پایان یافته است.")
    if not isinstance(targets, list):
        raise ValueError("فهرست کشورها نامعتبر است.")
    player = s.get("player")
    world = s.get("world") or {}
    cleaned = []
    for raw in targets:
        name = str(raw).strip()
        if name not in world:
            raise ValueError("کشور نامعتبر است: " + name)
        if name == player:
            raise ValueError("کشور بازیکن را نمی‌توان هدف اقدام دیپلماتیک قرار داد.")
        if name in s.get("eliminated", []):
            raise ValueError("کشور حذف‌شده قابل انتخاب نیست: " + name)
        if name not in cleaned:
            cleaned.append(name)
    if not cleaned or len(cleaned) > 20:
        raise ValueError("باید بین ۱ تا ۲۰ کشور یکتا انتخاب شود.")

    wars = s.setdefault("at_war", [])
    history = s.setdefault("diplomatic_history", [])
    today = str(s.get("game_date") or "")
    results = []
    for target in cleaned:
        pair_exists = any(
            wars[i] == player and wars[i + 1] == target or
            wars[i] == target and wars[i + 1] == player
            for i in range(0, len(wars) - 1, 2)
        )
        before = round(float(get_rel(s, player, target)), 1)
        if action == "improve_relations":
            if pair_exists:
                results.append({"country": target, "ok": False,
                                "reason": "در وضعیت جنگ، بهبود مستقیم روابط مجاز نیست.",
                                "relation_before": before, "relation_after": before})
                continue
            add_rel(s, player, target, 10)
            after = round(float(get_rel(s, player, target)), 1)
            detail = "روابط دو کشور بهبود یافت."
        elif action == "reduce_relations":
            add_rel(s, player, target, -10)
            after = round(float(get_rel(s, player, target)), 1)
            detail = "روابط دو کشور کاهش یافت."
        elif action == "declare_war":
            if pair_exists:
                results.append({"country": target, "ok": False,
                                "reason": "جنگ با این کشور از قبل برقرار است.",
                                "relation_before": before, "relation_after": before})
                continue
            if target in s.get("allies", []):
                results.append({"country": target, "ok": False,
                                "reason": "ابتدا باید وضعیت اتحاد با این کشور تعیین تکلیف شود.",
                                "relation_before": before, "relation_after": before})
                continue
            wars.extend([player, target])
            add_rel(s, player, target, -30)
            after = round(float(get_rel(s, player, target)), 1)
            detail = "اعلام جنگ ثبت شد؛ این اقدام به‌تنهایی نبرد یا نتیجه نظامی را شبیه‌سازی نمی‌کند."
        else:
            if not pair_exists:
                results.append({"country": target, "ok": False,
                                "reason": "با این کشور جنگ فعالی وجود ندارد.",
                                "relation_before": before, "relation_after": before})
                continue
            remaining = []
            for i in range(0, len(wars) - 1, 2):
                x, y = wars[i], wars[i + 1]
                if not ((x == player and y == target) or
                        (x == target and y == player)):
                    remaining.extend([x, y])
            wars[:] = remaining
            add_rel(s, player, target, 10)
            after = round(float(get_rel(s, player, target)), 1)
            detail = "آتش‌بس یک‌جانبه ثبت شد؛ وضعیت جنگ با این کشور پایان یافت."

        record = {
            "date": today, "action": action, "actor": player,
            "country": target, "status": "applied",
            "relation_before": before, "relation_after": after,
            "detail": detail
        }
        history.append(record)
        msg(s, "دیپلماسی: %s — %s" % (target, detail))
        results.append({"country": target, "ok": True,
                        "relation_before": before, "relation_after": after,
                        "detail": detail})
    del history[:-300]
    return {"ok": True, "action": action, "results": results,
            "success_count": sum(1 for x in results if x.get("ok")),
            "failed_count": sum(1 for x in results if not x.get("ok"))}

# ---------- بیانیه‌های هوش مصنوعی کشورها ----------
STMTS = {
    "generic": {
        "friend": ["روابط ما با {P} پایدار و رو به رشد است.", "{P} شریک معتبر ما در منطقه است."],
        "neutral": ["به منافع ملی خود پایبندیم و مسیر مستقل داریم.", "به تحولات منطقه با دقت نگاه می‌کنیم."],
        "hostile": ["سیاست‌های {P} escalation است و مسئولیت پیامدها با او خواهد بود.", "ما صبوریم اما حوصله‌مان حد دارد؛ {P} بداند."],
    },
    "daily": {
        "friend": ["امروز روز تازه‌ای است؛ آماده تعمیق همکاری با {P} هستیم.", "پروژه‌های مشترک با {P} را گسترش می‌دهیم."],
        "neutral": ["دیپلماسی فعال، راه جنگ نیست؛ سازندگی را ادامه می‌دهیم.", "به توصیه‌های {P} توجه می‌کنیم؛ اما منافع ملی اول است."],
        "hostile": ["به {P} هشدار می‌دهیم: ادامه مسیر کنونی به نفع هیچ‌کس نیست.", "دستی پنهان {P} را در منطقه می‌بینیم؛ حواستان باشد!", "زبان قدرت را نمی‌پذیریم؛ {P} باید بداند."],
    },
    "war_d": {
        "friend": ["در کنار {P} می‌ایستیم.", "از دفاع مشروع {P} حمایت می‌کنیم."],
        "neutral": ["جنگ کسی را به جایی نمی‌رساند؛ میز مذاکره را جدی بگیرید.", "برای آتش‌بس فوری میان طرفین تلاش می‌کنیم."],
        "hostile": ["در برابر حمله {P} تا آخرین نفس می‌جنگیم.", "جنگی که {P} آغاز کرد روزی تمام می‌شود؛ آن روز حساب تمام است."],
    },
    "nuke": {
        "friend": ["امنیت ملی حق همه است است؛ فشار بر {P} را نمی‌پذیریم."],
        "neutral": ["آزمایش هسته‌ای {P} نگران‌کننده است؛ خواستار خویشتن‌داری هستیم.", "آژانس انرژی اتمی باید فوراً پرونده {P} را بررسی کند."],
        "hostile": ["آزمایش هسته‌ای {P} تهدید مستقیم صلح جهانی است؛ واکنش ما قاطع خواهد بود.", "ما همه گزینه‌ها را برای پاسخ به {P} روی میز نگه می‌داریم."],
    },
    "sanc": {
        "friend": ["تحریم علیه {P} ظالمانه است؛ ما اجرای آن را نپذیرفته‌ایم."],
        "neutral": ["تحریم اثر مورد نظر را نخواهد داشت؛ دیپلماسی را ادامه می‌دهیم."],
        "hostile": ["در برابر فشار اقتصادی {P} می‌ایستیم و خودمان را می‌سازیم.", "تحریمِ {P} پاسخ سنگینی خواهد داشت."],
    },
    "war": {
        "friend": ["امنیت {T} امنیت ماست؛ در کنار {T} می‌مانیم."],
        "neutral": ["برای پایان‌دادن به جنگ میان {P} و {T} میانجی‌گری می‌کنیم."],
        "hostile": ["حمله {P} به {T} آغاز فاجعه است؛ بهای سنگینی خواهد پرداخت.", "تمام قدرت دفاعی خود را برای پاسخ به {P} به کار می‌گیریم."],
    },
    "ally": {
        "friend": ["اتحاد با {P} تضمین‌کننده امنیت مشترک است.", "این اتحاد آغاز عصر تازه‌ای از روابط ما با {P} است."],
        "neutral": ["توازن قدرت منطقه را تغییر می‌دهد؛ مراقب هستیم."],
        "hostile": ["اتحاد {P} را تهیدی برای منطقه می‌دانیم؛ پاسخ خواهیم داد."],
    },
    "pact": {
        "friend": ["پیمان عدم تعارض با {P} گام اول اعتمادسازی است."],
        "neutral": ["پیمان عدم تعارض میان ما نشانه ثبات است؛ از آن استقبال می‌کنیم."],
        "hostile": ["امضای پیمان با {P} پوششی برای نیات دیگر است؛ حواستان باشد."],
    },
    "break": {
        "friend": ["متأسفیم؛ رای راه گفت‌وگو با {P} با {P} هنوز باز است."],
        "neutral": ["پایان پیمان میان ما تغییر معادلات است؛ دیپلماسی ادامه دارد."],
        "hostile": ["این فسخ پرده از ماهیت رفتار {P} برداشت؛ دیگر اعتمادی نیست."],
    },
    "aide": {
        "friend": ["کمک اقتصادی {P} نشانه حسن همسایگی است؛ قدردانیم."],
        "neutral": ["کمک اقتصادی به صلح و توسعه کمک می‌کند؛ سپاس از {P}."],
        "hostile": ["کمک {P} به درد ملت ما نمی‌خورد؛ خارج شو دوست!"],
    },
    "trade": {
        "friend": ["روابط اقتصادی با {P} وارد فصل طلایی شده است."],
        "neutral": ["تجارت آزاد پیوند ملت‌ها است؛ قرارداد با {P} گشایی کرد."],
        "hostile": ["قرارداد {P} را راه نفوذ سیاسی می‌دانیم و مراقب خواهیم بود."],
    },
    "buy": {
        "friend": ["تقویت دفاع {P} ادعای تجاوزی ندارد؛ طبیعی است."],
        "neutral": ["تجهیزات {P} را زیر نظر داریم؛ توازن مهم است."],
        "hostile": ["جمع‌آوری زرادخانه {P} را با نگرانی شدید اجرا می‌کنیم؛ منطقه را به آتش نمی‌کشیم."],
    },
    "sell": {
        "friend": ["تسلیحات به‌دست‌آمده از {P} آماده تجهیز نیروهای ما است."],
        "neutral": ["معامله تسلیحاتی با {P} مصالح ماست؛ ارزیابی می‌کنیم."],
        "hostile": ["پول {P} برای تجهیز ما خرج خودش خواهد شد!"],
    },
    "iaea": {
        "friend": ["شفافیت {P} الگوئی خوبی برای منطقه است."],
        "neutral": ["شفافیت ارائه‌شده {P} example؛ برنامه باید صلح‌آمیز باشد."],
        "hostile": ["پرونده هسته‌ای {P} باید بماند تا همه بدانند ما متعهد به پیمان‌نامه‌های جهانی‌ایم."],
    },
    "spy": {
        "friend": ["رابطه ویژه با {P} را حفظ می‌کنیم."],
        "neutral": ["دستگاه‌های امنیتی ما همیشه فعال‌اند."],
        "hostile": ["جاسوسی {P} را کتمان نکنیم؛ دستگاه‌های ما امور را کشف می‌کنند!"],
    },
    "covert": {
        "friend": ["تلاش برای ثبات، مسیر سازنده‌ای است."],
        "neutral": ["دستگاه‌های امنیتی ما همیشه فعال‌اند."],
        "hostile": ["دست‌های پنهان {P} را می‌بینیم؛ پاسخ داده خواهد شد."],
    },
    "sabotage": {
        "friend": ["تراژدی تاسف‌آور است؛ متأسفیم."],
        "neutral": ["حادثه را پیگیری می‌کنیم و از عناصر مسئول نزد {P} می‌پرسیم."],
        "hostile": ["خرابکاری {P} اعلام جنگ پنهان است؛ می‌بایست پاسخ سنگینی خواهد داد!"],
    },
    "kill": {
        "friend": ["چنین عملی محکوم است؛ هر کسی انجام داده باشد."],
        "neutral": ["ترورِ رهبری امری جنایت‌کارانه است و مجامع جهانی باید پاسخگو باشند {P} را."],
        "hostile": ["پاسخ به جنایت {P} محتوم است؛ بهای سنگینی خواهد پرداخت."],
    },
    "proxy": {
        "friend": ["روابط ما با {P} شفاف است؛ از این مطلب اطلاع نداریم."],
        "neutral": ["درباره شبکه‌های نیابتی درباره این گفته‌ها سکوت نمی‌کنیم؛ پیگیری می‌کنیم."],
        "hostile": ["شبکه نیابتی {P} را کشف کرده‌ایم؛ پایگاه‌های خودمان را تعقیب می‌کنیم!"],
    },
    "propaganda": {
        "friend": ["صدای {P} را می‌شنویم و با آن همراه می‌شویم."],
        "neutral": ["کمپین رسانه‌ای {P} را رصد می‌کنیم."],
        "hostile": ["دروغ‌سازی {P} حتی یک لحظه هم دیر نمی‌پذیرد؛ بیهوده است!"],
    },
    "eco": {
        "friend": ["رشد اقتصادی {P} به نفع ما هم است."],
        "neutral": ["اقتصاد {P} را راه‌اندازی‌های تازه باید نتیجه بگیرد."],
        "hostile": ["اقتصاد {P} روی حمایت‌های ما، روی میز مذاکره است."],
    },
    "mil": {
        "friend": ["تقویت دفاع ما به معنای تهدید نیست."],
        "neutral": ["حرکات نظامی {P} را زیر نظر داریم."],
        "hostile": ["امضای نظامی {P} را معلا می‌کنیم و ما هم آماده‌ایم."],
    },
    "tech": {
        "friend": ["پیشرفت علمی ارزش جهانی دارد؛ آفرین به {P}."],
        "neutral": ["ما نیز در فناوری رقیب تازه‌ای هستیم."],
        "hostile": ["جهش فناوری {P} نشانه نیت بد خواهد بود؛ پیگیری می‌کنیم."],
    },
    "un": {
        "friend": ["تصمیم مجمع ملل درباره {T} را تایید می‌کنیم."],
        "neutral": ["سازمان ملل باید مستقل بماند؛ می‌پذیریم."],
        "hostile": ["پشت طرح محکومیت {T}، سیاست‌های {P} را می‌بینیم."],
    },
    "exit_iaea": {
        "friend": ["تصمیم مقاومانه‌ی {P} را می‌فهمیم و در کنارش می‌ایستیم."],
        "neutral": ["خروج {P} از آژانس نگران‌کننده است؛ دیپلماسی را احیا کنید."],
        "hostile": ["خروج {P} از آژانس نشانه‌ی گرایش به مرز سلاح هسته‌ای است؛ دور جدید تحریم در راه است."],
    },
    "freeze": {
        "friend": ["تعلیق غنی‌سازی {P} گام درست است؛ مسیر مذاکرات باز می‌شود."],
        "neutral": ["تعلیق غنی‌سازی از سوی {P} گام سازنده‌ای برای آرامش منطقه است."],
        "hostile": ["تعلیق کافی نیست؛ بازرسی‌های بدون قید و شرط باید آغاز شود."],
    },
    "resume": {
        "friend": ["حق فناوری صلح‌آمیز برای {P} حفظ خواهد شد و ما از آن حمایت می‌کنیم."],
        "neutral": ["ادامه‌ی غنی‌سازی {P} نگرانی جامعه‌ی جهانی را بالا می‌برد."],
        "hostile": ["ادامه‌ی غنی‌سازی {P} تهدید تلقی می‌شود؛ دور تازه‌ی تحریم‌ها در راه است."],
    },
    "neutrality": {
        "friend": ["بی‌طرفی {P} به پایداری منطقه کمک می‌کند و آن را خوش‌آمدگوییم."],
        "neutral": ["اعلام بی‌طرفی {P} گام معقولی برای حفاظت از صلح است."],
        "hostile": ["بی‌طرفی {P} صرفا توهم است؛ تجربه حرف ما را می‌گوید."],
    },
    "neg_ok": {
        "friend": ["مذاکره با {P} پربار بود؛ همسو و هم‌پیمان می‌مانیم."],
        "neutral": ["مذاکره صلح‌آمیزی داشتیم و توافق‌نامه امضا شد."],
        "hostile": ["مذاکره پربار بود، اما صلح نیازمند رفتار متقابل است."],
    },
    "neg_ref": {
        "friend": ["تلاش کردیم؛ اما شرایط فعلی را نمی‌پذیریم."],
        "neutral": ["شرایط پیشنهادی {P} منصفانه نیست؛ مذاکره متوقف می‌ماند."],
        "hostile": ["مذاکره با {P} پشتوانه‌ای ندارد؛ پاسخ روشنی به آن می‌دهیم."],
    },
    "neg_leak": {
        "friend": ["شایعاتی درباره مذاکرات محرمانه {P} در رسانه‌ها پیچیده؛ بی‌اهمیت است."],
        "neutral": ["فاش شدن مذاکرات محرمانه {P} شکاف اعتماد ایجاد کرده است."],
        "hostile": ["فاش شدن مذاکرات محرمانه {P} رسوایی‌آمیز است؛ پیگرد دیپلماتیک خواهد بود."],
    },
}


def _tone(s, a, b):
    rel = get_rel(s, a, b)
    if rel >= 40:
        return "friend"
    if rel <= -30:
        return "hostile"
    return "neutral"


def ai_statement(s, speaker, topic, about=None):
    if speaker == s["player"] or speaker in s.get("eliminated", []):
        return
    tone = _tone(s, speaker, s["player"])
    pool = STMTS.get(topic, STMTS["generic"])
    variants = pool.get(tone) or pool["neutral"]
    text = random.choice(variants).format(P=s["player"], me=speaker, T=about if about is not None else s["player"])
    msg(s, "🗣 " + speaker + " (" + leader(speaker) + "): " + text)
    st = s.setdefault("statements", [])
    st.append({"who": speaker, "lead": leader(speaker), "text": text, "topic": topic})
    s["statements"] = st[-80:]


def ai_react(s, topic, about=None, n=None):
    W = s["world"]; P = s["player"]
    cands = [n for n in W if n != P and n not in s.get("eliminated", [])]
    if not cands:
        return
    if n is None:
        n = random.choice((0, 1, 1, 1, 2))
    n = min(n, len(cands))
    if n <= 0:
        return
    chosen = random.sample(cands, n)
    if about and about in cands and about not in chosen:
        chosen[n - 1] = about
    for x in chosen:
        ai_statement(s, x, topic, about or None)


# ---------- سران واقعی دولت‌ها (مبنای رسمی ۲۰۲۵) ----------
LEADERS = {
    "سودان": "عبدالفتاح البرهان",
    "سودان جنوبی": "سالوا کیر میاردیت",
    "ایران": "آیت‌الله سید مجتبی خامنه‌ای",
    "آمریکا": "دونالد ترامپ",
    "روسیه": "ولادیمیر پوتین",
    "چین": "شی جین‌پینگ",
    "بریتانیا": "کیر استارمر",
    "فرانسه": "امانوئل مکرون",
    "آلمان": "فریدریش مرتس",
    "اسرائیل": "بنیامین نتانیاهو",
    "ترکیه": "رجب طیب اردوغان",
    "عربستان": "ملک سلمان بن عبدالعزیز",
    "امارات": "محمد بن زاید آل نهیان",
    "قطر": "امیر تمیم بن حمد آل ثانی",
    "مصر": "عبدالفتاح السیسی",
    "عراق": "محمد شیاع السودانی",
    "سوریه": "احمد الشرع",
    "لبنان": "جوزف عون",
    "فلسطین": "محمود عباس",
    "یمن": "رشاد محمد العلیمی",
    "اردن": "ملک عبدالله دوم",
    "بحرین": "ملک حمد بن عیسی آل خلیفه",
    "کویت": "امیر مشعل احمد الصباح",
    "عمان": "سلطان هیثم بن طارق",
    "هند": "نارندرا مودی",
    "پاکستان": "شهباز شریف",
    "ژاپن": "شیگرو ایشیبا",
    "کره جنوبی": "لی جه میونگ",
    "کره شمالی": "کیم جونگ اون",
    "تایوان": "لای چینگ‌ده",
    "استرالیا": "انتونی آلبانیزی",
    "نیوزیلند": "کریستوفر لاکسون",
    "کانادا": "مارک کرنی",
    "برزیل": "لولا داسیلوا",
    "آرژانتین": "خاویر میلی",
    "مکزیک": "کلودیا شینبوم",
    "ونزوئلا": "دلسی رودریگز",
    "کلمبیا": "ابیلاردو د لا اسپریلا",
    "شیلی": "خوزه آنتونیو کاست",
    "پرو": "کیکو فوجیموری",
    "السالوادور": "نجیب بوکله",
    "اکوادور": "دانیل نوبوآ",
    "بولیوی": "رودریگو پاز",
    "پاراگوئه": "سانتیاگو پنیا",
    "اوروگوئه": "یاماندو اورسی",
    "پاناما": "خوزه رائول مولینو",
    "کاستاریکا": "لائورا فرناندز دلگادو",
    "گواتمالا": "برناردو آروو",
    "هندوراس": "نصری خوان عصفوره",
    "نیکاراگوئه": "دانیل اورتگا و روزاریو موریو (هم‌رئیسان)",
    "دومینیکان": "لوئیس آبینادر",
    "جامائیکا": "اندرو هولنس",
    "هائیتی": "آلیکس دیدیه فیس-ایمه",
    "باربادوس": "میا موتلی",
    "باهاماس": "فیلیپ دیویس",
    "بلیز": "جانی بریسیگنیو",
    "ترینیداد و توباگو": "کاملا پرساد-بیسسار",
    "ایتالیا": "جورجیا ملونی",
    "اسپانیا": "پدرو سانچز",
    "پرتغال": "لوئیس مونته‌نگرو",
    "هلند": "دیک شوف",
    "بلژیک": "بارت دی واور",
    "لوکزامبورگ": "لوک فریدن",
    "سوئیس": "کارین کلر-سوتر",
    "اتریش": "کریستین اشتوکر",
    "سوئد": "اولف کریسترسون",
    "نروژ": "یوناس گار استوره",
    "دانمارک": "مت فردریکسن",
    "فنلاند": "پتریه اورپو",
    "ایسلند": "کریسترون فراستادوتیر",
    "ایرلند": "میخائل مارتین",
    "لهستان": "دونالد تاسک",
    "چک": "پیتر فیالا",
    "اسلواکی": "رابرت فیتسو",
    "مجارستان": "ویکتور اوربان",
    "رومانی": "نیکوشور دن",
    "بلغارستان": "روسن ژلیازکو",
    "یونان": "کیریاکوس میتسوتاکیس",
    "قبرس": "نیکوس کریستودولیدس",
    "کرواسی": "آندره پلنکویچ",
    "صربستان": "الکساندر ووچیچ",
    "بوسنی": "دنیس بچیروویچ",
    "اسلوونی": "رابرت گولوب",
    "آلبانی": "ادی راما",
    "مقدونیه شمالی": "هریستیان میتسکوسکی",
    "مونته‌نگرو": "میلویکا اسپایچ",
    "اوکراین": "ولودیمیر زلنسکی",
    "بلاروس": "الکساندر لوکاشنکو",
    "لتونی": "آندریس کولبرگس",
    "لیتوانی": "مینداگاس سینکویچیوس",
    "استونی": "کریستن میخال",
    "مالت": "رابرت آبلا",
    "مولداوی": "مایا ساندو",
    "گرجستان": "ایراکلی کوباخیدزه",
    "ارمنستان": "نیکول پاشینیان",
    "آذربایجان": "الهام علی‌یف",
    "قزاقستان": "قسم‌جومرت توکایف",
    "ازبکستان": "شوکت میرزیائیف",
    "ترکمنستان": "سردار بردی‌محمداف",
    "قرقزیستان": "صادر جاپاروف",
    "تاجیکستان": "امام‌علی رحمان",
    "افغانستان": "محمد حسن آخند (نخست‌وزیر)",
    "بنگلادش": "طارق رحمان",
    "سری‌لانکا": "آنورا کومارا دیسانایاکه",
    "نپال": "بالندرا شاه",
    "بوتان": "تشرینگ توبگای",
    "مالدیو": "محمد معیزو",
    "میانمار": "مین آنگ هلاینگ",
    "تایلند": "آنوتین چارنویراکول",
    "ویتنام": "تو لام",
    "لائوس": "تونگلون سیسولیت",
    "کامبوج": "هون مانه",
    "مالزی": "انور ابراهیم",
    "سنگاپور": "لارنس وانگ",
    "اندونزی": "پرابوو سوبیانتو",
    "فیلیپین": "فردیناند مارکوس جونیور",
    "برونئی": "سلطان حسنال بولکیاه",
    "پاپوآ گینه نو": "جیمز ماراپی",
    "فیجی": "سیتیونی رابوکا",
    "وانواتو": "جوتام ناپات",
    "جزایر سلیمان": "متیو وِیل",
    "ساموا": "لااولی لوئاتئا اشمیت",
    "تونگا": "لرد فاتافیهی فاکافانوا (نخست‌وزیر)",
    "تیمور شرقی": "خوزه راموس-هورتا",
    "مغولستان": "سانداگین بامباتسوگت (سرپرست ریاست‌جمهوری)",
    "مراکش": "پادشاه محمد ششم",
    "الجزایر": "عبدالمجید تبون",
    "تونس": "قیس سعید",
    "لیبی": "محمد یونس المنفی",
    "سودان": "عبدالفتاح البرهان",
    "سودان جنوبی": "سالوا کیر",
    "اتیوپی": "ابی احمد",
    "اریتره": "ایسایاس آفورکی",
    "جیبوتی": "اسماعیل عمر گله",
    "سومالی": "حسن شیخ محمود",
    "کنیا": "ویلیام روتو",
    "اوگاندا": "یووری موسه‌ونی",
    "تانزانیا": "سامیا سولوهو حسن",
    "رواندا": "پل کاگامه",
    "بوروندی": "اوارسته نداییشیمی",
    "کنگو دموکراتیک": "فلیکس تشسکی‌دی",
    "کنگو": "دنیس ساسو نگسو",
    "گابن": "بریس اویگی نگما",
    "گینه استوایی": "تئودورو اوبیانگ نگما",
    "کامرون": "پل بیا",
    "چاد": "محمد ادریس دبی",
    "نیجر": "عبدورحمانی تیانی",
    "مالی": "اسیمی گویتا",
    "بورکینافاسو": "ابراهیم ترائوره",
    "سنگال": "باسیر دیومایه",
    "گامبیا": "آداما برو",
    "گینه": "مامادی دونبویا",
    "گینه بیسائو": "ژنرال هورتا اینتا-آ نا مان",
    "سیرالئون": "جولیوس ماادا بیو",
    "لیبریا": "جوزف بوآکای",
    "ساحل عاج": "آلاسان واتارا",
    "غنا": "جان ماهاما",
    "توگو": "فور گنینگبه",
    "بنین": "روموالد وادانی",
    "نیجریه": "بولا تینوبو",
    "موریتانی": "محمد ولد الغزوانی",
    "زیمبابوه": "امرسون منگانگوا",
    "زامبیا": "هاکیند هیشیلیما",
    "موزامبیک": "دانیل چاپو",
    "ماداگاسکار": "میکائل راندریانیرینا",
    "موریس": "ناوین رامگولام",
    "کیپ‌ورد": "خوزه ماریا بورته",
    "لسوتو": "سام متاکانه",
    "اسواتینی": "پادشاه مسواتی سوم",
    "آنگولا": "ژائو لورنسو",
    "نامیبیا": "نتومبو نندی-ندایتح",
    "بوتسوانا": "دوکوما بوکو",
    "آفریقای جنوبی": "سیریل رامافوزا",
    "آفریقای مرکزی": "فوستن توادرا",
    "کوبا": "میگل دیاز-کانل",
    "سورینام": "جنیفر گرلینگ-سیمونز",
    "گویان": "ایروین علی",
}


def leader(name):
    return LEADERS.get(name, "رهبر " + name)


# ---------- شبکه‌های نیابتی واقعی دنیا ----------
PROXY_REAL = {
    ("ایران", "لبنان"): "حزب‌الله لبنان",
    ("ایران", "فلسطین"): "حماس",
    ("ایران", "یمن"): "انصارالله (حوثی‌ها)",
    ("ایران", "عراق"): "کتائب حزب‌الله",
    ("ایران", "سوریه"): "جبهه مقاومت جهانی",
    ("روسیه", "سوریه"): "گروه واگنر",
    ("روسیه", "مالی"): "گروه آفریقا",
    ("ترکیه", "سوریه"): "ارتش ملی سوریه",
    ("آمریکا", "سوریه"): "نیروهای دموکراتیک سوریه",
    ("عربستان", "یمن"): "اعزامی ائتلاف",
}


def proxy_label(sponsor, host):
    p = PROXY_REAL.get((sponsor, host))
    if p is None and sponsor == "ایران":
        p = "جبهه مقاومت جهانی در " + host
    if p is None:
        p = "شبکه نیابتی " + sponsor + " در " + host
    return p


# ---------- مذاکرات (علنی و محرمانه) ----------
NEG_KINDS = {
    "ally": ("اتحاد نظامی", 3),
    "pact": ("پیمان عدم تعارض", 2),
    "calm": ("کاهش تنش", 2),
    "fund": ("درخواست کمک مالی صندوق", 0),
    "arms": ("خرید فوری تسلیحات", 15),
    "ceasefire": ("آتش‌بس و پایان جنگ", 0),
    "bribe": ("تطمیع رهبر کشور", 8),
}
NEG_SECRET_LIKE = {"bribe"}


def negotiate(s, kind, target, secret=False):
    if kind not in NEG_KINDS:
        print("✗ نوع مذاکره نامشخص. انواع: " + "، ".join(sorted(NEG_KINDS)))
        return
    label, cost = NEG_KINDS[kind]
    W = s["world"]; P = s["player"]; me = W[P]
    if target is None or target == P:
        print("✗ کشور مذاکره را انتخاب کن.")
        return
    if target in s.get("eliminated", []):
        print("✗ این کشور از نقشه حذف شده است.")
        return
    t = W[target]
    rel = get_rel(s, P, target)
    prob = 0.35
    if rel >= 60:
        prob += 0.35
    elif rel >= 30:
        prob += 0.2
    elif rel >= 0:
        prob += 0.08
    elif rel >= -30:
        prob -= 0.15
    else:
        prob -= 0.3
    if t["stab"] < 40:
        prob -= 0.1
    if kind == "ally" and t["stab"] >= 65:
        prob += 0.12
    if kind == "calm":
        prob += 0.15
    if kind == "bribe":
        prob = 0.55 + (0.2 if rel > 30 else 0)
    if kind == "ceasefire":
        wars = [s["at_war"][i:i + 2] for i in range(0, len(s["at_war"]) - 1, 2)]
        if not any(P in pr and target in pr for pr in wars):
            print("✗ با " + target + " در جنگ نیستی؛ آتش‌بس معنا ندارد.")
            return
        prob = 0.5 + (0.3 if rel > -20 else 0)
    secret = bool(secret) or kind in NEG_SECRET_LIKE
    tag = "🤫 محرمانه — " if secret else ""
    print(tag + "🤝 مذاکره با " + target + " (" + leader(target) + ") آغاز شد: پیشنهاد «" + label + "»")
    if cost:
        if me["money"] < cost:
            print(f"⚠ بودجه کافی نیست (نیاز: {cost} میلیارد — موجود: {me['money']:.0f})")
            return
        me["money"] -= cost
    ok = random.random() < prob
    if ok:
        if kind == "ally":
            if target in s["allies"]:
                me["money"] += cost
                print("⚠ این کشور از قبل متحد توست.")
                return
            s["allies"].append(target)
            if target in s["pacts"]:
                s["pacts"].remove(target)
            add_rel(s, P, target, 8)
            print("✔ اتحاد نظامی با " + target + " امضا شد! (" + leader(target) + " در کنار توست)")
        elif kind == "pact":
            if target not in s["pacts"] and target not in s["allies"]:
                s["pacts"].append(target)
            add_rel(s, P, target, 10)
            print("✔ پیمان عدم تعارض با " + target + " بسته شد.")
        elif kind == "calm":
            add_rel(s, P, target, 14)
            print("✔ تنش با " + target + " کاهش یافت (روابط +14).")
        elif kind == "fund":
            amount = max(8, min(40, int(t["eco"] / 2)))
            me["money"] += amount
            add_rel(s, P, target, 5)
            print(f"✔ {target} تو را وارد صندوق مشترک کرد: {amount} میلیارد دریافت شد.")
        elif kind == "arms":
            me["mil"] += 6
            add_rel(s, P, target, 5)
            print("✔ محموله تسلیحات فوری تحویل شد (نظامی +6).")
        elif kind == "ceasefire":
            wars2 = [s["at_war"][i:i + 2] for i in range(0, len(s["at_war"]) - 1, 2)]
            s["at_war"] = [x for pr in wars2 if set(pr) != {P, target} for x in pr]
            add_rel(s, P, target, 15)
            print("✔ آتش‌بس با " + target + " امضا شد و جنگ تمام شد!")
        elif kind == "bribe":
            add_rel(s, P, target, 18)
            print("✔ " + leader(target) + " تطمیع شد و موضعش نرم‌تر شد (روابط +18).")
        if secret:
            msg(s, tag + "توافقی محرمانه با " + target + " بسته شد.")
            if random.random() < 0.15:
                ai_statement(s, target, "neg_leak", P)
                add_rel(s, P, target, -8)
                me["stab"] = max(0, me["stab"] - 2)
                print("⚠ مذاکره محرمانه فاش شد! اعتبار تو آسیب دید (ثبات -2).")
        else:
            ai_statement(s, target, "neg_ok", P)
            ai_react(s, "neg_ok", target)
    else:
        add_rel(s, P, target, -5)
        if secret:
            msg(s, tag + "مذاکره محرمانه با " + target + " نتیجه نداد.")
            if random.random() < 0.25:
                ai_statement(s, target, "neg_leak", P)
                print("⚠ انتشار خبر رد مذاکره محرمانه، آبروی تو را برد (روابط با " + target + " -10).")
                add_rel(s, P, target, -10)
        else:
            ai_statement(s, target, "neg_ref", P)
            ai_react(s, "neg_ref", target)
    save(s)


# ---------- تصمیم‌های اعلامی رهبری (بیانیه + پیامدها) ----------
DECISIONS = {
    "exit_iaea": "خروج از آژانس بین‌المللی انرژی اتمی",
    "freeze": "تعلیق غنی‌سازی و بازگشت به مذاکرات",
    "resume": "ادامه غنی‌سازی بدون محدودیت",
    "neutrality": "اعلام بی‌طرفی دائمی",
}


def decide_label(kind):
    return DECISIONS.get(kind, kind)


def _bump(s, key, delta):
    s[key] = max(0, s.get(key, 0) + delta)


def _rel_many(s, P, names, delta):
    for n in names:
        if n != P:
            add_rel(s, P, n, delta)


def announce(s, kind):
    if kind not in DECISIONS:
        print("✗ تصمیم نامشخص. موارد: " + "، ".join(sorted(DECISIONS)))
        return
    W = s["world"]; P = s["player"]; me = W[P]
    label = DECISIONS[kind]
    msg(s, "📢 بیانیه رسمی رهبری " + P + " (" + leader(P) + "): " + label)
    st = s.setdefault("statements", [])
    st.append({"who": P, "lead": leader(P), "text": label, "topic": kind})
    s["statements"] = st[-80:]
    print("📢 بیانیه رسمی رهبری: «" + label + "»")
    west = [f for f in WEST if f != P]
    east = [f for f in ("روسیه", "چین") if f != P]
    if kind == "exit_iaea":
        s["iaea_out"] = True
        if P not in NUKES0:
            s["un_censures"] = s.get("un_censures", 0) + 1
            print("🚪 بازرسان اژانس اخراج شدند؛ قطعنامه محکومیت صادر شد.")
        _rel_many(s, P, west, -18)
        _rel_many(s, P, east, 4)
        me["stab"] = max(0, me["stab"] - 3)
        print("⚠ روابط با غرب تنش‌زیاد شد (-18).")
    elif kind == "freeze":
        s["iaea_out"] = False
        _bump(s, "iaea_heat", -1)
        _rel_many(s, P, west, 12)
        _rel_many(s, P, east, -6)
        me["stab"] = max(0, me["stab"] - 2)
        print("❄ غنی‌سازی تعلیق شد؛ اژانس راضی، جبهه داخلی ناراضی (ثبات -2).")
    elif kind == "resume":
        _bump(s, "iaea_heat", 1)
        _rel_many(s, P, west, -10)
        _rel_many(s, P, east, 5)
        me["stab"] = min(100, me["stab"] + 2)
        print("☢ غنی‌سازی بدون محدودیت ادامه می‌یابد؛ دور تازه تحریم‌ها در راه است.")
    elif kind == "neutrality":
        for a in list(s.get("allies", [])):
            s["allies"].remove(a); add_rel(s, P, a, -12)
        for p in list(s.get("pacts", [])):
            s["pacts"].remove(p)
        wars = [s["at_war"][i:i + 2] for i in range(0, len(s["at_war"]) - 1, 2)]
        s["at_war"] = [x for pr in wars if P not in pr for x in pr]
        _rel_many(s, P, west, 6)
        _rel_many(s, P, east, 6)
        me["stab"] = min(100, me["stab"] + 4)
        me["mil"] = max(10, me["mil"] - 4)
        print("🕊 بی‌طرفی اعلام شد: اتحادها فسخ، جنگ‌ها پایان، ارتش (-4)، ثبات +4.")
    ai_react(s, kind)
    save(s)



# ---------- قراردادهای پیمان و اتحاد؛ پذیرش کشورها فقط از مسیر تصمیم معتبر ----------
AGREEMENT_PACT_TYPES = {
    "non_aggression": "عدم تجاوز",
    "trade": "تجاری",
    "defense": "دفاعی",
    "cooperation": "همکاری",
    "transit": "ترانزیت",
    "economic": "اقتصادی",
    "other": "سایر"
}


def _agreement_validate_parties(s, parties):
    if not isinstance(parties, list):
        raise ValueError("فهرست کشورهای توافق نامعتبر است.")
    world = s.get("world") or {}
    clean = []
    for name in parties:
        if not isinstance(name, str) or name not in world:
            raise ValueError("کشور نامعتبر در فهرست توافق: %s" % name)
        if name in (s.get("eliminated") or []):
            raise ValueError("کشور حذف‌شده نمی‌تواند عضو توافق باشد: %s" % name)
        if name not in clean:
            clean.append(name)
    player = s.get("player")
    if player not in clean:
        clean.insert(0, player)
    if len(clean) < 2 or len(clean) > 20:
        raise ValueError("توافق باید بین ۲ تا ۲۰ کشور باشد.")
    return clean


def submit_agreement_proposal(s, kind, parties, pact_type="non_aggression",
                              alliance_name="", terms=None, conversation_id=None):
    """ثبت پیشنهاد در انتظار پاسخ؛ هیچ عضویت یا اثر دیپلماتیکی فوراً اعمال نمی‌شود."""
    if kind not in ("pact", "alliance"):
        raise ValueError("نوع توافق باید پیمان یا اتحاد باشد.")
    clean = _agreement_validate_parties(s, parties)
    if kind == "pact" and pact_type not in AGREEMENT_PACT_TYPES:
        raise ValueError("نوع پیمان انتخاب‌شده معتبر نیست.")
    if not isinstance(terms, dict):
        terms = {}
    try:
        safe_terms = json.loads(json.dumps(terms, ensure_ascii=False))
    except (TypeError, ValueError):
        raise ValueError("شرایط توافق قابل ذخیره نیست.")
    if len(json.dumps(safe_terms, ensure_ascii=False)) > 8000:
        raise ValueError("متن شرایط توافق بیش از حد مجاز است.")
    linked_session = None
    if conversation_id:
        linked_session = get_conversation_session(s, conversation_id)
        if not linked_session:
            raise ValueError("نشست گفت‌وگوی مرتبط پیدا نشد.")
        if set(linked_session.get("participants") or []) != set(clean):
            raise ValueError("اعضای نشست گفت‌وگو باید دقیقاً با طرف‌های توافق یکسان باشند.")
    for old in s.get("agreement_proposals") or []:
        if old.get("status") == "pending" and old.get("kind") == kind and set(old.get("parties") or []) == set(clean):
            if kind != "pact" or old.get("pact_type") == pact_type:
                raise ValueError("پیشنهاد مشابهی برای این کشورها هنوز در انتظار پاسخ است.")
    seq = int(s.get("agreement_sequence", 0)) + 1
    s["agreement_sequence"] = seq
    today = s.get("game_date", "")
    proposal = {
        "id": "AGR-%06d" % seq, "kind": kind, "pact_type": pact_type if kind == "pact" else None,
        "name": str(alliance_name or "").strip()[:100] if kind == "alliance" else AGREEMENT_PACT_TYPES.get(pact_type, ""),
        "parties": clean, "initiator": s.get("player"), "status": "pending",
        "accepted_by": [s.get("player")], "rejected_by": [],
        "created_date": today, "updated_date": today,
        "terms": safe_terms, "conversation_id": conversation_id,
        "live_ai_required": True, "live_ai_status": "locked_until_phase_f"
    }
    s.setdefault("agreement_proposals", []).append(proposal)
    s.setdefault("agreement_history", []).append({
        "date": today, "action": "proposal_created", "proposal_id": proposal["id"],
        "kind": kind, "parties": list(clean), "actor": s.get("player"),
        "conversation_id": conversation_id
    })
    s["agreement_proposals"] = s["agreement_proposals"][-300:]
    s["agreement_history"] = s["agreement_history"][-500:]
    msg(s, "پیشنهاد %s %s ثبت شد؛ تا دریافت پذیرش معتبر از همه طرف‌ها توافق فعال نمی‌شود." %
        ("پیمان" if kind == "pact" else "اتحاد", proposal["id"]))
    return {"ok": True, "proposal": proposal,
            "note": "پیشنهاد ذخیره شد؛ عضویت و اثر توافق تا پذیرش همه طرف‌ها غیرفعال است."}


def decide_agreement_proposal(s, proposal_id, decision):
    """بازیکن فقط می‌تواند دعوت/پیشنهاد دریافتی را بپذیرد یا رد کند."""
    if decision not in ("accept", "reject"):
        raise ValueError("تصمیم نامعتبر است.")
    proposal = None
    for item in s.get("agreement_proposals") or []:
        if isinstance(item, dict) and item.get("id") == proposal_id:
            proposal = item
            break
    if proposal is None or proposal.get("status") != "pending":
        raise ValueError("پیشنهاد فعال و در انتظار پاسخ پیدا نشد.")
    player = s.get("player")
    if proposal.get("initiator") == player or player not in (proposal.get("parties") or []):
        raise ValueError("این پیشنهاد، دعوت دریافتی از کشور دیگر نیست.")
    today = s.get("game_date", "")
    if decision == "reject":
        proposal["status"] = "rejected"
        proposal.setdefault("rejected_by", []).append(player)
        action = "proposal_rejected"
    else:
        accepted = proposal.setdefault("accepted_by", [])
        if player not in accepted:
            accepted.append(player)
        if set(accepted) == set(proposal.get("parties") or []):
            proposal["status"] = "accepted"
            if proposal.get("kind") == "pact":
                seq = int(s.get("agreement_sequence", 0)) + 1
                s["agreement_sequence"] = seq
                record = {
                    "id": "PACT-%06d" % seq, "type": proposal.get("pact_type", "non_aggression"),
                    "name": proposal.get("name") or AGREEMENT_PACT_TYPES.get(proposal.get("pact_type"), ""),
                    "members": list(proposal.get("parties") or []), "status": "active",
                    "created_date": today, "updated_date": today, "terms": proposal.get("terms") or {},
                    "legacy": False, "proposal_id": proposal_id,
                    "conversation_id": proposal.get("conversation_id")
                }
                s.setdefault("pact_records", []).append(record)
                if player == s.get("player"):
                    for other in record["members"]:
                        if other != player and other not in s.setdefault("pacts", []):
                            s["pacts"].append(other)
            else:
                seq = int(s.get("agreement_sequence", 0)) + 1
                s["agreement_sequence"] = seq
                record = {
                    "id": "ALLY-%06d" % seq, "name": proposal.get("name") or "اتحاد جدید",
                    "type": "military", "members": list(proposal.get("parties") or []),
                    "status": "active", "created_date": today, "updated_date": today,
                    "terms": proposal.get("terms") or {}, "legacy": False,
                    "proposal_id": proposal_id,
                    "conversation_id": proposal.get("conversation_id")
                }
                s.setdefault("alliance_records", []).append(record)
                if player == s.get("player"):
                    for other in record["members"]:
                        if other != player and other not in s.setdefault("allies", []):
                            s["allies"].append(other)
        action = "proposal_accepted"
    proposal["updated_date"] = today
    s.setdefault("agreement_history", []).append({
        "date": today, "action": action, "proposal_id": proposal_id, "actor": player,
        "status": proposal.get("status"), "conversation_id": proposal.get("conversation_id")
    })
    s["agreement_history"] = s["agreement_history"][-500:]
    return {"ok": True, "proposal": proposal,
            "note": "تصمیم ثبت شد؛ هیچ پاسخ یا پذیرشی از طرف کشورهای دیگر جعل نشده است."}


def cancel_pact_record(s, pact_id):
    for record in s.get("pact_records") or []:
        if isinstance(record, dict) and record.get("id") == pact_id and record.get("status") == "active":
            if s.get("player") not in (record.get("members") or []):
                raise ValueError("بازیکن عضو این پیمان نیست.")
            record["status"] = "cancelled"
            record["updated_date"] = s.get("game_date", "")
            player = s.get("player")
            active_partners = set()
            for other_record in s.get("pact_records") or []:
                if other_record.get("status") == "active" and player in (other_record.get("members") or []):
                    active_partners.update(n for n in other_record.get("members", []) if n != player)
            s["pacts"] = sorted(active_partners)
            s["agreement_history"].append({"date": s.get("game_date", ""), "action": "pact_cancelled",
                                           "agreement_id": pact_id, "actor": player})
            s["agreement_history"] = s["agreement_history"][-500:]
            return {"ok": True, "record": record}
    raise ValueError("پیمان فعال موردنظر پیدا نشد.")


def submit_alliance_join_request(s, alliance_id):
    """ثبت درخواست عضویت بازیکن در اتحاد موجود؛ عضویت تا پذیرش همه اعضای دیگر فعال نمی‌شود."""
    player = s.get("player")
    alliance = None
    for record in s.get("alliance_records") or []:
        if isinstance(record, dict) and record.get("id") == alliance_id and record.get("status") == "active":
            alliance = record
            break
    if alliance is None:
        raise ValueError("اتحاد فعال موردنظر پیدا نشد.")
    members = alliance.get("members") or []
    if player in members:
        raise ValueError("کشور شما هم‌اکنون عضو این اتحاد است.")
    if any(x.get("alliance_id") == alliance_id and x.get("status") == "pending"
           for x in (s.get("alliance_join_requests") or []) if isinstance(x, dict)):
        raise ValueError("برای این اتحاد قبلاً درخواست عضویت در انتظار ثبت شده است.")
    seq = int(s.get("agreement_sequence", 0)) + 1
    s["agreement_sequence"] = seq
    request = {
        "id": "AJR-%06d" % seq, "alliance_id": alliance_id,
        "alliance_name": alliance.get("name") or "اتحاد ثبت‌شده",
        "requester": player, "current_members": list(members),
        "status": "pending", "created_date": s.get("game_date", ""),
        "updated_date": s.get("game_date", ""),
        "live_ai_required": True, "live_ai_status": "locked_until_phase_f"
    }
    s.setdefault("alliance_join_requests", []).append(request)
    s["alliance_join_requests"] = s["alliance_join_requests"][-200:]
    s.setdefault("agreement_history", []).append({
        "date": s.get("game_date", ""), "action": "alliance_join_requested",
        "request_id": request["id"], "agreement_id": alliance_id, "actor": player
    })
    s["agreement_history"] = s["agreement_history"][-500:]
    return {"ok": True, "request": request,
            "note": "درخواست ثبت شد؛ عضویت تا بررسی و پذیرش اعضای اتحاد فعال نمی‌شود."}


def leave_alliance(s, alliance_id):
    for record in s.get("alliance_records") or []:
        if isinstance(record, dict) and record.get("id") == alliance_id and record.get("status") == "active":
            player = s.get("player")
            if player not in (record.get("members") or []):
                raise ValueError("کشور بازیکن عضو این اتحاد نیست.")
            record["members"] = [n for n in record.get("members", []) if n != player]
            record["updated_date"] = s.get("game_date", "")
            if len(record["members"]) < 2:
                record["status"] = "dissolved"
            active_partners = set()
            for other_record in s.get("alliance_records") or []:
                if other_record.get("status") == "active" and player in (other_record.get("members") or []):
                    active_partners.update(n for n in other_record.get("members", []) if n != player)
            s["allies"] = sorted(active_partners)
            s["agreement_history"].append({"date": s.get("game_date", ""), "action": "alliance_left",
                                           "agreement_id": alliance_id, "actor": player})
            s["agreement_history"] = s["agreement_history"][-500:]
            return {"ok": True, "record": record}
    raise ValueError("اتحاد فعال موردنظر پیدا نشد.")


# ---------- تحریم‌های یک‌جانبه بازیکن ----------
PLAYER_SANCTION_CATEGORIES = {
    "goods", "air", "transit", "land",
    "bank", "energy", "technology", "sea"
}


def apply_player_sanctions(s, targets, categories):
    """ثبت پایدار تحریم‌های بازیکن؛ اثر اقتصادی تفصیلی تا تکمیل موتور اقتصاد اعمال نمی‌شود."""
    if not isinstance(targets, list) or not targets:
        raise ValueError("حداقل یک کشور هدف را انتخاب کن.")
    if not isinstance(categories, list) or not categories:
        raise ValueError("حداقل یک زمینه تحریم را انتخاب کن.")
    player = s.get("player")
    world = s.get("world") or {}
    clean_targets = []
    target_aliases = {"دومینیکان": "دومینیکن"}
    for target in targets:
        if isinstance(target, str):
            target = target_aliases.get(target, target)
        if not isinstance(target, str) or target not in world:
            raise ValueError("کشور هدف نامعتبر است: %s" % target)
        if target == player:
            raise ValueError("کشور بازیکن نمی‌تواند هدف تحریم خودش باشد.")
        if target in s.get("eliminated", []):
            raise ValueError("کشور حذف‌شده را نمی‌توان تحریم کرد: %s" % target)
        if target not in clean_targets:
            clean_targets.append(target)
    clean_categories = []
    for category in categories:
        if not isinstance(category, str) or category not in PLAYER_SANCTION_CATEGORIES:
            raise ValueError("زمینه تحریم نامعتبر است: %s" % category)
        if category not in clean_categories:
            clean_categories.append(category)

    records = s.setdefault("player_sanctions", {})
    if not isinstance(records, dict):
        records = {}
        s["player_sanctions"] = records
    history = s.setdefault("player_sanction_history", [])
    if not isinstance(history, list):
        history = []
        s["player_sanction_history"] = history
    today = s.get("game_date", "")
    changed = []
    for target in clean_targets:
        old = records.get(target) if isinstance(records.get(target), dict) else {}
        record = {
            "country": target, "actor": "player",
            "categories": list(clean_categories), "status": "active",
            "imposed_date": old.get("imposed_date") or today,
            "updated_date": today
        }
        records[target] = record
        history.append({
            "date": today, "action": "applied" if not old else "updated",
            "country": target, "categories": list(clean_categories), "actor": "player"
        })
        changed.append(dict(record))
    del history[:-200]
    msg(s, "تحریم‌های یک‌جانبه کشور بازیکن برای %s کشور ثبت/به‌روزرسانی شد؛ اثر اقتصادی تفصیلی هنوز فعال نیست." % len(changed))
    return {"ok": True, "count": len(changed), "sanctions": changed,
            "note": "ثبت و ذخیره تحریم انجام شد؛ اثر اقتصادی دسته‌بندی‌شده پس از تکمیل موتور اقتصاد در فاز C اضافه می‌شود."}


def cancel_player_sanctions(s, targets=None):
    """لغو تحریم‌های بازیکن؛ آثار تاریخی اقتصادی (در صورت وجود) بازگردانده نمی‌شوند."""
    records = s.setdefault("player_sanctions", {})
    if not isinstance(records, dict):
        records = {}
        s["player_sanctions"] = records
    if targets is None:
        selected = list(records.keys())
    elif not isinstance(targets, list):
        raise ValueError("فهرست کشورهای لغو تحریم نامعتبر است.")
    else:
        selected = []
        for target in targets:
            if not isinstance(target, str) or target not in (s.get("world") or {}):
                raise ValueError("کشور برای لغو تحریم نامعتبر است: %s" % target)
            if target not in selected:
                selected.append(target)
    history = s.setdefault("player_sanction_history", [])
    if not isinstance(history, list):
        history = []
        s["player_sanction_history"] = history
    today = s.get("game_date", "")
    removed = []
    for target in selected:
        old = records.pop(target, None)
        if old is not None:
            removed.append(target)
            history.append({
                "date": today, "action": "cancelled", "country": target,
                "categories": list(old.get("categories") or []), "actor": "player"
            })
    del history[:-200]
    if removed:
        msg(s, "تحریم‌های یک‌جانبه کشور بازیکن برای %s کشور لغو شد." % len(removed))
    return {"ok": True, "count": len(removed), "cancelled": removed}



def init_game(player):
    rng = random.Random()
    world = {}
    for name, base in COUNTRIES.items():
        c = dict(base)
        c["influence"] = rng.randint(20, 40)
        world[name] = c
    rel = {}
    names = list(COUNTRIES)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            key = frozenset((a, b))
            if key in DEFAULT_REL:
                v = DEFAULT_REL[key]
            elif key in ENMITY:
                v = ENMITY[key]
            elif key in FRIEND:
                v = FRIEND[key]
            elif COUNTRIES[a]["region"] == COUNTRIES[b]["region"]:
                v = 8
            else:
                v = rng.randint(-10, 30)
            rel[rel_key(a, b)] = v
    # پیمان‌های اولیه واقع‌گرایانه: ناتو و متحدان آمریکا
    pacts0 = []
    allies0 = []
    if player in NATO:
        allies0 = [n for n in NATO if n != player and n in COUNTRIES]
    elif player in US_PACT:
        allies0 = ["آمریکا"]
    political_state, political_baseline = load_political_baseline()
    political_baseline_state = json.loads(json.dumps(political_state))
    political_state = json.loads(json.dumps(political_state))
    state = dict(
        player=player, year=START_YEAR, turn=1, ap="\u221e", over=False,
        world=world, relations=rel,
        allies=allies0, pacts=pacts0,
        pact_records=[], alliance_records=[], agreement_proposals=[], agreement_history=[], agreement_sequence=0,
        alliance_join_requests=[],
        diplomatic_history=[],
        player_sanctions={}, player_sanction_history=[],
        inbox_messages=[], inbox_sequence=0,
        conversation_sessions=[], conversation_sequence=0,
        calendar_events=[], calendar_sequence=0, live_ai_active=False,
        politics={n: dict(parties=dict(PARTY_BASE if n == player else AI_PARTY_BASE), press=[]) for n in COUNTRIES},
        political_state=political_state, political_baseline=political_baseline,
        political_baseline_state=political_baseline_state,
        social_groups={player: dict(SOCIAL_GROUP_BASE)},
        legitimacy=50.0, regime_crisis=None,
        turn_events={},
        game_events=[], event_sequence=0,
        log=["۵ نوامبر ۲۰۲۶: تو رهبر %s شدی. جهان در آستانه یک دوران پرآشوب است." % player],
        at_war=[], eliminated=[], proxies=[],
        game_date=START_DATE.isoformat(), hour=0, minute=0, elapsed_days=0,
        day=START_DATE.day, iaea_heat=0, un_censures=0,
    )
    state["arsenal"] = _default_arsenal(rel)
    for name, c in state["world"].items():
        c["_arsenal"] = state["arsenal"].get(name, {})
    save(state)
    return state

# ---------- سیاست داخلی: احزاب و مطبوعات ----------

PARTY_BASE = {"اصلاح‌طلبان": 26, "جبهه انقلاب": 27, "ملی‌گرایان": 25, "تکنوکرات‌ها": 22}
WEST = {"آمریکا", "بریتانیا", "فرانسه", "آلمان", "ژاپن"}
EAST = {"روسیه", "چین"}

AI_PARTY_BASE = {"حاکمیت": 38, "اپوزیسیون": 24, "ارتش‌گرایان": 20, "تجار": 18}

# درصد مقبولیت اولیه هر گروه؛ شاخص‌ها مستقل‌اند و مجموعشان الزاماً ۱۰۰ نیست.
SOCIAL_GROUP_BASE = {
    "کارگران و مزدبگیران": 52.0,
    "کسب‌وکار و بازرگانان": 48.0,
    "کارمندان و خدمات عمومی": 50.0,
    "دانشجویان و جوانان": 54.0,
    "کشاورزان و مناطق روستایی": 51.0,
    "متخصصان و طبقه متوسط": 53.0,
}

AI_OUTLETS = [
    dict(name_fmt="روزنامه رسمی {who}", copy={
        "war_won": "پیروزی ملت؛ اقتدار حاکمیت درخشید",
        "war_lost": "بازسازی و ایستادگی؛ ملت سرپاست",
        "war_defended": "دفاع موفق؛ متجاوز واپس زده شد",
        "war_foreign": "جنگ {a} و {d}؛ پیام‌های امنیتی برای منطقه",
        "nuke": "گام راهبردی؛ اقتدار ملی تضمین شد",
        "sanctioned_by": "فشار بیگانه؛ ملت پشت دولت",
        "kill_victim": "ترور رهبر؛ ملت سوگوار اما سرپا ({a} متهم شد)",
        "kill_attempt": "نقشه ترور خنثی شد؛ عوامل به {a} می‌رسند",
        "sabotage_victim": "خرابکاری در تأسیسات؛ ردپا به {a} می‌رسد",
        "uprising": "عده معدود غوغاسازی کردند؛ نظیره برقرار است",
        "plague": "مدیریت بحران؛ دلسوزان در کنار مردم",
        "oil_crisis": "شوک انرژی؛ بسته حمایتی دولت اعلام شد",
        "boom": "گزارش سالانه: رشد و برکت",
        "eco": "پروژه‌های ملی افتتاح شد",
        "tech": "دستاورد علمی تازه؛ غرور ملی",
        "mil": "توان دفاعی روزافزون",
        "trees": "",  # placeholder
        "trade": "توافق اقتصادی با {t}؛ نفع دوطرفه",
        "ally": "پیمان با {t}؛ موقعیت تقویت شد",
        "sanction": "تحریم تامل‌برانگیز علیه {t}؛ اقتدار حفظ می‌شود",
        "covert_fail": "قالب نقشه خارجی شکسته شد",
        "pact": "پیمان با {t}؛ موقعیت تقویت شد",
    }, idle=["پروژه عمرانی افتتاح شد", "مردم در حال زندگی روزمره", "آب و هوا: آفتابی"]),
    dict(name_fmt="تربیون آزاد {who}", copy={
        "war_won": "پیروزی؛ اما صورت‌حساب جنگ چه؟",
        "war_lost": "فروپاشی راهبرد؛ مسئول کیست؟",
        "war_defended": "دفاع موفق؛ دیپلماسی جا ماند",
        "war_foreign": "جنگ {a} و {d}؛ بازارها نگرانند",
        "nuke": "هزینه‌ها؛ شفافیت کجاست؟",
        "sanctioned_by": "تحریم؛ صورتحساب بر سفره مردم",
        "kill_victim": "ترور رهبر؛ خلأ امنیتی آشکار شد ({a} متهم)",
        "kill_attempt": "ترور ناکام؛ پرسش‌های بی‌پاسخ",
        "sabotage_victim": "خرابکاری؛ امنیت زیرساخت زیر سؤال",
        "uprising": "اعتراض‌ها؛ صدایی که باید شنید",
        "plague": "بحران سلامت؛ شفافیت بیشتر لازم است",
        "oil_crisis": "بحران انرژی؛ سفره‌ها لاغر شدند",
        "boom": "رشد؛ اما به نفع همه؟",
        "eco": "رونق پایدار؟ کارشناسان تردید دارند",
        "tech": "جهش فناوری؛ سرمایه‌گذاری عمومی لازم",
        "mil": "بودحه دفاع؛ سهم خانه سلامت؟",
        "trade": "توافق با {t}; روشنی بیشتر می‌خواهیم",
        "ally": "پیمان با {t}; روشنی بیشتر می‌خواهیم",
        "covert_fail": "افشای عملیات؛ اعتبار آسیب دید",
        "pact": "پیمان با {t}; آزمون جدیت",
    }, idle=["بازار آرام؛ انتظار خبرهای بزرگ", "سریال و سینما؛ عقربه فرهنگ", "ورزش: برد شیرین"]),
]

PRESS_OUTLETS = [
    dict(name="صبح انقلاب", copy={
        "war_won": "پیروزی شکوهمت؛ دشمن به زانو درآمد",
        "war_lost": "ملت صبور می‌ماند؛ تسلیم در کار نیست",
        "war_defended": "دفاع مقدس جواب داد؛ متجاوز واپس زده شد",
        "war_foreign": "آتش جنگ {a} و {d}؛ چشم جهان به محور مقاومت است",
        "nuke": "اقتدار هسته‌ای؛ سند استقلال ملی",
        "sanctioned_by": "جنگ اقتصادی دشمن؛ ملت به ابهت خود افتخار می‌کند",
        "sanction": "سیلی تحریم بر چهره سیاست زورگویانه ({t})",
        "ally_west": "خلأ ایمانی؟ پیوند با سازشکاران غرب",
        "ally_east": "محور مقاومت جهانی گسترش یافت ({t})",
        "ally": "پیمان شرافت با {t} امضا شد",
        "trade_west": "دادوستد با غرب؛ وسوسه‌ای که پاسخ می‌خواهد ({t})",
        "trade_east": "پیوند راهبردی شرق تقویت شد ({t})",
        "trade": "تعامل سازنده؛ بذری کاشته شد ({t})",
        "covert_ok": "توطئه در گِرداب دشمن سقوط کرد ({t})",
        "covert_fail": "شایعه دخالت خارجی؛ تکذیب شد",
        "uprising": "عده معدود؛ بازی دست بیگانه",
        "propaganda": "ملت هم‌صدا پشت دلسوزان ملت",
        "eco": "تولید ملی؛ کلید اقتدار",
        "tech": "جوانان؛ آهنگران تمدن نو",
        "mil": "پاسداران آرامش؛ بودجه دفاعی سنگین شد",
        "plague": "سوگ ملی؛ کمی صبر، صبح نزدیک است",
        "boom": "برکت بر سر سفره ملت",
        "oil_crisis": "دشمن شیر بازار را بست؛ خوداتکایی پاسخ ماست",
        "pact": "پیمان عدم تجاوز با {t}; نتیجه دیپلماسی فعال",
    }, idle=["روزهای آرام؛ ملت در کار خود", "نسل جوان؛ آینده از آن ماست"]),
    dict(name="وطن‌خواه", copy={
        "war_won": "عظمت بازگشت؛ دشمن عبرت گرفت",
        "war_lost": "زخم است، اما ملت سرپاست",
        "war_defended": "وطن به‌پاخاست و شام ابرقدرت سیاه شد",
        "war_foreign": "تغییر موازنه: جنگ {a} و {d}; فرصت ما کجاست؟",
        "nuke": "پرده قدرت؛ سند افتخار ملی",
        "sanctioned_by": "محاصره می‌سوزد؛ خودکفایی پاسخ ما است",
        "sanction": "سیلی سخت به دشمن زورگو ({t}); عزت ملی",
        "ally_west": "خطر: قلب سیاست به برلن/واشنگتن کوچید؟ ({t})",
        "ally_east": "شرق‌گرایی؛ سند اقتدار ({t})",
        "ally": "متحد تازه؛ ملت منفعت برد ({t})",
        "trade_west": "تجارت با {t}; ولی در سکوت سیاست؟",
        "trade_east": "بازار شرق ما را می‌خواهند ({t})",
        "trade": "مزدور تجارت؛ ثروت برای ملت ({t})",
        "covert_ok": "دست بیگانه قطع شد ({t}); نبرد نیابتی ادامه دارد",
        "covert_fail": "افشای نقشه; عزم ما نمی‌شکند",
        "uprising": "اغتشاش; گردنکشان به ملت جواب دهند",
        "propaganda": "وحدت ملی؛ هم‌صدایی می‌آوریم",
        "eco": "خوداتکایی گسترش یافت",
        "tech": "علم و غرور ملی； توأمان",
        "mil": "زور ما به دشمن رسانه می‌رسد",
        "plague": "صلابت ملت در سختی؛ هیچ‌کس تنها نیست",
        "boom": "اقتصاد در مسیر عزت ملی",
        "oil_crisis": "تحریم سوخت؛ پاسخ ما شجاعت است",
        "pact": "دیپلماسی فعال؛ صلح با شرف ({t})",
    }, idle=["پرچم همیشه برافراشته", "ملت، همیشه درست انتخاب می‌کند"]),
    dict(name="خبر آزاد", copy={
        "war_won": "پیروزی در میدان؛ اما به قیمت چه؟",
        "war_lost": "میز مذاکره خالی ماند؛ پرسش‌های بی‌جواب",
        "war_defended": "دفاع موفق؛ دیپلماسی فرصت می‌خواست",
        "war_foreign": "جنگ {a} و {d}; جهان نگران، اقتصاد لرزان",
        "nuke": "جهان سخت‌تر شد؛ اقتصاد باور نمی‌کند",
        "sanctioned_by": "تحریم تازه؛ چه کسی صورتحساب را می‌پردازد؟",
        "sanction": "تحریم علیه {t}; ابزاری بی‌اثر؟ کارشناسان تردید دارند",
        "ally_west": "افق تازه در دیپلماسی؛ آغازی امیدوارکننده ({t})",
        "ally_east": "شراکت با {t}; شفافیت چقدر؟",
        "ally": "پیمان با {t}; روشنی بیشتر می‌خواهیم",
        "trade_west": "توافق تجاری با {t}; دیپلماسی اقتصادی کار کرد",
        "trade_east": "تجارت با {t}; نفع دو‌طرفه تا کجا؟",
        "trade": "بازار باز شد ({t}); اما پایداری؟",
        "covert_ok": "عملیات پشت‌پرده; حساب‌وکتاب کجاست؟",
        "covert_fail": "افشای عملیات؛ اعتبار دیپلماسی کشور آسیب دید",
        "uprising": "صدایی که باید شنید؛ اعتراض حق است",
        "propaganda": "کمپین تبلیغاتی گسترده; هزینه‌اش را چه کسی می‌دهد؟",
        "eco": "رونق؛ این بار پایدار خواهد بود؟",
        "tech": "جهش فناوری؛ استارتاپ‌ها جان تازه گرفتند",
        "mil": "بودجه دفاع بالا رفت; خانه سلامت سهمی نداشت",
        "plague": "قرنطینه؛ همدستی مردم، شفافیت دولت",
        "boom": "رشد اقتصادی؛ پیش‌بینی مثبت نهادهای بین‌المللی",
        "oil_crisis": "شوک انرژی؛ سفره‌ها لاغر شدند",
        "pact": "دیپلماسی: پیمان با {t}; قدم رو به جلو",
    }, idle=["بازار امروز آرام بود", "شهرداری: پروژه‌های شهری در جریان", "ورزش: برد شیرین، شادی ملی"]),
    dict(name="اقتصاد فردا", copy={
        "war_won": "سهم بازار پس از پیروزی باز می‌شود؟",
        "war_lost": "بازار سقوط کرد؛ سرمایه فراری است",
        "war_defended": "ریسک کشوری بالا رفت؛ بیم پناه سرمایه",
        "war_foreign": "جنگ {a} و {d}; قیمت نفت و لجستیک به آشوب رفت",
        "nuke": "هزینه تحریم‌ها؛ اقتصاد به مذاکره می‌اندیشد",
        "sanctioned_by": "شوک تحریم؛ فرار سرمایه و افت نرخ برابری",
        "sanction": "تحریم {t}; فرصت بازار جایگزین؟",
        "ally_west": "افق سرمایه‌گذاری باز شد ({t}); تحلیل‌گران خوش‌بین",
        "ally_east": "منطقه آزاد شرق ({t}); ریسک تحریمی باقی است",
        "ally": "پیمان با {t}; اثر تجاری مثبت",
        "trade_west": "توافق با {t}; دروازه واردات و صادرات باز شد",
        "trade_east": "وایر اینترکانکشن شرق ({t)); لجستیک بهتر",
        "trade": "قرارداد بلندمدت ({t}); پیش‌بینی رشد GDP +۱٪",
        "covert_ok": "عملیات موفق؛ اما هزینه‌های امنیتی بالا رفت",
        "covert_fail": "افشای عملیات؛ ریسک کشوری در رتبه‌بندی‌ها سالید",
        "uprising": "تعطیلی بازار؛ تجار در دوراهی",
        "propaganda": "هزینه تبلیغات; دفترخانه توقیف درآورد؟",
        "eco": "رشد اقتصادی؛ پیش‌بینی صندوق جهانی مثبت",
        "tech": "جهش فناوری؛ استارتاپ‌های متولد می‌شوند",
        "mil": "هزینه دفاعی؛ نگرانی بودجه سلامت و آموزش",
        "plague": "شکاف زنجیره تأمین؛ تورم می‌آید",
        "boom": "رونق بازار؛ جذب سرمایه بالارفت",
        "oil_crisis": "بحران انرژی؛ صنایع گاز بریدند",
        "pact": "امنیت تجاری با {t}; نرخ ریسک افت کرد",
    }, idle=["بورس روزی آرام", "بانک مرکزی: تورم مهارشدنی است", "زیرساخت: رویداد اقتصادی هفته"]),
]

EVENT_CATEGORIES = (
    "political", "economic", "trade", "military",
    "social", "diplomatic", "natural", "environmental", "nuclear"
)

EVENT_PRIORITY_LEVELS = {
    "ordinary": {"rank": 1, "label": "عادی"},
    "important": {"rank": 2, "label": "مهم"},
    "critical": {"rank": 3, "label": "بحرانی"},
    "very_critical": {"rank": 4, "label": "بسیار بحرانی"}
}


def get_event_priority(severity):
    """تبدیل شدت عددی رویداد به سطح اولویت نمایشی."""
    try:
        value = int(severity)
    except (TypeError, ValueError):
        value = 1
    value = max(1, min(5, value))
    if value <= 1:
        key = "ordinary"
    elif value <= 3:
        key = "important"
    elif value == 4:
        key = "critical"
    else:
        key = "very_critical"
    result = dict(EVENT_PRIORITY_LEVELS[key])
    result["key"] = key
    return result


EVENT_STATUS_TRANSITIONS = {
    "recorded": ("acknowledged", "investigating", "dismissed"),
    "acknowledged": ("investigating", "resolved", "dismissed"),
    "investigating": ("acknowledged", "resolved", "dismissed"),
    "resolved": ("closed",),
    "closed": (),
    "dismissed": ()
}


# مسیرهای اثرگذاری فقط مقصدهای بالقوه را مشخص می‌کنند؛
# تا زمان تکمیل سیستم پیامدها هیچ شاخصی از این طریق تغییر نمی‌کند.
EVENT_IMPACT_ROUTES = {
    "political": ["domestic_politics", "stability", "legitimacy", "press"],
    "economic": ["economy", "budget", "employment", "press"],
    "trade": ["trade", "economy", "diplomacy", "press"],
    "military": ["military_status", "security", "budget", "diplomacy"],
    "social": ["social_support", "stability", "domestic_politics", "press"],
    "diplomatic": ["foreign_relations", "agreements", "press"],
    "natural": ["population", "infrastructure", "economy", "environment"],
    "environmental": ["environment", "population", "economy", "public_health"],
    "nuclear": ["nuclear_policy", "international_security", "safeguards",
                "diplomacy", "economy", "environment", "press"]
}

# کاتالوگ محرک‌ها: فقط قرارداد داده‌ای برای اتصال آینده سیستم‌هاست.
# هیچ شرطی در این مرحله ارزیابی و هیچ رویدادی خودکار فعال نمی‌شود.
EVENT_TRIGGER_SPECS = [
    {"id": "political_reform_outcome", "category": "political",
     "source_system": "political_reforms", "signal": "reform_status_changed",
     "required_fields": ["proposal_id", "status", "country"],
     "description": "ثبت تصویب، توقف، شکست یا تکمیل یک اصلاح سیاسی."},
    {"id": "domestic_crisis_threshold", "category": "political",
     "source_system": "regime_crisis", "signal": "crisis_state_created",
     "required_fields": ["crisis_kind", "country", "date"],
     "description": "ثبت ایجاد وضعیت بحران داخلی؛ نه وقوع خودکار کودتا یا انقلاب."},
    {"id": "economic_indicator_shift", "category": "economic",
     "source_system": "economy", "signal": "economic_indicator_changed",
     "required_fields": ["country", "indicator", "old_value", "new_value"],
     "description": "ثبت تغییر مهم در شاخص‌های اقتصادی پس از تکمیل سیستم اقتصاد."},
    {"id": "budget_pressure", "category": "economic",
     "source_system": "budget", "signal": "budget_status_changed",
     "required_fields": ["country", "balance", "cause"],
     "description": "ثبت کسری، فشار بودجه‌ای یا تغییر مهم در منابع مالی."},
    {"id": "trade_disruption", "category": "trade",
     "source_system": "trade", "signal": "trade_route_or_deal_disrupted",
     "required_fields": ["country", "counterparty", "trade_id", "cause"],
     "description": "ثبت اختلال در مسیر یا توافق تجاری پس از تکمیل تجارت."},
    {"id": "trade_agreement_milestone", "category": "trade",
     "source_system": "trade", "signal": "trade_agreement_status_changed",
     "required_fields": ["country", "counterparty", "agreement_id", "status"],
     "description": "ثبت امضا، تعلیق، تمدید یا پایان توافق تجاری."},
    {"id": "military_status_change", "category": "military",
     "source_system": "military", "signal": "military_status_changed",
     "required_fields": ["country", "change_type", "date"],
     "description": "ثبت تغییر کلان وضعیت نظامی یا امنیتی، بدون جزئیات عملیاتی."},
    {"id": "war_status_change", "category": "military",
     "source_system": "conflict", "signal": "conflict_status_changed",
     "required_fields": ["participants", "status", "date"],
     "description": "ثبت آغاز، گسترش، آتش‌بس یا پایان درگیری در سطح کلان بازی."},
    {"id": "social_support_shift", "category": "social",
     "source_system": "social_groups", "signal": "support_level_changed",
     "required_fields": ["country", "group_id", "old_value", "new_value"],
     "description": "ثبت تغییر معنادار حمایت گروه‌های اجتماعی."},
    {"id": "diplomatic_agreement_change", "category": "diplomatic",
     "source_system": "diplomacy", "signal": "agreement_status_changed",
     "required_fields": ["country", "counterparty", "agreement_id", "status"],
     "description": "ثبت توافق، اختلاف، تعلیق یا گسست دیپلماتیک."},
    {"id": "natural_disaster", "category": "natural",
     "source_system": "disaster", "signal": "natural_disaster_confirmed",
     "required_fields": ["country", "disaster_type", "severity", "date"],
     "description": "ثبت بلای طبیعی تأییدشده و پیوند آن با پیامدهای غیرنظامی."},
    {"id": "environmental_incident", "category": "environmental",
     "source_system": "environment", "signal": "environmental_incident_confirmed",
     "required_fields": ["country", "incident_type", "severity", "date"],
     "description": "ثبت رخداد محیط‌زیستی و آثار عمومی آن."},
    {"id": "nuclear_safeguards_or_diplomacy", "category": "nuclear",
     "source_system": "nuclear_governance", "signal": "safeguards_or_diplomatic_status_changed",
     "required_fields": ["country", "status", "institution", "date"],
     "description": "ثبت تحولات سیاست هسته‌ای، نظارت، پادمان یا دیپلماسی در سطح حکمرانی."}
]

EVENT_TRIGGER_ACTIVATION = "design_only"


def get_event_trigger_catalog():
    """نمایش کاتالوگ محرک‌ها؛ این تابع هیچ محرکی را اجرا یا ارزیابی نمی‌کند."""
    return [dict(item, required_fields=list(item.get("required_fields") or []),
                 activation=EVENT_TRIGGER_ACTIVATION)
            for item in EVENT_TRIGGER_SPECS]


def validate_event_trigger_payload(trigger_id, payload):
    """اعتبارسنجی قرارداد داده محرک؛ بدون فعال‌سازی محرک یا ثبت رویداد."""
    spec = None
    for item in EVENT_TRIGGER_SPECS:
        if item.get("id") == trigger_id:
            spec = item
            break
    if spec is None:
        return {
            "valid": False,
            "trigger_id": trigger_id,
            "errors": ["شناسه محرک در کاتالوگ وجود ندارد."]
        }
    if not isinstance(payload, dict):
        return {
            "valid": False,
            "trigger_id": trigger_id,
            "errors": ["داده محرک باید از نوع شیء/دیکشنری باشد."]
        }

    errors = []
    for field in spec.get("required_fields") or []:
        if field not in payload:
            errors.append("فیلد الزامی موجود نیست: %s" % field)
            continue
        value = payload.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append("فیلد الزامی خالی است: %s" % field)
        elif isinstance(value, (list, tuple, dict)) and not value:
            errors.append("فیلد الزامی خالی است: %s" % field)

    return {
        "valid": not errors,
        "trigger_id": spec.get("id"),
        "category": spec.get("category"),
        "source_system": spec.get("source_system"),
        "signal": spec.get("signal"),
        "activation": EVENT_TRIGGER_ACTIVATION,
        "errors": errors
    }


def prepare_event_trigger_signal(trigger_id, payload):
    """ساخت بسته استاندارد سیگنال؛ بدون ارسال، ثبت رویداد یا اعمال پیامد."""
    validation = validate_event_trigger_payload(trigger_id, payload)
    if not validation.get("valid"):
        return {
            "prepared": False,
            "dispatched": False,
            "errors": list(validation.get("errors") or [])
        }

    return {
        "prepared": True,
        "dispatched": False,
        "dispatch_enabled": False,
        "activation": EVENT_TRIGGER_ACTIVATION,
        "trigger_id": validation.get("trigger_id"),
        "category": validation.get("category"),
        "source_system": validation.get("source_system"),
        "signal": validation.get("signal"),
        "payload": dict(payload),
        "status": "validated_not_dispatched",
        "errors": []
    }



def register_game_event(s, category, country=None, title="", description="",
                        severity=1, source="system", metadata=None, source_details=None):
    """ثبت رویداد همراه با منشأ قابل‌ردیابی؛ بدون اعمال پیامد بازی."""
    if category not in EVENT_CATEGORIES:
        raise ValueError("دسته‌بندی رویداد نامعتبر است: %s" % category)
    if country is not None and country not in (s.get("world") or {}):
        raise ValueError("کشور رویداد در جهان بازی وجود ندارد: %s" % country)
    try:
        severity = int(severity)
    except (TypeError, ValueError):
        severity = 1
    severity = max(1, min(5, severity))
    s["event_sequence"] = int(s.get("event_sequence", 0)) + 1
    event_id = "EV-%06d" % s["event_sequence"]
    event = {
        "id": event_id,
        "category": category,
        "country": country,
        "date": s.get("game_date", ""),
        "title": str(title or ""),
        "description": str(description or ""),
        "severity": severity,
        "priority": get_event_priority(severity)["key"],
        "priority_rank": get_event_priority(severity)["rank"],
        "priority_label": get_event_priority(severity)["label"],
        "status": "recorded",
        "status_updated_date": s.get("game_date", ""),
        "status_history": [{
            "date": s.get("game_date", ""),
            "from": None,
            "to": "recorded",
            "actor": "system",
            "note": "رویداد ثبت شد."
        }],
        "source": str(source or "system"),
        "source_info": _normalize_event_source(source, source_details),
        "impact_targets": list(EVENT_IMPACT_ROUTES.get(category, [])),
        "impact_plan": [],
        "impact_status": "pending_design",
        "effects_applied": False,
        "metadata": dict(metadata or {}),
        "chain_id": event_id,
        "parent_event_id": None,
        "child_event_ids": [],
        "chain_depth": 0
    }
    events = s.setdefault("game_events", [])
    events.append(event)
    if len(events) > 500:
        del events[:-500]
    return event


def _normalize_event_source(source, source_details=None):
    """یکسان‌سازی اطلاعات منشأ؛ ارجاعات شواهد صرفاً ثبت می‌شوند و خودکار راستی‌آزمایی نمی‌شوند."""
    details = source_details if isinstance(source_details, dict) else {}
    refs = details.get("evidence_refs") or []
    if not isinstance(refs, (list, tuple)):
        refs = [str(refs)]
    return {
        "source_system": str(details.get("source_system") or source or "system"),
        "source_record_id": str(details.get("source_record_id") or ""),
        "signal": str(details.get("signal") or ""),
        "recorded_by": str(details.get("recorded_by") or "system"),
        "evidence_refs": [str(item) for item in refs if item is not None and str(item).strip()],
        "review_status": "pending",
        "reviewed_by": "",
        "review_note": ""
    }


def find_duplicate_game_events(s, event):
    """یافتن موارد هم‌منشأ احتمالی؛ فقط هشدار می‌دهد و ثبت رویداد را مسدود نمی‌کند."""
    if not isinstance(event, dict):
        return []
    info = event.get("source_info") or {}
    source_system = str(info.get("source_system") or event.get("source") or "")
    source_record_id = str(info.get("source_record_id") or "")
    signal = str(info.get("signal") or "")
    if not source_record_id:
        return []
    matches = []
    for candidate in s.get("game_events") or []:
        if not isinstance(candidate, dict) or candidate.get("id") == event.get("id"):
            continue
        other = candidate.get("source_info") or {}
        if (candidate.get("category") == event.get("category")
                and candidate.get("country") == event.get("country")
                and candidate.get("date") == event.get("date")
                and str(other.get("source_system") or candidate.get("source") or "") == source_system
                and str(other.get("source_record_id") or "") == source_record_id
                and str(other.get("signal") or "") == signal):
            matches.append(candidate)
    return matches


def review_game_event_source(s, event_id, reviewer="system", status="reviewed", note=""):
    """ثبت نتیجه بازبینی منشأ؛ این تابع صحت بیرونی شواهد را مستقلاً تأیید نمی‌کند."""
    allowed = ("pending", "reviewed", "disputed")
    if status not in allowed:
        raise ValueError("وضعیت بازبینی منشأ نامعتبر است.")
    event = next((item for item in (s.get("game_events") or [])
                  if isinstance(item, dict) and item.get("id") == event_id), None)
    if event is None:
        raise ValueError("رویداد موردنظر پیدا نشد.")
    info = event.setdefault("source_info", _normalize_event_source(event.get("source")))
    info["review_status"] = status
    info["reviewed_by"] = str(reviewer or "system")
    info["review_note"] = str(note or "")
    info["reviewed_date"] = s.get("game_date", "")
    return info


def get_prioritized_game_events(s, limit=50, include_closed=False):
    """دریافت رویدادها بر اساس اولویت، بدون تغییر وضعیت یا اعمال پیامد."""
    events = s.get("game_events") or []
    selected = []
    for event in events:
        if not isinstance(event, dict):
            continue
        if not include_closed and event.get("status") in ("closed", "dismissed"):
            continue
        priority = get_event_priority(event.get("severity", 1))
        item = dict(event)
        item["priority"] = item.get("priority") or priority["key"]
        item["priority_rank"] = priority["rank"]
        item["priority_label"] = priority["label"]
        selected.append(item)

    selected.sort(key=lambda item: (
        -int(item.get("priority_rank", 1)),
        str(item.get("date", "")),
        str(item.get("id", ""))
    ))
    try:
        limit = max(1, min(500, int(limit)))
    except (TypeError, ValueError):
        limit = 50
    return selected[:limit]


def transition_game_event(s, event_id, new_status, actor="player", note=""):
    """تغییر وضعیت یک رویداد طبق چرخه مجاز؛ بدون اعمال پیامدهای بازی."""
    events = s.setdefault("game_events", [])
    event = None
    for item in events:
        if isinstance(item, dict) and item.get("id") == event_id:
            event = item
            break
    if event is None:
        raise ValueError("رویداد موردنظر پیدا نشد.")

    current_status = event.get("status", "recorded")
    allowed = EVENT_STATUS_TRANSITIONS.get(current_status)
    if allowed is None:
        raise ValueError("وضعیت فعلی رویداد ناشناخته است: %s" % current_status)
    if new_status not in allowed:
        raise ValueError("تغییر وضعیت از %s به %s مجاز نیست." %
                         (current_status, new_status))

    event["status"] = new_status
    event["status_updated_date"] = s.get("game_date", "")
    history = event.setdefault("status_history", [])
    history.append({
        "date": s.get("game_date", ""),
        "from": current_status,
        "to": new_status,
        "actor": str(actor or "system"),
        "note": str(note or "")
    })
    if len(history) > 50:
        del history[:-50]
    return event


def link_game_events(s, parent_event_id, child_event_id,
                     relation="caused_by", note=""):
    """پیوند دو رویداد و ثبت نوع ارتباط؛ بدون تولید رویداد یا اعمال پیامد."""
    allowed_relations = ("caused_by", "consequence_of", "related_to", "response_to")
    if relation not in allowed_relations:
        raise ValueError("نوع ارتباط رویدادها نامعتبر است.")

    events = s.setdefault("game_events", [])
    by_id = dict((item.get("id"), item) for item in events if isinstance(item, dict))
    parent = by_id.get(parent_event_id)
    child = by_id.get(child_event_id)
    if parent is None or child is None:
        raise ValueError("رویداد والد یا فرزند در فهرست رویدادهای موجود نیست.")
    if parent_event_id == child_event_id:
        raise ValueError("یک رویداد نمی‌تواند والد خودش باشد.")

    # جلوگیری از ایجاد چرخه در زنجیره.
    stack = [child_event_id]
    visited = set()
    while stack:
        current_id = stack.pop()
        if current_id in visited:
            continue
        visited.add(current_id)
        if current_id == parent_event_id:
            raise ValueError("این پیوند باعث ایجاد چرخه در زنجیره رویدادها می‌شود.")
        current = by_id.get(current_id)
        if current is not None:
            stack.extend(current.get("child_event_ids") or [])

    existing_parent = child.get("parent_event_id")
    if existing_parent and existing_parent != parent_event_id:
        raise ValueError("رویداد فرزند از قبل والد دیگری دارد.")
    if child_event_id not in (parent.get("child_event_ids") or []):
        parent.setdefault("child_event_ids", []).append(child_event_id)
    child["parent_event_id"] = parent_event_id
    child["parent_relation"] = relation
    child["parent_relation_note"] = str(note or "")
    child["relationship_updated_date"] = s.get("game_date", "")

    relations = parent.setdefault("child_relationships", [])
    relation_record = None
    for item in relations:
        if item.get("child_event_id") == child_event_id:
            relation_record = item
            break
    if relation_record is None:
        relation_record = {"child_event_id": child_event_id}
        relations.append(relation_record)
    relation_record.update({
        "relation": relation,
        "note": str(note or ""),
        "date": s.get("game_date", "")
    })

    root_id = parent.get("chain_id") or parent_event_id
    base_depth = int(parent.get("chain_depth", 0)) + 1
    pending = [(child, base_depth)]
    updated = set()
    while pending:
        item, depth = pending.pop()
        item_id = item.get("id")
        if item_id in updated:
            continue
        updated.add(item_id)
        item["chain_id"] = root_id
        item["chain_depth"] = depth
        for descendant_id in (item.get("child_event_ids") or []):
            descendant = by_id.get(descendant_id)
            if descendant is not None:
                pending.append((descendant, depth + 1))
    return {
        "parent_event_id": parent_event_id,
        "child_event_id": child_event_id,
        "chain_id": root_id,
        "chain_depth": base_depth,
        "relation": relation
    }


def get_event_chain(s, event_id):
    """بازیابی تمام اعضای زنجیره یک رویداد، از ریشه تا پیامدهای ثبت‌شده."""
    events = s.get("game_events") or []
    by_id = dict((item.get("id"), item) for item in events if isinstance(item, dict))
    target = by_id.get(event_id)
    if target is None:
        raise ValueError("رویداد موردنظر پیدا نشد.")

    chain_id = target.get("chain_id") or event_id
    chain = []
    for item in events:
        if not isinstance(item, dict):
            continue
        item_chain_id = item.get("chain_id") or item.get("id")
        if item_chain_id == chain_id:
            chain.append(item)
    chain.sort(key=lambda item: (
        int(item.get("chain_depth", 0)),
        str(item.get("date", "")),
        str(item.get("id", ""))
    ))
    return {
        "chain_id": chain_id,
        "event_count": len(chain),
        "events": chain
    }


def ev(s, who, *args):
    s.setdefault("turn_events", {}).setdefault(who, []).append(list(args))

def canon_events(s, who, events):
    P = s["player"]
    out = []
    def mk(pr, key, **kw):
        base = dict(t=kw.get("t", ""), a=kw.get("a", ""), d=kw.get("d", ""))
        out.append((pr, key, base))
    pri_map = {"sabotage_victim": 2, "kill_victim": 1, "kill_attempt": 3, "kill_ok": 3, "kill_fail": 3,
               "sabotage_ok": 4, "sabotage_fail": 4, "war_attrition": 8, "covert_ok": 6, "covert_fail": 3,
               "ally": 7, "trade": 8, "pact": 9, "propaganda": 9, "eco": 10, "tech": 10, "mil": 11,
               "oil_crisis": 9, "boom": 9}
    for e in events:
        k = e[0]
        if k == "war_result":
            _, atk, dfn, res = e
            if who not in (atk, dfn):
                mk(12, "war_foreign", a=atk, d=dfn)
            elif who == atk and res == "won":
                mk(1, "war_won", a=dfn, d=dfn)
            elif who == dfn and res == "lost":
                mk(1, "war_lost", a=atk, d=dfn)
            elif who == atk and res == "lost":
                mk(1, "war_lost", a=dfn, d=dfn)
            else:
                mk(1, "war_defended", a=atk, d=dfn)
        elif k == "nuke": mk(0, "nuke")
        elif k == "sanctioned_by": mk(2, "sanctioned_by", t=e[1])
        elif k == "uprising": mk(2, "uprising")
        elif k in pri_map:
            mk(pri_map[k], k, t=e[1] if len(e) > 1 else "", a=e[1] if len(e) > 1 else "")
        elif k in ("ally_west", "ally_east", "ally", "trade_west", "trade_east", "trade", "pact", "propaganda", "eco", "tech", "mil", "oil_crisis", "boom"):
            pri = {"ally_west": 5, "ally_east": 5, "ally": 7, "trade_west": 7, "trade_east": 7, "trade": 8, "pact": 9, "propaganda": 9, "eco": 10, "tech": 10, "mil": 11, "oil_crisis": 9, "boom": 9}.get(k, 12)
            mk(pri, k, t=e[1] if len(e) > 1 else "")
        elif k == "peace": mk(20, "peace")
    return out

def press_update(s, who, pol, events):
    P = s["player"]
    cands = sorted(canon_events(s, who, events), key=lambda x: x[0])
    press = pol.setdefault("press", [])
    heads = []
    outlets = PRESS_OUTLETS if who == P else AI_OUTLETS
    for oi, outlet in enumerate(outlets):
        head = None
        for pr, key, ctx in cands:
            tpl = outlet["copy"].get(key)
            if tpl:
                head = tpl.format(who=who, **ctx)
                break
        if head is None:
            head = random.choice(outlet["idle"])
        nm = outlet["name"] if who == P else outlet["name_fmt"].format(who=who)
        line = f"📰 «{nm}»: {head}"
        heads.append(line)
        press.append(line)
    cap = 12 if who == P else 4
    del press[:-cap]
    return heads

def parties_update(s, who, pol, events):
    P = s["player"]
    is_p = who == P
    base_map = PARTY_BASE if is_p else AI_PARTY_BASE
    pops = pol.setdefault("parties", dict(base_map))
    d = dict.fromkeys(base_map, 0.0)
    for pr, key, ctx in canon_events(s, who, events):
        if not is_p:
            if key == "eco": d["تجار"] += 2; d["اپوزیسیون"] += 1
            elif key == "tech": d["تجار"] += 1
            elif key == "mil": d["ارتش‌گرایان"] += 2; d["اپوزیسیون"] -= 1
            elif key == "nuke": d["حاکمیت"] += 3; d["ارتش‌گرایان"] += 2; d["اپوزیسیون"] -= 3
            elif key == "war_won": d["حاکمیت"] += 4; d["ارتش‌گرایان"] += 3; d["اپوزیسیون"] -= 2; d["تجار"] -= 1
            elif key == "war_lost": d["حاکمیت"] -= 6; d["ارتش‌گرایان"] -= 2; d["اپوزیسیون"] += 3; d["تجار"] -= 2
            elif key == "war_defended": d["حاکمیت"] += 3; d["ارتش‌گرایان"] += 2
            elif key == "war_attrition": d["حاکمیت"] -= 2; d["اپوزیسیون"] += 1
            elif key in ("sanctioned_by", "kill_victim", "kill_attempt", "sabotage_victim"):
                d["حاکمیت"] += 4; d["ارتش‌گرایان"] += 3; d["اپوزیسیون"] -= 2
            elif key == "sanction": d["ارتش‌گرایان"] += 1
            elif key in ("trade", "trade_west", "trade_east"): d["تجار"] += 2; d["اپوزیسیون"] += 1
            elif key in ("ally", "ally_west", "ally_east"): d["حاکمیت"] += 1; d["تجار"] += 1; d["اپوزیسیون"] += 1
            elif key in ("covert_fail", "kill_fail", "sabotage_fail"): d["حاکمیت"] -= 3; d["اپوزیسیون"] += 2
            elif key == "uprising": d["حاکمیت"] -= 4; d["اپوزیسیون"] += 2
            elif key == "plague": d["حاکمیت"] -= 2; d["تجار"] -= 1
            elif key == "oil_crisis": d["حاکمیت"] -= 2; d["تجار"] -= 1
            elif key == "boom": d["تجار"] += 2; d["اپوزیسیون"] += 1
            elif key == "eco": d["تجار"] += 2
            elif key == "peace": d["اپوزیسیون"] += 1
        else:
            if key == "eco": d["تکنوکرات‌ها"] += 2; d["اصلاح‌طلبان"] += 1.5
            elif key == "tech": d["تکنوکرات‌ها"] += 2.5
            elif key == "mil": d["جبهه انقلاب"] += 2; d["ملی‌گرایان"] += 1; d["اصلاح‌طلبان"] -= 1
            elif key == "nuke": d["جبهه انقلاب"] += 4; d["ملی‌گرایان"] += 2; d["اصلاح‌طلبان"] -= 5; d["تکنوکرات‌ها"] -= 2
            elif key == "ally_west": d["اصلاح‌طلبان"] += 5; d["تکنوکرات‌ها"] += 3; d["جبهه انقلاب"] -= 6; d["ملی‌گرایان"] -= 2
            elif key == "ally_east": d["جبهه انقلاب"] += 3; d["ملی‌گرایان"] += 1
            elif key == "ally": d["اصلاح‌طلبان"] += 1; d["ملی‌گرایان"] += 1; d["تکنوکرات‌ها"] += 1; d["جبهه انقلاب"] += 1
            elif key == "trade_west": d["اصلاح‌طلبان"] += 2; d["جبهه انقلاب"] -= 3; d["تکنوکرات‌ها"] += 2
            elif key == "trade_east": d["جبهه انقلاب"] += 1; d["تکنوکرات‌ها"] += 1
            elif key == "ally": d["جبهه انقلاب"] += 0
            elif key == "trade": d["تکنوکرات‌ها"] += 2; d["اصلاح‌طلبان"] += 1
            elif key == "pact": d["اصلاح‌طلبان"] += 2; d["تکنوکرات‌ها"] += 1
            elif key == "sanction": d["ملی‌گرایان"] += 2; d["جبهه انقلاب"] += 1; d["اصلاح‌طلبان"] -= 1
            elif key == "sanctioned_by": d["جبهه انقلاب"] += 3; d["ملی‌گرایان"] += 2; d["تکنوکرات‌ها"] -= 2; d["اصلاح‌طلبان"] -= 1
            elif key == "covert_ok": d["جبهه انقلاب"] += 2
            elif key == "covert_fail": d["اصلاح‌طلبان"] -= 2; d["تکنوکرات‌ها"] -= 2; d["ملی‌گرایان"] -= 2; d["جبهه انقلاب"] += 1
            elif key == "propaganda": d["جبهه انقلاب"] += 4; d["ملی‌گرایان"] += 3; d["اصلاح‌طلبان"] -= 2; d["تکنوکرات‌ها"] -= 1
            elif key == "sabotage_ok": d["ملی‌گرایان"] += 2; d["جبهه انقلاب"] += 1; d["اصلاح‌طلبان"] -= 1
            elif key == "sabotage_fail": d["اصلاح‌طلبان"] -= 2; d["تکنوکرات‌ها"] -= 2; d["ملی‌گرایان"] -= 2; d["جبهه انقلاب"] += 1
            elif key == "kill_ok": d["جبهه انقلاب"] += 3; d["ملی‌گرایان"] += 2; d["اصلاح‌طلبان"] -= 4; d["تکنوکرات‌ها"] -= 2
            elif key == "kill_fail": d["اصلاح‌طلبان"] -= 3; d["تکنوکرات‌ها"] -= 3; d["ملی‌گرایان"] -= 3; d["جبهه انقلاب"] += 1
            elif key == "kill_victim": d["جبهه انقلاب"] += 6; d["ملی‌گرایان"] += 5
            elif key == "kill_attempt": d["جبهه انقلاب"] += 3; d["ملی‌گرایان"] += 2
            elif key == "sabotage_victim": d["جبهه انقلاب"] += 2; d["ملی‌گرایان"] += 1; d["تکنوکرات‌ها"] -= 1
            elif key == "war_won": d["جبهه انقلاب"] += 4; d["ملی‌گرایان"] += 3; d["اصلاح‌طلبان"] -= 2; d["تکنوکرات‌ها"] -= 1
            elif key == "war_lost": d["جبهه انقلاب"] -= 6; d["ملی‌گرایان"] -= 2; d["اصلاح‌طلبان"] += 2; d["تکنوکرات‌ها"] -= 2
            elif key == "war_defended": d["جبهه انقلاب"] += 3; d["ملی‌گرایان"] += 2; d["اصلاح‌طلبان"] -= 1
            elif key == "war_attrition": d["جبهه انقلاب"] -= 1; d["اصلاح‌طلبان"] += 1
            elif key == "uprising": d["جبهه انقلاب"] -= 4; d["ملی‌گرایان"] -= 2; d["اصلاح‌طلبان"] += 2
            elif key == "plague": d["اصلاح‌طلبان"] -= 1; d["تکنوکرات‌ها"] -= 1; d["جبهه انقلاب"] -= 1; d["ملی‌گرایان"] -= 1
            elif key == "oil_crisis": d["تکنوکرات‌ها"] -= 2; d["اصلاح‌طلبان"] -= 1
            elif key == "boom": d["تکنوکرات‌ها"] += 2; d["اصلاح‌طلبان"] += 2
            elif key == "peace": d["اصلاح‌طلبان"] += 1
    for p in pops:
        v = pops[p] + d[p] + (base_map[p] - pops[p]) * 0.06
        pops[p] = max(5, min(75, v))
    total = sum(pops.values())
    for p in pops:
        pops[p] = round(pops[p] * 100.0 / total, 1)
    if is_p:
        ruling = pops["جبهه انقلاب"] + pops["ملی‌گرایان"]
    else:
        ruling = pops["حاکمیت"] + pops["ارتش‌گرایان"]
    me = s["world"][who]
    if ruling >= 55:
        me["stab"] = min(100, me["stab"] + 1)
    elif ruling <= 35:
        me["stab"] = max(0, me["stab"] - 2)
    if is_p and me["stab"] <= 0:
        end_of_action_checks(s)
    return [f"{p} {pops[p]:.0f}٪" for p in sorted(pops, key=lambda x: -pops[x])]

# ---------- player actions ----------

def do_act(s, args):
    if s["over"]:
        print("بازی تمام شده. با `reset` بازی جدید بساز.")
        return
    if len(args) < 1:
        print(HELP)
        return
    action = args[0].lower()
    W = s["world"]; P = s["player"]; me = W[P]
    NOTARGET = {"eco", "mil", "tech", "nuke", "propaganda", "iaea", "buy", "sell"}
    target = None
    if len(args) >= 2 and action not in NOTARGET:
        target = find_name(s, args[1])
        if target is None:
            print("✗ کشور نامعلوم: " + " ".join(args[1:]))
            return
        if target == P:
            print("✗ نمی‌توانی علیه یا به نفع خودت عمل کنی!")
            return
        if target in s.get("eliminated", []):
            print("✗ این کشور از نقشه حذف شده است.")
            return

    def pay(cost):
        if me["money"] < cost:
            print(f"⚠ بودجه کافی نیست (نیاز: {cost} میلیارد — موجود: {me['money']:.0f})")
            return False
        me["money"] -= cost
        return True

    def spend_turn():
        save(s)

    if action == "eco":
        if not pay(4): return
        me["eco"] += 6; me["stab"] += 1
        msg(s, "سرمایه‌گذاری کلان زیرساختی — اقتصاد رونق گرفت.")
        print(f"✔ اقتصاد بالا رفت → {me['eco']:.0f}")
        ev(s, P, "eco")
    elif action == "mil":
        if not pay(5): return
        me["mil"] += 7; me["stab"] -= 2
        msg(s, "بودجه دفاعی سنگین تخصیص یافت.")
        print(f"✔ ارتش تقویت شد → {me['mil']:.0f} (ثبات -۲)")
        ev(s, P, "mil")
    elif action == "tech":
        if not pay(4): return
        me["tech"] += 7; me["eco"] += 1
        print(f"✔ پیشرفت فناوری → {me['tech']:.0f}")
        ev(s, P, "tech")
    elif action == "nuke":
        if me["tech"] < 70:
            print("✗ برای برنامه هسته‌ای فناوری ≥ 70 لازم است.")
            return
        if not pay(12): return
        me["nukes"] += 1
        msg(s, f"{P} آزمایش هسته‌ای جدیدی انجام داد! جهان نگران شد.")
        for o in W:
            if o != P: add_rel(s, P, o, -12)
        print(f"☢ کلاهک ساخته شد → مجموع: {me['nukes']} (محکومیت جهانی، روابط همه -12)")
        if P not in NUKES0 and not s.get("iaea_out"):
            s["iaea_heat"] = s.get("iaea_heat", 0) + 1
            heat = s["iaea_heat"]
            if heat >= 3:
                print("🇺🇳 آژانس بین‌المللی انرژی اتمی: برنامه هسته‌ای تو «غیرقانونی» اعلام شد!")
            else:
                print(f"🔍 آژانس انرژی اتمی پرونده تو را باز کرد (سطح فشار {heat}/3) — با `act iaea` یا منوی نهادها شفافیت اعلام کن.")
        nw = [o for o in W if o != P and not (W[o]["nukes"] or o in NUKES0) and get_rel(s, P, o) < 40]
        random.shuffle(nw)
        sanctioned = nw[:3]
        if sanctioned:
            for o in sanctioned:
                me["eco"] = max(10, me["eco"] - 2)
                add_rel(s, P, o, -25)
                msg(s, f"🇺🇳 {o} به نشانه اعتراض به آزمایش هسته‌ای، تحریم اقتصادی علیه {P} وضع کرد.")
                print(f"⛔ تحریم از سوی {o}: اقتصاد تو -2، روابط -25")
            ev(s, P, "sanction", sanctioned[0])
        if me["nukes"] >= 3:
            s["un_censures"] = s.get("un_censures", 0) + 1
            me["stab"] = max(0, me["stab"] - 3)
            msg(s, f"🇺🇳 شورای امنیت برای بار {s['un_censures']}م {P} را محکوم کرد (ثبات -3).")
            print("🇺🇳 شورای امنیت سازمان ملل تو را محکوم کرد (ثبات -3، پرونده در `dash نهاد`).")
        ev(s, P, "nuke")
    elif action == "buy":
        if len(args) < 2:
            print("✗ نام تجهیز لازم است: `act buy F-35A` — فهرست تجهیزات: `dash mil`")
            return
        toks = args[1:]
        cnt = 1
        if toks and toks[-1].isdigit() and find_item(" ".join(toks[:-1])):
            cnt = max(1, int(toks[-1])); toks = toks[:-1]
        key = find_item(" ".join(toks))
        if key is None:
            print("✗ چنین تجهیزی فروخته نمی‌شود. فهرست: `dash mil`")
            return
        item = ARSENAL_ITEMS[key]; maker = item["mk"]
        if maker in s.get("eliminated", []):
            print("✗ سازندهٔ این تجهیز از نقشه حذف شده؛ از بازار جایگزین استفاده کن.")
            return
        if maker != P:
            if maker in s["at_war"]:
                print(f"✗ با سازنده ({maker}) در حال جنگید!")
                return
            rel = get_rel(s, P, maker)
            if rel < 10:
                print(f"✗ روابطت با {maker} کم است (نیاز ≥10) — اول دیپلماسی.")
                return
            if item["hi"] and rel < 30:
                print(f"✗ {key} از جنس فناوری پیشرفته است؛ فروش فقط با روابط ≥30 با {maker}.")
                return
            premium = 1.0 if rel >= 60 else (1.3 if rel >= 30 else 1.6)
        else:
            premium = 0.7
        cost = round(item["pr"] * cnt * premium, 2)
        if me["money"] < cost:
            print(f"⚠ بودجه کافی نیست (نیاز: {cost} — موجود: {me['money']:.0f})")
            return
        me["money"] -= cost
        if maker != P:
            W[maker]["money"] += cost * 0.7
            add_rel(s, P, maker, 3)
        s["arsenal"].setdefault(P, {})
        s["arsenal"][P][key] = s["arsenal"][P].get(key, 0) + cnt
        me["_arsenal"] = s["arsenal"][P]
        msg(s, f"🛒 {P} {cnt}× «{key}» را به ارزش {cost} میلیارد وارد زرادخانه کرد.")
        ev(s, P, "mil")
        print(f"✔ تحویل شد: {cnt}× {key} → زرادخانه (هزینه {cost} میلیارد)")
    elif action == "sell":
        if len(args) < 3:
            print("✗ شکل فرمان: `act sell <تجهیز> <کشور>`")
            return
        key = find_item(" ".join(args[1:-1]))
        buyer = find_name(s, args[-1])
        if key is None:
            print("✗ چنین تجهیزی در زرادخانه‌ای نیست.")
            return
        if buyer is None or buyer == P:
            print("✗ خریدار نامعتبر است.")
            return
        if buyer in s.get("eliminated", []):
            print("✗ این کشور از نقشه حذف شده.")
            return
        if get_rel(s, P, buyer) <= 20:
            print("✗ خریدار حاضر به معامله نیست (روابط >20 لازم).")
            return
        ars = s["arsenal"].setdefault(P, {})
        me["_arsenal"] = ars
        if ars.get(key, 0) < 1:
            print(f"✗ «{key}» در زرادخانه تو نیست.")
            return
        item = ARSENAL_ITEMS[key]
        gain = round(item["pr"] * 0.5, 2)
        ars[key] -= 1
        if ars[key] <= 0: del ars[key]
        me["money"] += gain
        W[buyer]["money"] = max(0, W[buyer]["money"] - gain)
        W[buyer]["mil"] = min(100, W[buyer]["mil"] + item["m"] * 0.25)
        s["arsenal"].setdefault(buyer, {})
        s["arsenal"][buyer][key] = s["arsenal"][buyer].get(key, 0) + 1
        W[buyer]["_arsenal"] = s["arsenal"][buyer]
        add_rel(s, P, buyer, 5)
        msg(s, f"🤝 {P} یک «{key}» به {buyer} فروخت ({gain} میلیارد).")
        ev(s, P, "trade", buyer)
        print(f"✔ فروش: 1× {key} به {buyer} → +{gain} میلیارد، روابط +5")
    elif action == "iaea":
        if s.get("iaea_out"):
            print("✗ تو از اژانس خارج شده‌ای؛ با «decide freeze» مسیر مذاکرات را باز کن.")
        if not pay(3): return
        s["iaea_heat"] = 0
        msg(s, f"{P} با آژانس بین‌المللی انرژی اتمی تفاهم‌نامه شفافیت امضا کرد.")
        print("🇺🇳 بازرسان پرونده تو را مختومه اعلام کردند؛ فشار آژانس صفر شد.")
    elif action == "un":
        if target is None:
            print("\u2717 \u06a9\u0634\u0648\u0631 \u0645\u0648\u0631\u062f \u062a\u0639\u0631\u06cc\u0641 \u0631\u0627 \u0628\u0646\u0648\u06cc\u0633: `act un \u06a9\u06cc\u0648\u0627\u0646`")
            return
        if target == P:
            print("\u2717 \u0646\u0645\u06cc\u200c\u062a\u0648\u0627\u0646\u06cc \u062e\u0648\u062f\u062a \u0631\u0627 \u062f\u0631 \u0633\u0627\u0632\u0645\u0627\u0646 \u0645\u0644\u0644 \u062a\u0639\u0631\u06cc\u0641 \u06a9\u0646\u06cc.")
            return
        tg = W[target]
        ch = 0.4 + me.get("influence", 0) / 500
        if P not in NUKES0:
            ch -= 0.1
        if random.random() < ch:
            tg["stab"] = max(0, tg["stab"] - 2)
            others = [n for n in W if n not in (P, target)]
            for n in others:
                add_rel(s, n, target, -5)
                add_rel(s, P, n, 2)
            msg(s, f"\U0001F1FA\U0001F1F3 \u0645\u062c\u0645\u0639 \u0639\u0645\u0648\u0645\u06cc \u0633\u0627\u0632\u0645\u0627\u0646 \u0645\u0644\u0644 \u0628\u0627 \u062a\u0648\u0635\u06cc\u0647 {P}\u060c {target} \u0631\u0627 \u0628\u0647 \u062e\u0627\u0637\u0631 \u0646\u0627\u0628\u0647\u0648\u0627\u06cc\u06cc \u0645\u0646\u0637\u0642\u0647\u200c\u0627\u06cc \u062a\u0639\u0631\u06cc\u0641 \u06a9\u0631\u062f.")
            print(f"\u2714 \u0637\u0648\u0645\u0627\u0631 \u0645\u0648\u0641\u0642 \u0628\u0648\u062f: \u0627\u0628\u0631\u0648\u0647 {target} \u062f\u0631 \u062c\u0647\u0627\u0646 \u0627\u0641\u062a \u06a9\u0631\u062f (\u062b\u0627\u0628\u062a \u22122\u060c \u0631\u0648\u0627\u0628\u0637\u0634 \u0628\u0627 \u0628\u0642\u06cc\u0647 \u22125).")
        else:
            print(f"\u2717 \u062a\u0648\u0645\u0627\u0631 \u0634\u06a9\u0633\u062a \u062e\u0648\u0631\u062f; \u0628\u0644\u0648\u06a9 \u0631\u0648\u0627\u0628\u0637 \u062c\u0644\u0648 \u062a\u0635\u0648\u06cc\u062a \u0631\u0627 \u06af\u0631\u0641\u062a.")
    elif action == "spy":
        if not pay(2): return
        t = W[target]
        add_rel(s, P, target, -5)
        if random.random() < 0.75:
            msg(s, f"جاسوسان در {target} اطلاعات نظامی کیف‌کردند.")
            print(f"🕵 گزارش از {target}: ارتش {t['mil']:.0f} | اقتصاد {t['eco']:.0f} | فناوری {t['tech']:.0f} | ثبات {t['stab']:.0f} | کلاهک: {t['nukes']}")
        else:
            print(f"⚠ مأمور لو رفت! آبرو رفت (روابط {P}–{target} افت کرد).")
    elif action == "aide":
        if target is None: print("✗ کشور مقصد را بنویس: `act aide کیوان`"); return
        if not pay(3): return
        add_rel(s, P, target, 14)
        t = W[target]; t["eco"] += 2
        print(f"✔ کمک اقتصادی به {target} — روابط +۱۴")
    elif action == "trade":
        if target is None: print("✗ کشور مقصد را بنویس."); return
        if not pay(2): return
        rel_before = get_rel(s, P, target)
        if rel_before < -40:
            print(f"✗ {target} حاضر به معامله با شما نیست (روابط {rel_before:.0f}). اول روابط را جور کن.")
            me["money"] += 20
            return
        me["eco"] += 3; W[target]["eco"] += 2; add_rel(s, P, target, 8)
        print(f"✔ قرارداد تجاری با {target} — اقتصاد +۳، روابط +۸")
        ev(s, P, "trade", target)
    elif action == "pact":
        if target is None: print("✗ کشور مقصد را بنویس."); return
        if target in s["pacts"]: print("⚠ پیمان عدم تجاوز از قبل هست."); return
        if not pay(1): return
        if get_rel(s, P, target) >= 35 and random.random() < 0.85:
            s["pacts"].append(target)
            add_rel(s, P, target, 8)
            print(f"📜 پیمان عدم تجاوز با {target} امضا شد.")
            ev(s, P, "pact", target)
        else:
            print(f"✗ {target} پیشنهاد را رد کرد (روابط کافی نیست).")
    elif action == "ally":
        if target is None: print("✗ کشور مقصد را بنویس."); return
        if target in s["allies"]: print("⚠ از قبل متحدید."); return
        if target in s["at_war"]: print("✗ در حال جنگیدن با او هستید!"); return
        if not pay(3): return
        if get_rel(s, P, target) >= 65 and random.random() < 0.8:
            s["allies"].append(target)
            s["pacts"] = [p for p in s["pacts"] if p != target]
            add_rel(s, P, target, 10)
            msg(s, f"{P} و {target} پیمان اتحاد نظامی امضا کردند.")
            print(f"🤝 اتحاد نظامی با {target} بسته شد!")
            ev(s, P, "ally", target)
        else:
            print(f"✗ {target} اتحاد را رد کرد — روابط ≥ ۶۵ لازم است.")
    elif action == "sanc":
        if target is None: print("✗ کشور مقصد را بنویس."); return
        t = W[target]
        loss = min(t["eco"], 5)
        t["eco"] -= loss; t["stab"] -= 3; me["eco"] -= 2
        add_rel(s, P, target, -25)
        msg(s, f"{P} علیه {target} تحریم اقتصادی اعلام کرد.")
        print(f"⛔ {target} تحریم شد — اقتصادش -{loss:.0f} (اقتصاد خودت -۲، روابط -۲۵)")
        ev(s, P, "sanction", target)
    elif action == "covert":
        if target is None: print("✗ کشور مقصد را بنویس."); return
        if not pay(5): return
        t = W[target]
        if random.random() < 0.55:
            t["stab"] -= 12
            msg(s, f"شایعه: عوامل ناشناس در {target} آشوب به‌پا کردند.")
            print(f"✔ بی‌ثباتی در {target} ایجاد شد — ثباتش -۱۲ (اکنون {t['stab']:.0f})")
            ev(s, P, "covert_ok", target)
        else:
            me["stab"] -= 5
            rels = [o for o in W if o not in (P, target)]
            for o in rels: add_rel(s, P, o, -6)
            print(f"⚠ عملیات کشف شد! ثبات خودت -۵ و روابط با بقیه آسیب دید.")
            ev(s, P, "covert_fail", target)
    elif action == "propaganda":
        if not pay(2): return
        ev(s, P, "propaganda")
        me["stab"] -= 1
        msg(s, "کمپین تبلیغاتی گسترده در داخل راه افتاد؛ فضای سیاسی دوقطبی شد.")
        print("📢 تبلیغات حزبی: حمایت ائتلاف حاکم بالا رفت (ثبات -۱)")
    elif action == "sabotage":
        if target is None: print("✗ هدف را مشخص کن: `act sabotage روسیه`"); return
        if not pay(5): return
        t = W[target]
        if random.random() < 0.55:
            t["mil"] = max(10, t["mil"] - 6); t["eco"] -= 2
            msg(s, f"انفجار در تأسیسات دفاعی {target}؛ اقتصاد نیز ضربه خورد.")
            print(f"💥 خرابکاری در {target} — ارتشش -۶، اقتصادش -۲")
            ev(s, P, "sabotage_ok", target); ev(s, target, "sabotage_victim", P)
        else:
            me["stab"] -= 3; add_rel(s, P, target, -15)
            for o in W:
                if o not in (P, target): add_rel(s, P, o, -5)
            print(f"⚠ خرابکاری لو رفت! عوامل دستگیر شدند (ثبات -۳، اعتبار آسیب دید)")
            ev(s, P, "sabotage_fail", target)
    elif action == "kill":
        if target is None: print("✗ هدف را مشخص کن: `act kill روسیه`"); return
        if not pay(8): return
        t = W[target]
        p = 0.25 if t["nukes"] else 0.35
        if random.random() < p:
            t["stab"] -= 15; t["eco"] -= 4; t["tech"] = max(10, t["tech"] - 2)
            msg(s, f"رهبر {target} ترور شد! اشاره‌ها به {P}؛ محکومیت جهانی.")
            print(f"☠ ترور موفق: رهبر {target} کشته شد! دوره گذار و آشوب ({target}: ثبات -۱۵، اقتصاد -۴)")
            add_rel(s, P, target, -35)
            for o in W:
                if o not in (P, target): add_rel(s, P, o, -8)
            ev(s, P, "kill_ok", target); ev(s, target, "kill_victim", P)
        else:
            me["stab"] -= 6; add_rel(s, P, target, -30)
            for o in W:
                if o not in (P, target): add_rel(s, P, o, -10)
            print(f"⚠ ترور شکست خورد و شبکه لو رفت! محکومیت جهانی (ثبات -۶، روابط تو -۱۰ برای همه)")
            ev(s, P, "kill_fail", target); ev(s, target, "kill_attempt", P)
    elif action == "proxy":
        if target is None:
            print("✂ کشور میزبان را مشخص کن: `act proxy فلسطین`")
            return
        if target in s["allies"]:
            print("✗ به متحد خود نمی‌توانی شبکه نیابتی نفوذ بدهی!")
            return
        existing = [x for x in s.get("proxies", []) if x["sponsor"] == P and x["host"] == target]
        cost = 4 if existing else 6
        if not pay(cost):
            return
        t = W[target]
        ok = 0.5 + (100 - t["stab"]) / 250
        roll = random.random()
        if roll < ok:
            if existing:
                if existing[0]["power"] >= 5:
                    me["money"] += cost
                    print(f"⚠ شبکه نیابتی در {target} از قبل در اوج قدرت (۵/۵) است.")
                    return
                existing[0]["power"] += 1
                t["stab"] = max(0, t["stab"] - 2)
                add_rel(s, P, target, -8)
                print(f"🕵 شبکه نیابتی تو در {target} تقویت شد → قدرت {existing[0]['power']}/۵ (مخفی)")
            else:
                s["proxies"].append({"sponsor": P, "host": target, "power": 2, "hidden": True, "name": proxy_label(P, target)})
                t["stab"] = max(0, t["stab"] - 5)
                add_rel(s, P, target, -15)
                print(f"🕵 شبکه نیابتی در {target} ایجاد شد (قدرت ۲/۵). این عملیات مخفی است — پیگیری در `dash ops`")
                ev(s, P, "covert_ok", target)
        else:
            me["stab"] = max(0, me["stab"] - 3)
            t["stab"] = max(0, t["stab"] - 3)
            add_rel(s, P, target, -20)
            print(f"⚠ مأموران در {target} لو رفتند و اخراج شدند! (ثبات تو -۳، روابط -۲۰)")
            ev(s, P, "covert_fail", target)
    elif action == "war":
        if target is None: print("✗ دشمن را مشخص کن: `act war هیرمند`"); return
        if target in s["allies"]: print("✗ به متحد نمی‌شود اعلام جنگ کرد! اول `act break` بزن."); return
        start_war(s, P, target)
    elif action == "break":
        if target is None: print("✗ کشور را بنویس."); return
        if target in s["allies"]:
            s["allies"].remove(target); add_rel(s, P, target, -30)
            print(f"💔 اتحاد با {target} برهم خورد.")
        elif target in s["pacts"]:
            s["pacts"].remove(target); add_rel(s, P, target, -20)
            print(f"💔 پیمان عدم تجاوز با {target} لغو شد.")
        else:
            print("⚠ پیمانی با این کشور نداری.")
    else:
        print("✗ فرمان ناشناخته. `help` بزن.")
        return
    ai_react(s, action, target)
    # پیامدهای مشترک
    spend_turn()

# ---------- war ----------

def start_war(s, atk, dfn):
    W = s["world"]
    A, D = W[atk], W[dfn]
    if dfn in s["at_war"]: print("⚠ همین الان با او در جنگی!"); return
    atk_pow = power(A) * (1.25 if atk == s["player"] else 1.0)
    dfn_pow = power(D)
    d_allies = [x for x in s["allies"] if x != atk and get_rel(s, x, dfn) > 50]
    for x in d_allies:
        dfn_pow += power(W[x]) * 0.3
    nato_help = []
    if dfn in NATO and atk not in NATO:
        top_nato = sorted([n for n in NATO if n in W and n not in s["eliminated"] and n not in (atk, dfn)],
                          key=lambda n: -power(W[n]))[:5]
        for n in top_nato:
            dfn_pow += power(W[n]) * 0.12
        nato_help = top_nato
        if nato_help:
            print("🛡 ناتو پیمان دفاع مشترک را فعال کرد؛ حمایت: " + "، ".join(nato_help[:3]))
            msg(s, "🛡 ناتو مادهٔ ۵ را برای حمایت از " + dfn + " فعال کرد.")
    a_allies = [x for x in W if x != atk and x in s["allies"] and x != dfn]
    for x in a_allies:
        atk_pow += power(W[x]) * 0.25
    for x in W:
        if x not in (atk, dfn):
            add_rel(s, atk, x, -10 if x == dfn or x == s["player"] else -4)
    s["at_war"] += [atk, dfn]
    msg(s, f"⚔ جنگ! {atk} به {dfn} حمله کرد.")
    if atk == s["player"] and dfn in NATO and atk not in NATO:
        joiners = sorted([n for n in NATO if n in W and n not in s["eliminated"] and n not in (atk, dfn)],
                         key=lambda n: -power(W[n]))[:3]
        for n in joiners:
            s["at_war"] += [n, atk]
            add_rel(s, n, atk, -30)
        if joiners:
            print("🛡 پاسخ ناتو: " + "، ".join(joiners) + " علیه تو وارد جنگ شدند!")
            msg(s, "⚔ اعضای ناتو " + "، ".join(joiners) + " به نفع " + dfn + " به جنگ شتافتند.")
    ratio = atk_pow / max(1.0, dfn_pow)
    r = random.uniform(0.85, 1.15)
    ratio *= r
    print("═" * 46)
    print(f"⚔ جنگ «{atk}» علیه «{dfn}» آغاز شد!")
    print(f"  قدرت مهاجم: {atk_pow:.0f}  |  قدرت مدافع: {dfn_pow:.0f}")
    if D["nukes"] and ratio < 2.0:
        print("☢ مدافع هسته‌ای است! مهاجم فقط می‌تواند تهاجم محدود انجام دهد.")
        ratio = min(ratio, 1.25)
    _wres = "won" if ratio >= 1.0 else "lost"
    ev(s, atk, "war_result", atk, dfn, _wres)
    ev(s, dfn, "war_result", atk, dfn, _wres)
    if ratio >= 1.0:
        gain = int(round((ratio - 0.8) * 10 + 6))
        A["influence"] += gain
        spoils = min(D["money"], 40 + gain * 2)
        A["money"] += spoils; D["money"] -= spoils
        D["mil"] = max(10, D["mil"] - 12); D["stab"] -= 10; D["eco"] -= 6
        A["mil"] = max(10, A["mil"] - 7); A["stab"] -= 4; A["eco"] -= 3
        print(f"🏆 پیروزی {atk}! نفوذ +{gain}، غنیمت {spoils:.0f} میلیارد، ارتش مدافع شکست.")
        if D["stab"] <= 10 and ratio >= 2.5:
            annex(s, atk, dfn)
        elif D["stab"] <= 15:
            print(f"⚠ {dfn} در آستانه فروپاشی است...")
    else:
        back = int(round((1 / max(ratio, 0.2) - 0.8) * 10 + 6))
        D["influence"] += back
        A["mil"] = max(10, A["mil"] - 14); A["stab"] -= 10; A["eco"] -= 6
        D["mil"] = max(10, D["mil"] - 6); D["stab"] -= 3
        print(f"🛡 {dfn} دفاع کرد و حمله را شکست! {atk} متحمل شکست سنگین شد (نفوذ {dfn} +{back}).")
        if atk == s["player"] and A["stab"] <= 15:
            print("⚠ شکست در جنگ، مردم را به خیابان کشانده...")
    s["at_war"] = list(dict.fromkeys(s["at_war"]))
    if s["player"] in s["at_war"]:
        s["at_war"] = [x for x in s["at_war"] if x != s["player"] and x != dfn] if s["player"] == atk else [x for x in s["at_war"] if x != s["player"] and x != atk]
    end_of_action_checks(s)
    save(s)

def annex(s, winner, loser):
    W = s["world"]; v = W[loser]; wc = W[winner]
    wc["mil"] += 5; wc["eco"] += 8; wc["influence"] += 15; wc["money"] += v["money"] * 0.5
    v["money"] = 0
    for o in W:
        if o not in (winner, loser):
            add_rel(s, winner, o, -12)
    s["un_censures"] = s.get("un_censures", 0) + 1
    wc["stab"] = max(0, wc["stab"] - 3)
    msg(s, "🇺🇳 مجمع عمومی سازمان ملل این حمله را محکوم کرد و اعتبار " + winner + " در جهان زیر سئوال رفت (ثبات -3).")
    print("🇺🇳 مجمع عمومی سازمان ملل الحاق «" + loser + "» را محکوم کرد (ثبات " + winner + ": -3).")
    if loser in s["allies"]: s["allies"].remove(loser)
    if loser in s["pacts"]: s["pacts"].remove(loser)
    s["eliminated"].append(loser)
    pairs = [s["at_war"][i:i + 2] for i in range(0, len(s["at_war"]) - 1, 2)]
    s["at_war"] = [x for pr in pairs
                   if loser not in pr and winner not in pr
                   for x in pr]
    v["stab"] = 0
    v["vassal_of"] = winner
    msg(s, f"⚑ {loser} ضمیمه {winner} شد و از نقشه جهان حذف شد!")
    print(f"⚑⚑ {winner} کشور {loser} را ضمیمه کرد! کشور از نقشه حذف شد.")
    if loser == s["player"]:
        s["over"] = True
        print("💀💀 کشور تو سقوط کرد و به تاریخ پیوست. GAME OVER 💀💀")

def end_of_action_checks(s):
    """بررسی فوری پیامدها؛ بحران داخلی در پایان روز ثبت می‌شود، نه Game Over."""
    me = s["world"][s["player"]]
    if me["stab"] <= 0:
        # آستانه بحران داخلی (<10) در check_player_regime_crisis و انتهای روز
        # ثبت می‌شود. افت ثبات به صفر به‌تنهایی به معنی سقوط قطعی حکومت نیست.
        # پایان بازی فقط از مسیرهای مستقل و صریح مانند حذف کشور بازیکن رخ می‌دهد.
        return

# ---------- turn resolution ----------

def _reform_party_impact(s, proposal, fraction, reverse=False):
    """اعمال تدریجی واکنش احزاب موجود؛ بدون ساخت احزاب یا کشور AI جدید."""
    player = s.get("player")
    politics = s.setdefault("politics", {})
    base = PARTY_BASE
    pol = politics.setdefault(player, {"parties": dict(base), "press": []})
    parties = pol.setdefault("parties", dict(base))
    reactions = ((proposal.get("review") or {}).get("party_reactions") or {})
    direction = -1.0 if reverse else 1.0
    for party, reaction in reactions.items():
        if party not in parties:
            continue
        delta = float(reaction.get("projected_change", 0)) * float(fraction) * direction
        parties[party] = max(0.0, min(100.0, float(parties.get(party, 0)) + delta))
    total = sum(max(0.0, float(v)) for v in parties.values())
    if total > 0:
        for party in list(parties):
            parties[party] = round(max(0.0, float(parties[party])) * 100.0 / total, 1)


def _reform_social_impact(s, proposal, fraction, reverse=False):
    """اعمال تدریجی تغییر حمایت گروه‌های اجتماعی؛ مقادیر نمایشی و شبیه‌سازی‌شده‌اند."""
    player = s.get("player")
    all_groups = s.setdefault("social_groups", {})
    groups = all_groups.setdefault(player, dict(SOCIAL_GROUP_BASE))
    reactions = ((proposal.get("review") or {}).get("social_reactions") or {})
    direction = -1.0 if reverse else 1.0
    for group_name, reaction in reactions.items():
        if group_name not in groups:
            continue
        delta = float(reaction.get("projected_change", 0)) * float(fraction) * direction
        groups[group_name] = max(0.0, min(100.0, float(groups.get(group_name, 0)) + delta))
    for group_name in list(groups):
        groups[group_name] = round(max(0.0, min(100.0, float(groups[group_name]))), 1)


def _reform_press_line(s, proposal, stage, detail):
    """ثبت تیتر اصلاحات در همان آرشیو مطبوعات داخلی بازی."""
    player = s.get("player", "کشور بازیکن")
    pol = s.setdefault("politics", {}).setdefault(
        player, {"parties": dict(PARTY_BASE), "press": []})
    press = pol.setdefault("press", [])
    label = {
        "start": "آغاز اجرای طرح",
        "midpoint": "ادامه اجرای طرح",
        "completed": "پایان اصلاحات",
        "failed": "ناکامی اصلاحات",
        "crisis": "توقف در بحران سیاسی",
        "resumed": "ازسرگیری اجرای طرح"
    }.get(stage, "تحولات اصلاحات")
    line = "📰 «رسانه‌های داخلی»: %s شماره %s؛ %s" % (
        label, proposal.get("id"), detail)
    press.append(line)
    del press[:-12]
    proposal.setdefault("impact", {}).setdefault("headlines", []).append(line)
    proposal["impact"]["headlines"] = proposal["impact"]["headlines"][-8:]
    return line


def _reform_impact_profile(proposal):
    fields = set((proposal.get("changes") or {}).keys())
    themes = []
    responses = []
    if fields.intersection(set(["official_ideology", "ruling_party_ideology", "ruling_coalition_ideology"])):
        themes.append("ایدئولوژیک")
        responses.append("احتمال قطبی‌شدن فضای سیاسی و فرهنگی")
    if fields.intersection(set(["government_form", "government_subform",
                                "executive_legislative_system", "regime_character"])):
        themes.append("نهادی و حکومتی")
        responses.append("بحث و چانه‌زنی درباره توزیع اختیارات نهادها")
    if "territorial_structure" in fields:
        themes.append("سرزمینی")
        responses.append("واکنش متفاوت مناطق و نهادهای مرکزی به بازتوزیع اختیارات")
    if "party_system" in fields:
        themes.append("حزبی")
        responses.append("بازآرایی رقابت و ائتلاف میان احزاب")
    if "گروه‌های اجتماعی" not in themes:
        themes.append("گروه‌های اجتماعی")
    if not themes:
        themes.append("سیاسی")
        responses.append("واکنش عمومی محدود به دامنه تغییرات")
    responses.append("تغییر حمایت گروه‌های اجتماعی به‌صورت عددی و مرحله‌ای شبیه‌سازی می‌شود")
    return {"themes": themes, "public_response": responses,
            "risk_note": "این پیامدها برآورد شبیه‌سازی بازی هستند، نه پیش‌بینی قطعی رویدادهای واقعی."}


def advance_player_political_reforms(s, daily_log):
    """اجرای روزانه طرح مصوب؛ فقط برای کشور بازیکن و بدون دخالت AI."""
    player = s.get("player")
    country = (s.get("world") or {}).get(player)
    if not isinstance(country, dict):
        return
    for proposal in (s.get("political_reform_proposals") or []):
        if proposal.get("country") != player or proposal.get("status") not in (
                "approved", "executing", "paused_funds", "paused_crisis"):
            continue

        stability = float(country.get("stab", 0))
        if stability < 15:
            if proposal.get("status") != "paused_crisis":
                proposal["status"] = "paused_crisis"
                proposal["last_update_date"] = s.get("game_date", "")
                impact = proposal.setdefault("impact", _reform_impact_profile(proposal))
                line = _reform_press_line(
                    s, proposal, "crisis",
                    "به‌دلیل افت ثبات داخلی، ادامه طرح موقتاً به تعویق افتاد.")
                daily_log.append(line)
            continue
        if proposal.get("status") == "paused_crisis":
            proposal["status"] = "executing"
            line = _reform_press_line(
                s, proposal, "resumed",
                "با بهبود شرایط سیاسی، روند اجرای طرح از سر گرفته شد.")
            daily_log.append(line)

        total_days = max(1, int(proposal.get("estimated_days", 1)))
        total_cost = max(0.0, float(proposal.get("estimated_cost", 0)))
        installment = total_cost / float(total_days)
        treasury = max(0.0, float(country.get("money", 0)))
        if treasury + 0.000001 < installment:
            if proposal.get("status") != "paused_funds":
                proposal["status"] = "paused_funds"
                proposal["last_update_date"] = s.get("game_date", "")
                daily_log.append("⏸ اجرای طرح اصلاحات سیاسی شماره %s به‌دلیل کمبود بودجه متوقف شد." % proposal.get("id"))
            continue

        if proposal.get("status") == "paused_funds":
            proposal["status"] = "executing"
            daily_log.append("▶️ اعتبار طرح اصلاحات سیاسی شماره %s تأمین شد و اجرا ادامه یافت." % proposal.get("id"))

        country["money"] = max(0.0, treasury - installment)
        proposal["status"] = "executing"
        proposal["elapsed_days"] = min(total_days, int(proposal.get("elapsed_days", 0)) + 1)
        proposal["progress"] = round(100.0 * proposal["elapsed_days"] / total_days, 1)
        proposal["spent_cost"] = round(float(proposal.get("spent_cost", 0)) + installment, 2)
        proposal["last_update_date"] = s.get("game_date", "")
        impact = proposal.setdefault("impact", _reform_impact_profile(proposal))
        stages = proposal.setdefault("impact_stages_applied", [])

        if "start" not in stages:
            _reform_party_impact(s, proposal, 0.25)
            _reform_social_impact(s, proposal, 0.25)
            stages.append("start")
            line = _reform_press_line(
                s, proposal, "start",
                "اجرای مرحله‌ای آغاز شد؛ محورهای اصلی: %s." % "، ".join(impact.get("themes", [])))
            daily_log.append(line)

        midpoint = max(2, int((total_days + 1) / 2))
        if proposal["elapsed_days"] >= midpoint and "midpoint" not in stages:
            _reform_party_impact(s, proposal, 0.50)
            _reform_social_impact(s, proposal, 0.50)
            stages.append("midpoint")
            line = _reform_press_line(
                s, proposal, "midpoint",
                "با پیشرفت %s٪، واکنش احزاب و گروه‌های اجتماعی همچنان در حال شکل‌گیری است." %
                proposal["progress"])
            daily_log.append(line)

        if proposal["elapsed_days"] < total_days:
            if proposal["elapsed_days"] == 1 or proposal["elapsed_days"] % 5 == 0:
                daily_log.append("🏛 اجرای طرح اصلاحات سیاسی شماره %s: پیشرفت %s٪." %
                                 (proposal.get("id"), proposal["progress"]))
            continue

        review = proposal.get("review") or {}
        if float(review.get("feasibility", 0)) < 25:
            proposal["status"] = "failed"
            proposal["progress"] = 100
            country["stab"] = max(0.0, float(country.get("stab", 0)) - 4.0)
            proposal["completed_date"] = s.get("game_date", "")
            _reform_party_impact(s, proposal, 0.75, reverse=True)
            _reform_social_impact(s, proposal, 0.75, reverse=True)
            line = _reform_press_line(
                s, proposal, "failed",
                "طرح پس از طی مراحل اجرایی به نتیجه نرسید و تغییرات نهایی اعمال نشد.")
            daily_log.append(line)
            continue

        state = s.setdefault("political_state", {})
        current = state.setdefault(player, {})
        for field, value in (proposal.get("changes") or {}).items():
            current[field] = value.get("new") if isinstance(value, dict) and "new" in value else value

        _reform_party_impact(s, proposal, 0.25)
        _reform_social_impact(s, proposal, 0.25)
        if "completed" not in stages:
            stages.append("completed")
        scope = len(proposal.get("changes") or {})
        stability_cost = min(8.0, 1.0 + scope * 1.2)
        country["stab"] = max(0.0, min(100.0, float(country.get("stab", 0)) - stability_cost))
        proposal["status"] = "completed"
        proposal["progress"] = 100
        proposal["completed_date"] = s.get("game_date", "")
        proposal["spent_cost"] = round(total_cost, 2)
        final_groups = dict(s.get("social_groups", {}).get(player, {}))
        impact["social_groups_final"] = final_groups
        history_item = {
            "date": s.get("game_date", ""), "country": player,
            "proposal_id": proposal.get("id"), "changes": proposal.get("changes", {}),
            "status": "completed", "impact": impact,
            "social_groups_final": final_groups,
            "social_score_at_review": (review.get("social_score") if review else None)
        }
        s.setdefault("political_history", []).append(history_item)
        line = _reform_press_line(
            s, proposal, "completed",
            "طرح با موفقیت به پایان رسید؛ تغییرات سیاسی در ساختار کشور ثبت شد.")
        daily_log.append(line)
        daily_log.append("✅ اصلاحات سیاسی طرح شماره %s با موفقیت اجرا شد." % proposal.get("id"))
        break


def _crisis_institution_profile(political, crisis_kind):
    """انتخاب نهاد سیاسی متناظر با ساختار ثبت‌شده کشور؛ بدون فرض نهاد ناموجود."""
    political = political if isinstance(political, dict) else {}
    system = political.get("executive_legislative_system") or "unknown"
    form = political.get("government_form") or "unknown"
    subform = political.get("government_subform") or "unknown"

    profiles = {
        "parliamentary": ("پارلمان و ائتلاف‌های حزبی", "ساختار پارلمانی"),
        "presidential": ("کنگره یا مجلس قانون‌گذاری و نهادهای نظارتی", "ساختار ریاستی"),
        "semi_presidential": ("پارلمان و نهاد ریاست‌جمهوری", "ساختار نیمه‌ریاستی"),
        "directorial": ("شورای اجرایی و مجلس قانون‌گذاری", "ساختار شورایی/دایرکتوری"),
        "monarchical_executive": ("دربار یا شورای سلطنتی و نهاد مشورتی موجود", "ساختار اجرایی پادشاهی"),
        "one_party": ("رهبری حزب حاکم و نهاد قانون‌گذاری موجود", "ساختار تک‌حزبی"),
        "military_council": ("شورای عالی نظامی", "ساختار شورای نظامی"),
        "transitional": ("شورای انتقالی و نهادهای نمایندگی موجود", "ساختار انتقالی"),
        "no_functioning_national_legislature": ("نهادهای رسمیِ فعالِ ثبت‌شده؛ بدون فرض پارلمان فعال", "نبود قوه مقننه ملیِ فعال"),
        "mixed": ("نهادهای اجرایی و قانون‌گذاری ثبت‌شده در ساختار مختلط", "ساختار مختلط"),
        "unknown": ("نهاد سیاسی نیازمند تعیین بر اساس اطلاعات معتبر کشور", "اطلاعات ساختاری ناکافی")
    }
    name, basis = profiles.get(system, profiles["unknown"])

    if form in ("monarchy", "emirate", "sultanate") and system == "unknown":
        name = "دربار، شورای سلطنتی/امارتی و نهاد مشورتیِ موجود"
        basis = "نوع حکومت سلطنتی؛ ساختار اجرایی دقیق نامشخص"
    elif form == "military_government" and system == "unknown":
        name = "شورای حاکم نظامی یا فرماندهی رسمی ثبت‌شده"
        basis = "حکومت نظامی؛ ساختار نهادی دقیق نامشخص"
    elif form == "transitional_government" and system == "unknown":
        name = "نهاد انتقالی رسمی ثبت‌شده"
        basis = "حکومت انتقالی؛ ساختار نهادی دقیق نامشخص"

    if crisis_kind == "coup_crisis":
        focus = "تمرکز بحران: فرماندهی نظامی و نهاد قانونیِ ناظر، متناسب با ساختار ثبت‌شده کشور."
    else:
        focus = "تمرکز بحران: نهادهای نمایندگی و گروه‌های اجتماعی، متناسب با ساختار ثبت‌شده کشور."

    return {
        "name": name,
        "basis": basis,
        "focus": focus,
        "government_form": form,
        "government_subform": subform,
        "executive_legislative_system": system
    }


def check_player_regime_crisis(s, daily_log):
    """ثبت بحران داخلی؛ بحران کودتا با وقوع کودتا تفاوت دارد و تریبون زنده در فاز AI فعال می‌شود."""
    if s.get("over") or s.get("regime_crisis"):
        return
    player = s.get("player")
    country = (s.get("world") or {}).get(player)
    if not isinstance(country, dict):
        return
    stability = max(0.0, min(100.0, float(country.get("stab", 0))))
    groups = (s.get("social_groups") or {}).get(player) or {}
    values = [max(0.0, min(100.0, float(v))) for v in groups.values()]
    social_average = sum(values) / float(len(values)) if values else 50.0
    military = max(0.0, min(100.0, float(country.get("mil", 0))))

    # افت شدید توان نظامی یا حمایت اجتماعی فقط «بحران کودتا» ایجاد می‌کند؛
    # به معنی وقوع کودتا یا سقوط حکومت نیست.
    if military < 20.0 or social_average < 30.0:
        crisis_kind = "coup_crisis"
        legitimacy = float(s.get("legitimacy", 50.0))
        label = "بحران کودتا"
    elif stability < 10.0:
        crisis_kind = "revolution_crisis"
        legitimacy = 5.0
        label = "بحران انقلاب"
    else:
        return

    political = (s.get("political_state") or {}).get(player) or {}
    institution = _crisis_institution_profile(political, crisis_kind)
    s["regime_crisis"] = {
        "kind": crisis_kind, "date": s.get("game_date", ""),
        "stability_at_event": round(stability, 1),
        "social_support_average": round(social_average, 1),
        "military_strength_at_event": round(military, 1),
        "legitimacy": round(legitimacy, 1), "status": "awaiting_live_tribune",
        "government_form": political.get("government_form"),
        "executive_legislative_system": political.get("executive_legislative_system"),
        "institution": institution
    }
    s["legitimacy"] = legitimacy
    line = "⚠️ %s در %s شکل گرفت؛ این وضعیت به‌تنهایی به معنی وقوع کودتا یا سقوط حکومت نیست." % (label, player)
    daily_log.append(line)
    press = s.setdefault("politics", {}).setdefault(player, {}).setdefault("press", [])
    press.append(line)
    del press[:-12]

def end_turn(s):
    if s["over"]:
        print("بازی تمام شده. با `reset` بازی جدید بساز.")
        return
    W = s["world"]; P = s["player"]
    s.setdefault("day", 1)
    day = int(s.get("elapsed_days", 0)) + 1
    log = []

    # ۱) درآمد روزانه
    for name, c in W.items():
        if name in s["eliminated"]:
            continue
        base = c["eco"] * INCOME_K
        if c["stab"] < 30:
            base *= 0.5
        c["money"] += base

    # ۲) رانش خفیف ثبات (روزانه)
    for name, c in W.items():
        if name in s["eliminated"]:
            continue
        drift = -0.7 if c["mil"] > 70 else 0.3
        if c["eco"] > 70:
            drift += 0.3
        c["stab"] = max(0.0, min(100.0, c["stab"] + drift + random.randint(-1, 1)))
        if name != P and c["stab"] < 12 and random.random() < 0.02:
            c["eco"] -= 2
            log.append(f"⚠ در {name} ناآرامی داخلی بالا گرفت.")

    # ۳) نشست تصمیم‌گیری کشورهای دیگر (هر ۱۰ روز)
    if day % 10 == 0:
        for name, c in W.items():
            if name in s["eliminated"] or name == P or s["over"]:
                continue
            targets = [o for o in W if o not in s["eliminated"] + [name]]
            if not targets:
                continue
            r = random.random()
            rivals = sorted(targets, key=lambda o: get_rel(s, name, o))[:2]
            friends = sorted(targets, key=lambda o: -get_rel(s, name, o))[:2]
            if r < 0.068:
                c["eco"] += 1.5
            elif r < 0.136:
                c["mil"] += 2
            elif r < 0.187 and friends:
                friend = random.choice(friends)
                add_rel(s, name, friend, 5)
            elif r < 0.221 and rivals:
                foe = random.choice(rivals)
                if get_rel(s, name, foe) < 0:
                    foe_c = W[foe]
                    foe_c["eco"] = max(10, foe_c["eco"] - 1.5)
                    add_rel(s, name, foe, -5)
                    log.append(f"⛔ {name} علیه {foe} محدودیت اقتصادی وضع کرد.")
                    if foe == P:
                        ev(s, P, "sanctioned_by", name)
                        ai_statement(s, name, "sanc", P)
            elif r < 0.245 and c["tech"] >= 70 and c["nukes"] < 2 and c["money"] > 15:
                c["money"] -= 12; c["nukes"] += 1
                log.append(f"☢ {name} وارد باشگاه هسته‌ای شد!")
                ai_statement(s, name, "nuke")
                for o in W:
                    if o not in s["eliminated"] + [name]:
                        add_rel(s, name, o, -6)
            elif r < 0.265 and c["aggr"] > 0.4 and rivals and c["mil"] > 65:
                foe = min(rivals, key=lambda o: power(W[o]))
                if foe != name and W[foe]["stab"] < 50:
                    if foe != P or c["aggr"] > 0.6:
                        start_war(s, name, foe)
                        log.append(f"⚔ {name} به {foe} حمله کرد!")
            elif r < 0.289:
                c["tech"] += 1.5
            elif r < 0.313 and rivals and c["aggr"] > 0.25:
                foe = min(rivals, key=lambda o: get_rel(s, name, o))
                if get_rel(s, name, foe) < -35 and foe not in s["eliminated"]:
                    foe_c = W[foe]
                    op = random.random()
                    if op < 0.55:
                        if random.random() < 0.55:
                            foe_c["mil"] = max(10, foe_c["mil"] - 3)
                            foe_c["eco"] = max(10, foe_c["eco"] - 1)
                            ev(s, name, "sabotage_ok", foe)
                            ev(s, foe, "sabotage_victim", name)
                            log.append(f"🕵 عملیات خرابکاری خاموش {name} علیه زیرساخت‌های {foe} موفق بود.")
                        else:
                            ev(s, name, "sabotage_fail", foe)
                    else:
                        if random.random() < 0.20:
                            foe_c["stab"] = max(0, foe_c["stab"] - 6)
                            foe_c["eco"] = max(10, foe_c["eco"] - 1.5)
                            add_rel(s, name, foe, -35)
                            for o in W:
                                if o not in (name, foe) and o not in s["eliminated"]:
                                    add_rel(s, name, o, -8)
                            ev(s, name, "kill_ok", foe)
                            ev(s, foe, "kill_victim", name)
                            log.append(f"☠ ترور دولتمردان ارشد {foe}! نقشه توسط {name} اجرا شده و جامعه جهانی را تکان داد.")
                        else:
                            add_rel(s, name, foe, -10)
                            ev(s, name, "kill_fail", foe)
                            ev(s, foe, "kill_attempt", name)
            elif r < 0.326 and rivals and c["aggr"] > 0.5 and c["money"] >= 8:
                foe = min(rivals, key=lambda o: get_rel(s, name, o))
                already = any(x["sponsor"] == name and x["host"] == foe for x in s.get("proxies", []))
                if get_rel(s, name, foe) < -30 and not already and foe not in s["eliminated"]:
                    c["money"] -= 6
                    s["proxies"].append({"sponsor": name, "host": foe, "power": 1, "hidden": True, "name": proxy_label(name, foe)})
                    W[foe]["stab"] = max(0, W[foe]["stab"] - 1.5)
                    add_rel(s, name, foe, -12)
                    log.append(f"🕵 شواهدی از شبکه نیابتی {name} در {foe} دیده شده است.")
                    if foe == P:
                        ai_statement(s, foe, "proxy", name)

    cands2 = [n for n in W if n != P and n not in s.get("eliminated", [])]
    if cands2 and random.random() < 0.45:
        sp = random.choice(cands2)
        topic = "war_d" if P in s.get("at_war", []) else "daily"
        ai_statement(s, sp, topic)

    # ۴) جنگ‌ها: فرسایش روزانه + پیامدها
    if s["at_war"]:
        war_pairs = [s["at_war"][i:i + 2] for i in range(0, len(s["at_war"]) - 1, 2)]
        for a, d in war_pairs:
            if a in s["eliminated"] or d in s["eliminated"]:
                continue
            Wa, Wd = W[a], W[d]
            done = False
            if random.random() < 0.20:
                if power(Wa) > power(Wd) * 1.6 and Wd["stab"] < 35:
                    annex(s, a, d); done = True
                elif power(Wd) > power(Wa) * 1.6 and Wa["stab"] < 35:
                    annex(s, d, a); done = True
            if not done:
                Wa["mil"] = max(10, Wa["mil"] - 0.7)
                Wd["mil"] = max(10, Wd["mil"] - 0.7)
                Wa["eco"] = max(10, Wa["eco"] - 0.3)
                Wd["eco"] = max(10, Wd["eco"] - 0.3)
                if s["player"] in (a, d) and random.random() < 0.10:
                    me2 = W[s["player"]]
                    me2["stab"] = max(0, me2["stab"] - 1.5)
                    log.append("جنگ سنگین است... ثبات تو سقوط کرد. مذاکره؟")
                elif random.random() < 0.04:
                    if s["player"] not in (a, d):
                        rel = get_rel(s, a, d) + 15
                        set_rel(s, a, d, rel)
                        s["at_war"] = [x for k, x in enumerate(s["at_war"]) if k not in (s["at_war"].index(a), s["at_war"].index(d))]
                        log.append(f"🕊 {a} و {d} آتش‌بس نسبی برقرار کردند.")
        seen = set(); final = []
        for pr in [s["at_war"][i:i + 2] for i in range(0, len(s["at_war"]) - 1, 2)]:
            if pr[0] in s["eliminated"] or pr[1] in s["eliminated"]:
                continue
            if pr[0] in seen or pr[1] in seen:
                continue
            seen.add(pr[0]); seen.add(pr[1]); final.extend(pr)
        s["at_war"] = final

    # ۵) نیروهای نیابتی: نگه‌داری روزانه (احتمال‌های ÷10)
    kept = []
    for px in s.get("proxies", []):
        sp, host = px.get("sponsor"), px.get("host")
        if sp not in W or host not in W or sp in s["eliminated"] or host in s["eliminated"]:
            continue
        pw = px["power"]
        Wh = W[host]
        Wh["stab"] = max(0, Wh["stab"] - (0.2 if pw >= 4 else 0.1))
        if sp in W and sp not in s["eliminated"]:
            W[sp]["influence"] += 0.017
        if random.random() < 0.008 + pw * 0.003:
            Wh["eco"] = max(10, Wh["eco"] - 2)
            Wh["stab"] = max(0, Wh["stab"] - 3)
            log.append(f"🔥 شبه‌نظامیان {sp} در {host} عملیات گسترده انجام دادند!")
            ev(s, host, "uprising", sp)
            if host == P:
                end_of_action_checks(s)
        elif host == P and random.random() < 0.04:
            log.append(f"⚠ شبه‌نظامیان {sp} در خاک تو فعال‌اند (قدرت {pw}/5).")
            ev(s, P, "sabotage_victim", sp)
            if Wh["stab"] >= 45 and random.random() < 0.20:
                s["proxies"] = [p2 for p2 in s["proxies"] if p2 is not px]
                log.append(f"✅ نیروهای امنیتی تو شبکه نیابتی {sp} را متلاشی کردند!")
                continue
        if random.random() < 0.010:
            add_rel(s, sp, host, -18)
            log.append(f"🔓 شبکه نیابتی {sp} در {host} لو رفت!")
            ev(s, sp, "covert_fail", host)
            ev(s, host, "sabotage_victim", sp)
            if sp == P:
                me_ = W[P]
                me_["stab"] = max(0, me_["stab"] - 1)
            continue
        kept.append(px)
    s["proxies"] = kept

    # ۶) رخداد تصادفی جهانی ~۲٪ روزانه
    if random.random() < 0.02:
        event = random.choice(["crisis_oil", "boom", "uprising", "tech_break",
                               "plague", "alliance_shift"])
        alive = [n for n in W if n not in s["eliminated"]]
        if alive:
            if event == "crisis_oil":
                n = random.choice(alive)
                W[n]["eco"] = max(10, W[n]["eco"] - 2); W[n]["money"] -= 5
                if n == P: ev(s, P, "oil_crisis")
                log.append(f"📉 بحران انرژی! چرخ اقتصادی {n} دچار افت شد.")
            elif event == "boom":
                n = random.choice(alive)
                W[n]["eco"] += 2; W[n]["money"] += 8
                if n == P: ev(s, P, "boom")
                log.append(f"📈 رونق جهانی بازار — {n} بیشترین سود را برد.")
            elif event == "uprising":
                core = [n for n in alive if W[n]["stab"] < 55] or alive
                n = random.choice(core)
                W[n]["stab"] -= 3
                log.append(f"🔥 خیزش مردمی در {n} — ثبات -3.")
                if n == s["player"]:
                    ev(s, P, "uprising")
                    end_of_action_checks(s)
            elif event == "tech_break":
                n = random.choice(alive)
                W[n]["tech"] += 2
                if n == P: ev(s, P, "tech_break")
                log.append(f"💡 جهش فناورانه در {n}.")
            elif event == "plague":
                n = random.choice(alive)
                W[n]["eco"] = max(10, W[n]["eco"] - 2); W[n]["stab"] -= 1.5
                if n == P: ev(s, P, "plague")
                log.append(f"🦠 بیماری همه‌گیر صنایع {n} را فلج کرد.")
            elif event == "alliance_shift":
                a, b = random.sample(alive, min(2, len(alive)))
                add_rel(s, a, b, 4)
                log.append(f"🌐 دیپلماسی خاموش: فاصله {a} و {b} بیشتر شد... یا کمتر؟")

    # ۷) احزاب و مطبوعات: واکنش روزانه همه کشورها
    politics = s.setdefault("politics", {})
    te = s.get("turn_events", {})
    pop_lines, heads, foreign_digest = [], [], []
    for name in W:
        if name in s["eliminated"]:
            continue
        events = [list(e) for e in te.get(name, [])]
        if name in s["at_war"]:
            events.append(["war_attrition"])
        elif not events:
            events.append(["peace"])
        pol = politics.setdefault(name, {"parties": dict(PARTY_BASE if name == P else AI_PARTY_BASE), "press": []})
        pl = parties_update(s, name, pol, events)
        hl = press_update(s, name, pol, events)
        if name == P:
            pop_lines, heads = pl, hl
        elif hl:
            foreign_digest.append(hl[0])
    s["turn_events"] = {}

    # ۸) شمارش روز و گزارش
    s["ap"] = "\u221e"
    previous_year = s["year"]
    next_date = datetime.date.fromisoformat(s["game_date"]) + datetime.timedelta(days=1)
    s["game_date"] = next_date.isoformat()
    s["year"] = next_date.year
    s["day"] = next_date.day
    s["elapsed_days"] = day
    _refresh_calendar(s)
    advance_player_political_reforms(s, log)
    check_player_regime_crisis(s, log)
    year_report = next_date.year != previous_year
    if year_report:
        s["turn"] += 1

        # نهادها در پایان سال
        me = W[P]
        if P not in NUKES0 and s.get("iaea_heat", 0) >= 3:
            me["eco"] = max(10, me["eco"] - 6)
            for o in WEST:
                if o in W and o != P:
                    add_rel(s, P, o, -20)
            msg(s, "🇺🇳 پرونده هسته‌ای تو به شورای امنیت ارجاع شد؛ تحریم‌های بین‌المللی اقتصاد را ضربه زد (-6).")
            log.append("🇺🇳 پرونده تو به شورای امنیت ارجاع شد؛ تحریم‌های تازه (اقتصاد -6)")
        elif P not in NUKES0 and s.get("iaea_heat", 0) > 0:
            log.append(f"🔍 فشار آژانس انرژی اتمی ادامه دارد (سطح {s['iaea_heat']}/3).")
        if s.get("un_censures", 0) >= 5 and random.random() < 0.5:
            me["stab"] = max(0, me["stab"] - 5)
            log.append("🇺🇳 انزوای دیپلماتیک به‌خاطر محکومیت‌های مکرر سازمان ملل؛ ثبات -5")

        # معاملات سالانه تسلیحاتی میان کشورهای هوش مصنوعی
        deals = 0
        ai_pool = [n for n in W if n != P and n not in s["eliminated"] and W[n]["money"] > 8]
        random.shuffle(ai_pool)
        for buyer in ai_pool:
            if deals >= 2:
                break
            options = [k for k, it in ARSENAL_ITEMS.items() if it["mk"] != buyer and get_rel(s, buyer, it["mk"]) >= 60 and W[it["mk"]]["money"] >= it["pr"]]
            if not options:
                continue
            key = random.choice(options)
            it = ARSENAL_ITEMS[key]; mk = it["mk"]
            W[buyer]["money"] -= it["pr"]
            W[mk]["money"] += it["pr"]
            s["arsenal"].setdefault(buyer, {})
            s["arsenal"][buyer][key] = s["arsenal"][buyer].get(key, 0) + 1
            W[buyer]["_arsenal"] = s["arsenal"][buyer]
            add_rel(s, buyer, mk, 2)
            deals += 1
            log.append(f"📄 قرارداد نظامی: {mk} → {buyer} (۱× {key})")

    s["log"] = (s.get("log", []) + log)[-40:]

    save(s)
    print()
    print("─" * 46)
    if year_report:
        print("📢 گزارش سال " + str(s["year"] - 1))
    else:
        print("🌙 گزارش روز " + (datetime.date.fromisoformat(s["game_date"]) - datetime.timedelta(days=1)).isoformat())
    for line in log[-8:]:
        print("  • " + line)
    if pop_lines:
        print(" 🏛 احزاب: " + " | ".join(pop_lines))
    for h in heads:
        print("   " + h)
    if foreign_digest:
        print(" 🌐 نشریات خارجی:")
        for fl in foreign_digest[:3]:
            print("  " + fl)
    print("─" * 46)
    if year_report:
        check_victory(s)
    if s["over"]:
        print("\n🏁 بازی تمام شد. برای شروع دوباره: `reset` بعد `init <کشور>`")
    else:
        if year_report:
            print(f"سال {s['year']} آغاز شد — روز ۱.")
        else:
            print(f"روز {s['day']} از ماه {s['turn']} — فرصت‌های امروز: ∞ (نامحدود)")
        print()

def _snapshot_clear():
    return None

def ranking(s):
    W = s["world"]
    rows = []
    for name, c in W.items():
        if name in s["eliminated"]:
            rows.append((name, -1, "حذف‌شده")); continue
        allies = 0
        if name == s["player"]:
            allies = len(s["allies"])
        else:
            allies = sum(1 for o in W if o != name and get_rel(s, name, o) > 70)
        score = dominance(c, allies, c["influence"])
        rows.append((name, score, f"قدرت {power(c):.0f} | ثبات {c['stab']:.0f} | نفوذ {c['influence']:.0f}"))
    rows.sort(key=lambda x: -x[1])
    return rows

def check_victory(s):
    rows = ranking(s)
    top = rows[0]
    me_score = dict((n, sc) for n, sc, _ in rows).get(s["player"], -1)
    second = rows[1][1] if len(rows) > 1 else 0
    if top[0] == s["player"] and me_score >= 55 and me_score >= second * 1.5:
        s["over"] = True
        print(f"👑👑👑 {s['player']} ابرقدرت بی‌رقیب جهان شد! VICTORY 👑👑👑")
    if s["year"] >= FINAL_YEAR and not s["over"]:
        rankp = [i + 1 for i, (n, _, _) in enumerate(rows) if n == s["player"]][0]
        if rankp == 1:
            print("👑 پایان زمان: تو قوی‌ترین قدرت جهان ماندی — VICTORY!")
        else:
            print(f"🏁 پایان زمان (سال {FINAL_YEAR}): سالخت رتبه {rankp} جهان.")
        s["over"] = True

# ---------- status ----------

def advance_time(s, minutes):
    """Advance the shared game clock; run the daily engine exactly at midnight."""
    minutes = int(minutes)
    if minutes not in (300, 1440):
        raise ValueError("فقط گام ۵ ساعت یا ۲۴ ساعت مجاز است.")
    remaining = minutes
    while remaining > 0 and not s.get("over", False):
        current = int(s.get("hour", 0)) * 60 + int(s.get("minute", 0))
        step = min(remaining, 1440 - current)
        current += step
        remaining -= step
        if current >= 1440:
            s["hour"], s["minute"] = 0, 0
            end_turn(s)
        else:
            s["hour"], s["minute"] = divmod(current, 60)
    save(s)
    return s


def show_status(s):
    W = s["world"]; P = s["player"]; me = W[P]
    print("═" * 56)
    print("  تاریخ " + s.get("game_date", START_DATE.isoformat()) +
          " | ساعت %02d:%02d | فرصت امروز: ∞ (نامحدود)" %
          (int(s.get("hour", 0)), int(s.get("minute", 0))))
    if s["over"]: print("  ‼ بازی به پایان رسیده — `reset` برای شروع دوباره")
    print("═" * 56)
    if s["player"] in s["eliminated"]:
        print("💀 کشور تو از نقشه حذف شده است.")
    else:
        print(f"🎖 {P} ({'، '.join(s['allies']) if s['allies'] else 'بدون متحد'})")
        print(f"  خزانه {me['money']:.0f} میلیارد | اقتصاد {me['eco']:.0f} | ارتش {me['mil']:.0f}")
        print(f"  فناوری {me['tech']:.0f} | ثبات {me['stab']:.0f} | کلاهک {me['nukes']} | نفوذ {me['influence']:.0f}")
        if s["player"] in s["at_war"]:
            print("  ⚔ در حال جنگ!")
    print("─" * 56)
    print(" رتبه  کشور           امتیاز  جزئیات")
    rows = ranking(s)
    shown = rows[:12]
    pi = next((i for i, (n, _, _) in enumerate(rows) if n == P), None)
    for i, (name, score, detail) in enumerate(shown):
        mark = "▶" if name == P else " "
        tag = " 💀" if name in s["eliminated"] else (" ⚔" if name in s["at_war"] else "")
        score_s = f"{score:.0f}" if score >= 0 else "  —"
        print(f"  {i+1:>2} {mark} {name:<12} {score_s:>5}   {detail}{tag}")
    if pi is not None and pi >= 12:
        name, score, detail = rows[pi]
        tag = " ⚔" if name in s["at_war"] else ""
        print(f"  … {pi-12} کشور دیگر")
        print(f"  {pi+1:>2} ▶ {name:<12} {score:.0f}   {detail}{tag}")
    elif len(rows) > 12:
        print(f"  … {len(rows)-12} کشور دیگر (رتبه‌بندی کامل: `rank`)")
    print("─" * 56)
    if s["at_war"]:
        pairs = [f"{s['at_war'][i]} ↔ {s['at_war'][i+1]}" for i in range(0, len(s['at_war']) - 1, 2)]
        print(" جنگ‌های فعال: " + " | ".join(pairs))
    others = [n for n in W if n != P and n not in s["eliminated"]]
    if others:
        frs = sorted(others, key=lambda n: -get_rel(s, P, n))[:5]
        fos = sorted(others, key=lambda n: get_rel(s, P, n))[:5]
        print(" 🤍 گرم‌ترین روابط: " + "، ".join(f"{n} ({get_rel(s,P,n):.0f})" for n in frs))
        print(" ⚔ تنش‌های اصلی: " + "، ".join(f"{n} ({get_rel(s,P,n):.0f})" for n in fos))
        print("   → پرونده هر کشور: `status <نام کشور>`")
    pol = s.get("politics", {}).get(P)
    parties = (pol or {}).get("parties")
    if parties:
        print("─" * 56)
        print(" 🏛 حزب‌های داخلی:")
        for p in sorted(parties, key=lambda x: -parties[x]):
            print(f"   {p:<14} [{bar(parties[p])}] {parties[p]:.0f}٪")
    if pol and pol.get("press"):
        print(" 📰 آخرین تیتر مطبوعات:")
        for h in pol["press"][-4:]:
            print("   " + h)
    foreign_press = [(n, (s.get("politics", {}).get(n) or {}).get("press", [])[-1])
                     for n in W if n != P and n not in s["eliminated"]
                     and (s.get("politics", {}).get(n) or {}).get("press")]
    if foreign_press:
        print(" 🌐 نشریات خارجی:")
        for n, h in foreign_press[:4]:
            print(f"   {n}: {h}")
    print("═" * 56)
    if s["log"]:
        print(" آخرین رویدادها:")
        for line in s["log"][-4:]:
            print("  • " + line)
    print()

# ---------- داشبورد ها ----------

def rank_of(s, name):
    for i, (n, _, _) in enumerate(ranking(s)):
        if n == name:
            return i + 1
    return None

def _rank_cat(s, cat):
    titles = {"mil": "رتبه‌بندی نظامی", "eco": "رتبه‌بندی اقتصادی",
              "tech": "رتبه‌بندی فناوری", "stab": "رتبه‌بندی ثبات", "nukes": "رتبه‌بندی کلاهک"}
    if cat not in titles:
        print("✗ دسته نامشخص. موارد: power، mil، eco، tech، stab، nukes")
        return
    W = s["world"]
    rows = sorted(((n, W[n].get(cat, 0)) for n in W if n not in s["eliminated"]), key=lambda x: -x[1])
    print("\u2550" * 56)
    print(f" 🌍 {titles[cat]} ({len(rows)} کشور)")
    print("\u2550" * 56)
    for i2, (name, val) in enumerate(rows):
        mark = "\u25b6" if name == s["player"] else " "
        print(f"  {i2+1:>3} {mark} {name:<14} {val:>5.0f}")
    print("\u2550" * 56)


def dash_domestic(s):
    W = s["world"]; P = s["player"]; me = W[P]
    pol = s.get("politics", {}).get(P, {})
    parties = pol.get("parties") or {}
    print("═" * 56)
    print(" 🏛 داشبورد سیاست داخلی — " + P)
    print("═" * 56)
    print(f"  ثبات ملی [{bar(me['stab'])}] {me['stab']:.0f}   |   خزانه {me['money']:.0f} میلیارد")
    if parties:
        ranked = sorted(parties.items(), key=lambda x: -x[1])
        two = sum(v for _, v in ranked[:2])
        gauge = "قوی ✅" if two >= 55 else ("متزلزل ⚠ " if two <= 35 else "متوسط")
        print(f"  ائتلاف دو حزب نخست ({ranked[0][0]} + {ranked[1][0]}) = {two:.0f}% — {gauge}")
        print()
        for p, v in ranked:
            print(f"   {p:<14} [{bar(v)}] {v:.0f}%")
    print()
    print(" 📰 تیترهای اخیر مطبوعات:")
    press = pol.get("press") or []
    if press:
        for h in press[-8:]:
            print("   " + h)
    else:
        print("   (هنوز خبری منتشر نشده)")
    print("═" * 56)

def dash_diplomacy(s):
    W = s["world"]; P = s["player"]
    print("═" * 56)
    print(" 🌐 داشبورد دیپلماسی — " + P)
    print("═" * 56)
    print(" 🤍 متحدان: " + ("، ".join(s["allies"]) if s["allies"] else "—"))
    print(" 📜 پیمان عدم تجاوز: " + ("، ".join(s["pacts"]) if s["pacts"] else "—"))
    wars = [(s["at_war"][i], s["at_war"][i + 1]) for i in range(0, len(s["at_war"]) - 1, 2)]
    my_wars = [f"{a} ↔ {d}" for a, d in wars if P in (a, d)]
    print(" ⚔ جنگ‌های تو: " + ("، ".join(my_wars) if my_wars else "—"))
    others = [n for n in W if n != P and n not in s["eliminated"]]
    print()
    print(" 🤝 گرم‌ترین روابط:")
    for n in sorted(others, key=lambda n: -get_rel(s, P, n))[:6]:
        r = get_rel(s, P, n)
        print(f"   {n:<14} [{bar(max(0, r))}] {r:>5.0f}")
    print(" ⚔ تنش‌های اصلی:")
    for n in sorted(others, key=lambda n: get_rel(s, P, n))[:4]:
        r = get_rel(s, P, n)
        print(f"   {n:<14} [{bar(max(0, -r))}] {r:>5.0f}")
    print()
    print(" 🗺 میانگین رابطه با تو به تفکیک منطقه:")
    by_region = {}
    for n in others:
        by_region.setdefault(W[n]["region"], []).append(get_rel(s, P, n))
    for reg in sorted(by_region, key=lambda reg: -sum(by_region[reg]) / len(by_region[reg])):
        vals = by_region[reg]
        avg = sum(vals) / len(vals)
        flag = "🤍" if avg >= 40 else ("⚔" if avg <= -25 else ("🤝" if avg >= 15 else "—"))
        print(f"   {reg:<18} [{bar(max(0, avg))}] {avg:>5.0f}  {flag}")
    print("═" * 56)

def dash_ops(s):
    W = s["world"]; P = s["player"]
    print("═" * 56)
    print(" 🕵 داشبورد عملیات‌های پنهان — " + P)
    print("═" * 56)
    prx = s.get("proxies", [])
    mine = [px for px in prx if px["sponsor"] == P]
    inside = [px for px in prx if px["host"] == P]
    if mine:
        print(" 🗡 شبکه‌های نیابتی تو:")
        for px in mine:
            st = "مخفی" if px.get("hidden", True) else "لو رفته"
            nm = px.get("name") or proxy_label(px["sponsor"], px["host"])
            print(f"   ▸ {nm} در {px['host']:<14} قدرت [{bar(px['power'] * 20)}] {px['power']}/۵  ({st})")
    else:
        print(" 🗡 هنوز شبکه نیابتی نداری — با `act proxy <کشور>` بساز (۶۰ میلیارد، مخفی).")
    if inside:
        print()
        print(" ⚠ شبکه‌های نیابتی بیگانه در خاک تو:")
        for px in inside:
            nm2 = px.get("name") or proxy_label(px["sponsor"], px["host"])
            print(f"   ▸ {nm2} — عوامل {px['sponsor']:<12} قدرت [{bar(px['power'] * 20)}] {px['power']}/۵")
        print("   💡 با تقویت ثبات داخلی یا عملیات `act covert` می‌توانی خنثی‌شان کنی.")
    hidden_others = len(prx) - len(mine) - len(inside)
    if hidden_others > 0:
        print(f"\n 🌑 {hidden_others} شبکه نیابتی ناشناس در دیگر کشورهای جهان مخفیانه فعال است.")
    intel = [l for l in s.get("log", []) if any(t in l for t in ("🕵", "🔥", "🔓", "ترور", "خرابکاری", "نیابتی"))][-6:]
    print()
    print(" 📡 گزیده گزارش‌های امنیتی:")
    if intel:
        for l in intel:
            print("   • " + l)
    else:
        print("   (گزارشی ثبت نشده)")
    print("═" * 56)

def dash_military(s):
    W = s["world"]; P = s["player"]; me = W[P]
    print("═" * 56)
    print(" ⚔ داشبورد نظامی — " + P)
    print("═" * 56)
    print(f"  ارتش [{bar(me['mil'])}] {me['mil']:.0f}   |   کلاهک هسته‌ای: {me['nukes']} ☢   |   فناوری [{bar(me['tech'])}] {me['tech']:.0f}")
    my_pow = power(me)
    print(f"  قدرت پروژه‌شده: {my_pow:.0f}   |   جوخه‌های متحد: {len(s['allies'])}")
    ars = s.get("arsenal", {}).get(P, {})
    if ars:
        top = sorted(ars.items(), key=lambda x: -x[1])[:8]
        print("  🛢 زرادخانه: " + "، ".join(f"{n}× {k}" for k, n in top))
        print("     → خرید/فروش تجهیزات: منوی [7] یا `act buy/sell`")
    else:
        print("  🛢 زرادخانه خالی است — منوی [7] بازار تجهیزات")
    rivals = [n for n in W if n != P and n not in s["eliminated"]]
    print()
    print(" 🥊 قوی‌ترین مردان نظامی جهان (مقایسه با تو):")
    for n in sorted(rivals, key=lambda n: -power(W[n]))[:8]:
        pw = power(W[n])
        ratio = pw / max(my_pow, 1)
        tag = "🚨 خطرناک" if ratio > 1.2 else ("⚖ برابر" if ratio > 0.8 else "🟢 ضعیف‌تر")
        print(f"   {n:<14} {pw:>4}  {tag}")
    wars = [(s["at_war"][i], s["at_war"][i + 1]) for i in range(0, len(s["at_war"]) - 1, 2)]
    my_wars = [f"{a} ↔ {d}" for a, d in wars if P in (a, d)]
    world_wars = [f"{a} ↔ {d}" for a, d in wars if P not in (a, d)]
    if my_wars:
        print("\n 🚨 جنگ‌های درگیر تو: " + "، ".join(my_wars))
    if world_wars:
        print(" 🌐 جنگ‌های دیگران: " + "؛ ".join(world_wars[:4]))
    print("═" * 56)

def dash_economy(s):
    W = s["world"]; P = s["player"]; me = W[P]
    print("═" * 56)
    print(" 💰 داشبورد اقتصاد — " + P)
    print("═" * 56)
    inc_d = me["eco"] * INCOME_K * (0.5 if me["stab"] < 30 else 1.0)
    print(f"  خزانه {me['money']:.0f} میلیارد   |   درآمد روزانه +{inc_d:.1f} (ماهانه ~{inc_d * 30:.0f})")
    print(f"  اقتصاد [{bar(me['eco'])}] {me['eco']:.0f}")
    others = [n for n in W if n != P and n not in s["eliminated"]]
    hostiles = sum(1 for n in others if get_rel(s, P, n) < -40)
    partners = sum(1 for n in others if get_rel(s, P, n) > 50)
    print(f"  شرکای تجاری بالقوه 🤍 {partners}   |   دشمنان اقتصادی ⚔ {hostiles}")
    print()
    print(" 🏆 بزرگ‌ترین اقتصادهای جهان:")
    for n in sorted(others, key=lambda n: -W[n]["eco"])[:8]:
        print(f"   {n:<14} [{bar(W[n]['eco'])}] {W[n]['eco']:.0f}")
    print("═" * 56)

DASH_SECTIONS = {
    "dom": ("🏛 سیاست داخلی", dash_domestic),
    "dip": ("🌐 دیپلماسی", dash_diplomacy),
    "ops": ("🕵 عملیات پنهان", dash_ops),
    "mil": ("⚔ نظامی", dash_military),
    "eco": ("💰 اقتصاد", dash_economy),
}


def dash_orgs(s):
    P = s["player"]
    line = "=" * 56
    print(line)
    print(" داشبورد نهادهای بین‌المللی — " + P)
    print(line)
    cens = s.get("un_censures", 0)
    print(" 🗳 سازمان ملل متحد — عضویت: ✔ (همه کشورها)")
    if cens == 0:
        print("    تاکنون پرونده‌ای در شورای امنیت نداری.")
    else:
        print(f"    ⚠ محکومیت‌های شورای امنیت: {cens} بار")
        if cens >= 3:
            print("    ⚠ هشدار: انزوای دیپلماتیک نزدیک می‌شود.")
    heat = s.get("iaea_heat", 0)
    if P in NUKES0:
        state_i = "عضو «باشگاه هسته‌ای»؛ کلاهکش قانونی شناخته می‌شود."
    elif heat == 0:
        state_i = "وضعیت شفاف — بازرسی‌ها کامل و بدون مانع است."
    elif heat < 3:
        state_i = f"تحت فشار بازرسی — سطح {heat}/3 (با شفافیت اعلام‌شده صفر می‌شود)"
    else:
        state_i = "برنامه هسته‌ای غیرقانونی اعلام شده؛ در مسیر تحریم شورای امنیت!"
    print(" ☢ آژانس بین‌المللی انرژی اتمی — فشار: " + f"{heat}/3")
    print("    " + state_i)
    if P in NATO:
        print(" 🛡 ناتو: ✔ عضو — مادهٔ ۵ دفاع مشترک تو را پشتیبانی می‌کند.")
        others = [n for n in NATO if n in s["world"] and n != P and n not in s["eliminated"]]
        if others:
            top = sorted(others, key=lambda n: -power(s["world"][n]))[:3]
            print("    قدرتمندترین هم‌پیمانان: " + "، ".join(top))
    else:
        print(" 🛡 ناتو: غیرعضو — پیمان دفاع مشترک شامل تو نمی‌شود.")
    print(line)

DASH_SECTIONS = {
    "dom": ("🏛 سیاست داخلی", dash_domestic),
    "dip": ("🌐 دیپلماسی", dash_diplomacy),
    "ops": ("🕵 عملیات پنهان", dash_ops),
    "mil": ("⚔ نظامی", dash_military),
    "eco": ("💰 اقتصاد", dash_economy),
    "org": ("🇺🇳 نهادهای بین‌المللی", dash_orgs),
}

def dash(s, section=""):
    section = section.strip().lower()
    alias = {
        "dom": "dom", "سیاست": "dom", "داخلی": "dom",
        "dip": "dip", "دیپلماسی": "dip", "خارجی": "dip",
        "ops": "ops", "عملیات": "ops", "جاسوسی": "ops", "نیابتی": "ops",
        "mil": "mil", "نظامی": "mil", "جنگ": "mil",
        "eco": "eco", "اقتصاد": "eco", "خزانه": "eco",
        "org": "org", "نهاد": "org", "نهادها": "org", "سازمان": "org",
        "ملل": "org", "آژانس": "org", "اتمی": "org",
    }
    key = alias.get(section)
    if key is None:
        print("📊 داشبوردها — یک بخش را انتخاب کن:")
        for k, (_title, fn) in DASH_SECTIONS.items():
            fn(s)
        return
    DASH_SECTIONS[key][1](s)

def show_country(s, name):
    W = s["world"]; P = s["player"]; c = W[name]
    rank = rank_of(s, name)
    r = get_rel(s, P, name)
    print("═" * 56)
    tags = []
    if name == P: tags.append("🏳 کشور شما")
    if name in s["allies"]: tags.append("🤍 متحد")
    if name in s["pacts"]: tags.append("📜 عدم تجاوز")
    if name in s["at_war"]: tags.append("⚔ در جنگ")
    if name in s["eliminated"]: tags.append("💀 حذف‌شده")
    print(f" 📊 پرونده «{name}» — منطقه {c['region']} | رتبه جهانی {rank if rank else '—'}")
    if tags: print("   برچسب‌ها: " + " | ".join(tags))
    print(f"   {c.get('trait', '')}")
    print()
    print(f"   ارتش  [{bar(c['mil'])}] {c['mil']:.0f}")
    print(f"   اقتصاد [{bar(c['eco'])}] {c['eco']:.0f}")
    print(f"   فن‌آوری [{bar(c['tech'])}] {c['tech']:.0f}")
    print(f"   ثبات  [{bar(c['stab'])}] {c['stab']:.0f}")
    print(f"   خزانه {c['money']:.0f} میلیارد | نفوذ {c['influence']:.0f} | کلاهک ☢ {c['nukes']}")
    tar_ars = s.get("arsenal", {}).get(name, {})
    if tar_ars:
        print("   🛢 تجهیزات اصلی: " + "، ".join(f"{n}× {k}" for k, n in sorted(tar_ars.items(), key=lambda x: -x[1])[:3]))
    if name != P:
        print(f"   رابطه با تو {P}: {r:.0f} [{bar(max(0, r))}]")
    pol = (s.get("politics") or {}).get(name) or {}
    prx = [px for px in s.get("proxies", []) if px["host"] == name]
    if prx:
        shown = [px for px in prx if px["sponsor"] == P]
        if shown:
            print("   🗡 شبکه نیابتی شما اینجا: " + "، ".join((px.get("name") or proxy_label(px["sponsor"], px["host"])) + f" قدرت {px['power']}/۵" for px in shown))
        else:
            print(f"   🌑 {len(prx)} شبکه نیابتی ناشناس در این کشور فعال است.")
    parties = pol.get("parties") or {}
    if parties:
        print("   🏛 حزب‌ها: " + " | ".join(f"{p} {v:.0f}%" for p, v in sorted(parties.items(), key=lambda x: -x[1])))
    press = (pol.get("press") or [])[-2:]
    if press and name != P:
        for h in press:
            print("   " + h)
    print("═" * 56)

def show_list(args):
    query = args[0] if args else None
    regions = {}
    for n, c in COUNTRIES.items():
        regions.setdefault(c["region"], []).append(n)
    total = 0
    for reg in regions:
        members = [n for n in regions[reg] if not query or query in n or query in reg]
        if not members:
            continue
        total += len(members)
        print(f"\n ─ {reg} ({len(members)})")
        print("   " + "، ".join(members))
    print()
    if total == 0:
        print("⚠ چیزی یافت نشد. نمونه‌ها: `list خاورمیانه` یا `list آفریقا`")
    else:
        print(f"✅ در مجموع {total} کشور واقعی — کل بازی: {len(COUNTRIES)} کشور.")

# ---------- main ----------

def _script_dir():
    return os.path.dirname(os.path.abspath(__file__))


def _start_log():
    path = os.path.join(_script_dir(), "run_log.txt")
    try:
        import io as _io
        f = _io.open(path, "w", encoding="utf-8-sig", errors="replace", buffering=1)
    except Exception:
        return None
    real = sys.__stdout__

    class _LogTee(object):
        def write(self, s):
            try:
                f.write(s)
                f.flush()
            except Exception:
                pass
            try:
                real.write(s)
                real.flush()
            except Exception:
                pass

        def flush(self):
            try:
                f.flush()
            except Exception:
                pass

        def isatty(self):
            return False

    sys.stdout = _LogTee()
    print("\U0001f9fe \u0644\u0627\u06af \u0627\u06cc\u0646 \u0627\u062c\u0631\u0627 \u062f\u0631 \u0641\u0627\u06cc\u0644 run_log.txt \u0630\u062e\u06cc\u0631\u0647 \u0645\u06cc\u200c\u0634\u0648\u062f.")
    return f


def _finish_log(f):
    try:
        f.write("\n===== END OF RUN (run_log.txt by play_logged.bat) =====\n")
    except Exception:
        pass
    try:
        f.close()
    except Exception:
        pass
    if os.name == "nt":
        try:
            os.startfile(os.path.join(_script_dir(), "run_log.txt"))
        except Exception:
            pass


def main(argv=None):
    args = argv if argv is not None else sys.argv[1:]
    logf = None
    if "play" in args and "log" in args:
        args = [a for a in args if a != "log"]
        logf = _start_log()
    if not args:
        if os.path.exists(STATE):
            show_status(load())
        else:
            print_intro()
        return
    cmd = args[0]
    if cmd in ("play", "بازی"):
        play()
        if logf:
            _finish_log(logf)
        return
    if cmd == "init":
        if len(args) < 2:
            print_intro()
            return
        q = args[1]
        player = next((n for n in COUNTRIES if q in n or n.startswith(q[:3])), None)
        if player is None:
            print("✗ کشور نامعتبر. گزینه‌ها: " + "، ".join(COUNTRIES))
            return
        s = init_game(player)
        print(f"✔ آغاز بازی! تو رهبر {player} هستی.")
        print()
        show_status(s)
        print(HELP)
        return
    if cmd == "reset":
        if os.path.exists(STATE):
            os.remove(STATE)
            print("✔ بازی قبلی حذف شد.")
        if len(args) >= 2:
            main(["init"] + args[1:])
        return
    if cmd in ("list", "لیست"):
        show_list(args[1:])
        return
    if not os.path.exists(STATE):
        print("⚠ بازی‌ای ساخته نشده. اول: `init <کشور>`")
        print_intro()
        return
    s = load()
    if cmd == "status":
        if len(args) >= 2:
            target = find_name(s, " ".join(args[1:]).split()[0]) or find_name(s, args[1])
            for cand in (" ".join(args[1:]), args[1]):
                target = find_name(s, cand)
                if target is not None:
                    break
            if target is None:
                print("✗ کشور نامعلوم. با `list` نام‌ها را ببین.")
            elif target == s["player"]:
                show_status(s)
            else:
                show_country(s, target)
        else:
            show_status(s)
    elif cmd in ("dash", "داشبورد"):
        dash(s, args[1] if len(args) > 1 else "")
    elif cmd in ("rank", "رتبه"):
        cat = args[1] if len(args) > 1 else "power"
        if cat != "power":
            _rank_cat(s, cat)
            return
        rows = ranking(s)
        print("═" * 56)
        print(f" 🌍 رتبه‌بندی کامل جهانی ({len(rows)} کشور)")
        print("═" * 56)
        for i2, (name, score, detail) in enumerate(rows):
            mark = "▶" if name == s["player"] else " "
            tag = " 💀" if name in s["eliminated"] else (" ⚔" if name in s["at_war"] else "")
            score_s = f"{score:.0f}" if score >= 0 else "  —"
            print(f"  {i2+1:>3} {mark} {name:<14} {score_s:>5}   {detail}{tag}")
        print("═" * 56)
    elif cmd in ("statement", "بیانیه"):
        text = " ".join(args[1:]).strip()
        if not text:
            print("✗ متن بیانیه را بنویس.")
            return
        msg(s, "📢 بیانیه رسمی رهبری " + s["player"] + ": " + text)
        s["statements"] = (s.get("statements") or [])[-79:] + [
            {"who": s["player"], "text": text, "topic": "player"}]
        ai_react(s, "generic")
        save(s)
        print("📢 بیانیه منتشر شد و در گزارش بازی ثبت گردید.")
    elif cmd in ("neg", "negotiate", "مذاکره"):
        kind = args[1] if len(args) > 1 else ""
        target = find_name(s, args[2]) if len(args) > 2 else None
        secret = len(args) > 3 and args[3] in ("s", "secret", "محرمانه")
        negotiate(s, kind, target, secret)
    elif cmd == "negos":
        print("🤝 انواع مذاکره — مورد: neg <نوع> <کشور> [s = محرمانه]")
        for k, (lab, cost) in NEG_KINDS.items():
            sec = " [همیشه محرمانه]" if k in NEG_SECRET_LIKE else ""
            print(f"   {k:<10} {lab} (هزینه {cost}م){sec}")
    elif cmd in ("decide", "تصمیم"):
        kind = args[1] if len(args) > 1 else ""
        if not kind:
            print("🧠 تصمیم‌های کلیدی — مورد: " + "، ".join(sorted(DECISIONS)))
            return
        announce(s, kind)
    elif cmd == "help":
        print(HELP)
    elif cmd == "act":
        do_act(s, args[1:])
    elif cmd == "end":
        end_turn(s)
    else:
        print("✗ فرمان ناشناخته. `help` بزن.")

def pick_country(s, title):
    W = s["world"]; P = s["player"]
    print(f"\n≡ {title} (شماره بزن یا نام کشور را بنویس؛ 0 = بازگشت)")
    regions = {}
    for n in W:
        if n == P or n in s["eliminated"]:
            continue
        regions.setdefault(W[n].get("region", "دیگر"), []).append(n)
    regs = list(regions)
    for ri, reg in enumerate(regs, 1):
        print(f"  [{ri}] {reg} ({len(regions[reg])} کشور)")
    raw = input("  منطقه? ").strip()
    if raw in ("0", ""):
        return None
    members = None
    if raw.isdigit() and 1 <= int(raw) <= len(regs):
        members = regions[regs[int(raw) - 1]]
    else:
        t = find_name(s, raw)
        if t and t != P:
            return t
        print("  ✗ یافت نشد.")
        return None
    for ci, m in enumerate(members, 1):
        c = W[m]
        print(f"   {ci:>3} {m:<18} ارتش {c['mil']:.0f} | اقتصاد {c['eco']:.0f} | رابطه {get_rel(s, P, m):.0f}")
    raw2 = input("  شماره کشور? ").strip()
    if raw2.isdigit() and 1 <= int(raw2) <= len(members):
        return members[int(raw2) - 1]
    return None


def equip_menu(s):
    P = s["player"]
    while True:
        print("\n" + "═" * 56)
        print(" 🛒 بازار جهانی تجهیزات نظامی")
        print("═" * 56)
        me = s["world"][P]
        ars = s.get("arsenal", {}).get(P, {})
        if ars:
            print(" زرادخانه تو: " + "، ".join(f"{n}x {k}" for k, n in sorted(ars.items(), key=lambda x: -x[1])[:10]))
        print(f" خزانه: {me['money']:.0f} میلیارد")
        print("─" * 56)
        for ci, cat in enumerate(EQUIP_CATS, 1):
            print(f"  [{ci}] {cat} ({len(EQUIPMENT[cat])} قلم)")
        print("  [9] فروش تجهیز    [0] بازگشت")
        raw = input(" دسته? ").strip()
        if raw in ("0", ""):
            return
        if raw == "9":
            if not ars:
                print(" زرادخانه تو خالی است.")
                continue
            items = sorted(ars.items(), key=lambda x: -x[1])
            for ci, (k, n) in enumerate(items, 1):
                print(f"   {ci:>3} {k:<28} {n}x")
            raw2 = input(" کدام تجهیز را بفروشی? ").strip()
            if raw2.isdigit() and 1 <= int(raw2) <= len(items):
                key = items[int(raw2) - 1][0]
                buyer = pick_country(s, "به کدام کشور بفروشی؟")
                if buyer:
                    main(["act", "sell", key, buyer])
                    s = load()
            continue
        if raw.isdigit() and 1 <= int(raw) <= len(EQUIP_CATS):
            cat = EQUIP_CATS[int(raw) - 1]
            for ii, e in enumerate(EQUIPMENT[cat], 1):
                relmk = get_rel(s, P, e["mk"])
                prem = "تولید خودت ×0.7" if e["mk"] == P else ("قیمت عادی" if relmk >= 60 else ("×1.3" if relmk >= 30 else "×1.6"))
                print(f"   {ii:>3} {e['n']:<28} سازنده {e['mk']:<10} قیمت {e['pr']:>5} | اثر نظامی +{e['m']} | {prem}")
            raw2 = input(" شماره تجهیز (یا نامش را بنویس)? ").strip()
            key = None
            if raw2.isdigit() and 1 <= int(raw2) <= len(EQUIPMENT[cat]):
                key = EQUIPMENT[cat][int(raw2) - 1]["n"]
            else:
                key = find_item(raw2)
            if not key:
                print(" ✗ تجهیز نامعتبر.")
                continue
            raw3 = input(" چند عدد? (ENTER=1) ").strip()
            cnt = int(raw3) if raw3.isdigit() and int(raw3) > 0 else 1
            main(["act", "buy", key, str(cnt)])
            s = load()
        else:
            main(["help"] if raw == "h" else ["act"] + raw.split())
            s = load()


def orgs_menu(s):
    P = s["player"]
    while True:
        print("\n" + "═" * 56)
        print(" 🏛 نهادهای بین‌المللی")
        print("═" * 56)
        print("  [1] داشبورد نهادها (ملل/ناتو/آژانس)")
        print("  [2] اعلام شفافیت به آژانس انرژی اتمی (3م)")
        print("  [3] طرح محکومیت یک کشور در مجمع عمومی ملل")
        print("  [0] بازگشت")
        raw = input(" انتخاب? ").strip()
        if raw in ("0", ""):
            return
        if raw == "1":
            main(["dash", "org"])
        elif raw == "2":
            main(["act", "iaea"])
        elif raw == "3":
            t = pick_country(s, "کدام کشور را در مجمع عمومی محکوم کنی؟")
            if t:
                main(["act", "un", t])
        s = load()


def negotiate_menu(s):
    kinds = list(NEG_KINDS.items())
    while True:
        print("\U0001f91d \u0645\u0630\u0627\u06a9\u0631\u0647 \u2014 \u0627\u0646\u0648\u0627\u0639:")
        for k2, (kk, (lab, cost)) in enumerate(kinds, 1):
            sec = " [\u0645\u062d\u0631\u0645\u0627\u0646\u0647]" if kk in NEG_SECRET_LIKE else ""
            print(f"   [{k2}] {lab} (\u0647\u0632\u06cc\u0646\u0647 {cost}\u0645){sec}")
        print("   [0] \u0628\u0627\u0632\u06af\u0634\u062a")
        raw = input(" \u06a9\u062f\u0627\u0645\u061f ").strip()
        if raw in ("0", ""):
            return
        if not (raw.isdigit() and 1 <= int(raw) <= len(kinds)):
            continue
        kk = kinds[int(raw) - 1][0]
        t = pick_country(s, "\u0628\u0627 \u06a9\u062f\u0627\u0645 \u06a9\u0634\u0648\u0631\u061f")
        if not t:
            continue
        if kk in NEG_SECRET_LIKE:
            main(["neg", kk, t])
        else:
            sc = input(" \u0645\u062d\u0631\u0645\u0627\u0646\u0647\u061f (y/N): ").strip().lower()
            main(["neg", kk, t] + (["s"] if sc == "y" else []))
        s = load()


def decide_menu(s):
    items = sorted(DECISIONS.items())
    print("\U0001f9e0 \u062a\u0635\u0645\u06cc\u0645\u200c\u0647\u0627\u06cc \u06a9\u0644\u06cc\u062f\u06cc \u0631\u0647\u0628\u0631\u06cc \u2014 \u0647\u0631 \u062a\u0635\u0645\u06cc\u0645 \u0628\u0647 \u0635\u0648\u0631\u062a \u0628\u06cc\u0627\u0646\u06cc\u0647 \u0627\u0639\u0644\u0627\u0645 \u0648 \u06a9\u0634\u0648\u0631\u0647\u0627 \u0648\u0627\u06a9\u0646\u0634 \u0646\u0634\u0627\u0646 \u0645\u06cc\u200c\u062f\u0647\u0646\u062f:")
    for k2, (kk, lab) in enumerate(items, 1):
        print(f"   [{k2}] {lab} ({kk})")
    print("   [0] \u0628\u0627\u0632\u06af\u0634\u062a")
    raw = input(" \u06a9\u062f\u0627\u0645\u061f ").strip()
    if raw.isdigit() and 1 <= int(raw) <= len(items):
        main(["decide", items[int(raw) - 1][0]])


def play():
    """حالت تعاملی منو‌محور: همه کارها با شماره‌ها انجام می‌شود."""
    if not os.path.exists(STATE):
        print_intro()
        player = None
        while player is None:
            q = input("با کدام کشور شروع کنی؟ (ENTER = ایران): ").strip() or "ایران"
            player = next((n for n in COUNTRIES if q in n or n.startswith(q[:3])), None)
            if player is None:
                print("✗ کشور نامعتبر؛ دوباره بنویس (نمونه: ایران، ترکیه، روسیه)")
        main(["init", player])
    s = load()
    dash_names = {"1": "dom", "2": "dip", "3": "ops", "4": "mil", "5": "eco", "6": "org"}
    bar_menu = ("[1]📊 وضعیت [2]📋 داشبورد [3]🤝 دیپلماسی [4]🪖 ارتش/هسته‌ای [5]🕶 عملیات پنهان "
                "[6]💰 اقتصاد [7]🛒 بازار تجهیزات [8]🏛 نهادها [9]📁 پرونده کشور [10]🏆 رتبه "
                "[12]🤝 مذاکره [13]🧠 تصمیم کلیدی "
                "[0]🌙 پایان روز [خ] خروج")
    while True:
        try:
            line = input(f"\n{bar_menu}\n🎬 انتخاب: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 خداحافظ! بازی ذخیره شد.")
            return
        if not line:
            continue
        if line.lower() in ("خ", "خروج", "exit", "quit", "q"):
            print("👋 خداحافظ! بازی ذخیره شد.")
            return
        try:
            if line == "1":
                main(["status"])
            elif line == "2":
                print(" داشبورد: [1]سیاست [2]دیپلماسی [3]عملیات [4]نظامی [5]اقتصاد [6]نهادها")
                r = input("  کدام؟ ").strip()
                if r in dash_names:
                    main(["dash", dash_names[r]])
            elif line == "3":
                print(" دیپلماسی: [1]کمک اقتصادی [2]تجارت [3]پیمان عدم تعارض [4]اتحاد نظامی "
                      "[5]فسخ پیمان [6]تحریم [7]محکومیت در ملل")
                r = input("  کدام؟ ").strip()
                acts = {"1": "aide", "2": "trade", "3": "pact", "4": "ally", "5": "break", "6": "sanc", "7": "un"}
                if r in acts:
                    t = pick_country(s, f"کدام کشور؟ ({acts[r]})")
                    if t:
                        main(["act", acts[r], t])
            elif line == "4":
                print(" ارتش: [1]بودجه نظامی [2]فناوری [3]کلاهک هسته‌ای [4]شفافیت آژانس [5]اعلان جنگ")
                r = input("  کدام؟ ").strip()
                if r == "1":
                    main(["act", "mil"])
                elif r == "2":
                    main(["act", "tech"])
                elif r == "3":
                    main(["act", "nuke"])
                elif r == "4":
                    main(["act", "iaea"])
                elif r == "5":
                    t = pick_country(s, "به کدام کشور حمله کنی؟")
                    if t:
                        main(["act", "war", t])
            elif line == "5":
                print(" عملیات: [1]جاسوسی [2]بی‌ثبات‌سازی [3]خرابکاری [4]ترور [5]شبکه نیابتی")
                r = input("  کدام؟ ").strip()
                acts = {"1": "spy", "2": "covert", "3": "sabotage", "4": "kill", "5": "proxy"}
                if r in acts:
                    t = pick_country(s, f"هدف؟ ({acts[r]})")
                    if t:
                        main(["act", acts[r], t])
            elif line == "6":
                print(" اقتصاد: [1]سرمایه‌گذاری کلان [2]کمپین تبلیغاتی")
                r = input("  کدام؟ ").strip()
                if r == "1":
                    main(["act", "eco"])
                elif r == "2":
                    main(["act", "propaganda"])
            elif line == "7":
                equip_menu(s)
                s = load()
            elif line == "8":
                orgs_menu(s)
                s = load()
            elif line == "9":
                t = pick_country(s, "پرونده کدام کشور؟")
                if t:
                    main(["status", t])
            elif line == "10":
                main(["rank"])
            elif line == "0":
                main(["end"])
            elif line == "11":
                main(["help"])
            elif line == "12":
                negotiate_menu(s)
            elif line == "13":
                decide_menu(s)
            else:
                main(line.split())
            s = load()
        except SystemExit:
            raise
        except Exception as e:
            print(f"⚠ خطا در اجرای فرمان: {e}")

def print_intro():
    print("╔" + "═" * 52 + "╗")
    print("║        ⚔  ژئوپلیتیک: رقابت قدرت‌ها  ⚔                 ║")
    print("╚" + "═" * 52 + "╝")
    print()
    print(f" یک کشور را انتخاب کن تا رهبرش باشی (`init <نام>`):")
    notable = [n for n in COUNTRIES if n in SPECIAL] or list(COUNTRIES)[:10]
    for name in notable:
        c = COUNTRIES[name]
        print(f"  • {name:<12} {c['trait']}  (ارتش {c['mil']:.0f}، اقتصاد {c['eco']:.0f}، فناوری {c['tech']:.0f}، ثبات {c['stab']:.0f})")
    print(f"\n 🌍 کل کشورهای واقعی جهان در بازی حاضرند: {len(COUNTRIES)} کشور ({len(REGIONS)} منطقه) — فهرست: `list`")
    print("   هر کشور را می‌توانی برانگیزی؛ متحدت شو یا شبکه‌ی نیابتی در خاکش بیندازی!")
    print()
    print(f" هدف: تا سال {FINAL_YEAR} ابرقدرت اول جهان شو")
    print(" (یا باقی بمان! انقلاب و ضمیمه‌شدن = باخت)")
    print()
    print(HELP)

if __name__ == "__main__":
    main()
