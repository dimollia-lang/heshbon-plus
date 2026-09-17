# -*- coding: utf-8 -*-
"""Сборка SEO-раздела heshbonplus.com/prava/ — справочник прав работника.

Запуск: python tools/build_prava.py   (из корня репозитория israel-tax-app)
Добавить страницу: дописать объект в PAGES и запустить заново. Скрипт сам
пересобирает /prava/index.html (хаб), sitemap.xml и robots.txt.

❗Правила: никаких сторонних трекеров (privacy.html обещает их отсутствие),
цифры — из rates.json и проверенных источников, в конце каждой страницы дата
проверки и дисклеймер «не юридическая консультация».
"""
import io, os, json, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://heshbonplus.com"
TODAY = datetime.date.today()
RU_MONTH = ["января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"]
UPDATED = "%d %s %d" % (TODAY.day, RU_MONTH[TODAY.month-1], TODAY.year)
BOT = "https://t.me/TlushScanBot?start=seo"

rates = json.loads(io.open(os.path.join(ROOT, "rates.json"), encoding="utf-8-sig").read())

CSS = """
:root{--bg:#f2f5fa;--card:#fff;--text:#1a2333;--muted:#64748b;--accent:#1a56db;--accent-soft:#e8effc;--green:#0e9f6e;--amber:#b45309;--amber-soft:#fdf3e3;--border:#e2e8f0;--radius:14px}
@media (prefers-color-scheme:dark){:root{--bg:#0e131d;--card:#171f2e;--text:#e6ecf5;--muted:#8b98ab;--accent:#6c9bff;--accent-soft:#1b2a4a;--green:#34d399;--amber:#fbbf24;--amber-soft:#33281180;--border:#26314a}}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--text);font:17px/1.7 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;-webkit-text-size-adjust:100%}
.wrap{max-width:760px;margin:0 auto;padding:0 18px}
nav{background:var(--card);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:5}
nav .in{max-width:760px;margin:0 auto;padding:0 18px;height:54px;display:flex;align-items:center;gap:16px;overflow-x:auto;white-space:nowrap}
nav a{color:var(--muted);text-decoration:none;font-size:.95rem}
nav a.brand{font-weight:800;color:var(--text);font-size:1.05rem}
nav a:hover{color:var(--accent)}
header{padding:30px 0 6px}
h1{font-size:1.85rem;line-height:1.28;margin-bottom:12px}
h2{font-size:1.28rem;margin:32px 0 10px}
h3{font-size:1.06rem;margin:20px 0 6px}
p{margin-bottom:14px}
a{color:var(--accent)}
ul,ol{margin:0 0 14px 22px}
li{margin-bottom:7px}
.lead{color:var(--muted);font-size:1.05rem}
.bc{font-size:.85rem;color:var(--muted);padding-top:14px}
.bc a{color:var(--muted)}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:18px;margin:18px 0}
.note{background:var(--amber-soft);border:1px solid var(--border);border-radius:var(--radius);padding:14px 16px;margin:18px 0;font-size:.95rem}
.tblwrap{overflow-x:auto;margin:16px 0;border:1px solid var(--border);border-radius:var(--radius)}
table{border-collapse:collapse;width:100%;background:var(--card);font-size:.95rem}
th,td{padding:10px 12px;border-bottom:1px solid var(--border);text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600;white-space:nowrap}
tr:last-child td{border-bottom:none}
.cta{display:inline-block;background:var(--accent);color:#fff;font-weight:700;text-decoration:none;padding:12px 18px;border-radius:12px;margin:6px 8px 6px 0}
.cta.alt{background:transparent;color:var(--accent);border:1px solid var(--accent)}
details{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:12px 16px;margin:10px 0}
summary{cursor:pointer;font-weight:600}
details p{margin:10px 0 2px}
.grid{display:grid;gap:12px;margin:18px 0}
@media(min-width:620px){.grid{grid-template-columns:1fr 1fr}}
a.tile{display:block;background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px;text-decoration:none;color:var(--text)}
a.tile:hover{border-color:var(--accent)}
a.tile b{display:block;margin-bottom:4px}
a.tile span{color:var(--muted);font-size:.92rem}
footer{border-top:1px solid var(--border);margin-top:40px;padding:22px 0 50px;color:var(--muted);font-size:.87rem}
""".strip()

NAV = ('<nav><div class="in">'
       '<a class="brand" href="/">Хешбон+</a>'
       '<a href="/prava/">Справочник прав</a>'
       '<a href="/">Калькуляторы</a>'
       '<a href="' + BOT + '" rel="nofollow">Разбор тлуша</a>'
       '</div></nav>')

def faq_jsonld(faq):
    items = [{"@type": "Question", "name": q,
              "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]
    return json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": items},
                      ensure_ascii=False)

def crumbs_jsonld(slug, name):
    items = [{"@type": "ListItem", "position": 1, "name": "Хешбон+", "item": SITE + "/"},
             {"@type": "ListItem", "position": 2, "name": "Права работника", "item": SITE + "/prava/"}]
    if slug:
        items.append({"@type": "ListItem", "position": 3, "name": name, "item": SITE + "/prava/" + slug + "/"})
    return json.dumps({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items},
                      ensure_ascii=False)

def page(slug, title, desc, h1, lead, body, faq, crumb):
    url = SITE + "/prava/" + (slug + "/" if slug else "")
    bc = ('<div class="bc"><a href="/">Главная</a> · <a href="/prava/">Права работника</a>'
          + (" · " + crumb if slug else "") + "</div>")
    faq_html = ""
    if faq:
        faq_html = "<h2>Частые вопросы</h2>\n" + "\n".join(
            "<details><summary>%s</summary><p>%s</p></details>" % (q, a) for q, a in faq)
    cta = ('<div class="card"><p><b>Проверьте свой случай по цифрам.</b> Пришлите фото тлуша боту в Telegram: '
           'он разберёт строки на русском и покажет, где расходится с законом. Бесплатно, без регистрации.</p>'
           '<a class="cta" href="' + BOT + '" rel="nofollow">Разобрать тлуш в боте</a>'
           '<a class="cta alt" href="/">Открыть калькуляторы</a></div>')
    tail = ('<footer><div class="wrap" style="padding:0">'
            '<p>Данные проверены ' + UPDATED + ' года. Ставки берём из официальных источников и обновляем в приложении.</p>'
            '<p>Материал образовательный и не является юридической консультацией. Спорные случаи решает суд по труду, '
            'по личной ситуации обращайтесь к адвокату по трудовому праву.</p>'
            '<p>© 2026 Хешбон+ · <a href="/">heshbonplus.com</a> · <a href="/prava/">Справочник прав</a></p>'
            '</div></footer>')
    scripts = '<script type="application/ld+json">%s</script>' % crumbs_jsonld(slug, crumb)
    if faq:
        scripts += '\n<script type="application/ld+json">%s</script>' % faq_jsonld(faq)
    return """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Хешбон+">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{site}/play/feature-1024x500.png">
{scripts}
<style>{css}</style>
</head>
<body>
{nav}
<div class="wrap">
{bc}
<header><h1>{h1}</h1><p class="lead">{lead}</p></header>
<main>
{body}
{cta}
{faq}
</main>
</div>
{tail}
</body>
</html>
""".format(title=title, desc=desc, url=url, site=SITE, scripts=scripts, css=CSS, nav=NAV,
           bc=bc, h1=h1, lead=lead, body=body, cta=cta, faq=faq_html, tail=tail)
