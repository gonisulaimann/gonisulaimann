"""Regenerate the living pulse strip: last 30 days of contributions,
rendered in the banner's signal-bars language. Dark + light variants.
Runs daily via .github/workflows/pulse.yml. Needs GITHUB_TOKEN."""

import json
import os
import urllib.request
from datetime import date

USER = "gonisulaimann"
DAYS = 30
W, H = 1200, 116
TOP, BASE, MAXH = 44, 104, 60
LEFT, RIGHT = 8, 1192

QUERY = """
query($login:String!){
  user(login:$login){
    contributionsCollection{
      contributionCalendar{
        weeks{ contributionDays{ date contributionCount } }
      }
    }
  }
}
"""

PALETTES = {
    "pulse.svg": {
        "text": "#8b949e", "green": "#3fb950", "track": "#21262d",
    },
    "pulse-light.svg": {
        "text": "#57606a", "green": "#1a7f37", "track": "#ebedf0",
    },
}

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,Liberation Mono,monospace"


def fetch_days(token):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "pulse",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        payload = json.load(res)
    days = [
        d
        for w in payload["data"]["user"]["contributionsCollection"][
            "contributionCalendar"
        ]["weeks"]
        for d in w["contributionDays"]
        if d["date"] <= date.today().isoformat()
    ]
    return days[-DAYS:]


def render(days, pal, filename):
    counts = [d["contributionCount"] for d in days]
    peak = max(counts) if max(counts) > 0 else 1
    step = (RIGHT - LEFT) / len(days)
    bw = min(26.0, step * 0.66)
    bars = []
    for i, c in enumerate(counts):
        x = LEFT + i * step + (step - bw) / 2
        if c == 0:
            bars.append(
                f'<rect x="{x:.1f}" y="{BASE - 6}" width="{bw:.1f}"'
                f' height="6" fill="{pal["track"]}"/>'
            )
        else:
            h = 6 + (MAXH - 6) * (c / peak)
            op = 0.25 + 0.75 * (c / peak)
            bars.append(
                f'<rect x="{x:.1f}" y="{BASE - h:.1f}" width="{bw:.1f}"'
                f' height="{h:.1f}" fill="{pal["green"]}"'
                f' opacity="{op:.2f}"><title>{days[i]["date"]}:'
                f" {c} contributions</title></rect>"
            )
    total = sum(counts)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Contribution pulse: {total} contributions in the last {DAYS} days">
  <text x="{LEFT}" y="26" font-family="{MONO}" font-size="20" fill="{pal["text"]}">pulse <tspan fill="{pal["green"]}">·</tspan> last {DAYS} days</text>
  <text x="{RIGHT}" y="26" text-anchor="end" font-family="{MONO}" font-size="20" fill="{pal["text"]}">{total} contributions</text>
  {''.join(bars)}
</svg>
"""
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", filename)
    with open(out, "w") as f:
        f.write(svg)
    print(f"wrote {out} ({total} contributions)")


if __name__ == "__main__":
    token = os.environ["GITHUB_TOKEN"]
    days = fetch_days(token)
    for filename, pal in PALETTES.items():
        render(days, pal, filename)
