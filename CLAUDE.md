# CLAUDE.md — Skill 253: fighting-game-combo-optimizer

## Skill Identity
- **Skill Name:** `fighting-game-combo-optimizer`
- **Tagline:** Optimal Combo Coordination Strategy for Fighting Games — Fighting-Game Combo & Frame-Data Optimization analysis & decision-support harness.
- **Current Phase:** Phase 0 — Architecture & Research
- **Folder:** `D:\972026\253-fighting-game-combo-optimizer\`

---

## Problem This Skill Solves

This skill provides a structured, evidence-backed analytical workflow for
**Fighting-Game Combo & Frame-Data Optimization**. It gathers authoritative real-time and reference data, applies
recognized domain methods, cross-references academic research, and delivers
actionable outputs that are fully evidenced, risk/limitation-disclosed, and
traceable to authoritative sources — continuously self-improving through an
automated knowledge crawl pipeline.

---

## Harness Flow Summary

```
/fighting-game-combo-optimizer invoked
│
├─ Step 1: sub-gather-requirements   → Clarify the object of analysis, constraints, timeframe, available inputs, target audience, and language before any data fetching.
├─ Step 2: sub-evidence-collector   → Fetch authoritative real-time and reference data for the object: current status/parameters, authoritative documents/standards, and recent developments from domain and academic sources.
├─ Step 3: sub-core-analysis   → Analyze and propose optimal combo coordination for fighting games, optimizing damage, meter, and punish routes from frame data.
├─ Step 4: sub-knowledge-updater   → Query SECOND-KNOWLEDGE-BRAIN.md for authoritative academic and professional evidence; surface citations with tier labels and flag gaps for the crawl pipeline.
├─ Step 5: sub-advisor   → Synthesize all prior analysis into a risk-disclosed conclusion with a full evidence chain and recommended actions.
└─ Step 6: main (quality gate)       → verify evidence hierarchy, disclosure, output polish
```

---

## Sub-Skills

| `skills/sub-gather-requirements.md` | Clarify the object of analysis, constraints, timeframe, available inputs, target audience, and language before any data fetching. |
| `skills/sub-evidence-collector.md` | Fetch authoritative real-time and reference data for the object: current status/parameters, authoritative documents/standards, and recent developments from domain and academic sources. |
| `skills/sub-core-analysis.md` | Analyze and propose optimal combo coordination for fighting games, optimizing damage, meter, and punish routes from frame data. |
| `skills/sub-knowledge-updater.md` | Query SECOND-KNOWLEDGE-BRAIN.md for authoritative academic and professional evidence; surface citations with tier labels and flag gaps for the crawl pipeline. |
| `skills/sub-advisor.md` | Synthesize all prior analysis into a risk-disclosed conclusion with a full evidence chain and recommended actions. |

---

## Tools Required

- **WebSearch** — live domain news, reports, standards updates
- **WebFetch** — scrape Fighting-Game Combo & Frame-Data Optimization authoritative sources
- **Read / Write** — read SECOND-KNOWLEDGE-BRAIN.md; append knowledge entries
- **Bash** — run `tools/knowledge_updater.py` for periodic crawl
- **Skill** — invoke sub-skills sequentially through the harness

---

## Knowledge Sources

### Domain Authoritative Sources
- Frame-data databases (FatOnline, Dustloop, Mizuumi)
- Game-specific combo docs
- Community combo databases (SuperCombo)
- Pro player combo showcases
- Damage-scaling & meter references
- Matchup & punish data

### Academic & Research Sources
- Proceedings of CHI PLAY (ACM)
- IEEE Transactions on Games
- Entertainment Computing — Elsevier
- Computers in Human Behavior — Elsevier
- Simulation & Gaming — SAGE
- Journal of Game Design & Development Education

### Academic Crawl Targets
- Semantic Scholar / Google Scholar for "Fighting-Game Combo & Frame-Data Optimization" keyword clusters
- Domain preprint servers where applicable
- Standards bodies and professional associations (see data sources)

---

## Supporting Python Tools

| File | Purpose |
|------|---------|
| `tools/knowledge_updater.py` | Crawl pipeline: fetches latest papers + news → appends to SECOND-KNOWLEDGE-BRAIN.md |

---

## Automated Knowledge Update Schedule

```cron
# Weekly academic update (Mondays 8:00 AM)
0 8 * * 1 python D:/972026/253-fighting-game-combo-optimizer/tools/knowledge_updater.py >> logs/knowledge_update.log 2>&1

# Daily news update (Daily 7:00 AM)
0 7 * * * python D:/972026/253-fighting-game-combo-optimizer/tools/knowledge_updater.py --news-only >> logs/knowledge_news.log 2>&1
```

Manual: `python tools/knowledge_updater.py --dry-run` | `--keywords "..."` | `--news-only`

---

## Active Development Tasks

- [x] Phase 0: Architecture & source map (this file, PROJECT-detail.md, PDPT.md)
- [x] Phase 1: Core sub-skills (production-grade)
- [x] Phase 2: Main harness + quality gates + degradation
- [x] Phase 3: Knowledge pipeline + tests + cron
- [x] Phase 4: Testing & validation (all validators pass)
- [x] Phase 5: Integration & polish (PRODUCTION READY v1.0.0)

---

## References

- `PROJECT-detail.md` — full technical specification
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — build roadmap
- `SECOND-KNOWLEDGE-BRAIN.md` — self-improving knowledge base
- `D:\972026\SKILL-STANDARD.md` — library-wide standard
- Reference impl: `D:\vn-finance-analysis-hd-skill`
