# Quip-Order - Occupational Therapy Management System

## 📋 Project Overview

**Quip-Order** is a comprehensive Full-Stack Django web application designed for occupational therapists in NHS/Private Practice s to efficiently manage:

- Equipment ordering and inventory tracking
- Role-based access control (Therapists vs Patients)

### 🎯 Project Purpose
This system streamlines the workflow for occupational therapists by providing:
- Centralized patient management
- Equipment request and approval workflows
- Real-time caseload monitoring
- Secure, role-based access to sensitive medical information

## Tech Stack
- **Backend:** Python 3.11+, Django 4.2+
- **Database:** PostgreSQL
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Authentication:** Django Allauth with OAuth2
- **Deployment:** Render/Heroku
- **Version Control:** Git with conventional commits

## Setup Instructions

### Prerequisites
- Python 3.11+
- PostgreSQL
- Git

### Installation Steps

#### 1. Clone the Repository
```
git clone https://github.com/yourusername/quip-order.git
cd quip-order
```

#### 2. Create Virtual Environment
```
# Create isolated Python environment
python -m venv venv

# Activate it
# On Mac/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install django
django-admin startproject quipster .
python manage.py startapp users
python manage.py startapp equipment
python manage.py startapp dashboard
```

### Install Dependencies
```
pip install -r requirements.txt
.env
```

### Project Structure
```
quip-order/
│
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── README.md                # This file      
│
└── quiporder/             # Main project configuration
│   │
│   └── __pycache__/       # Tracks database changes
│        └── __init__.cpython-313.pyc
│   ├── __init__.py        # Tells Python this is a package
│   ├── asgi.py            # For async servers 
│   ├── settings.py        # Project settings
│   ├── urls.py            # URL routing
│   └── wsgi.py            # For deploying to web servers
│
└──users/                  # User management app
│  │
   └── migrations/          # Tracks database changes
        └── __init__.py
    │
    ├── __init__.py          # Makes this a Python package
    ├── admin.py             # Register models to appear in admin panel 
    ├── apps.py              # App configuration
    ├── models.py            # Database tables (User, Therapist, Patient)
    ├── tests.py             # Test code goes here
    ├── views.py             # Authentication views

└── equipment/               # Equipment management app
│   ├── models.py            # Equipment, Order models
│   ├── views.py             # CRUD operations
│   ├── forms.py             # Django forms
│   └── tests.py             # Equipment tests
│
└── dashboard/               # Dashboard app
    ├── views.py             # Role-based dashboards
    └── tests.py             # Dashboard tests
    

```