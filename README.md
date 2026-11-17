# Online Course (Django final project)

Django application for the IBM "Django Application Development with SQL and Databases"
final project. It implements an online course platform with lessons, multiple-choice
exams, automatic grading, and a customized Django admin site.

## Features

- Course list and course detail pages (Bootstrap)
- User registration / login / logout
- Course enrollment for authenticated users
- Mock exam built from lesson questions (`Question` / `Choice`)
- Exam submission and automatic grading (`Submission`, `show_exam_result`)
- Customized admin site with inline editing for lessons, questions, and choices

## Models

`Instructor`, `Learner`, `Course`, `Lesson`, `Enrollment`, `Question`, `Choice`, `Submission`

## Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Demo accounts:

- Admin: `admin` / `Admin12345!` (http://127.0.0.1:8000/admin/)
- Learner: `learner` / `Learner12345!`

## Screenshots

- `screenshots/03-admin-site.png` — admin site with Authentication and Authorization
  and OnlineCourse sections
- `screenshots/07-final.png` — successful mock exam result
