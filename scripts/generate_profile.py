#!/usr/bin/env python3
import os, time, json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
USER = os.getenv("GITHUB_USERNAME", "IronWillDevops")
TOKEN = os.getenv("GITHUB_TOKEN", "")
API = "https://api.github.com"
HEADERS = {"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2026-03-10","User-Agent":"IronWillDevops-profile-generator"}
if TOKEN:
    HEADERS["Authorization"] = "Bearer " + TOKEN

def api(path):
    req = Request(API + path, headers=HEADERS)
    for attempt in range(4):
        try:
            with urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode())
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2)

def esc(v):
    return str(v).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def svg(height):
    return '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="%s" viewBox="0 0 1200 %s"><defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%%" stop-color="#020617"/><stop offset="55%%" stop-color="#0b1120"/><stop offset="100%%" stop-color="#111827"/></linearGradient><linearGradient id="cyan" x1="0" y1="0" x2="1" y2="0"><stop offset="0%%" stop-color="#22d3ee"/><stop offset="100%%" stop-color="#38bdf8"/></linearGradient></defs><rect width="1200" height="%s" rx="18" fill="url(#bg)" stroke="#1e293b"/>' % (height,height,height)

def save(name, body):
    (ASSETS/name).write_text(body + "</svg>\n", encoding="utf-8")

def main():
    ASSETS.mkdir(exist_ok=True)
    user = api("/users/" + USER)
    repos = [r for r in api("/users/" + USER + "/repos?per_page=100&sort=updated") if not r.get("fork")]
    events = api("/users/" + USER + "/events/public?per_page=30")
    stars = sum(r.get("stargazers_count",0) for r in repos)
    forks = sum(r.get("forks_count",0) for r in repos)
    langs = Counter(r.get("language") for r in repos if r.get("language"))
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    s = svg(390)
    s += '<text x="70" y="85" fill="#64748b" font-family="monospace" font-size="18">$ identity --profile</text>'
    s += '<text x="70" y="145" fill="#f8fafc" font-family="sans-serif" font-size="54" font-weight="800">IRONWILL</text>'
    s += '<text x="72" y="182" fill="#38bdf8" font-family="monospace" font-size="20">DEVOPS / INFRASTRUCTURE / SOFTWARE</text>'
    s += '<line x1="70" y1="215" x2="1130" y2="215" stroke="#1e293b"/>'
    s += '<text x="70" y="260" fill="#cbd5e1" font-family="sans-serif" font-size="20">Build systems. Automate operations. Keep learning.</text>'
    s += '<text x="70" y="300" fill="#64748b" font-family="monospace" font-size="15">Linux / Docker / Proxmox / MikroTik / Laravel / Automation</text>'
    s += '<circle cx="1050" cy="115" r="14" fill="#22d3ee"/><text x="1080" y="121" fill="#22d3ee" font-family="monospace" font-size="15">ONLINE</text>'
    s += '<text x="70" y="350" fill="#475569" font-family="monospace" font-size="13">generated '+esc(now)+'</text>'
    save("ironwill-hero.svg",s)

    metrics=[("REPOSITORIES",len(repos)),("STARS",stars),("FORKS",forks),("FOLLOWERS",user.get("followers",0)),("FOLLOWING",user.get("following",0)),("PUBLIC EVENTS",len(events))]
    s=svg(360)
    for (label,value),(x,y) in zip(metrics,[(70,105),(410,105),(750,105),(70,245),(410,245),(750,245)]):
        s += f'<rect x="{x}" y="{y-45}" width="280" height="105" rx="14" fill="#0f172a" stroke="#1e293b"/><text x="{x+22}" y="{y-12}" fill="#64748b" font-family="monospace" font-size="13">{label}</text><text x="{x+22}" y="{y+31}" fill="#f8fafc" font-family="sans-serif" font-size="34" font-weight="800">{value}</text>'
    s += '<text x="70" y="325" fill="#475569" font-family="monospace" font-size="12">Updated '+esc(now)+'</text>'
    save("ironwill-stats.svg",s)

    s=svg(360)
    s += '<text x="70" y="55" fill="#f8fafc" font-family="sans-serif" font-size="26" font-weight="700">TECHNOLOGY MATRIX</text><text x="70" y="82" fill="#64748b" font-family="monospace" font-size="13">Detected from public repositories</text>'
    top=langs.most_common(6)
    if top:
        maximum=max(c for _,c in top)
        for i,(lang,count) in enumerate(top):
            y=125+i*36
            bar=int(430*count/maximum)
            s += f'<text x="70" y="{y}" fill="#cbd5e1" font-family="monospace" font-size="15">{esc(lang)}</text><rect x="210" y="{y-14}" width="430" height="16" rx="8" fill="#1e293b"/><rect x="210" y="{y-14}" width="{bar}" height="16" rx="8" fill="url(#cyan)"/><text x="665" y="{y}" fill="#64748b" font-family="monospace" font-size="13">{count} repos</text>'
    for i,item in enumerate(["Linux","Docker","Proxmox","MikroTik","Laravel","GitHub Actions"]):
        x=800+(i%2)*170; y=120+(i//2)*58
        s += f'<rect x="{x}" y="{y}" width="150" height="34" rx="17" fill="#0f172a" stroke="#164e63"/><text x="{x+75}" y="{y+22}" text-anchor="middle" fill="#38bdf8" font-family="monospace" font-size="12">{item}</text>'
    save("ironwill-stack.svg",s)

    s=svg(360)
    s += '<text x="70" y="55" fill="#f8fafc" font-family="sans-serif" font-size="26" font-weight="700">RECENT GITHUB ACTIVITY</text><text x="70" y="82" fill="#64748b" font-family="monospace" font-size="13">Latest public events</text>'
    for i,e in enumerate(events[:7]):
        y=120+i*32; typ=e.get("type","").replace("Event",""); repo=e.get("repo",{}).get("name",""); date=e.get("created_at","")[:10]
        s += f'<circle cx="80" cy="{y-5}" r="5" fill="#22d3ee"/><text x="100" y="{y}" fill="#cbd5e1" font-family="monospace" font-size="13">{esc(typ)[:22]}</text><text x="350" y="{y}" fill="#94a3b8" font-family="monospace" font-size="13">{esc(repo)[:58]}</text><text x="1080" y="{y}" text-anchor="end" fill="#475569" font-family="monospace" font-size="12">{esc(date)}</text>'
    save("ironwill-activity.svg",s)

if __name__ == "__main__":
    main()
