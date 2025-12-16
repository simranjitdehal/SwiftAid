# SwiftAID

A backend-driven hospital emergency and patient management system with role-based access control.

## Overview

SwiftAid is a role-based hospital management system designed to handle emergency requests,
patient workflows, and staff coordination.

The project focuses on backend logic, authorization, authentication and operational workflows rather than UI complexity.

## Tech Stack

**Backend**

- Python
- Django

**Database**

- SQLite3

**Frontend / Templating**

- HTML
- Jinja2
- Bootstrap
- JavaScript

## Features

- Role-based system supporting patients, hospital admins, and medical staff
- Secure authentication and authorization with role-based access control
- Emergency request submission for patients without registration using guest identifiers
- Admin workflows for request review, ambulance dispatch, bed and staff assignment, and patient discharge
- Staff dashboards to manage assigned patients and update treatment status
- Relational database models supporting request lifecycle tracking and resource availability

## Getting Started

Clone the repository and run the Django development server:

```bash
git clone https://github.com/simranjitdehal/SwiftAid
cd swiftaid
python manage.py migrate
python manage.py runserver
```

## License

[MIT](https://choosealicense.com/licenses/mit/)
