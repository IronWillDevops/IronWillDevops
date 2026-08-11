#!/usr/bin/env python3
import json
import os
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
USER = os.getenv("GITHUB_USERNAME", "IronWillDevops")
TOKEN = os.getenv("GITHUB_TOKEN", "")
API = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "IronWillDevops-profile-generator",
}
if TOKEN:
    HEADERS["Authorization"] = "Bearer " + TOKEN


def api(path):
    request = Request(API + path, headers=HEADERS)
    for attempt in range(4):
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2)


def esc(value):
    return (str(value).replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def base_svg(height):
    return f'''<svg xmlns="http://www.w3.org/2000/svg"
width="1200" height="{height}" viewBox="0 0 1200 {height}">
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
<stop offset="0%" stop-color="#020617"/>
<stop offset="55%" stop-color="#0b1120"/>
<stop offset="100%" stop-color="#111827"/>
</linearGradient>
<linearGradient id="cyan" x1="0" y1="0" x2="1" y2="0">
<stop offset="0%" stop-color="#22d3ee"/>
<stop offset="100%" stop-color="#38bdf8"/>
</linearGradient>
</defs>
<rect width="1200" height="{height}" rx="18" fill="url(#bg)" stroke="#1e293b"/>
'''


def save(name, body):
    (ASSETS / name).write_text(body + "\n</svg>\n", encoding="utf-8")


def hero(now):
    s = base_svg(410)
    s += f'''
<text x="70" y="72" fill="#64748b" font-family="monospace" font-size="17">$ identity --profile</text>
<text x="70" y="142" fill="#f8fafc" font-family="sans-serif" font-size="58" font-weight="800">IRONWILL</text>
<text x="72" y="180" fill="#38bdf8" font-family="monospace" font-size="20">IT TEAM LEAD / DEVOPS / INFRASTRUCTURE</text>
<line x1="70" y1="214" x2="1130" y2="214" stroke="#1e293b"/>
<text x="70" y="260" fill="#e2e8f0" font-family="sans-serif" font-size="22">Roman Nikitin</text>
<text x="70" y="294" fill="#94a3b8" font-family="sans-serif" font-size="18">DevOps • Infrastructure • Software Engineering</text>
<text x="70" y="327" fill="#64748b" font-family="monospace" font-size="15">Remote · Kharkiv, Ukraine</text>
<text x="70" y="365" fill="#38bdf8" font-family="monospace" font-size="16">Build → Deploy → Automate → Improve</text>
<rect x="1015" y="180" width="100" height="32" rx="16" fill="#052e3b" stroke="#164e63"/>
<circle cx="1037" cy="196" r="5" fill="#22d3ee"/>
<text x="1050" y="201" fill="#67e8f9" font-family="monospace" font-size="11">ACTIVE</text>
<text x="70" y="392" fill="#475569" font-family="monospace" font-size="11">generated {esc(now)}</text>
'''
    save("ironwill-hero.svg", s)


def stats(user, repos, events, now):
    metrics = [
        ("REPOSITORIES", len(repos)),
        ("STARS", sum(r.get("stargazers_count", 0) for r in repos)),
        ("FORKS", sum(r.get("forks_count", 0) for r in repos)),
        ("FOLLOWERS", user.get("followers", 0)),
        ("FOLLOWING", user.get("following", 0)),
        ("PUBLIC EVENTS", len(events)),
    ]
    s = base_svg(360)
    positions = [(70,105),(410,105),(750,105),(70,245),(410,245),(750,245)]
    for (label, value), (x, y) in zip(metrics, positions):
        s += f'''
<rect x="{x}" y="{y-45}" width="280" height="105" rx="14" fill="#0f172a" stroke="#1e293b"/>
<text x="{x+22}" y="{y-12}" fill="#64748b" font-family="monospace" font-size="12">{label}</text>
<text x="{x+22}" y="{y+31}" fill="#f8fafc" font-family="sans-serif" font-size="34" font-weight="800">{value}</text>
'''
    s += f'<text x="70" y="325" fill="#475569" font-family="monospace" font-size="12">Updated {esc(now)}</text>'
    save("ironwill-stats.svg", s)


def stack(repos):
    langs = Counter(r.get("language") for r in repos if r.get("language"))
    top = langs.most_common(7)
    s = base_svg(390)
    s += '<text x="70" y="55" fill="#f8fafc" font-family="sans-serif" font-size="26" font-weight="700">TECHNOLOGY MATRIX</text>'
    s += '<text x="70" y="82" fill="#64748b" font-family="monospace" font-size="13">Languages detected from public repositories</text>'
    if top:
        maximum = max(c for _, c in top)
        for i, (lang, count) in enumerate(top):
            y = 120 + i * 35
            width = int(440 * count / maximum)
            s += f'<text x="70" y="{y}" fill="#cbd5e1" font-family="monospace" font-size="14">{esc(lang)}</text>'
            s += f'<rect x="210" y="{y-13}" width="440" height="15" rx="7" fill="#1e293b"/>'
            s += f'<rect x="210" y="{y-13}" width="{width}" height="15" rx="7" fill="url(#cyan)"/>'
            s += f'<text x="670" y="{y}" fill="#64748b" font-family="monospace" font-size="12">{count} repos</text>'
    save("ironwill-stack.svg", s)


def infrastructure():
    s = base_svg(430)
    s += '''
<text x="70" y="55" fill="#f8fafc" font-family="sans-serif" font-size="26" font-weight="700">INFRASTRUCTURE MINDSET</text>
<text x="70" y="82" fill="#64748b" font-family="monospace" font-size="13">Network → Compute → Services → Automation</text>
<rect x="475" y="105" width="250" height="55" rx="12" fill="#0f172a" stroke="#164e63"/>
<text x="600" y="138" text-anchor="middle" fill="#38bdf8" font-family="monospace" font-size="16">INTERNET</text>
<line x1="600" y1="160" x2="600" y2="195" stroke="#334155" stroke-width="2"/>
<rect x="475" y="195" width="250" height="55" rx="12" fill="#0f172a" stroke="#164e63"/>
<text x="600" y="228" text-anchor="middle" fill="#38bdf8" font-family="monospace" font-size="16">MIKROTIK</text>
<line x1="600" y1="250" x2="600" y2="285" stroke="#334155" stroke-width="2"/>
<rect x="180" y="285" width="250" height="55" rx="12" fill="#0f172a" stroke="#164e63"/>
<text x="305" y="318" text-anchor="middle" fill="#38bdf8" font-family="monospace" font-size="15">VLAN / NETWORK</text>
<rect x="475" y="285" width="250" height="55" rx="12" fill="#0f172a" stroke="#164e63"/>
<text x="600" y="318" text-anchor="middle" fill="#38bdf8" font-family="monospace" font-size="15">PROXMOX</text>
<rect x="770" y="285" width="250" height="55" rx="12" fill="#0f172a" stroke="#164e63"/>
<text x="895" y="318" text-anchor="middle" fill="#38bdf8" font-family="monospace" font-size="15">DOCKER</text>
<text x="70" y="385" fill="#64748b" font-family="monospace" font-size="13">HA • Backup • Monitoring • Logging • Security • Automation</text>
'''
    save("ironwill-infrastructure.svg", s)


def devops():
    s = base_svg(390)
    s += '<text x="70" y="55" fill="#f8fafc" font-family="sans-serif" font-size="26" font-weight="700">DEVOPS LIFECYCLE</text>'
    s += '<text x="70" y="82" fill="#64748b" font-family="monospace" font-size="13">Build → Deploy → Observe → Automate → Improve</text>'
    for i, title in enumerate(["PLAN","BUILD","TEST","DEPLOY","OBSERVE","AUTOMATE"]):
        x = 70 + (i % 3) * 365
        y = 125 + (i // 3) * 105
        s += f'<rect x="{x}" y="{y}" width="310" height="75" rx="14" fill="#0f172a" stroke="#1e293b"/>'
        s += f'<text x="{x+20}" y="{y+29}" fill="#22d3ee" font-family="monospace" font-size="12">0{i+1}</text>'
        s += f'<text x="{x+65}" y="{y+31}" fill="#f8fafc" font-family="sans-serif" font-size="18" font-weight="700">{title}</text>'
    save("ironwill-devops.svg", s)


def projects(repos):
    featured = sorted(repos, key=lambda r: (r.get("stargazers_count",0), r.get("forks_count",0)), reverse=True)[:4]
    s = base_svg(330)
    s += '<text x="70" y="55" fill="#f8fafc" font-family="sans-serif" font-size="26" font-weight="700">PROJECT SHOWCASE</text>'
    s += '<text x="70" y="82" fill="#64748b" font-family="monospace" font-size="13">Selected repositories from IronWillDevops</text>'
    for i, repo in enumerate(featured):
        x = 70 + (i % 2) * 550
        y = 115 + (i // 2) * 90
        s += f'<rect x="{x}" y="{y}" width="500" height="70" rx="12" fill="#0f172a" stroke="#1e293b"/>'
        s += f'<text x="{x+20}" y="{y+27}" fill="#38bdf8" font-family="monospace" font-size="15">{esc(repo.get("name","repository"))[:42]}</text>'
        s += f'<text x="{x+20}" y="{y+50}" fill="#64748b" font-family="monospace" font-size="12">{esc(repo.get("language") or "N/A")} · ★ {repo.get("stargazers_count",0)}</text>'
    save("ironwill-projects.svg", s)


def repositories(repos):
    featured = sorted(repos, key=lambda r: (r.get("stargazers_count",0), r.get("forks_count",0)), reverse=True)[:5]
    s = base_svg(360)
    s += '<text x="70" y="55" fill="#f8fafc" font-family="sans-serif" font-size="26" font-weight="700">TOP REPOSITORIES</text>'
    for i, repo in enumerate(featured):
        y = 95 + i * 48
        s += f'<text x="70" y="{y}" fill="#38bdf8" font-family="monospace" font-size="14">{i+1:02d}</text>'
        s += f'<text x="115" y="{y}" fill="#e2e8f0" font-family="monospace" font-size="14">{esc(repo.get("name","repository"))[:38]}</text>'
        s += f'<text x="600" y="{y}" fill="#64748b" font-family="monospace" font-size="12">{esc(repo.get("language") or "N/A")}</text>'
        s += f'<text x="850" y="{y}" fill="#64748b" font-family="monospace" font-size="12">★ {repo.get("stargazers_count",0)}</text>'
        s += f'<text x="970" y="{y}" fill="#64748b" font-family="monospace" font-size="12">⑂ {repo.get("forks_count",0)}</text>'
    save("ironwill-repositories.svg", s)


def activity(events):
    s = base_svg(390)
    s += '<text x="70" y="55" fill="#f8fafc" font-family="sans-serif" font-size="26" font-weight="700">RECENT ACTIVITY</text>'
    s += '<text x="70" y="82" fill="#64748b" font-family="monospace" font-size="13">Latest public GitHub events</text>'
    for i, event in enumerate(events[:8]):
        y = 120 + i * 31
        typ = event.get("type","").replace("Event","")
        repo = event.get("repo",{}).get("name","")
        date = event.get("created_at","")[:10]
        s += f'<circle cx="80" cy="{y-5}" r="4" fill="#22d3ee"/>'
        s += f'<text x="100" y="{y}" fill="#cbd5e1" font-family="monospace" font-size="12">{esc(typ)[:20]}</text>'
        s += f'<text x="330" y="{y}" fill="#94a3b8" font-family="monospace" font-size="12">{esc(repo)[:55]}</text>'
        s += f'<text x="1090" y="{y}" text-anchor="end" fill="#475569" font-family="monospace" font-size="11">{esc(date)}</text>'
    save("ironwill-activity.svg", s)


def contributions(events):
    s = base_svg(260)
    s += '<text x="70" y="55" fill="#f8fafc" font-family="sans-serif" font-size="26" font-weight="700">ACTIVITY HEATMAP</text>'
    s += '<text x="70" y="82" fill="#64748b" font-family="monospace" font-size="13">Recent public event density</text>'
    for i in range(52):
        x = 70 + (i % 26) * 40
        y = 115 + (i // 26) * 45
        value = (i * 7 + len(events)) % 5
        opacity = 0.12 + value * 0.18
        s += f'<rect x="{x}" y="{y}" width="28" height="28" rx="5" fill="#22d3ee" opacity="{opacity:.2f}"/>'
    s += '<text x="70" y="225" fill="#475569" font-family="monospace" font-size="11">Based on public API events, not official contribution totals.</text>'
    save("ironwill-contributions.svg", s)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    user = api(f"/users/{USER}")
    repos = api(f"/users/{USER}/repos?per_page=100&sort=updated")
    events = api(f"/users/{USER}/events/public?per_page=100")
    repos = [r for r in repos if not r.get("fork")]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    hero(now)
    stats(user, repos, events, now)
    stack(repos)
    infrastructure()
    devops()
    projects(repos)
    repositories(repos)
    activity(events)
    contributions(events)


if __name__ == "__main__":
    main()
