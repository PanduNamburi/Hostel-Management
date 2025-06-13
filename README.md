# Hostel Management System

A comprehensive hostel management system built with Django and modern web technologies.

## Features

- Role-based access control (Students, Wardens, Admins, Security Staff)
- Real-time notifications and updates
- QR code-based outing passes
- Interactive dashboards with analytics
- Mobile-responsive design
- Dark/Light mode support
- Real-time status updates

## Tech Stack

- Backend: Django 4.x
- Frontend: Tailwind CSS, Alpine.js
- Database: SQLite (default)
- Authentication: Django Custom User Model
- Real-time: Django Channels
- API: Django REST Framework

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
HostelManagement/
├── accounts/           # Custom user model and auth
├── students/           # Student-specific models and views
├── wardens/           # Warden functionalities
├── admin_panel/       # Admin controls
├── security/          # Security gate panel
├── core/              # Shared utilities, announcements
├── templates/         # Tailwind-powered templates
├── static/            # Tailwind CSS, JS, images
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. # Hostel-Management
