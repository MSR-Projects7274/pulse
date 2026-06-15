Pulse – Django Discussion Platform
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)
![Status](https://img.shields.io/badge/Status-Complete-success)
![Framework](https://img.shields.io/badge/Backend-Django%20MVT-lightgrey)
---
⚠️ Important Note
The first commit for this project is considerably larger than would typically be expected.
During the early stages of development, a widely reported Remote Code Execution (RCE) vulnerability affecting a tool within the development ecosystem was disclosed. As a precautionary measure, commits and asset uploads were temporarily delayed until the situation stabilised and it was considered safe to resume normal repository activity.
Development of the project itself continued during this time; however, changes were intentionally withheld from the repository to avoid committing work during a period of uncertainty.
As a result, the initial commit contains a substantial portion of the project that would normally have been distributed across multiple incremental commits.
This approach was taken to maintain a security-conscious and responsible development workflow.
---
Table of Contents
Overview
Purpose
Features
Built With
Project Structure
Installation
User Features
Security
Development Challenges
Lessons Learned
Future Improvements
Credits
---
Overview
Pulse is a Reddit-style discussion platform built using Django.
It allows users to create posts, comment on content, and interact within a structured community environment.
The project focuses on backend architecture, authentication systems, and full CRUD-based interaction between users and content.
---
Purpose
This project was developed to:
Practise Django MVT architecture
Implement full user authentication flows
Build a relational database-backed application
Develop CRUD-based interaction systems
Explore real-world forum-style application design
---
Features
User registration and authentication
Secure login and logout system
Create, edit, and delete posts
Commenting system on posts
User-owned content permissions
Timestamp tracking for posts and comments
Protected routes for authenticated users only
Clean template-based UI structure
---
Built With
Python – Core backend logic
Django – Web framework (MVT architecture)
HTML5 – Template structure
CSS3 – Styling and layout
SQLite – Development database
Git & GitHub – Version control
---
Project Structure
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
Installation
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
User Features
Accounts
Register new users
Login and logout system
Session-based authentication
Posts
Create posts
Edit and delete own posts
View all community posts
Individual post detail pages
Comments
Add comments to posts
Edit and delete comments
Threaded discussion support
---
Security
Django authentication system
CSRF protection enabled
Permission-based access control
Secure form validation
Route protection for authenticated users
---
Development Challenges
Handling Django URL routing conflicts in multi-app structure
Resolving shell/model import issues during early database testing
Managing template resolution errors across apps
Ensuring correct app registration and migration order
Debugging authentication flow inconsistencies
---
Lessons Learned
Django project structure depends heavily on correct app configuration
URL routing requires careful namespace management
Model changes must be migrated carefully to avoid state mismatches
Django shell is essential for backend debugging
Authentication flows must be tested end-to-end early
---
Future Improvements
User profiles with avatars
Post categories and tagging system
Notification system
Rich text editor for posts
Image uploads
Moderation tools
---
Credits
Django Documentation
Python Software Foundation
GitHub (version control)
ChatGPT (debugging support, structure guidance, and development assistance)