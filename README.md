# Online Examination System

A full-stack **Online Examination System** built using **Django (Backend)** and **HTML, CSS, Bootstrap (Frontend)**.
The system allows administrators, teachers, and students to manage and participate in online exams.

---

# Project Structure

```
online-examination-system
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
│   └── diagrams
│
├── requirements.txt
└── README.md
```

---

# Prerequisites

Make sure you have the following installed:

- Python **3.10+**
- Git
- pip

Check versions:

```bash
python --version
git --version
```

---

# Step 1: Clone the Repository

```bash
git clone https://github.com/Yusuf8856/online-exam-system.git
```

Move into the project directory:

```bash
cd online-exam-system
```

---

# Step 2: Create Virtual Environment

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

### Windows

```bash
venv\Scripts\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

---

# Step 3: Install Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

If requirements file does not exist:

```bash
pip install django
```

---

# Step 4: Go to Backend Folder

```bash
cd backend
```

---

# Step 5: Run Database Migration

```bash
python manage.py migrate
```

---

# Step 6: Run Development Server

```bash
python manage.py runserver
```

Server will start at:

```
http://127.0.0.1:8000
```

---

# Project Modules

| Module    | Description                   |
| --------- | ----------------------------- |
| Users     | Authentication and user roles |
| Students  | Student management            |
| Teachers  | Teacher management            |
| Exams     | Exam creation and scheduling  |
| Questions | Question bank                 |
| Results   | Result calculation            |

---

# Git Workflow for Team Members

Always pull the latest code first:

```bash
git pull origin main
```

Create a new branch for your task:

```bash
git checkout -b feature-name
```

Example:

```
git checkout -b student-module
```

After completing your work:

```bash
git add .
git commit -m "Added student module"
git push origin student-module
```

Create a **Pull Request** on GitHub.

---

# Team Task Assignment

| Member | Responsibility |
| ------ | -------------- |

---

# Static Files

Static assets are stored in:

```
static/
```

Example:

```
static/css
static/js
static/images
```

---

# Templates

All frontend pages are located in:

```
templates/
```

Example pages:

```
login.html
dashboard.html
exam.html
result.html
```

---

# Documentation

Project documentation is available in:

```
docs/
```

Includes:

- SRS
- MRD
- ER Diagram
- DFD

---

# Running the Project

Final command to run the project:

```bash
python manage.py runserver
```

Then open:

```
http://127.0.0.1:8000
```

---

# Contributors

Project Team – Online Examination System

---
