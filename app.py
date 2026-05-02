from flask import Flask, request, redirect, render_template, url_for, session
import sqlite3
import bcrypt
import os

app = Flask(__name__)
app.secret_key = "demo_secret_key_for_security_project"

USE_HTTPS = os.environ.get("USE_HTTPS") == "1"

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=USE_HTTPS
)
#  Database Initialization

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
  
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS comments
                 (id INTEGER PRIMARY KEY, content TEXT)''')
  
    admin_password = bcrypt.hashpw("Admin@12345".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    c.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
              ("admin", admin_password, "admin"))
    
    conn.commit()
    conn.close()


init_db()



@app.route('/')
def home():
    
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        #Passwords are hashed securely using bcrypt with a unique salt.
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        #Parameterized query is used to prevent SQL injection.
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed, "user"))

        conn.commit()
        conn.close()
        return "Registered successfully! <a href='/login'>Login here</a>"

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        #Fetch user by username using a parameterized query.
        result = c.execute("SELECT * FROM users WHERE username=?",
                           (username,)).fetchone()

        conn.close()

        #bcrypt.checkpw verifies the entered password against the stored bcrypt hash.
        if result and bcrypt.checkpw(password.encode('utf-8'), result[2].encode('utf-8')):
            session['user_id'] = result[0]
            session['username'] = result[1]
            session['role'] = result[3]
            return redirect(url_for('dashboard'))
        else:
            return "Login failed!"

    return render_template('login.html')
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    if request.method == 'POST':
      #User comments are stored in the database. The template escapes output to prevent XSS.
        comment = request.form.get('comment')
        if comment:
            c.execute("INSERT INTO comments (content) VALUES (?)", (comment,))
            conn.commit()


    comments = c.execute("SELECT content FROM comments ORDER BY id DESC").fetchall()
    conn.close()
    return render_template(
        'dashboard.html',
        comments=comments,
        username=session.get('username')
    )
@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('role') != 'admin':
        return "Access denied: Admins only", 403

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    users = c.execute("SELECT username, password, role FROM users").fetchall()

    conn.close()

    return render_template('admin.html', users=users)

@app.route('/fake-malicious-site')
def fake_site():
    return render_template('warning.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

#Running the Web

if __name__ == '__main__':
    if USE_HTTPS:
        app.run(debug=True, port=5000, ssl_context='adhoc')
    else:
        app.run(debug=True, port=5000)