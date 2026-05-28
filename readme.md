# Real-Time Chat Application

A real-time chat application with online status indicators built with Django, WebSockets, and PostgreSQL.

## Features

- 💬 Real-time messaging using WebSockets
- 🟢 Online/Offline user status
- 📝 User authentication (login/register)
- 💾 Message history
- 📱 Responsive design

## Tech Stack

- Backend: Django, Django Channels
- Database: PostgreSQL (production) / SQLite (development)
- Real-time: WebSockets, Redis
- Frontend: HTML, CSS, JavaScript

## Local Development

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `.\venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`
7. Run server: `python manage.py runserver`

## Deployment

This app is configured for deployment on Render.com with PostgreSQL and Redis support.

## Live Demo

[ its URL will be here after deployment]

## License

blogs-after-code 