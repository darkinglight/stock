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

## Quirks

- No lint, formatter, typecheck, or CI workflows configured
- Legacy `stocks/src/hk/hkreport.py` references `src.stocks.SqliteTool` and `src.stocks.hkstock` — likely dead code, its import style differs from the refactored modules
- Linux builds require GTK3 system packages (`libgtk-3.0`, `gir1.2-gtk-3.0`)
