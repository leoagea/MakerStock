# MakerStock
A physical and digital inventory system for electronic components. Organize your parts with 3D-printed modular drawers and easily track, search, and locate everything from a web interface.

## Setup

Copy `.env.example` to `.env`, then start the project:

```bash
cp .env.example .env
docker compose up --build
```

In a second terminal, apply the migrations and create an admin superuser:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

The application is available at <http://localhost:8000/> and the Django admin is available at <http://localhost:8000/admin/>.
