#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python odoo/odoo-bin -c odoo.conf "$@"
