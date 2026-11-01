"""Regenerate the CSVs and index.html for the Cearn Solar Farm data set.

Usage: python build.py cearn-solar-farm-sources.json
"""
import csv
import html
import json
import os
import sys

EM_DASH = "—"

src = sys.argv[1]
out = os.path.dirname(os.path.abspath(src))
raw = open(src, encoding="utf-8").read()
if EM_DASH in raw:
    sys.exit("em dash found in data; replace it before building")
d = json.loads(raw)


def flat(v):
    if isinstance(v, list):
        if v and isinstance(v[0], dict) and "url" in v[0]:
            return " | ".join(f"{x['url']} ({x.get('status', '')})" for x in v)
        return " | ".join(str(x) for x in v)
    return "" if v is None else str(v)


def write_csv(name, rows):
    rows = [r for r in rows if isinstance(r, dict)]
    cols = []
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    with open(os.path.join(out, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: flat(r.get(c, "")) for c in cols})
    return cols


SECTIONS = [
    ("key_dates", "key-dates.csv", "Key dates and timeline"),
    ("nearby_solar_schemes", "nearby-solar-schemes.csv", "Nearby solar schemes"),
    ("local_councils", "local-councils.csv", "Parish and town councils"),
    ("representatives", "representatives.csv", "Representatives and decision-makers"),
    ("council_positions", "council-positions.csv", "Council and organisation positions"),
    ("campaign_groups", "campaign-groups.csv", "Campaign groups"),
    ("national_and_other_sources", "national-and-other-sources.csv", "Monitoring sources"),
    ("how_to_get_involved", "how-to-get-involved.csv", "How to get involved"),
]

e = html.escape


def cell(v):
    if isinstance(v, list):
        if v and isinstance(v[0], dict):
            return "<br>".join(f"{link(x['url'])} <small>{e(x.get('status', ''))}</small>" for x in v)
        return "<br>".join(link(str(x)) for x in v)
    s = flat(v)
    return link(s)


def link(s):
    if s.startswith("http"):
        return f'<a href="{e(s)}" target="_blank" rel="noopener">{e(s)}</a>'
    return e(s)


def badge(v):
    cls = "v" if v.startswith("verified") else ("p" if v.startswith("partly") else "u")
    return f'<span class="b {cls}">{e(v)}</span>'


def table(rows, cols):
    h = "<div class='tw'><table><thead><tr>" + "".join(
        f"<th>{e(c.replace('_', ' ').capitalize())}</th>" for c in cols) + "</tr></thead><tbody>"
    for r in rows:
        if not isinstance(r, dict):
            continue
        h += "<tr>" + "".join(
            f"<td>{badge(r.get(c, '')) if c == 'verification' and r.get(c) else cell(r.get(c, ''))}</td>"
            for c in cols) + "</tr>"
    return h + "</tbody></table></div>"


body = ""
nav = ""
for key, fname, title in SECTIONS:
    rows = d.get(key, [])
    cols = write_csv(fname, rows)
    anchor = key.replace("_", "-")
    nav += f'<a href="#{anchor}">{e(title)}</a>'
    body += f'<h2 id="{anchor}">{e(title)}</h2>' + table(rows, cols)

m = d["meta"]
sch = d["scheme"]
lr = d["links_to_reservoir"]
scheme_html = "<ul>" + "".join(
    f"<li><b>{e(k.replace('_', ' ').capitalize())}:</b> {cell(v) if not isinstance(v, list) or (v and isinstance(v[0], str)) else ''}</li>"
    for k, v in sch.items() if k != "developer_documents") + "</ul>"
docs_html = "<ul>" + "".join(f"<li>{e(x['title'])}: {link(x['url'])}</li>" for x in sch["developer_documents"]) + "</ul>"
links_html = "<ul>" + "".join(f"<li><b>{e(k.replace('_', ' ').capitalize())}:</b> {e(v)}</li>" for k, v in lr.items()) + "</ul>"
todo_html = "<ul>" + "".join(f"<li>{e(x)}</li>" for x in d["still_to_check_by_hand"]) + "</ul>"

page = f"""<!DOCTYPE html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cearn Solar Farm: verified data sources</title>
<style>
:root{{--bg:#fbfaf7;--fg:#1d1d1b;--mut:#5f5e5a;--line:#e3e0d8;--acc:#7a5a1f;--g:#2e7d4f;--a:#a86b12;--r:#a8322d}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161615;--fg:#ecebe6;--mut:#a3a19a;--line:#33322f;--acc:#e0b866;--g:#6fcf97;--a:#e0a84a;--r:#ef7f78}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:1200px;margin:0 auto;padding:24px 16px 64px}}
h1{{font-size:1.6rem;margin:0 0 4px}} h2{{font-size:1.15rem;margin:36px 0 8px;border-bottom:1px solid var(--line);padding-bottom:4px}}
p.m{{color:var(--mut);margin:0 0 12px}} a{{color:var(--acc);word-break:break-all}}
nav a{{margin-right:14px;word-break:normal;display:inline-block}}
.tw{{overflow-x:auto;border:1px solid var(--line);border-radius:6px}}
table{{border-collapse:collapse;width:100%;font-size:13px}} th,td{{text-align:left;vertical-align:top;padding:6px 8px;border-bottom:1px solid var(--line)}}
th{{position:sticky;top:0;background:var(--bg);font-weight:600}} td{{min-width:90px}}
.b{{display:inline-block;padding:1px 6px;border-radius:10px;font-size:12px;border:1px solid currentColor;white-space:nowrap}}
.v{{color:var(--g)}} .p{{color:var(--a)}} .u{{color:var(--r)}}
input{{width:100%;max-width:420px;padding:8px;border:1px solid var(--line);border-radius:6px;background:transparent;color:var(--fg);margin:8px 0}}
small{{color:var(--mut)}} ul{{padding-left:20px}}
</style></head><body><main>
<h1>Cearn Solar Farm: verified data sources</h1>
<p class="m">Checked {e(m['checked_on'])}. Planning Inspectorate reference {e(m['pins_reference'])}. {e(m['stage'])}</p>
<p class="m">{e(m['consenting_route'])}</p>
<p class="m">{badge('verified')} fetched and confirmed &nbsp; {badge('partly verified')} some fields confirmed &nbsp; {badge('unverified')} needs a manual check</p>
<nav><a href="#scheme">The scheme</a><a href="#links">Links to the reservoir</a>{nav}<a href="#todo">Still to check</a></nav>
<input id="q" placeholder="Filter all tables (e.g. Charney, Goosey, Farmoor)">
<h2 id="scheme">The scheme</h2>{scheme_html}<p class="m">Developer documents:</p>{docs_html}
<h2 id="links">Links to the White Horse Reservoir</h2>{links_html}
{body}
<h2 id="todo">Still to check by hand</h2>{todo_html}
</main>
<script>
document.getElementById('q').addEventListener('input',function(){{var q=this.value.toLowerCase();document.querySelectorAll('tbody tr').forEach(function(r){{r.style.display=r.textContent.toLowerCase().indexOf(q)>-1?'':'none';}});}});
</script></body></html>"""
if EM_DASH in page:
    sys.exit("em dash found in page")
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page)
print("ok", {k: len(d.get(k, [])) for k, _, _ in SECTIONS})
