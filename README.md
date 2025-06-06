# SmartCVSystem

Welcome to SmartCV System Repo

# 📘 SmartCVSystem

A Django-powered candidate–job matching platform using MySQL. It parses digital CVs, matches skills & experience to roles, and provides basic fit-reports.

---

## 🛠️ Tech Stack

| Layer / Concern   | Technology                                            |
| ----------------- | ----------------------------------------------------- |
| **Framework**     | Django 4 (on Python 3.8 +)                            |
| **Database**      | MySQL 8                                               |
| **File Storage**  | Amazon S3 (object storage for uploaded CVs & reports) |
| **Cloud Hosting** | AWS (e.g., Elastic Beanstalk / EC2 / ECS)             |
| **CI / VCS**      | Git & GitHub                                          |

---

## 🚀 Features

1. **Resume Parsing**  
   Automatically extracts skills, experience, and education from uploaded CVs.
2. **Candidate–Role Matching**  
   Algorithmic matching based on keyword analysis and weightings.
3. **Secure Data Storage**  
   All applicant and match data encrypted at rest in MySQL.
4. **Fit Reports**  
   Simple downloadable summaries of match scores.

---

## 📥 Prerequisites

- Python 3.8+
- MySQL server (local or remote)
- `virtualenv` or `venv`

---

## ⚙️ Installation & Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/your-username/SmartCVSystem.git
   cd SmartCVSystem
   ```

## 📂 Suggested Django Project Layout

_Each top-level package maps directly to the functional modules in your design._

```text
SmartCVSystem/
├── manage.py
├── requirements.txt
├── .env.example
├── config/                  # Django project settings & root URLs
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── authx/               # Authentication & Authorization
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── profiles/            # User & Profile Management
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── resumes/             # CV Upload, Storage & Parsing
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── services/
│   │   │   └── parser.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── repository/          # Search & Filtering
│   │   ├── migrations/
│   │   ├── search.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── jobposts/            # Job Postings Management
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── matching/            # Candidate Scoring
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── rules.py
│   │   └── views.py
│   ├── shortlist/           # Shortlisting Panel
│   │   ├── migrations/
│   │   ├── models.py
│   │   └── views.py
│   └── common/              # Reusable utilities
│       ├── mixins.py
│       └── validators.py
├── templates/               # Global base templates (per-app templates live inside each app)
│   └── base.html
└── static/                  # Global static assets


python manage.py startapp authx apps/authx
python manage.py startapp profiles apps/profiles
python manage.py startapp resumes    apps/resumes
python manage.py startapp repository apps/repository
python manage.py startapp jobposts   apps/jobposts
python manage.py startapp matching   apps/matching
python manage.py startapp shortlist  apps/shortlist
python manage.py startapp dashboard  apps/dashboard
python manage.py startapp common     apps/common

## After clone

# 1. Clone the repo (if they haven’t already)
git clone https://github.com/your-username/SmartCVSystem.git
cd SmartCVSystem

# 2. Create a Python virtual environment
#    (Use `python3` on macOS/Linux or just `python` on Windows if that’s your default)
python -m venv .venv

# 3. Activate the virtual environment
#    On macOS / Linux:
source .venv/bin/activate
#    On Windows (PowerShell):
.venv\Scripts\Activate.ps1
#    On Windows (CMD):
.venv\Scripts\activate.bat

# 4. Upgrade pip (optional, but recommended)
pip install --upgrade pip

# 5. Install all required libraries
pip install -r requirements.txt

# 6. Copy the example env file and fill in any secrets
cp .env.example .env          # macOS / Linux
copy .env.example .env        # Windows CMD
# — then open `.env` in your editor and add your DB credentials, SECRET_KEY, AWS keys, etc.

# 7. Apply migrations & create a superuser
python manage.py migrate
python manage.py createsuperuser

# 8. Run the dev server
python manage.py runserver
```

## 🐳 Running with Docker

1. **Build and start the containers**

   ```bash
   docker compose up --build
   ```

2. **Apply migrations and create a superuser**
   Open a new terminal and run:

   ```bash
   # if you have any new models
   docker compose exec web python manage.py makemigrations <model_name>
   docker compose exec web python manage.py migrate
   docker compose exec web python manage.py createsuperuser
   ```

3. **Access the app**

   - The web app will be available at [http://localhost:8000](http://localhost:8000)
   - The Django admin at [http://localhost:8000/admin](http://localhost:8000/admin)

4. **Stopping the containers**
   Press `Ctrl+C` in the terminal running Docker Compose, or run:
   ```bash
   docker compose down
   ```
5. **Create new app**
   Open a new terminal and run:

   ```bash
   docker compose exec web python manage.py startapp <app_name> apps/<app_name>
   ```
**Note:**
Make sure your `.env` file is configured with the correct database and AWS credentials before starting the containers.
