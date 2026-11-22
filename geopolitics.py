#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""بازی استراتژیک ژئوپلیتیک متنی — ثبت وضعیت در game_state.json"""
import json, os, random, sys

STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game_state.json")

START_YEAR = 2025
FINAL_YEAR = 2065

# آمار تقریبی بر پایه داده‌های ۲۰۲۴ — اقتصاد (PPP-نسبی)، ارتش، فناوری، ثبات، خزانه آزاد
COUNTRIES = {
    "آمریکا":    dict(mil=95, eco=95, tech=95, stab=70, money=500, nukes=5, aggr=0.45, trait="ابَرقدرت فعلی، ۵ کلاهک (نماد منور ۵۰۰۰+)"),
    "چین":       dict(mil=88, eco=88, tech=82, stab=80, money=420, nukes=3, aggr=0.35, trait="ابَرقدرت نوظهور، نخستین اقتصاد دوم جهان"),
    "روسیه":     dict(mil=82, eco=55, tech=72, stab=62, money=180, nukes=5, aggr=0.60, trait="بازیگر خطرپذیر، انبار سلاح هسته‌ای"),
    "هند":       dict(mil=68, eco=62, tech=62, stab=58, money=200, nukes=1, aggr=0.30, trait="قدرت رو به رشد با جمعیت عظیم"),
    "آلمان":     dict(mil=52, eco=73, tech=85, stab=78, money=280, nukes=0, aggr=0.15, trait="قلب اقتصادی اروپا، صلح‌طلب"),
    "ژاپن":      dict(mil=55, eco=72, tech=88, stab=80, money=260, nukes=0, aggr=0.15, trait="فناوری پیشرفته، دفاعی"),
    "فرانسه":    dict(mil=64, eco=64, tech=80, stab=66, money=190, nukes=1, aggr=0.30, trait="قدرت هسته‌ای اروپایی، مداخله‌گر سابق"),
    "بریتانیا":  dict(mil=63, eco=63, tech=80, stab=68, money=180, nukes=1, aggr=0.40, trait="پیمان ویژه با آمریکا"),
    "ایران":     dict(mil=50, eco=45, tech=48, stab=45, money=70,  nukes=0, aggr=0.50, trait="تحت تحریم، منطقه‌ای و پرتحرک (حالت سخت)"),
}

# روابط اولیه واقع‌گرایانه (مقیاس -۱۰۰ تا +۱۰۰)
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
  act war   <کشور>     اعلان جنگ ⚔
  end                  پایان نوبت (نوبت کشورهای دیگر + رخداد تصادفی)
  status               وضعیت جهان
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
            rel[rel_key(a, b)] = DEFAULT_REL.get(key, rng.randint(-10, 30))
    # پیمان‌های اولیه واقع‌گرایانه: ناتو و متحدان
    pacts0 = []
    allies0 = []
    if player in ("آمریکا", "بریتانیا", "آلمان", "فرانسه"):
        for partner in ("آمریکا", "بریتانیا", "آلمان", "فرانسه"):
            if partner != player:
                allies0.append(partner)
    elif player == "ژاپن":
        allies0 = ["آمریکا"]
    state = dict(
        player=player, year=START_YEAR, turn=1, ap=2, over=False,
        world=world, relations=rel,
        allies=allies0, pacts=pacts0,
        politics={n: dict(parties=dict(PARTY_BASE if n == player else AI_PARTY_BASE), press=[]) for n in COUNTRIES},
        turn_events={},
        log=["سال ۲۰۲۵: تو رهبر %s شدی. جهان در آستانه یک دوران پرآشوب است." % player],
        at_war=[], eliminated=[],
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
    for i, (name, score, detail) in enumerate(ranking(s)):
        mark = "▶" if name == P else " "
        tag = " 💀" if name in s["eliminated"] else (" ⚔" if name in s["at_war"] else "")
        score_s = f"{score:.0f}" if score >= 0 else "  —"
        print(f"  {i+1:>2} {mark} {name:<12} {score_s:>5}   {detail}{tag}")
    print("─" * 56)
    if s["at_war"]:
        pairs = [f"{s['at_war'][i]} ↔ {s['at_war'][i+1]}" for i in range(0, len(s['at_war']) - 1, 2)]
        print(" جنگ‌های فعال: " + " | ".join(pairs))
    allies_all = [(n, o) for n in W for o in W if n < o and get_rel(s, n, o) > 70]
    print(" روابط شما:")
    for name in W:
        if name == P or name in s["eliminated"]: continue
        r = get_rel(s, P, name)
        tags = []
        if name in s["allies"]: tags.append("متحد")
        elif name in s["pacts"]: tags.append("عدم تجاوز")
        if name in s["at_war"]: tags.append("در جنگ")
        if name in s["eliminated"]: tags.append("حذف‌شده")
        print(f"  {name:<12} [{bar(r)}] {r:>4}  {' '.join(tags)}")
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
    if not os.path.exists(STATE):
        print("⚠ بازی‌ای ساخته نشده. اول: `init <کشور>`")
        print_intro()
        return
    s = load()
    if cmd == "status":
        show_status(s)
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
    while True:
        try:
            line = input("\n🎬 فرمان> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 خداحافظ! بازی به‌طور خودکار ذخیره شده بود.")
            return
        if not line:
            continue
        if line.lower() in ("خروج", "exit", "quit", "q"):
            print("👋 خداحافظ! بازی به‌طور خودکار ذخیره شده بود.")
            return
        try:
            main(line.split())
        except Exception as e:
            print(f"⚠ خطا در اجرای فرمان: {e}")

def print_intro():
    print("╔" + "═" * 52 + "╗")
    print("║        ⚔  ژئوپلیتیک: رقابت قدرت‌ها  ⚔                 ║")
    print("╚" + "═" * 52 + "╝")
    print()
    print(" یک کشور را انتخاب کن تا رهبرش باشی (`init <نام>`):")
    for name, c in COUNTRIES.items():
        print(f"  • {name:<12} {c['trait']}  (ارتش {c['mil']}، اقتصاد {c['eco']}، فناوری {c['tech']}، ثبات {c['stab']})")
    print()
    print(f" هدف: تا سال {FINAL_YEAR} ابرقدرت اول جهان شو")
    print(" (یا باقی بمان! انقلاب و ضمیمه‌شدن = باخت)")
    print()
    print(HELP)

if __name__ == "__main__":
    main()
