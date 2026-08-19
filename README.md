# hackathon1 — OpenAIRE AI Hackathon

**Submission for:** [OpenAIRE AI Hackathon - Powered by Alien Intelligence](https://graph.openaire.eu/component/eventbooking/hackathons/openaire-ai-hackathon-powered-by-alien-intelligence)
**Deadline:** August 20, 2026 (23:59 CET)

---

## What is OpenAIRE?

OpenAIRE Graph is one of the world's largest scholarly knowledge graphs — **386.6M+ research products** aggregated from Crossref, PubMed, ORCID, DataCite, Zenodo, arXiv, and 1000+ repositories.

### Key APIs

| API | Base URL | What it does |
|-----|----------|--------------|
| **Graph API V3** | `https://api.openaire.eu/graph/v3/` | Search/filter research products, orgs, projects, persons |
| **Graph API V4 (BETA)** | `https://api-beta.openaire.eu/graph/v4/` | Unified filter syntax, aggregations, sparse fieldsets |
| **ScholeXplorer** | `https://api.scholexplorer.openaire.eu/` | Dataset-publication & dataset-dataset links |
| **Broker API** | TBD | Enrich metadata for repositories |

### Data Model Entities

| Entity | Description |
|--------|-------------|
| **ResearchProduct** | Publications, datasets, software, other research outputs |
| **Organization** | Universities, research institutions, funders |
| **DataSource** | Repositories, journals, aggregators |
| **Project** | Funded research grants |
| **Person** | Authors and contributors |
| **Community** | Research infrastructures, alliances |

### Research Product Sub-types

- **Publication** — journal articles, conference papers, books, theses
- **Data** — datasets, geolocations, versions
- **Software** — code repos, programming languages, docs
- **Other** — protocols, methods, etc.

---

## Quick Start

```bash
cd /root/hackathon1
pip install -r requirements.txt

# Explore the API
python explore_api.py

# Search for something
python search.py "open access"
```

---

## Links

- [OpenAIRE Graph](https://graph.openaire.eu/)
- [Graph API Docs](https://graph.openaire.eu/docs/apis/graph-api/)
- [V4 API Docs](https://graph.openaire.eu/docs/apis/graph-api-v4/)
- [Swagger UI (V3)](https://api.openaire.eu/graph/swagger-ui/index.html)
- [Swagger UI (V4)](https://api-beta.openaire.eu/graph/swagger-ui/index.html)
- [Full Dataset (Zenodo)](https://doi.org/10.5281/zenodo.3516917)
- [Hackathon Page](https://graph.openaire.eu/component/eventbooking/hackathons/openaire-ai-hackathon-powered-by-alien-intelligence)
