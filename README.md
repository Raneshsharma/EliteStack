# Placement Copilot

**AI-powered resume builder for college students, graduates, and early-career job seekers.**

Build professional resumes, generate cover letters, optimize for ATS, prep for interviews, and more — all in one place.

## Features

### Resume Builder
- Guided multi-section form: Personal Info, Education, Experience, Projects, Skills
- 3 template styles: Classic, Modern, Minimal
- Live preview with one-click switching
- Export to PDF
- Duplicate, set primary, and manage multiple resumes

### AI Features (Pro/Premium)

| Feature | Free | Pro | Premium |
|---------|------|-----|---------|
| AI Resume Rewrite | — | 20/day | 50/day |
| Cover Letter Generator | — | 10/day | 30/day |
| Job Match / Keyword Tailoring | — | 5/day | 20/day |
| ATS Score Checker | — | 10/day | 30/day |
| AI Career Chat | 5/day | 50/day | 100/day |
| Interview Prep | — | 10/day | 30/day |
| Email Templates | — | 20/day | 50/day |
| LinkedIn Optimizer | — | 10/day | 30/day |
| Salary Calculator | Median only | Full ranges | Full ranges |

### Tools
- **Salary Calculator** — real salary data for 30+ job titles across 4 experience levels and 50+ US cities
- **Portfolio Builder** — public portfolio page at `/u/<username>/` with 3 theme options
- **AI Chat** — floating chat panel accessible on every page

## Tech Stack

- **Backend:** Django 4.2 + Django REST Framework
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Frontend:** Django templates + Tailwind CSS + vanilla JavaScript
- **AI:** OpenAI API (GPT-4o-mini)
- **PDF Generation:** ReportLab

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/Raneshsharma/EliteStack.git
cd EliteStack
```

### 2. Set up virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and add your values:
#   SECRET_KEY=your-secret-key
#   OPENAI_API_KEY=sk-your-openai-key
```

Generate a secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Run migrations & start server

```bash
python manage.py migrate
python manage.py runserver
```

Open **http://localhost:8000** in your browser.

### 5. (Optional) Create a superuser

```bash
python manage.py createsuperuser
```
Then access the admin panel at `/admin/` to manage users and subscription tiers.

## Deploy

### Render (Recommended — free tier)

1. Connect your GitHub repo at [render.com](https://render.com)
2. Create a **Web Service** with:
   - **Build Command:** `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
   - **Start Command:** `gunicorn placement_copilot.wsgi:application`
3. Add environment variables from `.env` (set `DEBUG=False`, add a real `SECRET_KEY`, configure PostgreSQL)
4. Create a **PostgreSQL** database on Render and update `DATABASE_*` vars

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Django secret key | Yes |
| `DEBUG` | `True` or `False` | Yes |
| `ALLOWED_HOSTS` | Comma-separated hostnames | Yes |
| `OPENAI_API_KEY` | Your OpenAI API key | Yes (for AI features) |
| `OPENAI_MODEL` | OpenAI model (`gpt-4o-mini` default) | No |
| `DATABASE_ENGINE` | `sqlite` or `postgresql` | No |
| `DATABASE_NAME` | PostgreSQL database name | If using PostgreSQL |
| `DATABASE_USER` | PostgreSQL username | If using PostgreSQL |
| `DATABASE_PASSWORD` | PostgreSQL password | If using PostgreSQL |
| `EMAIL_HOST` | SMTP host (e.g. `smtp.gmail.com`) | If sending email |

## Project Structure

```
placement_copilot/   Django project settings
accounts/            User auth, profiles, portfolio
resumes/              Resume models, views, AI endpoints
ai/                   AI services, rate limiter, salary data
templates/            Django HTML templates
static/css/           Stylesheets
```

## Running Tests

```bash
python manage.py test accounts.tests resumes.tests
```

143 tests covering models, views, APIs, authentication, and AI features.

## License

MIT
