# Science Portal

A Django-based science learning platform with courses, lessons, enrollment, REST API, and English/Turkmen i18n.

## Quick Start

```bash
bash setup.sh
source venv/bin/activate
python manage.py runserver
```

Open http://127.0.0.1:8000

## Credentials (after seed)

> ⚠️ **IMPORTANT**: Change all default passwords in production!

| Role       | Username    | Password (change me!) |
|------------|-------------|----------------------|
| Admin      | admin       | admin123             |
| Instructor | instructor  | instructor123        |

Create new users via `/register/` or Django admin (`/admin/`).

## URL Map

| URL                              | Description            |
|----------------------------------|------------------------|
| /                                | Home                   |
| /courses/                        | Course list + search   |
| /courses/<slug>/                 | Course detail          |
| /courses/<slug>/enroll/          | Enroll                 |
| /courses/<slug>/lessons/<slug>/  | Lesson page            |
| /profile/                        | User profile           |
| /auth/login/                     | Login                  |
| /register/                       | Register               |
| /admin/                          | Django admin           |
| /api/courses/                    | DRF — courses          |
| /api/courses/<slug>/lessons/     | DRF — lessons          |
| /api/enrollments/                | DRF — my enrollments   |
| /api/categories/                 | DRF — categories       |
| /api/me/                         | DRF — current user     |

## API Examples

```bash
# List courses
curl http://127.0.0.1:8000/api/courses/

# Search
curl "http://127.0.0.1:8000/api/courses/?search=physics"

# Filter by level
curl "http://127.0.0.1:8000/api/courses/?level=beginner"
```

## Switch Language

Use the dropdown in the navbar to switch between **English** and **Turkmen**.

## Tech Stack

- Python 3.10+
- Django 4.2
- Django REST Framework 3.15
- SQLite (dev) / PostgreSQL (prod)
- Bootstrap 5

## Switch to PostgreSQL

Edit `DATABASES` in `science_portal/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'scienceportal',
        'USER': 'postgres',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
