# Secure Web Application Project

## Overview
This project is a simple Flask web application developed for the Computer Security course. The application provides a basic user management system with user registration, login, dashboard access, shared comments, and an admin panel.

The project demonstrates common web security vulnerabilities and their mitigations, including SQL Injection, weak password storage, Cross-Site Scripting (XSS), broken access control, and secure handling of sensitive data.

## Features
- User registration
- User login
- User dashboard with logged-in username
- Shared comment posting section
- Admin dashboard
- Role-Based Access Control (RBAC)
- Secure password hashing using bcrypt
- XSS prevention through template escaping
- Parameterized SQL queries
- Secure session cookie settings
- Optional HTTPS local testing

## Technologies Used
- Python
- Flask
- SQLite
- HTML
- CSS
- bcrypt
- pyOpenSSL

## Project Structure

```text
Security-Project-main/
│
├── app.py
├── README.md
│
├── static/
│   └── style.css
│
└── templates/
    ├── home.html
    ├── register.html
    ├── login.html
    ├── dashboard.html
    ├── admin.html
    └── warning.html
```
## How to Run the Application

### 1. Install required packages

```bash
pip install flask bcrypt pyopenssl
```

### 2. Run the application

```bash
python app.py
```

### 3. Open the application

Open the following URL in the browser:

```text
http://127.0.0.1:5000
```

## Default Admin Account

The application automatically creates a default admin account when the application runs:

```text
Username: admin
Password: Admin@12345
```

Regular users can create their own accounts using the Register page.

## Security Features and Testing Instructions

### 1. SQL Injection Mitigation

#### Vulnerable Behavior
Initially, SQL queries were written by directly inserting user input into query strings. This made the login and registration forms vulnerable to SQL Injection attacks.

#### Mitigation
The application now uses parameterized queries with placeholders to separate user input from SQL commands.

Example fixed query:

```python
c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
          (username, hashed, "user"))
```

#### How to Test
Go to the Login page and enter:

```text
Username: ' OR '1'='1
Password: anything
```

#### Expected Result
The application should display:

```text
Login failed!
```

This confirms that SQL Injection is blocked.

---

### 2. Weak Password Storage Mitigation

#### Vulnerable Behavior
Initially, passwords were stored using MD5 hashing, which is considered weak and insecure.

#### Mitigation
The application now uses bcrypt with a unique salt for each password.

Example fixed code:

```python
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
```

During login, the entered password is checked using:

```python
bcrypt.checkpw(password.encode('utf-8'), result[2].encode('utf-8'))
```

#### How to Test
1. Log in using the admin account.
2. Open the Admin Panel.
3. Look at the password column.

#### Expected Result
Stored password hashes should start with:

```text
$2b$
```

This confirms that bcrypt is being used instead of MD5.

---

### 3. Cross-Site Scripting (XSS) Prevention

#### Vulnerable Behavior
Initially, user comments were rendered using `|safe`, which allowed JavaScript code entered by users to execute in the browser.

Example vulnerable payload:

```html
<script>alert('Hacked by XSS')</script>
```

#### Mitigation
The `|safe` filter was removed from the template. Flask/Jinja now escapes user input automatically, so scripts are displayed as text instead of being executed.

Fixed template code:

```html
<div class="status-box">{{ comment[0] }}</div>
```

#### How to Test
Log in and post the following in the comment box:

```html
<script>alert('Hacked by XSS')</script>
```

#### Expected Result
No alert should appear. The script should be displayed as normal text on the page.

---

### 4. Access Control / RBAC

#### Vulnerable Behavior
Initially, users could access pages they should not be able to access, such as the admin page.

#### Mitigation
The application now uses session-based Role-Based Access Control (RBAC). Only users with the `admin` role can access the Admin Panel.

Fixed access control logic:

```python
if session.get('role') != 'admin':
    return "Access denied: Admins only", 403
```

#### How to Test as a Normal User
1. Register a normal user.
2. Log in using that normal user.
3. Open:

```text
http://127.0.0.1:5000/admin
```

#### Expected Result
The application should display:

```text
Access denied: Admins only
```

#### How to Test as Admin
1. Log in using:

```text
Username: admin
Password: Admin@12345
```

2. Open:

```text
http://127.0.0.1:5000/admin
```

#### Expected Result
The Admin Dashboard should open successfully.

---

### 5. Secure Session and HTTPS Support

#### Secure Session Cookies
The application uses secure session cookie settings:

```python
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=USE_HTTPS
)
```

- `SESSION_COOKIE_HTTPONLY=True` helps prevent JavaScript from reading the session cookie.
- `SESSION_COOKIE_SAMESITE='Lax'` helps reduce cross-site request risks.
- `SESSION_COOKIE_SECURE=USE_HTTPS` enables secure cookies when HTTPS mode is used.

#### Optional HTTPS Mode
The application supports optional HTTPS local testing using Flask's `ssl_context='adhoc'`.

To run the application in HTTPS mode using PowerShell:

```powershell
$env:USE_HTTPS="1"
python app.py
```

Then open:

```text
https://127.0.0.1:5000
```

#### Note
Because this uses a self-signed local certificate, some browsers may show a warning or block access during local testing. The default mode runs on HTTP for easier local testing:

```bash
python app.py
```

---

## Educational XSS Impact Demo

The dashboard includes an **XSS Impact Demo** button. This is an educational simulation that shows how a fake login page could be used by attackers after a successful XSS or social engineering attack.

This page is not part of the normal secure application flow. It is included only to demonstrate the real-world impact of web vulnerabilities.

## Shared Comments Note

The comment section is shared between users for demonstration purposes. This helps show how Stored XSS can affect multiple users if user-generated content is not sanitized. In a real application, comments or notes may be separated per user depending on the system requirements.

## Important Security Notes

- Password hashes are displayed in the Admin Panel only for educational verification in this project.
- In a real production system, password hashes should not be displayed in any user interface.
- The default admin account is created for testing and demonstration purposes.
- The application is designed for educational use and should not be deployed as-is in production.

## Summary of Security Improvements

| Vulnerability | Initial Issue | Mitigation |
|---|---|---|
| SQL Injection | User input inserted directly into SQL queries | Parameterized queries |
| Weak Password Storage | MD5 password hashing | bcrypt with salt |
| XSS | User comments rendered with `|safe` | Template escaping |
| Broken Access Control | Any user could access admin page | Session-based RBAC |
| Session / Secure Communication | Basic session handling | HTTPOnly, SameSite, optional HTTPS |

## References / Libraries

- Flask documentation
- SQLite documentation
- bcrypt Python library
- pyOpenSSL for local HTTPS testing

## Author

Computer Security Course Project