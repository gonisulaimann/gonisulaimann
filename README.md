# Goni Sulaiman

> I build systems that keep your data where it belongs — on your device.

No accounts. No uploads. No leaks. Just software that does the job and gets out of the way.

---

### Work

| | What | Stack |
|---|---|---|
| **[Filecraft](https://github.com/Filecraft/Filecraft)** | Local-first file tools. Prepare a PDF, resize an image, convert a document — work on a copy, keep the original. Ships on Windows, macOS, Linux, browser. | Python · Swift · Web · Extensions |
| **[filecraft.github.io](https://filecraft.github.io/)** | Product site, docs, download & release infrastructure. EN / FR / ES. | Static · Docs-as-code |
| **[ceii-platform](https://github.com/Centre-For-Energy/ceii-platform)** | Institutional platform for the Centre for Energy Investment and Innovation, Abuja. Modular monolith with hard boundaries: presentation never touches data directly. | React / Vite / Tailwind · FastAPI · PostgreSQL · Strapi · Docker |

<details>
<summary><b>How I work — architecture in 30 seconds</b></summary>
<br>

```
Users
  │
  ▼
Presentation (React / static) ── REST ──► Application (FastAPI / local engine)
                                              ├──► Owned data (PostgreSQL / local files)
                                              └──► Editorial (Strapi / docs)
```

- One source of truth per domain. Nothing duplicated, nothing fabricated.
- Frontend never becomes the business-logic layer.
- Public content comes from verified sources only.

</details>

---

### Principles

1. **Local first.** If it can run on your machine, it should.
2. **Small surface, hard edges.** Fewer features, clean boundaries, no magic.
3. **No slop.** Every file earns its place or gets deleted.

---

### Now

- Shipping Filecraft `0.10` beta across desktop + browser + extension
- Building CEII platform foundation — probes, migrations, CI, app shell
- Mirroring [OmniRoute](https://github.com/gonisulaimann/OmniRoute) for local AI-gateway experiments

---

### Contact

`linkedin` — [gonisulaimann](https://linkedin.com/in/gonisulaimann) · `x` — [@gonisulaimann](https://x.com/gonisulaimann) · `web` — [filecraft.github.io](https://filecraft.github.io/)

Open an issue on any repo. I read everything.

---
<sub>Filecraft · Centre for Energy Investment and Innovation · Abuja / Remote</sub>
