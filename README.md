# TwoHobby app


<img width="2048" height="762" alt="My First Board (1)" src="https://github.com/user-attachments/assets/52fb7127-198d-46bc-8a90-e1c243f22ce0">



# TwoHobby – Social & Dating Platform

## Overview

**TwoHobby** is a modern social and dating web application built with Django.  
The platform allows users to create profiles, upload images, browse other users, and communicate in real-time through chat and voice features.

The project focuses on:
- Real-time communication
- Modern responsive UI
- Media optimization
- Scalable Django architecture
- WebSocket integration
- Cloud-based media storage

---

# Features

## User Authentication
- User registration and login
- Secure authentication using Django Allauth
- Profile management
- Logout functionality

## User Profiles
- Profile image uploads
- Custom bio and personal information
- Age, location, and interests
- Responsive mobile-friendly profile cards

## Real-Time Chat
- WebSocket-powered messaging
- Django Channels integration
- Instant message updates
- Private chat rooms

## Voice & Call Features
- WebRTC voice communication
- Echo cancellation support
- Noise suppression
- Real-time audio streaming

## Media Handling
- Cloudinary integration
- Automatic image optimization
- WebP image support
- Reduced bandwidth usage

## Responsive Design
- Mobile-first layout
- Tinder/Badoo-inspired interface
- Optimized for Android and iPhone
- Dynamic grid system

---

# Technologies Used

## Backend
- Python
- Django
- Django Channels
- Daphne
- Redis

## Frontend
- HTML5
- CSS3
- JavaScript
- WebSockets
- WebRTC

## Database
- PostgreSQL

## Media & Deployment
- Cloudinary
- Heroku
- WhiteNoise

---

# Project Structure

```bash
twohobby/
│
├── chat/
├── profiles/
├── static/
├── templates/
├── media/
├── config/
│
├── manage.py
├── requirements.txt
├── Procfile
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/twohobby.git
cd twohobby
```

---

## Create Virtual Environment

```bash
python -m venv .venv
```

Activate virtual environment:

### Windows

```bash
.venv\Scripts\activate
```

### Mac/Linux

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create an `env.py` file or use Heroku Config Vars.

Example:

```python
import os

os.environ.setdefault("SECRET_KEY", "your_secret_key")
os.environ.setdefault("DATABASE_URL", "your_database_url")
os.environ.setdefault("CLOUDINARY_URL", "your_cloudinary_url")
os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:6379")
```

---

# Database Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

---

# Create Superuser

```bash
python manage.py createsuperuser
```

---

# Running the Project

## Local Development

```bash
python manage.py runserver
```

## WebSocket Server

```bash
daphne config.asgi:application
```

---

# Redis Setup

## Using Podman

```bash
podman run -d \
  --name redis \
  -p 6379:6379 \
  docker.io/library/redis
```

---

# Deployment

The application is deployed using:
- Heroku
- Cloudinary
- PostgreSQL

## Heroku Deployment

```bash
heroku login
heroku create your-app-name
git push heroku main
```

---

# WebSocket Architecture

```text
Client
   ↓
WebSocket Connection
   ↓
Django Channels
   ↓
Redis Channel Layer
   ↓
Connected Users
```

---

# Security Features

- CSRF protection
- Secure authentication
- User validation
- Private chat access control
- Protected WebSocket connections

---

# Future Improvements

- Video calls
- Matching system
- AI translation
- Push notifications
- Advanced search filters
- User verification
- Voice message translation
- Mobile application release

---

# Testing

## Manual Testing
- Authentication testing
- Chat functionality testing
- Mobile responsiveness
- Image upload validation
- WebRTC audio testing

## Code Quality
- PEP8 validation
- Django system checks
- Responsive UI testing

---

# Credits

## Frameworks & Libraries
- Django
- Django Channels
- Redis
- Cloudinary
- WebRTC

## Inspiration
- Badoo
- Tinder
- Modern social networking platforms

---

# Author

**Azamat**

- Full Stack Developer
- Django & Python Enthusiast
- Real-Time Communication Systems

---

# License

This project is for educational and portfolio purposes.
