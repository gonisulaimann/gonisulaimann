# Goni Sulaiman

Systems and developer tooling engineer building native macOS software, static analysis engines, and high-throughput AI infrastructure. Core contributor to production routing and streaming runtimes.

<a href="https://github.com/gonisulaimann/Grounded"><img height="20" src="https://img.shields.io/badge/Grounded-v0.5.0-blue?style=flat-square&logo=python" alt="Grounded"/></a>
<a href="https://github.com/gonisulaimann/Notcher"><img height="20" src="https://img.shields.io/badge/Notcher-macOS%2014+-orange?style=flat-square&logo=swift" alt="Notcher"/></a>
<a href="https://github.com/diegosouzapw/OmniRoute"><img height="20" src="https://img.shields.io/badge/OmniRoute-Core%20Contributor-2ea44f?style=flat-square&logo=github" alt="OmniRoute"/></a>
<a href="https://linkedin.com/in/gonisulaimann"><img height="20" src="https://img.shields.io/badge/LinkedIn-gonisulaimann-0077B5?style=flat-square&logo=linkedin" alt="LinkedIn"/></a>

## 📌 Featured projects

<table>
  <tr>
    <td width="50%" valign="top">
      <b><a href="https://github.com/gonisulaimann/Grounded">Grounded</a></b>
      <a href="https://github.com/gonisulaimann/Grounded"><img height="18" src="https://img.shields.io/badge/-Public-lightgrey?style=flat-square" alt="Public"/></a><br/>
      <sub>Zero-dependency static analysis engine detecting comment-code drift across Python, JavaScript/TypeScript, and Go. Parses AST and token streams to catch dead symbol names and broken file references.</sub><br/>
      <img height="18" src="https://img.shields.io/badge/-Python-3776AB?style=flat-square" alt="Python"/>
      <a href="https://github.com/gonisulaimann/Grounded/stargazers"><img height="18" src="https://img.shields.io/github/stars/gonisulaimann/Grounded?style=social" alt="stars"/></a>
    </td>
    <td width="50%" valign="top">
      <b><a href="https://github.com/gonisulaimann/Notcher">Notcher</a></b>
      <a href="https://github.com/gonisulaimann/Notcher"><img height="18" src="https://img.shields.io/badge/-Public-lightgrey?style=flat-square" alt="Public"/></a><br/>
      <sub>Native macOS menu bar and Dynamic Island system utility built with Swift & SwiftUI. Features spring-physics HUD morphing around hardware notch geometry and local peer-to-peer iOS synchronization.</sub><br/>
      <img height="18" src="https://img.shields.io/badge/-Swift-F05138?style=flat-square" alt="Swift"/>
      <a href="https://github.com/gonisulaimann/Notcher/releases"><img height="18" src="https://img.shields.io/github/v/release/gonisulaimann/Notcher?style=flat-square" alt="release"/></a>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <b><a href="https://github.com/gonisulaimann/OmniRoute">OmniRoute (Upstream Work)</a></b>
      <a href="https://github.com/diegosouzapw/OmniRoute"><img height="18" src="https://img.shields.io/badge/-Contributor-2ea44f?style=flat-square" alt="Contributor"/></a><br/>
      <sub>Active upstream contributor to OmniRoute, an open-source AI gateway routing across 350+ providers. Diagnosed and fixed critical URL rewrite authorization bypasses, upstream SSE payload leaks, and WebSocket transports.</sub><br/>
      <img height="18" src="https://img.shields.io/badge/-TypeScript-3178C6?style=flat-square" alt="TypeScript"/>
      <a href="./OPEN_SOURCE.md"><img height="18" src="https://img.shields.io/badge/Contributions-Index-blue?style=flat-square" alt="Index"/></a>
    </td>
    <td width="50%" valign="top">
      <b><a href="https://github.com/Centre-For-Energy/ceii-platform">CEII Platform</a></b>
      <a href="https://github.com/Centre-For-Energy/ceii-platform"><img height="18" src="https://img.shields.io/badge/-Public-lightgrey?style=flat-square" alt="Public"/></a><br/>
      <sub>Modular enterprise energy research web platform. Engineered the foundational application shell, component primitives, WCAG AA accessibility architecture, and modular routing infrastructure.</sub><br/>
      <img height="18" src="https://img.shields.io/badge/-TypeScript-3178C6?style=flat-square" alt="TypeScript"/>
      <a href="https://github.com/Centre-For-Energy/ceii-platform/pulls?q=is%3Apr+author%3Agonisulaimann"><img height="18" src="https://img.shields.io/badge/PRs-Merged-green?style=flat-square" alt="PRs"/></a>
    </td>
  </tr>
</table>

## What I build

I focus on systems where correctness, low latency, and runtime reliability matter:

- **Static Analysis & Tooling**: Writing zero-dependency lexical scanners and AST-based parsers that run fast enough for pre-commit hooks and local CI.
- **Native Systems & Desktop UX**: Building native macOS applications with Swift, AppKit, and SwiftUI that integrate deeply with Apple hardware APIs and local networking.
- **AI Gateway Infrastructure**: Developing proxy pipelines, real-time streaming engines (SSE, WebSockets), failover circuit breakers, and security enforcement mechanisms for LLM traffic.

## Open-Source Contributions

I actively contribute to high-traffic open-source infrastructure projects. In [OmniRoute](https://github.com/diegosouzapw/OmniRoute) (68k+ stars, 350+ providers), my work covers:

- **Security & Authorization**: Fixed a critical access-control bypass on URL rewrite aliases where non-canonical paths escaped category checks ([#13741](https://github.com/diegosouzapw/OmniRoute/pull/13741)).
- **Streaming & Protocol Correctness**: Eliminated upstream HTTP 400 Bad Request errors on strict providers (NVIDIA NIM, Groq) caused by internal routing marker leakage ([#12735](https://github.com/diegosouzapw/OmniRoute/pull/12735)).
- **Real-Time Transports**: Implemented bi-directional WebSocket transport dispatch and turn parameter normalization for the Codex App-Server provider ([#14281](https://github.com/diegosouzapw/OmniRoute/pull/14281)).
- **Database & Migration Resilience**: Silenced false-positive boot crashes during legacy Bifrost slot index renumbering ([#14274](https://github.com/diegosouzapw/OmniRoute/pull/14274)).
- **Storage & Retention Engineering**: Added retention pruning and period reset sweeps for unpruned `compression_engine_breakdown` telemetry tables ([#14285](https://github.com/diegosouzapw/OmniRoute/pull/14285)).
- **Test Harness Engineering**: Authored synthetic event delivery verification for native macOS GUI test harnesses in [Filecraft](https://github.com/Filecraft/Filecraft) ([#7](https://github.com/Filecraft/Filecraft/pull/7)).

👉 **See my complete [Upstream Maintenance Log & Engineering Notes](./OPEN_SOURCE.md)** for detailed problem diagnoses, execution traces, and PR breakdowns.

## Connect

- **GitHub**: [@gonisulaimann](https://github.com/gonisulaimann)
- **LinkedIn**: [linkedin.com/in/gonisulaimann](https://linkedin.com/in/gonisulaimann)
