# Stage 5 — Specialize

By now you know Python itself. Stage 5 is about building real software in one domain.
**Pick one track and go deep** (about 8–12 weeks) before you sample another.

| Track | Pick it if you want to… | Guide |
|---|---|---|
| Web backend | build APIs and web services | [web_backend.md](web_backend.md) |
| Data / analytics | analyze data and build reports and pipelines | [data_analytics.md](data_analytics.md) |
| ML / AI | train models or build LLM-powered applications | [ml_ai.md](ml_ai.md) |
| Automation / DevOps | script infrastructure, CI and repetitive work | [automation_devops.md](automation_devops.md) |
| Scientific computing | run simulations and numerical methods | [scientific.md](scientific.md) |

## How the tracks work

From here on, you need third-party libraries, so there are no auto-graded stubs.
Each track has **milestones** instead. Each milestone has:

- **Learn:** the concepts and libraries, with official docs linked.
- **Build:** a concrete deliverable.
- **Done when:** objective acceptance criteria that you check yourself.

Use the Stage 3 tooling for every milestone: a `uv` project, type hints, `pytest`, `ruff` and git.

```bash
uv init my-track-project && cd my-track-project
uv add <libraries>
uv add --dev pytest ruff mypy
```
