# 🎓 Eventory - Campus Event Reporting System

## 📌 Project Overview

This project is a simple **Campus Event Management & Reporting System** designed as to monitor event registrations.

It simulates a real-world platform where:

- **Admins (College Staff)** can create and manage events.  
- **Students** can browse events, register, check-in on the day, and provide feedback.  

The main agenda of this system is **event reporting**, analyzing registrations, attendance, and feedback for meaningful insights.

---

## 🚀 Features Implemented

### Event Management
- Create and manage events (workshops, seminars, hackathons, fests and Techtalks).

### Student Interaction
- Register students for events.  
- Mark attendance.  
- Collect event feedback and rate event (1–5)

### Reports & Analytics
- 📊 Event Popularity Report (sorted by registrations).  
- 📊 Student Participation Report (events attended per student).  
- 📊 Attendance percentage per event.  
- 📊 Average feedback score per event.  
- ⭐ Bonus: Top 3 Most Active Students.  

---

## 🏗️ System Design

### Data to Track
- Event details (ID, name, type, college, date).  
- Student details (ID, name, college).  
- Registrations (event ↔ student).  
- Attendance records.  
- Feedback (rating).  

---

## 🔌 API Endpoints

### Event APIs
- `POST /events` → Create a new event.  
- `GET /events` → List all events.  

### Student APIs
- `POST /students` → Register a new student.  
- `GET /students/{id}` → Get student details.  

### Registration APIs
- `POST /events/{event_id}/register` → Register student to an event.  
- `GET /events/{event_id}/registrations` → Get all registrations.  

### Attendance APIs
- `POST /events/{event_id}/attendance` → Mark student attendance.  
- `GET /events/{event_id}/attendance` → Attendance report for event.  

### Feedback APIs
- `POST /events/{event_id}/feedback` → Submit feedback.  
- `GET /feedbacks` → Get feedback summary.  

### Reports APIs
- `GET /reports/event-popularity` → Registrations per event.  
- `GET /reports/student-participation` → Events attended per student.  
- `GET /reports/top-students` → Top 3 active students.  

---

## 🔄 Workflows

### Event Lifecycle
Admin creates event → Students browse & register → Attendance taken on event day → Students submit feedback → Reports generated.  

### Reporting Flow
Registration data → Attendance records → Feedback → Aggregated into event & student reports.  

---

## ⚙️ Tech Stack
- **Backend:** Python (Django / REST Framework)  
- **Database:** SQLite 
- **API Testing:** Postman 

---
## 📂 Project Structure
```

campus-event-reporting/
│── src/
│   ├── app.py               # Main app
│   ├── models.py            # Database models
│   ├── routes/              # API endpoints
│   └── utils/               # Helper functions
│── docs/
│   ├── design\_doc.md        # ER diagram, workflows
│   └── reports/             # Sample reports/screenshots
│── requirements.txt         # Dependencies
│── README.md                # This file

backend/
├── manage.py
├── requirements.txt
├── .venv
├── eventory/                # Main app
│ ├── __init__.py
│ ├── asgi.py
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
└── events/                  # App
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
│ └── __init__.py
├── models.py               # Database models
├── serializer.py
├── urls.py
├── views.py                # API endpoints
├── permissions.py
├── reports.py
├── tests.py
│── docs/
│   ├── API_Doc.md          # API endpoints
|   ├── database.dbml       # Database representation code
│   └── reports/            # Sample reports/screenshots
│── requirements.txt        # Dependencies
│── README.md               # This file

````

---

## ▶️ Setup & Run Instructions

**Clone Repo**
```bash
git clone <repo_url>
cd eventory
````

**Setup Environment**

```bash
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)
```

**Install Dependencies**

```bash
pip install -r requirements.txt
```

**Run App**

```bash
python manage.py runserver
```

**Test APIs**
Use Postman or curl to test endpoints.

---

## 📌 Assumptions

* Each student is uniquely identified across the system.
* Event IDs are unique per college.
* One student can attend multiple events.
* Feedback is optional, but if given, only once per student per event.
* Scale assumption: \~50 colleges × 500 students × 20 events per semester.

---