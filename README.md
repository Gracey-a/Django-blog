# Elegant Django Blog

A feature‑rich blog platform built with Django, featuring user authentication, rich text editor, image uploads, categories, tags, comments, likes, and a magazine‑style responsive design.

## Features
- User registration, login, logout, profiles
- Create, edit, delete posts (with draft & publish)
- Schedule posts for future publication
- Soft delete (trash) and restore
- Image upload for posts and avatars
- Categories, tags, and search
- Comments with delete permission
- Like system showing who liked
- Dark/light mode toggle
- Magazine‑style homepage with 2‑column grid

## Setup
1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install: `pip install -r requirements.txt`
5. Migrate: `python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`
7. Run: `python manage.py runserver`	
