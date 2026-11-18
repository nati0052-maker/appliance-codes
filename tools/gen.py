#!/usr/bin/env python3
"""Generate Appliance Codes pages from PAGES data. Run from repo root."""
import html, json, os, re, sys, datetime

BASE = "https://nati0052-maker.github.io/appliance-codes"
TODAY = datetime.date.today().isoformat()
FONT = 'font-family="system-ui,sans-serif"'

LOGO = ('<svg class="logo" width="34" height="34" viewBox="0 0 40 40" aria-hidden="true"><rect x="3" y="3" width="34" height="34" rx="8" fill="#fff"/>'
        '<rect x="8" y="8" width="24" height="5" rx="2" fill="#0f6fde"/><circle cx="20" cy="25" r="8.5" fill="none" stroke="#0f6fde" stroke-width="3"/>'
        '<circle cx="20" cy="25" r="3" fill="#0f8a5f"/></svg>')
ICON_FIX = '<svg width="28" height="28" viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="16" fill="#e6f6ef"/><path d="M20.5 8.5a5 5 0 0 0-6.3 6.3l-6 6a1.8 1.8 0 0 0 2.5 2.5l6-6a5 5 0 0 0 6.3-6.3l-2.8 2.8-2.4-.6-.6-2.4z" fill="#0f8a5f"/></svg>'
ICON_PRO = '<svg width="28" height="28" viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="16" fill="#fdece4"/><path d="M11 8h3l1.5 4-2 1.5a10 10 0 0 0 5 5l1.5-2 4 1.5v3a2 2 0 0 1-2 2A15 15 0 0 1 9 10a2 2 0 0 1 2-2z" fill="#c2410c"/></svg>'
ICON_LIST = '<svg width="28" height="28" viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="16" fill="#e8f0fc"/><rect x="9" y="10" width="14" height="2.6" rx="1.3" fill="#0f6fde"/><rect x="9" y="15" width="14" height="2.6" rx="1.3" fill="#0f6fde"/><rect x="9" y="20" width="9" height="2.6" rx="1.3" fill="#0f6fde"/></svg>'

SEV = {"easy": ("easy", "Usually an easy fix", "Easy"),
       "mid": ("mid", "Some fixes need a technician", "Moderate"),
       "pro": ("pro", "Usually needs a technician", "Technician")}

def t(x, y, s, size=12, anchor="middle", fill="#16202a", bold=False):
    w = ' font-weight="700"' if bold else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{w} {FONT}>{s}</text>'

def fig(svg, label, caption):
    return (f'<figure>\n<svg viewBox="0 0 640 300" role="img" aria-label="{label}">\n'
            f'<rect x="0" y="0" width="640" height="300" fill="#f6f8fb" rx="10"/>\n{svg}\n</svg>\n'
            f'<figcaption>{caption}</figcaption>\n</figure>')

def fig_drain_filter():
    svg = ('<rect x="60" y="20" width="220" height="260" rx="14" fill="#fff" stroke="#9aa5b1" stroke-width="2"/>'
           '<rect x="76" y="34" width="188" height="26" rx="5" fill="#e2e8ee"/>'
           '<circle cx="170" cy="150" r="66" fill="#eef2f7" stroke="#9aa5b1" stroke-width="4"/><circle cx="170" cy="150" r="44" fill="#fff" stroke="#cfd6de" stroke-width="3"/>'
           + t(170, 155, "Door", 12, fill="#5d6a76") +
           '<rect x="76" y="236" width="70" height="32" rx="5" fill="#fff3e0" stroke="#b26b00" stroke-width="2.5"/>'
           '<circle cx="111" cy="252" r="38" fill="none" stroke="#0f8a5f" stroke-width="3" stroke-dasharray="6 5"/>'
           '<line x1="145" y1="246" x2="330" y2="160" stroke="#0f8a5f" stroke-width="3" stroke-dasharray="6 5"/>'
           '<circle cx="450" cy="150" r="110" fill="#fff" stroke="#0f8a5f" stroke-width="4"/>'
           '<rect x="380" y="95" width="140" height="80" rx="10" fill="#e2e8ee"/>'
           '<circle cx="470" cy="135" r="24" fill="#fff" stroke="#16202a" stroke-width="3"/><rect x="458" y="131" width="24" height="8" rx="3" fill="#16202a"/>'
           '<path d="M410 150 q0 40 -10 60" stroke="#16202a" stroke-width="5" fill="none" stroke-linecap="round"/><circle cx="400" cy="212" r="5" fill="#16202a"/>'
           + t(470, 196, "Filter cap", 12, bold=True) + t(400, 232, "Small drain hose", 11, fill="#5d6a76") +
           t(450, 250, "Drain into a shallow tray first", 11, fill="#5d6a76"))
    return fig(svg, "Diagram of a front-load washer showing the drain pump filter behind the small access panel at the bottom front",
               "Front-load washers: the drain pump filter sits behind the small panel at the bottom front. Drain the water through the small hose before unscrewing the cap.")

def fig_dishwasher():
    svg = ('<rect x="40" y="30" width="250" height="240" rx="12" fill="#fff" stroke="#9aa5b1" stroke-width="2"/>'
           '<rect x="56" y="46" width="218" height="180" rx="8" fill="#eef2f7"/>'
           '<line x1="70" y1="110" x2="260" y2="110" stroke="#9aa5b1" stroke-width="4"/><line x1="70" y1="170" x2="260" y2="170" stroke="#9aa5b1" stroke-width="4"/>'
           '<rect x="140" y="200" width="50" height="22" rx="4" fill="#fff3e0" stroke="#b26b00" stroke-width="2.5"/>'
           + t(165, 250, "Filter (tub floor)", 12, bold=True) +
           '<path d="M290 240 C330 240 330 80 400 80 C450 80 450 200 500 200" stroke="#5d6a76" stroke-width="7" fill="none" stroke-linecap="round"/>'
           '<rect x="470" y="200" width="120" height="70" rx="8" fill="#fff" stroke="#9aa5b1" stroke-width="2"/>'
           + t(530, 240, "Sink drain or", 11, fill="#5d6a76") + t(530, 256, "disposal", 11, fill="#5d6a76") +
           t(400, 64, "High loop", 12, bold=True) + t(400, 112, "No kinks or crushing", 11, fill="#5d6a76") +
           '<circle cx="500" cy="200" r="16" fill="none" stroke="#0f8a5f" stroke-width="3" stroke-dasharray="5 4"/>'
           + t(560, 186, "New disposal:", 11, anchor="middle", fill="#c2410c", bold=True) + t(560, 172, "knockout plug removed?", 11, fill="#c2410c"))
    return fig(svg, "Diagram of a dishwasher showing the filter on the tub floor and the drain hose running in a high loop to the sink drain",
               "Most drain codes come from a clogged filter on the tub floor or a drain hose that is kinked, crushed, or connected to a new disposal with its plug still in.")

def fig_door():
    svg = ('<rect x="60" y="20" width="220" height="260" rx="14" fill="#fff" stroke="#9aa5b1" stroke-width="2"/>'
           '<rect x="76" y="34" width="188" height="26" rx="5" fill="#e2e8ee"/>'
           '<circle cx="170" cy="160" r="78" fill="#eef2f7" stroke="#9aa5b1" stroke-width="4"/>'
           '<circle cx="170" cy="160" r="60" fill="#fff" stroke="#16202a" stroke-width="6"/>'
           '<path d="M120 196 q14 20 30 4" stroke="#b26b00" stroke-width="7" fill="none" stroke-linecap="round"/>'
           '<rect x="244" y="150" width="14" height="22" rx="3" fill="#c2410c"/>'
           '<line x1="258" y1="161" x2="360" y2="120" stroke="#0f8a5f" stroke-width="3" stroke-dasharray="6 5"/>'
           '<line x1="150" y1="204" x2="360" y2="215" stroke="#0f8a5f" stroke-width="3" stroke-dasharray="6 5"/>'
           '<rect x="360" y="90" width="250" height="60" rx="10" fill="#fff" stroke="#0f8a5f" stroke-width="2"/>'
           + t(485, 115, "Door latch and lock", 13, bold=True) + t(485, 134, "Press the door firmly until it clicks", 11, fill="#5d6a76") +
           '<rect x="360" y="185" width="250" height="60" rx="10" fill="#fff" stroke="#0f8a5f" stroke-width="2"/>'
           + t(485, 210, "Rubber door seal", 13, bold=True) + t(485, 229, "No laundry caught between door and seal", 11, fill="#5d6a76"))
    return fig(svg, "Diagram of a washer door showing the latch and the rubber seal where laundry can get caught",
               "Door codes usually mean the latch could not lock: check for laundry caught in the seal, then close the door firmly.")

def fig_balance():
    svg = ('<g transform="translate(40 0)">'
           '<circle cx="130" cy="150" r="100" fill="#fff" stroke="#9aa5b1" stroke-width="4"/>'
           '<path d="M60 200 A90 90 0 0 0 200 210 L170 180 Q130 200 80 170 Z" fill="#c2410c" opacity=".85"/>'
           + t(130, 70, "Unbalanced", 13, bold=True, fill="#c2410c") + t(130, 280, "Heavy items bunched on one side", 11, fill="#5d6a76") + '</g>'
           '<path d="M300 150 h40" stroke="#0f6fde" stroke-width="5" marker-end="url(#a)"/>'
           '<defs><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8z" fill="#0f6fde"/></marker></defs>'
           '<g transform="translate(330 0)">'
           '<circle cx="150" cy="150" r="100" fill="#fff" stroke="#9aa5b1" stroke-width="4"/>'
           '<circle cx="150" cy="150" r="78" fill="none" stroke="#0f8a5f" stroke-width="18" opacity=".8"/>'
           + t(150, 70, "Balanced", 13, bold=True, fill="#0f8a5f") + t(150, 280, "Load spread evenly, about 2/3 full", 11, fill="#5d6a76") + '</g>')
    return fig(svg, "Diagram comparing an unbalanced drum with laundry on one side and a balanced drum with laundry spread evenly",
               "Spread the laundry evenly around the drum. A single heavy item, or a very small load, is the most common cause.")

INLET = open('/home/claude/tools/inlet_fig.html').read()
FIGS = {"drain": fig_drain_filter, "dish": fig_dishwasher, "door": fig_door, "balance": fig_balance, "inlet": lambda: INLET}

APPL_NAME = {"washer": "Washer", "dishwasher": "Dishwasher", "dryer": "Dryer"}

def page_path(p): return f"{p['brand']}/{p['appl']}/{p['slug']}/"

def render(p, all_pages, related_extra):
    depth = "../../../"
    brand = p['brand_name']; appl = APPL_NAME[p['appl']]; code = p['code']
    title = f"{brand} {appl} {code} Error Code: What It Means and How to Fix It"
    sev = SEV[p['sev']]
    badges = f'<span class="badge {sev[0]}">{sev[1]}</span><span class="badge info">{p["time"]}</span>'
    if p.get('alt'): badges += f'<span class="badge info">Also shown as {p["alt"]}</span>'
    steps = "\n".join(f'<li><strong>{a}</strong> {b}</li>' for a, b in p['steps'])
    figure = FIGS[p['fig']]() + "\n" if p.get('fig') else ""
    # related table: same brand+appliance pages, plus extra rows
    rows = []
    for q in all_pages:
        if q['brand'] == p['brand'] and q['appl'] == p['appl']:
            label = q['code'] + (f" / {q['alt'].split(',')[0].strip()}" if q.get('alt') else "")
            s = SEV[q['sev']]
            if q is p:
                rows.append(f'<tr><td><strong>{label}</strong></td><td>{q["short_meaning"]} (this page)</td><td><span class="badge {s[0]}">{s[2]}</span></td></tr>')
            else:
                rows.append(f'<tr><td><strong><a href="{depth}{page_path(q)}">{label}</a></strong></td><td>{q["short_meaning"]}</td><td><span class="badge {s[0]}">{s[2]}</span></td></tr>')
    for c, mtxt, sv in related_extra.get((p['brand'], p['appl']), []):
        s = SEV[sv]
        rows.append(f'<tr><td><strong>{c}</strong></td><td>{mtxt}</td><td><span class="badge {s[0]}">{s[2]}</span></td></tr>')
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f"What does {code} mean on a {brand} {appl.lower()}?", "acceptedAnswer": {"@type": "Answer", "text": p['faq_meaning']}},
        {"@type": "Question", "name": f"Can I fix a {brand} {code} error myself?", "acceptedAnswer": {"@type": "Answer", "text": p['faq_fix']}}]}
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{html.escape(p['desc'])}">
<meta name="theme-color" content="#0b4fa3">
<link rel="stylesheet" href="{depth}style.css?v=2">
<script type="application/ld+json">
{json.dumps(faq)}
</script>
</head>
<body>
<header class="site-head"><div class="wrap">
<a href="{depth}">{LOGO}Appliance Codes</a>
<span class="tag">Plain answers to error codes</span>
</div></header>

<main class="wrap">
<div class="crumbs"><a href="{depth}">Home</a> / {brand} / {appl} / {code}</div>
<h1>{title}</h1>
<div class="badges">{badges}</div>

<div class="answer"><strong>Short answer:</strong> {p['short']}</div>

{figure}<h2>{ICON_FIX}{p.get('steps_title', 'Fix it yourself: checks in order')}</h2>
<ol class="steps">
{steps}
</ol>
<p>{p['after']}</p>

<h2>{ICON_PRO}When to call a technician</h2>
<div class="answer warn">{p['pro']}</div>

<h2>{ICON_LIST}Related {brand} {appl.lower()} codes</h2>
<table>
<tr><th>Code</th><th>Meaning</th><th>Difficulty</th></tr>
{chr(10).join(rows)}
</table>
<p class="meta">Codes vary by model. Your owner's manual is the final reference for your specific {appl.lower()}.</p>
</main>
<footer><div class="wrap">Independent guide, not affiliated with {brand}. Written from manufacturer troubleshooting guidance. <a href="{depth}about/">About and disclosures</a></div></footer>
</body>
</html>
'''

BRANDS = [("samsung", "Samsung"), ("lg", "LG"), ("whirlpool", "Whirlpool"), ("bosch", "Bosch"), ("ge", "GE"), ("frigidaire", "Frigidaire")]

def card_label(p):
    alt = f" / {p['alt'].split(',')[0].strip()}" if p.get('alt') else ""
    return f"{APPL_NAME[p['appl']]} {p['code']}{alt}: {p['card']}"

def build_index(all_pages):
    s = open('index.html').read()
    cards = []
    for b, name in BRANDS:
        ps = [p for p in all_pages if p['brand'] == b]
        if ps:
            items = "\n".join(f'<li><a href="{page_path(p)}">{card_label(p)}</a></li>' for p in sorted(ps, key=lambda x: (x['appl'], x['code'])))
            cards.append(f'<div class="brand-card" style="--c:var(--{b})"><h3>{name}</h3><ul>\n{items}\n</ul></div>')
        elif b in ("bosch", "ge"):
            cards.append(f'<div class="brand-card soon" style="--c:var(--{b})"><h3>{name}</h3><ul><li>Coming soon</li></ul></div>')
    new = '<div class="brands">\n' + "\n".join(cards) + '\n</div>'
    s = re.sub(r'<div class="brands">.*?\n</div>\n(?=\n<div class="how">)', new + '\n', s, flags=re.S)
    open('index.html', 'w').write(s)

def build_sitemap(all_pages):
    urls = [f"{BASE}/", f"{BASE}/about/"] + [f"{BASE}/{page_path(p)}" for p in all_pages]
    body = "\n".join(f"<url><loc>{u}</loc></url>" for u in urls)
    open('sitemap.xml', 'w').write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n')
