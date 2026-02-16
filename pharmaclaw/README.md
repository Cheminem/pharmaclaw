# PharmaClaw 🧪

[![Built with OpenClaw](https://img.shields.io/badge/Built%20with-OpenClaw-667eea?style=flat-square)](https://openclaw.ai)
[![Available on ClawHub](https://img.shields.io/badge/Available%20on-ClawHub-indigo?style=flat-square)](https://clawhub.com)
[![License: Open Source](https://img.shields.io/badge/License-Open%20Source-green?style=flat-square)](#license)

AI-powered drug discovery pipeline built on OpenClaw.

## What is PharmaClaw?

7 specialized AI agents that chain together for end-to-end drug analysis:

- 🧪 **Chemistry Query** — PubChem lookups, RDKit molecular properties, 2D structure visualization
- 💊 **Pharmacology** — ADME profiling, Lipinski/Veber rules, druglikeness scoring
- ☠️ **Toxicology** — hERG risk, hepatotoxicity flags, safety alerts
- 🔬 **Synthesis Planning** — Retrosynthesis routes, feasibility scoring, reagent availability
- 💼 **IP Expansion** — FTO analysis, bioisostere suggestions, patent landscape
- 📊 **Market Intelligence** — FAERS adverse event trends, competitive landscape
- 📄 **Report Generator** — Unified PDF/JSON reports with color-coded assessments

## Features

### Free
- Chemistry Query (PubChem + RDKit)
- Pharmacology profiling (Lipinski, ADME heuristics)
- Demo compound reports

### Pro ($49/mo, $29 founding member)
- All 7 agents with multi-agent chaining
- Compound Comparison Mode
- PDF Report Export
- Batch Analysis (1-500 compounds)
- Synthesis Planning & Feasibility
- Enhanced ADME Profiling (80+ properties)
- Watch Lists & Alerts (FAERS monitoring)
- API access

### Enterprise
- Unlimited everything
- Custom agents
- On-prem deployment
- Priority support

## Pipeline

```
Input SMILES → 🧪 Chemistry → 💊 Pharmacology → ☠️ Toxicology → 🔬 Synthesis → 💼 IP Check → 📊 Market Intel → 📄 Report
```

## Quick Start

Install from ClawHub:

```bash
clawhub install chemistry-query
clawhub install pharma-pharmacology-agent
```

## Pro Tools CLI

```bash
# Compare compounds
python scripts/compound_comparison.py "SMILES1" "SMILES2" --ml --synth

# Batch analysis
python scripts/batch_analysis.py compounds.csv --ml --synth --pdf

# Retrosynthesis
python scripts/retrosynthesis.py "SMILES"

# Watch lists
python scripts/watchlist_manager.py add --name "My Watch" --drug sotorasib
python scripts/watchlist_scanner.py
```

## Links

- 🌐 Website: [pharmaclaw.com](https://pharmaclaw.com)
- 📦 ClawHub: [clawhub.com](https://clawhub.com)
- 🤖 OpenClaw: [openclaw.ai](https://openclaw.ai)
- 📧 Contact: cheminem602@gmail.com

## License

Open-source agents on OpenClaw.

© 2026 PharmaClaw
