#!/usr/bin/env python3
"""
Autonomous Maintenance Log & Live Engineering Changelog Generator
Author: Goni Sulaiman (@gonisulaimann)

Automatically queries GitHub for all authored PRs, commits, pushes, and releases
across all public repositories and formats a real-time engineering maintenance log.
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
        "notes": "Fixed 731k+ leaked telemetry rows in `compression_engine_breakdown` (#14268). Wired table into retention cleanup (30d default) and `RESET_TARGETS`."
    },
    ("diegosouzapw/OmniRoute", 14281): {
        "subsystem": "Transports & Protocols",
        "notes": "Wired Codex App-Server WebSocket transport dispatch and normalized reasoning model aliases (`-low`, `-medium`, `-high`) into turn effort parameters (#14277)."
    },
    ("diegosouzapw/OmniRoute", 14275): {
        "subsystem": "LiveWS / Real-Time",
        "notes": "Allowed anonymous dashboard LiveWS connections when `requireLogin=false` (#14256), fixing local disconnections."
    },
    ("diegosouzapw/OmniRoute", 14274): {
        "subsystem": "Storage / Boot",
        "notes": "Silenced false-alarm boot crashes for legacy Bifrost slot index renumbering (#14262)."
    },
    ("diegosouzapw/OmniRoute", 14271): {
        "subsystem": "Routing / Engine",
        "notes": "Recursively expanded combo-ref targets when computing capabilities (#14232) to prevent capability masking."
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
        # Map known fork mirrors to upstream if needed
        if "omniroute" in repo_name.lower():
            repo_name = "diegosouzapw/OmniRoute"
        
        repos_touched.add(repo_name)
        msg = c.get("commit", {}).get("message", "").split("\n")[0]
        # Ignore merge commits or automated noisy bumps
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

    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    total_prs = len(prs)
    merged_count = len(merged_prs)
    open_count = len(open_prs)
    repo_count = len(repos_touched)

    print(f"Stats: Total PRs={total_prs}, Merged={merged_count}, Open={open_count}, Repos={repo_count}, Commits={len(recent_commits)}")

    lines = []
    lines.append("# 🛠️ Upstream Maintenance Log & Live Engineering Changelog\n")
    lines.append("> **Autonomous Running Log**: Tracks all production pull requests, commits, and releases authored by [@gonisulaimann](https://github.com/gonisulaimann) across any public repository on GitHub. Automatically synced via GitHub Actions.\n")

    # Live Shields Badges
    lines.append(f"[![Merged PRs](https://img.shields.io/badge/Merged%20PRs-{merged_count}-success?style=for-the-badge&logo=git&logoColor=white)](https://github.com/pulls?q=is%3Apr+author%3Agonisulaimann+is%3Amerged) ")
    lines.append(f"[![In-Flight PRs](https://img.shields.io/badge/In--Flight%20PRs-{open_count}-orange?style=for-the-badge&logo=github&logoColor=white)](https://github.com/pulls?q=is%3Apr+author%3Agonisulaimann+is%3Aopen) ")
    lines.append(f"[![Active Repos](https://img.shields.io/badge/Repositories%20Maintained-{repo_count}-blue?style=for-the-badge&logo=open-source-initiative&logoColor=white)](https://github.com/gonisulaimann) ")
    lines.append(f"[![Last Auto-Sync](https://img.shields.io/badge/Last%20Auto--Sync-{now_str.replace(' ', '%20')}-informational?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/gonisulaimann/gonisulaimann/actions)\n")

    lines.append("```")
    lines.append(f"Telemetry Snapshot ({now_str}):")
    lines.append(f"├── Total Tracked Upstream PRs : {total_prs}")
    lines.append(f"├── Production Merged PRs      : {merged_count} ({(merged_count / max(1, total_prs) * 100):.1f}%)")
    lines.append(f"├── In-Flight / In Review      : {open_count}")
    lines.append(f"└── Public Repositories Active : {repo_count}")
    lines.append("```\n")

    lines.append("## 📊 Live Activity & Contribution Graphs\n")
    lines.append("[![Goni's Activity Graph](https://github-readme-activity-graph.vercel.app/graph?username=gonisulaimann&theme=github-compact)](https://github.com/gonisulaimann)\n")

    lines.append("---\n")
    lines.append("## 🟡 In-Flight & Active Pull Requests (Queue & Review)\n")
    lines.append("Pull requests currently under review, undergoing checks, or queued in merge-trains across upstream systems.\n")
    lines.append("| Repository | PR | Live Status | Scope & What I Found / Did | Created |")
    lines.append("| :--- | :--- | :---: | :--- | :---: |")

    for p in open_prs:
        repo = p["repository"]["nameWithOwner"]
        num = p["number"]
        url = p["url"]
        title = p["title"].replace("|", "\\|")
        created = format_date(p.get("createdAt"))

        # Look up landmark context if available
        meta = LANDMARK_CONTEXT.get((repo, num))
        if meta:
            desc = f"**{meta['subsystem']}**: {meta['notes']}"
        else:
            desc = title

        # Live shields.io badge that queries GitHub on the fly
        owner, repo_name = repo.split("/")
        live_badge = f"[![Status](https://img.shields.io/github/pulls/detail/state/{owner}/{repo_name}/{num}?style=flat-square)]({url})"

        lines.append(f"| **[{repo}](https://github.com/{repo})** | **[#{num}]({url})** | {live_badge} | {desc} | `{created}` |")

    lines.append("\n---\n")
    lines.append("## 🟢 Merged Production Pull Requests (Shipped Upstream)\n")
    lines.append("Production code merged into default branches across AI proxies, native desktop tools, and web infrastructure.\n")
    lines.append("| Repository | PR | Status | Description & Engineering Summary | Merged Date |")
    lines.append("| :--- | :--- | :---: | :--- | :---: |")

    for p in merged_prs:
        repo = p["repository"]["nameWithOwner"]
        num = p["number"]
        url = p["url"]
        title = p["title"].replace("|", "\\|")
        merged_date = format_date(p.get("closedAt"))

        meta = LANDMARK_CONTEXT.get((repo, num))
        if meta:
            desc = f"**{meta['subsystem']}**: {meta['notes']}"
        else:
            desc = title

        status_badge = "[![Merged](https://img.shields.io/badge/merged-8957e5?style=flat-square&logo=git-merge&logoColor=white)](" + url + ")"
        lines.append(f"| **[{repo}](https://github.com/{repo})** | **[#{num}]({url})** | {status_badge} | {desc} | `{merged_date}` |")

    lines.append("\n---\n")
    lines.append("## ⚡ Live Commit Stream (Recent Direct Commits & Pushes)\n")
    lines.append("Extracted dynamically from public commit activity across all canonical repositories.\n")
    lines.append("| Repository | Commit | Message | Date |")
    lines.append("| :--- | :---: | :--- | :---: |")

    for c in recent_commits:
        repo = c["repo"]
        sha = c["sha"]
        url = c["url"]
        msg = c["message"].replace("|", "\\|")
        date = c["date"]
        lines.append(f"| **[{repo}](https://github.com/{repo})** | [`{sha}`]({url}) | {msg} | `{date}` |")

    lines.append("\n---\n")
    lines.append("## 🧠 Architectural Deep Dives & Postmortems\n")
    lines.append("Detailed breakdowns of non-trivial production bugs I diagnosed, isolated, and fixed.\n")

    lines.append("### 1. Storage Leak: 731,000+ Orphaned Telemetry Rows in OmniRoute")
    lines.append("- **PR**: [OmniRoute #14285](https://github.com/diegosouzapw/OmniRoute/pull/14285) fixing [Issue #14268](https://github.com/diegosouzapw/OmniRoute/issues/14268)")
    lines.append("- **Subsystem**: SQLite Storage Engine & Retention Sweeper")
    lines.append("- **Diagnosis**: When stacked prompt compression telemetry was added, per-engine breakdown logs were written to `compression_engine_breakdown`. While the parent `compression_analytics` table was regularly trimmed on an operator-configurable retention policy (default 30 days) and purged on usage resets, `compression_engine_breakdown` was omitted from both `cleanup.ts` and `RESET_TARGETS`. In long-running deployments (5+ months), it grew past 731,000 rows without any deletion path.")
    lines.append("- **Fix**: Built `cleanupCompressionEngineBreakdown()` with a 30-day indexed cutoff, wired it into nightly auto-cleanup, and added the table to `RESET_TARGETS` so manual purges clean it completely. Tested across 4 unit test suites.\n")
    lines.append("```mermaid")
    lines.append("flowchart LR")
    lines.append('    A["Nightly Auto-Cleanup"] --> B["compression_analytics (30d retention)"]')
    lines.append('    A -.-> C["compression_engine_breakdown (Before: MISSED — 731k leaked rows)"]')
    lines.append('    A ==> D["cleanupCompressionEngineBreakdown (My Fix: 30d cutoff & reset wipe)"]')
    lines.append("```\n")

    lines.append("### 2. Security Bypass: Authorization Bypass on URL Rewrite Aliases")
    lines.append("- **PR**: [OmniRoute #13741](https://github.com/diegosouzapw/OmniRoute/pull/13741) fixing [Issue #13685](https://github.com/diegosouzapw/OmniRoute/issues/13685)")
    lines.append("- **Subsystem**: Reverse Proxy Access Control & API Key Scopes")
    lines.append("- **Diagnosis**: When restricted API keys had `allowedEndpoints: [\"search\"]`, calling client-facing rewrite aliases like `/chat/completions` or `/codex/*` evaluated against `resolveEndpointCategory()`. Because that function only recognized canonical `/v1/...` routes, it returned `null`. The policy engine interpreted `null` as \"uncategorized; allow access,\" permitting restricted keys to invoke unauthorized LLM endpoints.")
    lines.append("- **Fix**: Implemented `resolveCanonicalEndpointPath()` to normalize all client aliases to canonical `/v1/...` paths before category resolution, preserving fail-open error handling while closing the bypass completely.\n")
    lines.append("```mermaid")
    lines.append("flowchart TD")
    lines.append('    Req["Incoming Client Request: /chat/completions"] --> Auth["validateEndpointAccess(req)"]')
    lines.append('    Auth --> Old{"Before My Fix"}')
    lines.append('    Old -->|Raw URL checked| Bypass["resolveEndpointCategory(\'/chat/completions\') == null<br/>-> Access Allowed (CRITICAL BYPASS!)"]')
    lines.append('    Auth --> New{"After My Fix"}')
    lines.append('    New -->|Canonicalized first| Secure["resolveCanonicalEndpointPath -> \'/v1/chat/completions\'<br/>-> Evaluates \'chat\' category -> 403 Forbidden"]')
    lines.append("```\n")

    lines.append("### 3. Egress Leak: Leaked Proxy Routing Markers Triggering Upstream 400s")
    lines.append("- **PR**: [OmniRoute #12735](https://github.com/diegosouzapw/OmniRoute/pull/12735) fixing [Issue #12729](https://github.com/diegosouzapw/OmniRoute/issues/12729)")
    lines.append("- **Subsystem**: Streaming Egress Serialization")
    lines.append("- **Diagnosis**: Internal loop-prevention flags (`_omnirouteInternalRequest`, `_omnirouteSkipContextRelay`) were injected into request bodies during multi-model hops but were never stripped before sending upstream. Strict providers like NVIDIA NIM and Groq reject extra keys with HTTP 400 `Unsupported parameter(s)`, causing 504 logged production failures.")
    lines.append("- **Fix**: Audited the executor inheritance tree. Rather than blindly editing all executors, identified that `DarioExecutor` and `NineRouterExecutor` bypassed base dispatch. Added targeted stripping in those specific executors and at the base serialization choke point.\n")
    lines.append("```mermaid")
    lines.append("sequenceDiagram")
    lines.append("    participant Client")
    lines.append("    participant OmniRoute")
    lines.append("    participant Upstream as Upstream (NVIDIA NIM / Groq)")
    lines.append("    Client->>OmniRoute: POST /v1/chat/completions")
    lines.append("    Note over OmniRoute: Injects loop-guard marker:<br/>_omnirouteInternalRequest: true")
    lines.append("    alt Before Fix")
    lines.append('        OmniRoute->>Upstream: Body includes "_omnirouteInternalRequest"')
    lines.append('        Upstream-->>OmniRoute: 400 Bad Request ("unrecognized parameter")')
    lines.append("    else After My Fix")
    lines.append("        OmniRoute->>OmniRoute: stripInternalMarkers() in executor chain")
    lines.append("        OmniRoute->>Upstream: Clean, valid JSON body")
    lines.append("        Upstream-->>OmniRoute: 200 OK (Stream / Completion)")
    lines.append("    end")
    lines.append("```\n")

    lines.append("### 4. Flakey CI: Synthetic Event Delivery Probing on macOS")
    lines.append("- **PR**: [Filecraft #7](https://github.com/Filecraft/Filecraft/pull/7)")
    lines.append("- **Subsystem**: Native macOS System Test Harness (Swift / AppKit)")
    lines.append("- **Diagnosis**: The automated GUI test harness suffered non-deterministic CI failures following host reboots because macOS Accessibility preflight APIs frequently report cached success even when the window server is silently dropping synthetic keyboard and mouse events.")
    lines.append("- **Fix**: Implemented an active delivery verification probe: before executing test journeys, the harness fires an innocuous virtual `F13` key event and verifies receipt within the run loop. If the host environment drops synthetic events, it falls back to `--human-driven` mode.\n")

    lines.append("---\n")
    lines.append("## 🤖 Autonomous Pipeline Architecture\n")
    lines.append("This document is kept permanently in sync by an autonomous GitHub Actions workflow ([`.github/workflows/sync-maintenance-log.yml`](./.github/workflows/sync-maintenance-log.yml)):\n")
    lines.append("1. **Continuous Ingestion**: Every 6 hours (or upon push), the workflow executes [`scripts/generate_maintenance_log.py`](./scripts/generate_maintenance_log.py).")
    lines.append("2. **Cross-Repo Discovery**: Discovers any new pull request, commit, or release authored by `@gonisulaimann` across any public repository on GitHub.")
    lines.append("3. **Real-Time State Evaluation**: Parses state transitions (Open ➔ In-Review ➔ Merged) and injects live Shields.io telemetry badges.")
    lines.append("4. **Zero-Touch Publishing**: Commits and pushes updates back to `main` without manual intervention.\n")

    lines.append("---\n")
    lines.append("*Maintained autonomously by [@gonisulaimann](https://github.com/gonisulaimann) • Powered by Python & GitHub Actions*")

    content = "\n".join(lines) + "\n"

    target_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "MAINTENANCE_LOG.md")
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully generated {target_path} ({len(content)} bytes)")

    # Also update OPEN_SOURCE.md as an alias pointing to MAINTENANCE_LOG.md
    alias_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "OPEN_SOURCE.md")
    with open(alias_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Successfully mirrored to {alias_path}")


if __name__ == "__main__":
    main()
