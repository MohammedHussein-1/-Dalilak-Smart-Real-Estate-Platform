# دليلك – منصة عقارية ذكية | Dalilak – Smart Real Estate Platform

> مشروع تخرج – أكاديمية الشروق، كلية نظم معلومات ، 2025–2026 | Project #45

---

## Features

- 🏠 Property browsing and filtering (buy / rent)
- 🗺️ Interactive map powered by Leaflet.js
- 🤖 AI chatbot — Gemini API with local rule-based fallback
- 👤 User authentication (login / signup)
- 📋 Admin dashboard — approve / reject listings and verify identities
- 📸 Property image uploads
- 🔖 Save favourite properties
- 🌙 Dark mode + bilingual UI (Arabic / English)
- ✅ National ID verification

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11+, Flask 3.0 |
| ORM | Flask-SQLAlchemy 3.1, SQLAlchemy 2.0 |
| Auth | Flask-Login 0.6 |
| Database | SQLite |
| Frontend | Jinja2, Tailwind CSS (CDN) |
| Maps | Leaflet.js |
| AI (Primary) | Google Gemini API (`google-generativeai`) |
| AI (Fallback) | Local `RealEstateChatbot` in `chatbot.py` |
| Config | python-dotenv |
| Security | Werkzeug 3.0 |

---

## Directory Structure

```
├── app.py                  # Main Flask app and all routes
├── chatbot.py              # Local fallback chatbot (rule-based)
├── models.py               # SQLAlchemy models
├── data.py                 # Mock property data
├── requirements.txt        # Python dependencies
├── reset_db.py             # DB reset and seed utility
├── .env.example            # Environment variables template
├── database/
│   ├── schema.sql
│   └── seed_data.sql
├── static/
│   ├── uploads/            # User-uploaded property images
│   └── js/translations.js  # AR/EN i18n strings
└── templates/
    ├── base.html
    ├── home.html
    ├── map.html
    ├── property.html
    ├── submit_property.html
    ├── auth.html
    ├── profile.html
    ├── my_listings.html
    ├── admin.html
    └── verify.html
```

---

## Local Setup

### 1. Prerequisites

- Python 3.11+
- pip

### 2. Clone and install

```bash
git clone <repo-url>
cd "RealEstate_grad MH"
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configuration

```bash
cp .env.example .env
```

Open `.env` and fill in your values:

```env
SECRET_KEY=your_strong_secret_key_here
GOOGLE_API_KEY=your_gemini_api_key_here
GENAI_MODEL=gemini-1.5-flash
DATABASE_URL=sqlite:///realestate.db
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216
```

> Without `GOOGLE_API_KEY` the local fallback chatbot runs automatically.

### 4. Database Initialization

```bash
python reset_db.py
```

Creates all tables and seeds a default admin account:

| Field | Value |
|-------|-------|
| Email | `admin@example.com` |
| Password | `admin123` |

### 5. Run

```bash
python app.py
```

App is available at **http://127.0.0.1:5001**

---

## Main Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Homepage |
| `/map` | GET | Interactive property map |
| `/property/<id>` | GET | Property detail |
| `/submit-property` | GET / POST | Submit a new listing |
| `/chat` | POST | Chatbot JSON API |
| `/login` | GET / POST | Login |
| `/signup` | GET / POST | Register |
| `/profile` | GET | User profile |
| `/my-listings` | GET | User's own listings |
| `/verify` | GET | ID verification |
| `/admin` | GET | Admin dashboard (admin only) |

---

## User Roles

| Role | Permissions |
|------|-------------|
| `user` | Browse, submit listings, save favourites, verify identity |
| `admin` | All of the above + approve/reject listings, manage users |

---

## Chatbot

The chatbot works in two layers:

1. **Gemini AI** (primary) — requires `GOOGLE_API_KEY` in `.env`
2. **Local fallback** — `RealEstateChatbot` in `chatbot.py`, works with no API key

Supports search by city, listing type (buy/rent), number of bedrooms, price range, and property type. Responds in Arabic or English based on the user's input.