#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""بازی استراتژیک ژئوپلیتیک متنی — ثبت وضعیت در game_state.json"""
import json, os, random, sys

STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game_state.json")

START_YEAR = 2025
FINAL_YEAR = 2065

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

# روابط اولیه منجمد بین قدرت‌های بزرگ (مازاد بر کینه‌ها و دوستی‌ها بالا)
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
 فرمان‌ها (هر نوبت ۲ فرصت داری):

  act eco   <کشور؟>   سرمایه‌گذاری اقتصادی (۴۰ میلیارد)
  act mil              تقویت ارتش (۵۰ میلیارد)
  act tech             پژوهش فناوری (۳۵ میلیارد)
  act nuke             برنامه هسته‌ای (۱۲۰ میلیارد، فناوری ≥ ۷۰)
  act spy   <کشور>     جاسوسی (۱۵ میلیارد — اطلاعات + خطر تنش)
  act aide  <کشور>     کمک اقتصادی → بهبود روابط (۳۰ میلیارد)
  act trade <کشور>     قرارداد تجاری → هر دو نفع می‌برید (۲۰ میلیارد)
  act pact  <کشور>     پیمان عدم تجاوز (روابط ≥ ۳۵)
  act ally  <کشور>     اتحاد نظامی (روابط ≥ ۶۵)
  act sanc  <کشور>     تحریم اقتصادی (روابط ↓↓)
  act covert <کشور>    عملیات مخفي: بی‌ثبات‌سازی (خطرناک، ۵۰ میلیارد)
  act propaganda       تبلیغات حزبی — حمایت ائتلاف حاکم ↑ (۲۰ میلیارد)
  act sabotage <کشور>  خرابکاری در صنایع دفاعی (۴۵ میلیارد، ریسک کشف)
  act kill  <کشور>     ترور رهبر دشمن ☠ (۸۰ میلیارد، بسیار پرخطر)
  act proxy <کشور>     ایجاد/تقویت شبکه نیابتی مخفی 🗡 (۶۰، تکرار: ۴۰ میلیارد)
  act war   <کشور>     اعلان جنگ ⚔
  end                  پایان نوبت (نوبت کشورهای دیگر + رخداد تصادفی)
  status               وضعیت مختصر جهان (۱۲ قدرت نخست)
  status <کشور>        پرونده کامل یک کشور 📊 (مثال: status ترکیه)
  dash <بخش؟>          داشبورد: dom | dip | ops | mil | eco (بدون اسم = همه)
  rank                 رتبه‌بندی کامل همه کشورها
  list <منطقه؟>        فهرست کشورهای واقعی به تفکیک منطقه
  help                 راهنما
  help                 راهنما
"""

def load():
    with open(STATE, encoding="utf-8") as f:
        s = json.load(f)
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
    if not isinstance(s.get("turn_events"), dict):
        s["turn_events"] = {}
    s.setdefault("proxies", [])
    return s

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
    return c["mil"] * (1 + c["tech"] / 200) * (1.1 if c["nukes"] else 1.0) * (0.8 if c["stab"] < 40 else 1.0)

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
    state = dict(
        player=player, year=START_YEAR, turn=1, ap=2, over=False,
        world=world, relations=rel,
        allies=allies0, pacts=pacts0,
        politics={n: dict(parties=dict(PARTY_BASE if n == player else AI_PARTY_BASE), press=[]) for n in COUNTRIES},
        turn_events={},
        log=["سال ۲۰۲۵: تو رهبر %s شدی. جهان در آستانه یک دوران پرآشوب است." % player],
        at_war=[], eliminated=[], proxies=[],
    )
    save(state)
    return state

# ---------- سیاست داخلی: احزاب و مطبوعات ----------

PARTY_BASE = {"اصلاح‌طلبان": 26, "جبهه انقلاب": 27, "ملی‌گرایان": 25, "تکنوکرات‌ها": 22}
WEST = {"آمریکا", "بریتانیا", "فرانسه", "آلمان", "ژاپن"}
EAST = {"روسیه", "چین"}

AI_PARTY_BASE = {"حاکمیت": 38, "اپوزیسیون": 24, "ارتش‌گرایان": 20, "تجار": 18}

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
    if s["ap"] <= 0:
        print("⚠ فرصت این نوبت تمام شده. با `end` نوبت را ببند.")
        return
    if len(args) < 1:
        print(HELP)
        return
    action = args[0].lower()
    W = s["world"]; P = s["player"]; me = W[P]
    target = None
    if len(args) >= 2:
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
        s["ap"] -= 1
        save(s)
        print(f"فرصت باقی‌مانده در این نوبت: {s['ap']}")

    if action == "eco":
        if not pay(40): return
        me["eco"] += 6; me["stab"] += 1
        msg(s, "سرمایه‌گذاری کلان زیرساختی — اقتصاد رونق گرفت.")
        print(f"✔ اقتصاد بالا رفت → {me['eco']:.0f}")
        ev(s, P, "eco")
    elif action == "mil":
        if not pay(50): return
        me["mil"] += 7; me["stab"] -= 2
        msg(s, "بودجه دفاعی سنگین تخصیص یافت.")
        print(f"✔ ارتش تقویت شد → {me['mil']:.0f} (ثبات -۲)")
        ev(s, P, "mil")
    elif action == "tech":
        if not pay(35): return
        me["tech"] += 7; me["eco"] += 1
        print(f"✔ پیشرفت فناوری → {me['tech']:.0f}")
        ev(s, P, "tech")
    elif action == "nuke":
        if me["tech"] < 70:
            print("✗ برای برنامه هسته‌ای فناوری ≥ ۷۰ لازم است.")
            return
        if not pay(120): return
        me["nukes"] += 1; add_rel(s, P, None, 0)
        msg(s, f"{P} آزمایش هسته‌ای جدیدی انجام داد! جهان نگران شد.")
        for o in W:
            if o != P: add_rel(s, P, o, -8)
        print(f"☢ کلاهک ساخته شد → مجموع: {me['nukes']} (محکومیت جهانی، روابط همه -۸)")
        ev(s, P, "nuke")
    elif action == "spy":
        if not pay(15): return
        t = W[target]
        add_rel(s, P, target, -5)
        if random.random() < 0.75:
            msg(s, f"جاسوسان در {target} اطلاعات نظامی کیف‌کردند.")
            print(f"🕵 گزارش از {target}: ارتش {t['mil']:.0f} | اقتصاد {t['eco']:.0f} | فناوری {t['tech']:.0f} | ثبات {t['stab']:.0f} | کلاهک: {t['nukes']}")
        else:
            print(f"⚠ مأمور لو رفت! آبرو رفت (روابط {P}–{target} افت کرد).")
    elif action == "aide":
        if target is None: print("✗ کشور مقصد را بنویس: `act aide کیوان`"); return
        if not pay(30): return
        add_rel(s, P, target, 14)
        t = W[target]; t["eco"] += 2
        print(f"✔ کمک اقتصادی به {target} — روابط +۱۴")
    elif action == "trade":
        if target is None: print("✗ کشور مقصد را بنویس."); return
        if not pay(20): return
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
        if not pay(10): return
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
        if not pay(25): return
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
        if not pay(50): return
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
        if not pay(20): return
        ev(s, P, "propaganda")
        me["stab"] -= 1
        msg(s, "کمپین تبلیغاتی گسترده در داخل راه افتاد؛ فضای سیاسی دوقطبی شد.")
        print("📢 تبلیغات حزبی: حمایت ائتلاف حاکم بالا رفت (ثبات -۱)")
    elif action == "sabotage":
        if target is None: print("✗ هدف را مشخص کن: `act sabotage روسیه`"); return
        if not pay(45): return
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
        if not pay(80): return
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
        cost = 40 if existing else 60
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
                s["proxies"].append({"sponsor": P, "host": target, "power": 2, "hidden": True})
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
    a_allies = [x for x in W if x != atk and x in s["allies"] and x != dfn]
    for x in a_allies:
        atk_pow += power(W[x]) * 0.25
    for x in W:
        if x not in (atk, dfn):
            add_rel(s, atk, x, -10 if x == dfn or x == s["player"] else -4)
    s["at_war"] += [atk, dfn]
    msg(s, f"⚔ جنگ! {atk} به {dfn} حمله کرد.")
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
    me = s["world"][s["player"]]
    if me["stab"] <= 0:
        s["over"] = True
        print("💀💀💥 انقلاب داخلی! دولت تو سرنگون شد. GAME OVER 💀💀")

# ---------- turn resolution ----------

def end_turn(s):
    if s["over"]: print("بازی تمام شده."); return
    W = s["world"]; P = s["player"]
    log = []
    # درآمد
    for name, c in W.items():
        if name in s["eliminated"]: continue
        base = c["eco"] * 0.25
        if c["stab"] < 30: base *= 0.5
        c["money"] += base
        if name == P:
            log.append(f"درآمد سالانه: +{base:.0f} میلیارد")
    # آشوب داخلی
    for name, c in W.items():
        if name in s["eliminated"]: continue
        drift = -2 if c["mil"] > 70 else 1
        if c["eco"] > 70: drift += 1
        c["stab"] = max(0, min(100, c["stab"] + drift + random.randint(-2, 2)))
        if name != P and c["stab"] < 15 and random.random() < 0.15:
            c["eco"] -= 5
            log.append(f"⚠ در {name} ناآرامی داخلی بالا گرفت.")
    # هوش مصنوعی کشورها
    for name, c in W.items():
        if name in s["eliminated"] or name == P: continue
        targets = [o for o in W if o not in s["eliminated"] + [name]]
        r = random.random()
        rivals = sorted(targets, key=lambda o: get_rel(s, name, o))[:2]
        friends = sorted(targets, key=lambda o: -get_rel(s, name, o))[:2]
        if r < 0.20:
            c["eco"] += 4; log.append(f"{name} روی اقتصادش سرمایه‌گذاری کرد.")
        elif r < 0.40:
            c["mil"] += 5; log.append(f"📖 {name} بودجه نظامی را افزایش داد.")
        elif r < 0.55:
            friend = random.choice(friends)
            add_rel(s, name, friend, 10)
            log.append(f"🤝 {name} و {friend} روابطشان را گرم کردند.")
        elif r < 0.65 and rivals:
            foe = random.choice(rivals)
            if get_rel(s, name, foe) < 0:
                foe_c = W[foe]; foe_c["eco"] = max(10, foe_c["eco"] - 3)
                add_rel(s, name, foe, -5)
                log.append(f"⛔ {name} علیه {foe} تحریم وضع کرد.")
                if foe == P: ev(s, P, "sanctioned_by", name)
        elif r < 0.72 and c["tech"] >= 70 and c["nukes"] < 2 and c["money"] > 100:
            c["money"] -= 100; c["nukes"] += 1
            log.append(f"☢ {name} وارد باشگاه هسته‌ای شد!")
            for o in W:
                if o not in s["eliminated"] + [name]: add_rel(s, name, o, -6)
        elif r < 0.78 and c["aggr"] > 0.4 and rivals and c["mil"] > 65:
            foe = min(rivals, key=lambda o: power(W[o]))
            if foe != name and W[foe]["stab"] < 55 and name not in s["eliminated"]:
                if foe != P or c["aggr"] > 0.6:
                    before = _snapshot_clear()
                    start_war(s, name, foe)
                    log.append(f"⚔ {name} به {foe} اعلان جنگ داد!")
        elif r < 0.85:
            c["tech"] += 4; log.append(f"🔬 {name} در فناوری رشد کرد.")
        elif r < 0.92 and rivals and c["aggr"] > 0.25:
            foe = min(rivals, key=lambda o: get_rel(s, name, o))
            if get_rel(s, name, foe) < -35 and foe not in s["eliminated"]:
                foe_c = W[foe]
                op = random.random()
                if op < 0.55:
                    if random.random() < 0.55:
                        foe_c["mil"] = max(10, foe_c["mil"] - 6); foe_c["eco"] = max(10, foe_c["eco"] - 2)
                        ev(s, name, "sabotage_ok", foe); ev(s, foe, "sabotage_victim", name)
                        log.append(f"🕵 عملیات خرابکاری خاموش {name} علیه زیرساخت‌های {foe} موفق بود.")
                    else:
                        ev(s, name, "sabotage_fail", foe)
                        log.append(f"🕵 عملیات خرابکاری {name} علیه {foe} افشا و ناکام ماند.")
                elif op < 0.80:
                    log.append(f"🕵 سازمان اطلاعاتی {name} فعالیت جاسوسی گسترده‌ای را کلید زد.")
                else:
                    if random.random() < 0.30:
                        foe_c["stab"] = max(0, foe_c["stab"] - 15); foe_c["eco"] = max(10, foe_c["eco"] - 3)
                        add_rel(s, name, foe, -35)
                        for o in W:
                            if o not in (name, foe) and o not in s["eliminated"]:
                                add_rel(s, name, o, -8)
                        ev(s, name, "kill_ok", foe); ev(s, foe, "kill_victim", name)
                        log.append(f"☠ ترور دولتمردان ارشد {foe}! نقشه توسط {name} اجرا شده و جامعه جهانی را تکان داد.")
                    else:
                        add_rel(s, name, foe, -10)
                        ev(s, name, "kill_fail", foe); ev(s, foe, "kill_attempt", name)
                        log.append(f"☠ نقشه ترور عوامل {name} در {foe} افشا و خنثی شد.")
        elif r < 0.96 and rivals and c["aggr"] > 0.5 and c["money"] >= 60:
            foe = min(rivals, key=lambda o: get_rel(s, name, o))
            already = any(x["sponsor"] == name and x["host"] == foe for x in s.get("proxies", []))
            if get_rel(s, name, foe) < -30 and not already and foe not in s["eliminated"]:
                c["money"] -= 60
                s["proxies"].append({"sponsor": name, "host": foe, "power": 2, "hidden": True})
                W[foe]["stab"] = max(0, W[foe]["stab"] - 4)
                add_rel(s, name, foe, -15)
                log.append(f"🕵 شواهدی از شبکه نیابتی {name} در {foe} دیده شده است.")
                if foe == P:
                    ev(s, P, "sabotage_victim", name)
    # جنگ‌های در جریان: فرسایش صلح
    if s["at_war"]:
        war_pairs = [s["at_war"][i:i + 2] for i in range(0, len(s["at_war"]) - 1, 2)]
        for a, d in war_pairs:
            if a in s["eliminated"] or d in s["eliminated"]: continue
            Wa, Wd = W[a], W[d]
            done = False
            if power(Wa) > power(Wd) * 1.6 and Wd["stab"] < 35:
                annex(s, a, d); done = True
            elif power(Wd) > power(Wa) * 1.6 and Wa["stab"] < 35:
                annex(s, d, a); done = True
            if not done:
                Wa["mil"] = max(10, Wa["mil"] - 2); Wd["mil"] = max(10, Wd["mil"] - 2)
                Wa["eco"] -= 1; Wd["eco"] -= 1
                if random.random() < 0.12:
                    if s["player"] in (a, d):
                        me2 = W[s["player"]]; me2["stab"] -= 4
                        log.append(f"جنگ فرسایشی ادامه دارد... ثبات {s['player']} افت کرد (-۴). نوبت مذاکره؟")
                    else:
                        if random.random() < 0.5:
                            rel = get_rel(s, a, d) + 15
                            set_rel(s, a, d, rel)
                            log.append(f"🕊 {a} و {d} آتش‌بس نسبی برقرار کردند.")
        seen = set(); final = []
        for pr in war_pairs:
            if pr[0] in s["eliminated"] or pr[1] in s["eliminated"]: continue
            if pr[0] in seen or pr[1] in seen: continue
            seen.add(pr[0]); seen.add(pr[1]); final.extend(pr)
        s["at_war"] = final

    # نیروهای نیابتی: نگه‌داری، عملیات و کشف
    kept = []
    for px in s.get("proxies", []):
        sp, host = px.get("sponsor"), px.get("host")
        if sp not in W or host not in W or sp in s["eliminated"] or host in s["eliminated"]:
            continue
        pw = px["power"]
        Wh = W[host]
        Wh["stab"] = max(0, Wh["stab"] - (2 if pw >= 4 else 1))
        if sp in W and sp not in s["eliminated"]:
            W[sp]["influence"] += 0.5
        if Wh["stab"] < 45 and random.random() < 0.08 + pw * 0.03:
            Wh["eco"] = max(10, Wh["eco"] - 5)
            Wh["stab"] = max(0, Wh["stab"] - 5)
            log.append(f"🔥 شبه‌نظامیان {sp} در {host} عملیات گسترده انجام دادند!")
            ev(s, host, "uprising", sp)
            if host == P:
                end_of_action_checks(s)
        elif host == P and random.random() < 0.35:
            log.append(f"⚠ شبه‌نظامیان {sp} در خاک تو فعال‌اند (قدرت {pw}/۵).")
            ev(s, P, "sabotage_victim", sp)
        if random.random() < 0.10:
            add_rel(s, sp, host, -18)
            log.append(f"🔓 شبکه نیابتی {sp} در {host} لو رفت!")
            ev(s, sp, "covert_fail", host)
            ev(s, host, "sabotage_victim", sp)
            if sp == P:
                me_ = W[P]
                me_["stab"] = max(0, me_["stab"] - 2)
            continue
        kept.append(px)
    s["proxies"] = kept

    # رخداد تصادفی جهانی
    if random.random() < 0.55:
        event = random.choice([
            "crisis_oil", "boom", "uprising", "tech_break",
            "plague", "alliance_shift",
        ])
        alive = [n for n in W if n not in s["eliminated"]]
        if event == "crisis_oil":
            n = random.choice(alive)
            W[n]["eco"] -= 6; W[n]["money"] -= 30
            if n == P: ev(s, P, "oil_crisis")
            log.append(f"📉 بحران انرژی! چرخ اقتصادی {n} دچار افت شد.")
        elif event == "boom":
            n = random.choice(alive)
            W[n]["eco"] += 6; W[n]["money"] += 40
            if n == P: ev(s, P, "boom")
            log.append(f"📈 رونق جهانی بازار — {n} بیشترین سود را برد.")
        elif event == "uprising":
            core = [n for n in alive if W[n]["stab"] < 55] or alive
            n = random.choice(core)
            W[n]["stab"] -= 10
            log.append(f"🔥 خیزش مردمی در {n} — ثبات -۱۰.")
            if n == s["player"]:
                ev(s, P, "uprising")
                end_of_action_checks(s)
        elif event == "tech_break":
            n = random.choice(alive)
            W[n]["tech"] += 6
            if n == P: ev(s, P, "tech_break")
            log.append(f"💡 جهش فناورانه در {n} — فناوری +۶.")
        elif event == "plague":
            n = random.choice(alive)
            W[n]["eco"] -= 4; W[n]["stab"] -= 4; W[n]["mil"] = max(10, W[n]["mil"] - 2)
            if n == P: ev(s, P, "plague")
            log.append(f"🦠 بیماری همه‌گیر صنایع {n} را فلج کرد.")
        elif event == "alliance_shift":
            a, b = random.sample(alive, min(2, len(alive)))
            if a == s["player"] or b == s["player"]:
                log.append("🌐 مجمع جهانی: شور و شورای دیپلماتیک، همه مشغول لابی‌گری.")
            add_rel(s, a, b, 6)
            log.append(f"🌐 دیپلماسی خاموش: فاصله {a} و {b} بیشتر شد... یا کمتر؟")
    if s["at_war"] and s["player"] in s["at_war"]:
        me = W[s["player"]]
        me["stab"] = max(0, me["stab"] - 2)
    # احزاب و مطبوعات همه کشورها به رخدادها واکنش نشان می‌دهند
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
    # پیشرفت سال
    s["year"] += 1; s["turn"] += 1; s["ap"] = 2
    save(s)
    print()
    print("─" * 46)
    print("📣 گزارش سال " + str(s["year"] - 1))
    for line in log[-8:]:
        print("  • " + line)
    if pop_lines:
        print(" 🏛 حزب‌ها: " + " | ".join(pop_lines))
    for h in heads:
        print("   " + h)
    if foreign_digest:
        print(" 🌐 نشریات خارجی:")
        for fl in foreign_digest[:3]:
            print("  " + fl)
    print("─" * 46)
    check_victory(s)
    if s["over"]:
        print("\n🏁 بازی تمام شد. برای شروع دوباره: `reset` بعد `init <کشور>`")
    else:
        print(f"سال {s['year']} — نوبت تو بود! ({s['ap']} فرصت)\n")

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

def show_status(s):
    W = s["world"]; P = s["player"]; me = W[P]
    print("═" * 56)
    print(f"  سال {s['year']} | نوبت {s['turn']} | فرصت این نوبت: {s['ap']}")
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
            print(f"   ▸ در {px['host']:<14} قدرت [{bar(px['power'] * 20)}] {px['power']}/۵  ({st})")
    else:
        print(" 🗡 هنوز شبکه نیابتی نداری — با `act proxy <کشور>` بساز (۶۰ میلیارد، مخفی).")
    if inside:
        print()
        print(" ⚠ شبکه‌های نیابتی بیگانه در خاک تو:")
        for px in inside:
            print(f"   ▸ عوامل {px['sponsor']:<12} قدرت [{bar(px['power'] * 20)}] {px['power']}/۵")
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
    inc = me["eco"] * 0.25 * (0.5 if me["stab"] < 30 else 1.0)
    print(f"  خزانه {me['money']:.0f} میلیارد   |   درآمد تخمینی سالانه +{inc:.0f}")
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

def dash(s, section=""):
    section = section.strip().lower()
    alias = {
        "dom": "dom", "سیاست": "dom", "داخلی": "dom",
        "dip": "dip", "دیپلماسی": "dip", "خارجی": "dip",
        "ops": "ops", "عملیات": "ops", "جاسوسی": "ops", "نیابتی": "ops",
        "mil": "mil", "نظامی": "mil", "جنگ": "mil",
        "eco": "eco", "اقتصاد": "eco", "خزانه": "eco",
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
    if name != P:
        print(f"   رابطه با تو {P}: {r:.0f} [{bar(max(0, r))}]")
    pol = (s.get("politics") or {}).get(name) or {}
    prx = [px for px in s.get("proxies", []) if px["host"] == name]
    if prx:
        shown = [px for px in prx if px["sponsor"] == P]
        if shown:
            print("   🗡 شبکه نیابتی شما اینجا: " + "، ".join(f"قدرت {px['power']}/۵" for px in shown))
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

def main(argv=None):
    args = argv if argv is not None else sys.argv[1:]
    if not args:
        if os.path.exists(STATE):
            show_status(load())
        else:
            print_intro()
        return
    cmd = args[0]
    if cmd in ("play", "بازی"):
        play()
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
    elif cmd == "help":
        print(HELP)
    elif cmd == "act":
        do_act(s, args[1:])
    elif cmd == "end":
        end_turn(s)
    else:
        print("✗ فرمان ناشناخته. `help` بزن.")

def play():
    """حالت تعاملی: `python geopolitics.py play` — فرمان‌ها را پشت‌سرهم اجرا می‌کند."""
    if os.path.exists(STATE):
        show_status(load())
    else:
        print_intro()
    print("حالت تعاملی فعال شد. فرمان‌ها را بنویس (`help`) — برای خروج: خروج")
    menu = {
        "1": ["status"], "2": ["dash", "dom"], "3": ["dash", "dip"],
        "4": ["dash", "ops"], "5": ["dash", "mil"], "6": ["dash", "eco"],
        "7": ["end"], "8": ["help"], "9": ["rank"],
    }
    bar_menu = ("[1]📊 وضعیت [2]🏛 سیاست [3]🌐 دیپلماسی [4]🕵 عملیات "
                "[5]⚔ نظامی [6]💰 اقتصاد [7]✅ پایان نوبت [8]❔ راهنما [9]🌍 رتبه‌بندی")
    while True:
        try:
            line = input(f"\n{bar_menu}\n🎬 فرمان> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 خداحافظ! بازی به‌طور خودکار ذخیره شده بود.")
            return
        if not line:
            continue
        if line.lower() in ("خروج", "exit", "quit", "q"):
            print("👋 خداحافظ! بازی به‌طور خودکار ذخیره شده بود.")
            return
        try:
            if line in menu:
                main(menu[line])
            else:
                main(line.split())
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
