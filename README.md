# 🎓 Digital Assessment Platform

A **comprehensive Digital Assessment Platform** built using **Django (Backend)** and **HTML, CSS, Bootstrap (Frontend)**.
This system enables educational institutions to orchestrate the full lifecycle of examinations, from digital question bank management to automated performance analytics.

---

# 📌 Features

- Student Registration
- Teacher Management
- Exam Creation
- Question Bank
- Online Exam Interface
- Automatic Result Generation
- Admin Dashboard
- Role-based Access (Admin / Teacher / Student)

---

# 🛠 Tech Stack

**Backend**

- Django
- Python

**Frontend**

- HTML
- CSS
- Bootstrap
- JavaScript

**Database**

- SQLite (development)
- PostgreSQL/MySQL (production)

---

# 📂 Project Structure

```id="n6sdh0"
online-exam-system
│
├── backend
│   ├── manage.py
│   ├── backend
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   │
│   ├── users
│   ├── students
│   ├── teachers
│   ├── exams
│   ├── questions
│   └── results
│
├── templates
│
├── static
│   ├── css
│   ├── js
│   └── images
│
├── docs
│   ├── SRS.pdf
│   ├── MRD.pdf
│   ├── ERD
│   └── DFD
│
├── requirements.txt
└── README.md
```

---

# ⚙️ Project Setup (For Team Members)

## 0️⃣ Prerequisites

Ensure you have the following installed on your machine:

- **Python** (version 3.8 or higher)
- **Git**

## 1️⃣ Clone Repository

```bash id="s1zzs1"
git clone https://github.com/Yusuf8856/online-exam-system.git
```

Move into the project directory:

```bash id="t9jpk6"
cd online-exam-system
```

---

## 2️⃣ Create Virtual Environment

```bash id="f0d1y0"
python -m venv venv
```

Activate it:

### Windows

```bash id="7sj62r"
venv\Scripts\activate
```

### Linux / Mac

```bash id="ojhdri"
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash id="40vfj9"
pip install -r requirements.txt
```

---

## 4️⃣ Run Migrations

```bash id="dc5uea"
cd backend
python manage.py migrate
```

---

## 5️⃣ Start Development Server

```bash id="fcf70t"
python manage.py runserver
```

Open browser:

```id="dd2g1q"
http://127.0.0.1:8000
```

---

# 👥 Git Workflow (Team Development)

⚠️ **Direct push to `main` is not allowed.**

Follow these steps:

### Pull latest code

```bash id="ik3jsg"
git pull origin main
```

---

### Create a new branch

```bash id="e6g4s3"
git checkout -b your-module-name
```

Example:

```bash id="bjq7cr"
git checkout -b students-module
```

---

### Work on your module

After changes:

```bash id="w2ftv5"
git add .
git commit -m "Added students module"
```

---

### Push branch

```bash id="wglr9t"
git push origin students-module
```

---

### Create Pull Request on GitHub

1. Go to repository
2. Click **Compare & Pull Request**
3. Request review
4. Merge into `main`

---

# 📦 Project Modules

| Module    | Description                      |
| --------- | -------------------------------- |
| Users     | Authentication & role management |
| Students  | Student profiles                 |
| Teachers  | Teacher profiles                 |
| Exams     | Exam creation & scheduling       |
| Questions | Question bank                    |
| Results   | Result calculation               |

---

# 🔄 System Architecture (DFD)

### Level 0: Context

- **Students**: Submit attempts, receive results.
- **Teachers**: Manage students, create exams, analyze performance.
- **Admins**: Oversight and system configuration.

### Level 1: Core Processes

1. **Identity & Access**: Role-based redirection (Student/Teacher/Admin).
2. **Content Orchestration**: Management of Exams and Question banks.
3. **Execution Engine**: Real-time randomized exam delivery and capture.
4. **Analytics Pipeline**: Automated grading and report generation.

---

# 📊 Database Schema (ERD)

- **User ↔ Profile**: 1:1 Relationship (Role management).
- **Exam ↔ Question**: 1:N Relationship (Content structure).
- **Exam/Student ↔ Result**: N:M through Result (Performance tracking).

---

# � Documentation

All project documentation is stored in:

```id="r0pqhy"
docs/
```

Includes:

- SRS (Software Requirements Specification)
- MRD (Market Requirements Document)
- ER Diagram
- DFD Diagrams

---

# 👨‍💻 Contributors

Project Team – Online Examination System

---

# 📄 License

This project is developed for **educational purposes**.

---
