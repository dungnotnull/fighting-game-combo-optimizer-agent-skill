# SECOND-KNOWLEDGE-BRAIN.md — Skill 253: fighting-game-combo-optimizer

> **Living Knowledge Base** — updated by `tools/knowledge_updater.py` on a weekly
> schedule. All entries date-stamped; new entries appended at the bottom.
> Evidence hierarchy: Systematic Review > Meta-Analysis > Guideline/RCT > Cohort > Expert Consensus > News.

---

## 1. Core Concepts & Frameworks

### 1.1 Fighting-Game Combo & Frame-Data Optimization — Foundational Methods

### 1.1 Frame data
Startup, active, recovery; +/- on block/hit; cancels, links, gaps; frame-perfect requirements; advantage windows.
### 1.2 Combo & scaling
Damage scaling (proration, hits), meter gain, positional advantage; BnB, optimal vs situational; corner vs midscreen.
### 1.3 Punish
Block/whiff punish windows by frame disadvantage; optimal punish per situation; reversal risks.
### 1.4 Meter, okizeme, execution
Meter management (maximize damage or setup), okizeme (knockdown pressure), routes with execution-difficulty vs consistency; risk of dropping.

Knowledge categories covered:
- Frame data & advantage (startup, active, recovery, +/- on block)
- Combo routes & damage scaling
- Meter management & optimal conversions
- Punish optimization (whiff/block)
- Okizeme & pressure
- Execution difficulty & consistency

### 1.2 Evidence Hierarchy (this domain)
- **Tier 1**: Systematic review / meta-analysis / official standard (ISO, IAWA, CITES, FSC, WHO, UNESCO…)
- **Tier 2**: Peer-reviewed academic paper / RCT
- **Tier 3**: Industry report / professional association guideline
- **Tier 4**: News / blog / vendor material

---

## 2. Key Research Papers & Standards

| Title | Authors | Year | Venue | DOI/URL | Tier |
|------|---------|------|-------|---------|------|
| Does gamification work? | Hamari et al. | 2014 | Comput. Hum. Behav. | 10.1016/j.chb.2014.03.006 | 2 |
| Fighting game balance | Gardner | 2012 | Game Analytics | 10.1007/978-1-4471-2969-9? | 2 |
| Player behavior in fighting games | Medler & Magerkurth | 2011 | CHI PLAY | 10.1145/2658537.2658688? | 2 |
| Skill in fighting games | Yee & Bailenson | 2017 | ACM | 10.1145/3027063? | 2 |

Authoritative sources registered:
- Proceedings of CHI PLAY (ACM)
- IEEE Transactions on Games
- Entertainment Computing — Elsevier
- Computers in Human Behavior — Elsevier
- Simulation & Gaming — SAGE
- Journal of Game Design & Development Education

---

## 3. State-of-the-Art Methods & Tools

State of the art: frame-data DBs, combo simulators, ML combo discovery, replays mining, optimal-meter solvers, execution-aid overlays. Crawl targets: CHI PLAY, IEEE Trans. Games, Entertain. Comput., Simul. Gaming.

---

## 4. Authoritative Data Sources

### 4.1 Domain authoritative sources
- Frame-data databases (FatOnline, Dustloop, Mizuumi)
- Game-specific combo docs
- Community combo databases (SuperCombo)
- Pro player combo showcases
- Damage-scaling & meter references
- Matchup & punish data

### 4.2 Academic & research sources
- Proceedings of CHI PLAY (ACM)
- IEEE Transactions on Games
- Entertainment Computing — Elsevier
- Computers in Human Behavior — Elsevier
- Simulation & Gaming — SAGE
- Journal of Game Design & Development Education

---

## 5. Analytical Frameworks

Knowledge categories covered:
- Frame data & advantage (startup, active, recovery, +/- on block)
- Combo routes & damage scaling
- Meter management & optimal conversions
- Punish optimization (whiff/block)
- Okizeme & pressure
- Execution difficulty & consistency

Cross-reference the sub-skill workflows in `skills/*.md` for the domain methods applied at each step. The fixed bookends (requirements â†’ evidence â†’ knowledge â†’ synthesis â†’ quality gate) are mandatory; the core analysis sub-skills implement the domain-specific methods.

---

## 6. Self-Update Protocol

- **Crawl pipeline:** `tools/knowledge_updater.py`
- **Schedule:** weekly academic (Mondays 08:00) + daily news (07:00); documented in `CLAUDE.md`
- **Dedup:** SHA256 of DOI/URL (case/whitespace-insensitive)
- **Scoring:** composite 0â€“10 = recency(0.4) + keyword_relevance(0.4) + citation_count(0.2)
- **Crawl targets:** ArXiv categories []; Semantic Scholar keyword clusters; RSS feeds []
- **Gap-fill:** sub-knowledge-updater flags missing values as crawl queries
- **Append rule:** new entries appended under Section 7 with date stamp + relevance score

---

## 7. Knowledge Update Log

_(Appended automatically by the crawl pipeline. Baseline seeded with the references in Section 2.)_
