import json, csv, sys, html, os

src = sys.argv[1]
out = os.path.dirname(src)
d = json.load(open(src, encoding="utf-8"))

raw = open(src, encoding="utf-8").read()
assert "—" not in raw, "em dash found"

def write_csv(name, rows, cols):
    with open(os.path.join(out, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            r = dict(r)
            if "feeds" in r:
                r["feeds"] = " | ".join(f"{x['url']} ({x['status']})" for x in r["feeds"])
            w.writerow({c: r.get(c, "") for c in cols})

lc_cols = ["name","type","access_points","affected_how","website","meetings_url","meeting_pattern","latest_minutes","minutes_format","platform","feeds","reservoir_mention","contact","facebook","verification","notes"]
write_csv("local-councils.csv", d["local_councils"], lc_cols)
rep_cols = ["tier","body","area","places","name","party","profile_url","email","phone","stance","verification"]
write_csv("representatives.csv", d["representatives"], rep_cols)
ap_cols = ["id","roads","localities","purpose","status","peak_hgv_per_hr","peak_lgv_per_hr","figure_confidence"]
write_csv("access-points.csv", d["access_points"], ap_cols)
ns_cols = ["name","level","url","feed","status","notes"]
write_csv("national-and-other-sources.csv", d["national_and_other_sources"], ns_cols)

e = html.escape
def link(u):
    if u.startswith("http"):
        return f'<a href="{e(u)}" target="_blank" rel="noopener">{e(u)}</a>'
    return e(u)
def badge(v):
    cls = "v" if v.startswith("verified") else ("p" if v.startswith("partly") else "u")
    return f'<span class="b {cls}">{e(v)}</span>'

def table(rows, cols, labels, linkcols=(), vcol=None):
    h = "<div class='tw'><table><thead><tr>" + "".join(f"<th>{e(l)}</th>" for l in labels) + "</tr></thead><tbody>"
    for r in rows:
        h += "<tr>"
        for c in cols:
            v = r.get(c, "")
            if c == "feeds":
                cell = "<br>".join(f"{link(x['url'])} <small>{e(x['status'])}</small>" for x in v) or "None"
            elif c == vcol:
                cell = badge(v)
            elif c in linkcols:
                cell = link(v)
            else:
                cell = e(v)
            h += f"<td>{cell}</td>"
        h += "</tr>"
    return h + "</tbody></table></div>"

m = d["meta"]; lgr = d["local_government_reorganisation"]
pc = []
for c in d["principal_councils"]:
    pc.append({"name": c["name"], "moderngov": c["moderngov"], "rss": f"{c['rss']['url']} ({c['rss']['status']})",
               "webservice": c["webservice"]["status"], "news": f"{c['news_feed']['url']} ({c['news_feed']['status']})",
               "committees": c["committees"], "public_speaking": c["public_speaking"]})

page = f"""<!DOCTYPE html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>White Horse Reservoir: verified data sources</title>
<style>
:root{{--bg:#fbfaf7;--fg:#1d1d1b;--mut:#5f5e5a;--line:#e3e0d8;--acc:#1f5e7a;--g:#2e7d4f;--a:#a86b12;--r:#a8322d}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161615;--fg:#ecebe6;--mut:#a3a19a;--line:#33322f;--acc:#7cc0de;--g:#6fcf97;--a:#e0a84a;--r:#ef7f78}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:1200px;margin:0 auto;padding:24px 16px 64px}}
h1{{font-size:1.6rem;margin:0 0 4px}} h2{{font-size:1.15rem;margin:36px 0 8px;border-bottom:1px solid var(--line);padding-bottom:4px}}
p.m{{color:var(--mut);margin:0 0 12px}} a{{color:var(--acc);word-break:break-all}}
nav a{{margin-right:14px;word-break:normal}}
.tw{{overflow-x:auto;border:1px solid var(--line);border-radius:6px}}
table{{border-collapse:collapse;width:100%;font-size:13px}} th,td{{text-align:left;vertical-align:top;padding:6px 8px;border-bottom:1px solid var(--line)}}
th{{position:sticky;top:0;background:var(--bg);font-weight:600}} td{{min-width:90px}}
.b{{display:inline-block;padding:1px 6px;border-radius:10px;font-size:12px;border:1px solid currentColor;white-space:nowrap}}
.v{{color:var(--g)}} .p{{color:var(--a)}} .u{{color:var(--r)}}
input{{width:100%;max-width:420px;padding:8px;border:1px solid var(--line);border-radius:6px;background:transparent;color:var(--fg);margin:8px 0}}
small{{color:var(--mut)}} ul{{padding-left:20px}}
</style></head><body><main>
<h1>White Horse Reservoir: verified data sources</h1>
<p class="m">Checked {e(m['checked_on'])}. Planning Inspectorate reference {e(m['pins_reference'])}. {e(m['stage'])}</p>
<p class="m">{badge('verified')} fetched and confirmed &nbsp; {badge('partly verified')} some fields confirmed &nbsp; {badge('unverified')} needs a manual check</p>
<nav><a href="#lc">Parish and town councils</a><a href="#rep">Representatives</a><a href="#pc">Principal councils</a><a href="#ns">National and other</a><a href="#ap">Access points</a><a href="#lgr">Reorganisation</a><a href="#todo">Still to check</a></nav>
<input id="q" placeholder="Filter all tables (e.g. Hanney, Marcham, A338)">
<h2 id="lc">Parish and town councils</h2>
{table(d['local_councils'], lc_cols, ['Council','Type','Access points','How affected','Website','Meetings','Pattern','Latest minutes','Format','Platform','Feeds','Reservoir mention','Contact','Facebook','Status','Notes'], ('website','meetings_url','facebook','reservoir_mention'), 'verification')}
<h2 id="rep">Representatives</h2>
{table(d['representatives'], rep_cols, ['Tier','Body','Ward / division / seat','Places','Name','Party','Profile','Email','Phone','Stance','Status'], ('profile_url',), 'verification')}
<h2 id="pc">Principal councils</h2>
{table(pc, ['name','moderngov','rss','webservice','news','committees','public_speaking'], ['Council','ModernGov','RSS','Web service','News feed','Committee IDs','Public speaking'], ('moderngov',))}
<h2 id="ns">National, promoter, campaign and media sources</h2>
{table(d['national_and_other_sources'], ns_cols, ['Source','Level','URL','Feed','Status','Notes'], ('url',))}
<h2 id="ap">Construction access points (Sept 2026)</h2>
<p class="m">{e(d['access_points_notes'])}</p>
{table(d['access_points'], ap_cols, ['ID','Roads','Localities','Purpose','Status','Peak HGV/hr','Peak LGV/hr','Figure confidence'])}
<p class="m">Sources: {' , '.join(link(u) for u in d['access_points_sources'])}</p>
<h2 id="lgr">Local government reorganisation</h2>
<ul>{''.join(f'<li><b>{e(k.replace("_"," ").capitalize())}:</b> {e(v)}</li>' for k,v in lgr.items() if k!='sources')}</ul>
<p class="m">Sources: {' , '.join(link(u) for u in lgr['sources'])}</p>
<h2 id="todo">Still to check by hand</h2>
<ul>{''.join(f'<li>{e(x)}</li>' for x in d['still_to_check_by_hand'])}</ul>
</main>
<script>
document.getElementById('q').addEventListener('input',function(){{var q=this.value.toLowerCase();document.querySelectorAll('tbody tr').forEach(function(r){{r.style.display=r.textContent.toLowerCase().indexOf(q)>-1?'':'none';}});}});
</script></body></html>"""
assert "—" not in page
open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(page)
print("ok", len(d["local_councils"]), len(d["representatives"]), len(d["access_points"]), len(d["national_and_other_sources"]))
