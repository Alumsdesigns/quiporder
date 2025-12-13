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

### Initial Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install django
django-admin startproject quipster .
python manage.py startapp users
python manage.py startapp equipment
python manage.py startapp dashboard