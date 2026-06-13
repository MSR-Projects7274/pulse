> ## ⚠️ Important Note
>
> The first commit for this project is considerably larger than would typically be expected.
>
> During the early stages of development, a widely reported Remote Code Execution (RCE) vulnerability affecting a tool used within the development workflow was publicly disclosed. As a precautionary measure, commits and asset uploads were temporarily delayed until guidance and updates relating to the issue became available.
>
> Development of the project continued during this period; however, work was intentionally withheld from the repository until it was deemed appropriate to resume normal commit practices.
>
> As a result, the initial commit contains a substantial amount of functionality and project assets that would ordinarily have been distributed across multiple smaller commits.
>
> This approach was taken to prioritise security-conscious development practices and ensure the project repository remained unaffected during the period of uncertainty surrounding the reported vulnerability.

# Pulse

---

## Project Overview

Pulse is a Reddit-style discussion platform developed using Django. The application enables users to create posts, participate in discussions through comments, and engage with content shared by other members of the community.

The project demonstrates the use of Django's Model-View-Template (MVT) architecture, user authentication, database management, and full CRUD functionality.

---

## Features

### User Authentication

* User registration
* User login and logout
* Authentication-protected actions
* User account management

### Posts

* Create posts
* View community posts
* Edit existing posts
* Delete posts
* Dedicated post detail pages

### Comments

* Add comments to posts
* Edit comments
* Delete comments
* Community discussion functionality

### Security

* Django authentication system
* CSRF protection
* Permission-based content management
* Secure form handling and validation

---

## Technologies Used

### Backend

* Python
* Django

### Frontend

* HTML5
* CSS3
* Django Templates

### Database

* SQLite

### Version Control

* Git
* GitHub

---

## Installation

### Clone the Repository

```bash
git clone <repository-url>
cd pulse
```

### Create a Virtual Environment

```bash
python -m venv venv
```

#### Windows

```bash
venv\Scripts\activate
```

#### macOS / Linux

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Apply Database Migrations

```bash
python manage.py migrate
```

### Create an Administrator Account (Optional)

```bash
python manage.py createsuperuser
```

### Run the Development Server

```bash
python manage.py runserver
```

Navigate to:

```text
http://127.0.0.1:8000/
```

---

## Project Structure

```text
pulse/
│
├── accounts/
├── posts/
├── comments/
├── templates/
├── static/
├── media/
├── manage.py
├── db.sqlite3
└── requirements.txt
```

---

## Future Improvements

Potential future enhancements include:

* Upvote and downvote functionality
* User profile customisation
* Community creation and moderation tools
* Search functionality
* Post categories and tags
* User notifications
* Dark mode support
* Enhanced media uploads

---

## Learning Outcomes

This project demonstrates knowledge and practical application of:

* Django project architecture
* Model-View-Template (MVT) design
* User authentication and authorisation
* Database relationships
* CRUD operations
* Template inheritance
* Static file management
* Form validation
* Git version control workflows

---

## Acknowledgements

This project was developed for educational and portfolio purposes using:

* Python
* Django
* HTML5
* CSS3
* Git
* GitHub

---

## License

This project is provided for educational and portfolio purposes only.
