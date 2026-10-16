# AGENTS.md

## Dev commands

- **Venv**: activate `.venv` before any python/pip/briefcase/pytest calls. `uv` commands auto-use the venv.

  ```powershell
  # repo root (Windows)
  .venv\Scripts\activate
  ```

  ```bash
  # repo root (Linux/macOS)
  source .venv/bin/activate
  ```

- **Run app**:
  ```
  cd stocks
  briefcase dev
  ```
- **Update & run**: `briefcase run -u -r` (from `stocks/`)
- **Build exe**: `briefcase create && briefcase build && briefcase run` (from `stocks/`)
- **Package installer**: `briefcase package --adhoc-sign` (from `stocks/`)
- **Setup from scratch**: `uv venv && uv sync`
- **Update akshare**: `pip install akshare --upgrade`
- **Test**: `pytest -vv` (from `stocks/`, requires `briefcase dev` first to install test deps)

## Structure

- `pyproject.toml` at root — uv project, only deps: `akshare`, `briefcase`
- `stocks/pyproject.toml` — Briefcase app config (sources, builds, backends)
- **Must run briefcase from `stocks/`**, not repo root
- Entrypoint: `stocks/src/stocks/__main__.py` → `app.py` → toga.App subclass
- 6 source packages under `stocks/src/`: `stocks/` (app + controller), `services/`, `models/`, `database/`, `view/`, `hk/` (legacy)

## Architecture

- **Briefcase/Toga** desktop app (cross-platform GUI via Python)
- **akshare** for Chinese stock data (A-share + HK)
- **SQLite** via singleton per-thread connection manager (`database/connection.py`)
- Database path is **hardcoded** in `stocks/src/stocks/app.py:16` (`D:\Site\stock\finance.db`)
- Config persisted in SQLite `config` table via `ConfigService`
- Python 3.14+ required

## Stock Analysis Framework

**Default: always use the `investment-analysis-framework` skill for any stock/company analysis** (triggers on 「分析公司」「股票分析」「投资分析」). Do not improvise a panel from memory.

- **Three-person panel**: Munger (生意质量) : Greenblatt (价值/魔法公式) : Taleb (尾部风险/反脆弱), weighted **3:4:3**
- **Final score** = (Munger×3 + Greenblatt×4 + Taleb×3) / 10
- **8.0-10** ⭐⭐⭐⭐⭐ 强烈推荐 | **7.0-7.9** ⭐⭐⭐⭐ 推荐 | **6.0-6.9** ⭐⭐⭐ 观望 | **5.0-5.9** ⭐⭐⭐☆ 谨慎 | **<5.0** ⭐⭐ 回避
- **Taleb holds veto power** (governance score < 3.0 or extreme tail risk → auto-reject)
- Full framework at `.agents/skills/investment-analysis-framework/SKILL.md`

> **Deprecated:** `.agents/skills/stock_analysis/SKILL.md` (Munger/Taleb/Schloss 4:3:3) is **not registered/deprecated** — its SKILL.md lacks YAML frontmatter so it never loads. Use `investment-analysis-framework` instead.

## Quirks

- No lint, formatter, typecheck, or CI workflows configured
- Legacy `stocks/src/hk/hkreport.py` references `src.stocks.SqliteTool` and `src.stocks.hkstock` — likely dead code, its import style differs from the refactored modules
- Linux builds require GTK3 system packages (`libgtk-3.0`, `gir1.2-gtk-3.0`)

<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tools** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them. `codegraph_node` returns one symbol's source + callers, or reads a whole file with line numbers. If the tools are listed but deferred, load them by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` and `codegraph node <symbol-or-file>` print the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->
