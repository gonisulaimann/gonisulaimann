#!/usr/bin/env python3
"""
Upstream Maintenance Log & Changelog Generator
Author: Goni Sulaiman (@gonisulaimann)

Automatically queries GitHub for all authored PRs and commits
across all public repositories and formats a clean engineering maintenance log.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

# Curated technical context for landmark contributions to preserve deep engineering notes
LANDMARK_CONTEXT = {
    ("diegosouzapw/OmniRoute", 14285): {
        "subsystem": "Storage & Database",
        "notes": "Pruned 731k+ unpruned telemetry rows in `compression_engine_breakdown` (#14268). Wired table into retention cleanup (30d default) and `RESET_TARGETS`."
    },
    ("diegosouzapw/OmniRoute", 14281): {
        "subsystem": "Transports & Protocols",
        "notes": "Wired Codex App-Server WebSocket transport dispatch and normalized reasoning model aliases (`-low`, `-medium`, `-high`) into turn effort parameters (#14277)."
    },
    ("diegosouzapw/OmniRoute", 14275): {
        "subsystem": "LiveWS / Real-Time",
        "notes": "Allowed anonymous dashboard LiveWS connections when `requireLogin=false` (#14256), resolving local dev disconnections."
    },
    ("diegosouzapw/OmniRoute", 14274): {
        "subsystem": "Storage / Boot",
        "notes": "Silenced false-alarm boot warnings for legacy Bifrost slot index renumbering (#14262)."
    },
    ("diegosouzapw/OmniRoute", 14271): {
        "subsystem": "Routing / Engine",
        "notes": "Recursively expanded combo-ref targets when computing capabilities (#14232) to prevent capability masking in composite pipelines."
    },
    ("diegosouzapw/OmniRoute", 14185): {
        "subsystem": "Ingress / Protocols",
        "notes": "Corrected ingress body classifier for non-standard `/v1beta` routes to OpenAI format."
    },
    ("diegosouzapw/OmniRoute", 14184): {
        "subsystem": "Networking",
        "notes": "Probe HTTP proxies on default port 80 when port is omitted in connection string."
    },
    ("diegosouzapw/OmniRoute", 14155): {
        "subsystem": "CI / Tooling",
        "notes": "Fixed env/doc synchronization gates on checkouts whose paths need URL encoding."
    },
    ("diegosouzapw/OmniRoute", 14153): {
        "subsystem": "Streaming / Translator",
        "notes": "Prevented post-close trailing text chunks from corrupting completed Responses message items."
    },
    ("diegosouzapw/OmniRoute", 13741): {
        "subsystem": "Security / Policy",
        "notes": "Fixed critical authorization bypass on URL rewrite aliases (#13685) via canonical path normalization in `validateEndpointAccess`."
    },
    ("diegosouzapw/OmniRoute", 12735): {
        "subsystem": "Streaming / Egress",
        "notes": "Stripped internal proxy routing markers (`_omniroute*`) from outgoing request bodies (#12729), preventing upstream 400 Bad Request on strict providers (NVIDIA NIM, Groq)."
    },
    ("diegosouzapw/OmniRoute", 12736): {
        "subsystem": "Frontend / Settings",
        "notes": "Exposed Modal Base URL field in provider connection modal (#12704)."
    },
    ("diegosouzapw/OmniRoute", 12371): {
        "subsystem": "Model Registry",
        "notes": "Restricted reasoning effort parameters to Kimi K3 base models only."
    },
    ("diegosouzapw/OmniRoute", 12369): {
        "subsystem": "Localization",
        "notes": "Escaped placeholder variables in ICU single quotes across all 43 locales to prevent onboarding crashes."
    },
    ("diegosouzapw/OmniRoute", 12368): {
        "subsystem": "CLI Runtime",
        "notes": "Removed duplicate positional parameter in tunnel create CLI command."
    },
    ("Filecraft/Filecraft", 7): {
        "subsystem": "System Test Harness",
        "notes": "Gated macOS GUI harness on proven synthetic event delivery (virtual F13 probe) to eliminate post-reboot CI flakes."
    },
    ("Filecraft/Filecraft", 6): {
        "subsystem": "Distribution",
        "notes": "Release packaging and distribution pipeline hardening for macOS consumer binaries."
    },
    ("Filecraft/Filecraft", 8): {
        "subsystem": "Distribution",
        "notes": "Consumer distribution updates and release verification."
    },
    ("gonisulaimann/Grounded", 2): {
        "subsystem": "Test Harness",
        "notes": "Bootstrap sys.path in test runner for zero-install discovery across environments."
    },
    ("gonisulaimann/Grounded", 3): {
        "subsystem": "Typing / Packaging",
        "notes": "Package PEP 561 `py.typed` marker for static type checker compliance across consumers."
    },
    ("Centre-For-Energy/ceii-platform", 1): {
        "subsystem": "Architecture",
        "notes": "Established foundational application shell, design system component primitives, and modular routing."
    },
    ("Centre-For-Energy/ceii-platform", 2): {
        "subsystem": "Frontend",
        "notes": "Engineered institutional homepage with responsive accessibility primitives."
    },
    ("Centre-For-Energy/ceii-platform", 3): {
        "subsystem": "Frontend",
        "notes": "Established institutional About page and shared layout framework."
    },
    ("Centre-For-Energy/ceii-platform", 4): {
        "subsystem": "Governance",
        "notes": "Built institutional governance portal and policy navigation layout."
    },
    ("Centre-For-Energy/ceii-platform", 5): {
        "subsystem": "Programs",
        "notes": "Engineered institutional research programs page."
    }
}


def run_cmd(cmd):
    """Run a shell command and return stdout."""
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Warning: command failed: {' '.join(cmd)}\n{res.stderr}", file=sys.stderr)
        return ""
    return res.stdout


def fetch_prs():
    """Fetch all PRs authored by gonisulaimann across all repos."""
    print("Fetching PRs authored by @gonisulaimann...")
    out = run_cmd([
        "gh", "search", "prs",
        "--author", "gonisulaimann",
        "--limit", "100",
        "--json", "repository,number,title,state,url,createdAt,closedAt"
    ])
    if not out:
        return []
    try:
        return json.loads(out)
    except Exception as e:
        print(f"Error parsing PR JSON: {e}", file=sys.stderr)
        return []


def fetch_commits():
    """Fetch recent commits authored by gonisulaimann."""
    print("Fetching recent commits...")
    out = run_cmd([
        "gh", "search", "commits",
        "--author", "gonisulaimann",
        "--sort", "committer-date",
        "--limit", "60",
        "--json", "repository,sha,commit,url"
    ])
    if not out:
        return []
    try:
        return json.loads(out)
    except Exception as e:
        print(f"Error parsing commits JSON: {e}", file=sys.stderr)
        return []


def format_date(iso_str):
    """Format ISO timestamp to readable date."""
    if not iso_str or iso_str.startswith("0001"):
        return "-"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return iso_str[:10]


def main():
    prs = fetch_prs()
    raw_commits = fetch_commits()

    # Partition PRs
    merged_prs = []
    open_prs = []
    closed_prs = []
    repos_touched = set()

    for p in prs:
        repo_name = p["repository"]["nameWithOwner"]
        repos_touched.add(repo_name)
        s = p["state"].lower()
        if s == "merged":
            merged_prs.append(p)
        elif s == "open":
            open_prs.append(p)
        else:
            closed_prs.append(p)

    # Sort merged PRs by closed date descending
    merged_prs.sort(key=lambda x: x.get("closedAt") or "", reverse=True)
    # Sort open PRs by created date descending
    open_prs.sort(key=lambda x: x.get("createdAt") or "", reverse=True)

    # Process commits
    recent_commits = []
    seen_msgs = set()
    for c in raw_commits:
        repo_info = c.get("repository", {})
        repo_name = repo_info.get("fullName", "")
        if "omniroute" in repo_name.lower():
            repo_name = "diegosouzapw/OmniRoute"
        
        repos_touched.add(repo_name)
        msg = c.get("commit", {}).get("message", "").split("\n")[0]
        if msg.startswith("Merge branch") or msg in seen_msgs:
            continue
        seen_msgs.add(msg)

        date_val = c.get("commit", {}).get("author", {}).get("date", "")
        sha_val = c.get("sha", "")
        recent_commits.append({
            "sha": sha_val[:7],
            "full_sha": sha_val,
            "message": msg,
            "repo": repo_name,
            "date": format_date(date_val),
            "url": f"https://github.com/{repo_name}/commit/{sha_val}"
        })

    # Limit commits to top 25
    recent_commits = recent_commits[:25]

    total_prs = len(prs)
    merged_count = len(merged_prs)
    open_count = len(open_prs)
    repo_count = len(repos_touched)

    print(f"Stats: Total PRs={total_prs}, Merged={merged_count}, Open={open_count}, Repos={repo_count}, Commits={len(recent_commits)}")

    lines = []
    lines.append("# Upstream Maintenance Log & Changelog\n")
    lines.append("> Running log of production pull requests, commits, and releases authored by [@gonisulaimann](https://github.com/gonisulaimann) across public repositories.\n")

    # Clean, reliable Shields Badges
    lines.append(f"[![Merged PRs](https://img.shields.io/badge/Merged%20PRs-{merged_count}-2ea44f?style=flat-square)](https://github.com/pulls?q=is%3Apr+author%3Agonisulaimann+is%3Amerged) ")
    lines.append(f"[![In-Flight PRs](https://img.shields.io/badge/In--Flight%20PRs-{open_count}-d29922?style=flat-square)](https://github.com/pulls?q=is%3Apr+author%3Agonisulaimann+is%3Aopen) ")
    lines.append(f"[![Active Repos](https://img.shields.io/badge/Repositories%20Maintained-{repo_count}-0969da?style=flat-square)](https://github.com/gonisulaimann)\n")

    lines.append("```")
    lines.append("Telemetry:")
    lines.append(f"├── Total Tracked Upstream PRs : {total_prs}")
    lines.append(f"├── Production Merged PRs      : {merged_count} ({(merged_count / max(1, total_prs) * 100):.1f}%)")
    lines.append(f"├── In-Flight / In Review      : {open_count}")
    lines.append(f"└── Public Repositories Active : {repo_count}")
    lines.append("```\n")

    lines.append("## In-Flight & Active Pull Requests (Queue & Review)\n")
    lines.append("Pull requests currently under review, undergoing checks, or queued in merge-trains.\n")
    lines.append("| Repository | PR | Status | Scope & Problem Description | Created |")
    lines.append("| :--- | :--- | :---: | :--- | :---: |")

    for p in open_prs:
        repo = p["repository"]["nameWithOwner"]
        num = p["number"]
        url = p["url"]
        title = p["title"].replace("|", "\\|")
        created = format_date(p.get("createdAt"))

        meta = LANDMARK_CONTEXT.get((repo, num))
        if meta:
            desc = f"**{meta['subsystem']}**: {meta['notes']}"
        else:
            desc = title

        status_badge = f"[![In Review](https://img.shields.io/badge/in--review-d29922?style=flat-square)]({url})"
        lines.append(f"| **[{repo}](https://github.com/{repo})** | **[#{num}]({url})** | {status_badge} | {desc} | `{created}` |")

    lines.append("\n---\n")
    lines.append("## Merged Production Pull Requests\n")
    lines.append("Production code merged into default branches across upstream codebases.\n")
    lines.append("| Repository | PR | Status | Description & Engineering Summary |")
    lines.append("| :--- | :--- | :---: | :--- |")

    for p in merged_prs:
        repo = p["repository"]["nameWithOwner"]
        num = p["number"]
        url = p["url"]
        title = p["title"].replace("|", "\\|")

        meta = LANDMARK_CONTEXT.get((repo, num))
        if meta:
            desc = f"**{meta['subsystem']}**: {meta['notes']}"
        else:
            desc = title

        status_badge = f"[![Merged](https://img.shields.io/badge/merged-8957e5?style=flat-square)]({url})"
        lines.append(f"| **[{repo}](https://github.com/{repo})** | **[#{num}]({url})** | {status_badge} | {desc} |")

    lines.append("\n---\n")
    lines.append("## Live Commit Stream\n")
    lines.append("Recent direct commits and contributions across canonical repositories.\n")
    lines.append("| Repository | Commit | Message | Date |")
    lines.append("| :--- | :---: | :--- | :---: |")

    for c in recent_commits:
        repo = c["repo"]
        sha = c["sha"]
        url = c["url"]
        msg = c["message"].replace("|", "\\|")
        date = c["date"]
        lines.append(f"| **[{repo}](https://github.com/{repo})** | [`{sha}`]({url}) | {msg} | `{date}` |")

    content = "\n".join(lines) + "\n"

    target_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "MAINTENANCE_LOG.md")
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully generated {target_path} ({len(content)} bytes)")

    alias_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "OPEN_SOURCE.md")
    with open(alias_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully mirrored to {alias_path}")


if __name__ == "__main__":
    main()
