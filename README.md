# Pulse – Django Discussion Platform

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![Status](https://img.shields.io/badge/Status-Complete-success)
![Framework](https://img.shields.io/badge/Backend-Django%20MVT-lightgrey)

---

## ⚠️ Important Note

The first commit for this project is considerably larger than would typically be expected.
During the early stages of development, a widely reported Remote Code Execution (RCE) vulnerability affecting a tool within the development ecosystem was disclosed. As a precautionary measure, commits and asset uploads were temporarily delayed until the situation stabilised and it was considered safe to resume normal repository activity.
Development of the project itself continued during this time; however, changes were intentionally withheld from the repository to avoid committing work during a period of uncertainty.
As a result, the initial commit contains a substantial portion of the project that would normally have been distributed across multiple incremental commits.
This approach was taken to maintain a security-conscious and responsible development workflow.

---

## Table of Contents

- Overview
- Purpose
- Features
- Built With
- Project Structure
- Installation
- User Features
- Security
- Development Challenges
- Lessons Learned
- Future Improvements
- Credits

---

## Overview

Pulse is a Reddit-style discussion platform built using Django.

It allows users to create posts, comment on content, and interact within a structured community environment.

The project focuses on backend architecture, authentication systems, and full CRUD-based interaction between users and content.

---

## Purpose

This project was developed to:

- Practise Django MVT architecture
- Implement full user authentication flows
- Build a relational database-backed application
- Develop CRUD-based interaction systems
- Explore real-world forum-style application design

---

## Features

- User registration and authentication
- Secure login and logout system
- Create, edit, and delete posts
- Commenting system on posts
- User-owned content permissions
- Timestamp tracking for posts and comments
- Protected routes for authenticated users only
- Clean template-based UI structure

---

## Built With

- **Python** – Core backend logic
- **Django** – Web framework (MVT architecture)
- **HTML5** – Template structure
- **CSS3** – Styling and layout
- **SQLite** – Development database

---

## Project Structure

```
pulse/
├── accounts/
├── posts/
├── comments/
├── templates/
├── static/
├── db.sqlite3
├── manage.py
└── requirements.txt
```

---

## Viewing the Site Locally

Clone Repository

```bash
git clone <repository-url>
cd pulse
```

Create Virtual Environment

```bash
python -m venv venv
```

Activate Environment
Windows

```bash
venv\Scripts\activate
```

macOS / Linux

```bash
source venv/bin/activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Apply Migrations

```bash
python manage.py migrate
```

Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

Run Server

```bash
python manage.py runserver
```

Open in your browser:

```
http://127.0.0.1:8000/
```

---

## User Features

- Accounts
- Register new users
- Login and logout system
- Session-based authentication
- Posts
- Create posts
- Edit and delete own posts
- View all community posts
- Individual post detail pages
- Comments
- Add comments to posts
- Edit and delete comments
- Threaded discussion support

---

## Security

- Django authentication system
- CSRF protection enabled
- Permission-based access control
- Secure form validation
- Route protection for authenticated users

---

## Development Challenges

<details>
<summary>Click to expand development challenges</summary>

| Challenge | Issue | Resolution |
|-----------|------|-----------|
| Multi-app URL routing conflicts | Overlapping `urls.py` patterns between apps caused incorrect route matching and occasional 404 errors | Separated URL configurations per app using `include()` and enforced consistent URL namespaces |
| URL namespace and reverse lookup issues | `reverse()` and `{% url %}` sometimes resolved to the wrong view due to missing or inconsistent namespaces | Standardised `app_name` declarations and refactored URL naming conventions across all apps |
| Shell / model import issues | Django shell could not reliably import models due to incorrect import paths or early app loading issues | Fixed import paths, ensured proper app registration, and used fully qualified model references where needed |
| App registration and load order problems | Certain apps/models were unavailable during migrations or shell sessions due to incorrect `INSTALLED_APPS` ordering | Reordered `INSTALLED_APPS` and validated inter-app dependencies before migration                            |
| Migration dependency conflicts | Cross-app foreign keys caused migrations to fail or apply in incorrect order | Rebuilt migration chain where necessary and explicitly defined migration `dependencies` |
| Template resolution errors across apps | Django failed to consistently locate templates due to inconsistent folder structure | Standardised template structure using `templates/<app_name>/` and ensured `APP_DIRS = True` |
| Authentication flow inconsistencies| Login/logout sessions behaved unpredictably across different views and redirects | Unified authentication flow, standardised middleware usage, and fixed redirect handling logic |

</details>
---

## Lessons Learned

Django project structure depends heavily on correct app configuration
URL routing requires careful namespace management
Model changes must be migrated carefully to avoid state mismatches
Django shell is essential for backend debugging
Authentication flows must be tested end-to-end early

---

## Future Improvements

Potential future improvements include:

- User profiles with avatars
- Notification system
- Rich text editor for posts
- Image uploads
- Moderation tools

---

## Credits

- **Favicons:** [Favicon.io](Favicon.io)
- **Bug fixes and advice:** ChatGPT provided guidance, code extracts and troubleshooting support
- **Favicon Design:** [Perchance.org](https://perchance.org/ai-text-to-image-generator)
