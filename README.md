# Hostel Leave Management System

A professional hostel leave management system built using Django and MySQL.

Students can apply for leave requests, and approvals flow through Proctor → HOD (optional) → Rector.

---

# Features

- Student Registration & Login
- Rector Verification for Students
- Apply Leave Form
- Leave Tracking System
- Multi-Level Approval Workflow
- Proctor Dashboard
- HOD Dashboard
- Rector Dashboard
- Parent Notification System
- Leave History
- Session-Based Authentication
- Hostel-wise Access Control

---

# Approval Workflow

1. Student submits leave request
2. Request goes to Proctor
3. If Proctor approves:
   - Request goes directly to Rector
4. If Proctor forwards:
   - Request goes to HOD
5. HOD approves/rejects
6. Final approval handled by Rector

---

# Tech Stack

## Backend
- Django
- Python

## Frontend
- HTML
- CSS
- JavaScript

## Database
- MySQL

---

# Project Structure

leaveform/
│
├── leaveform/           # Main project settings
├── students/            # Main application
├── templates/           # HTML templates
├── static/              # CSS/JS/Images
├── requirements.txt
├── manage.py
├── .env
└── README.md# Hostel Leave Management System

# Installation Guide

## 1. Clone Repository

```bash
git clone https://github.com/Devsmita30/hostelleavemanagement.git
cd hostelleavemanagement
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv env
env\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv env
source env/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Create MySQL Database

Open MySQL and run:

```sql
CREATE DATABASE leave_management;
```

---

## 5. Create `.env` File

Create a `.env` file in root folder:

```env
SECRET_KEY=your-secret-key

DB_NAME=leave_management
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=3306
```

---

## 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 7. Start Development Server

```bash
python manage.py runserver
```

Open browser:

```text
http://127.0.0.1:8000/
```