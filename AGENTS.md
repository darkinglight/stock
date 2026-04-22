# AGENTS.md

## Dev commands

- **Setup**: `cd stocks && briefcase dev` (must `cd stocks`, not root)
- **Run**: `briefcase run`
- **Build exe**: `briefcase create && briefcase build && briefcase run`
- **Update & run**: `briefcase run -u -r`
- **Package installer**: `briefcase package --adhoc-sign`

## Key facts

- Briefcase/Toga desktop app (cross-platform GUI via Python)
- Python 3.14+, dependencies from `pyproject.toml`
- Main code in `stocks/src/stocks/`: `app.py`, `a_stock_controller.py`
- Services in `stocks/src/services/`: a_*_service.py files (stock data fetching via akshare)
- Models in `stocks/src/models/`: bonus.py, financial.py, stock.py
- Tests in `stocks/tests/` using pytest
- Data package uses akshare for Chinese stock data

## Quirks

- Must run briefcase from `stocks/` directory, not repo root
- Linux builds require GTK3 system packages (libgtk-3.0, gir1.2-gtk-3.0)
- ak share data updates require pip (`pip install akshare --upgrade`)