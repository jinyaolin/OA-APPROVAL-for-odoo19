# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

```
odoo19/
├── odoo/          # Odoo 19 source (cloned from github.com/odoo/odoo, branch 19.0)
├── venv/          # Python 3.11 virtual environment
├── logs/          # Runtime logs (odoo.log)
├── odoo.conf      # Odoo server configuration
└── start.sh       # Convenience startup script
```

## Commands

### Start Odoo
```bash
./start.sh
# or manually:
source venv/bin/activate
python odoo/odoo-bin -c odoo.conf
```

### Start with a specific database
```bash
./start.sh -d mydb
```

### Install/update a module
```bash
./start.sh -d mydb -i module_name     # install
./start.sh -d mydb -u module_name     # update
```

### Run tests for a module
```bash
./start.sh -d testdb --test-enable -i module_name --stop-after-init
```

### Activate virtual environment
```bash
source venv/bin/activate
```

## Infrastructure

- **Python**: 3.11 (venv at `venv/`)
- **Database**: PostgreSQL 14, running locally on port 5432
- **DB user**: `odoo` (superuser, no password)
- **Web**: http://127.0.0.1:8069

## Odoo Architecture

Odoo is a monolithic Python web framework with these key layers:

- **`odoo/odoo/`** — core framework: ORM (`models/`), HTTP (`http.py`), fields, SQL
- **`odoo/addons/`** — all official modules (each is a Python package with `__manifest__.py`)
- **`odoo/odoo/addons/`** — base module (always loaded)

Each addon module contains:
- `__manifest__.py` — metadata, dependencies, data files
- `models/` — Python classes inheriting `models.Model` (mapped to PostgreSQL tables via ORM)
- `views/` — XML UI definitions (form, list, kanban, etc.)
- `controllers/` — HTTP routes (`http.route`)
- `security/` — access control (`ir.model.access.csv`, record rules)
- `data/` — XML/CSV seed data
- `static/` — JS/CSS/assets

## Custom Addons

Place custom addons in a separate directory (e.g., `custom_addons/`) and add it to `odoo.conf`:
```ini
addons_path = custom_addons,odoo/addons,odoo/odoo/addons
```
