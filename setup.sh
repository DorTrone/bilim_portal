#!/bin/bash
set -e

echo "=== Science Portal — Local Setup ==="

# 1. Virtual env
python3 -m venv venv
source venv/bin/activate

# 2. Dependencies
pip install -r requirements.txt

# 3. Compile Turkmen translations
python manage.py compilemessages --locale tk || echo "msgfmt not found, skipping translations"

# 4. Migrations
python manage.py makemigrations
python manage.py migrate

# 5. Seed demo data
python manage.py seed_data

echo ""
echo "=== Done! ==="
echo "Run:  source venv/bin/activate && python manage.py runserver"
echo "Open: http://127.0.0.1:8000"
echo "Admin: http://127.0.0.1:8000/admin  (admin / admin123)"
