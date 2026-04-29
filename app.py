from flask import Flask, request, redirect, render_template, render_template_string, url_for
import sqlite3
import bcrypt

app = Flask(__name__)


#  Database Initialization

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
  
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)''')
    
 
  
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

        # FIX: Strong password hashing using bcrypt
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        # FIX: Prevent SQL Injection using parameterized query
        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed, 'user')
        )

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

        # FIX: Prevent SQL Injection using parameterized query
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        conn.close()

        # FIX: Verify password using bcrypt
        if result and bcrypt.checkpw(password.encode('utf-8'), result[2].encode('utf-8')):
            return redirect(url_for('dashboard'))
        else:
            return "Login failed!"

    return render_template('login.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    if request.method == 'POST':
      # VULNERABILITY: user-generated content is rendered without proper sanitation
        comment = request.form.get('comment')
        if comment:
            c.execute("INSERT INTO comments (content) VALUES (?)", (comment,))
            conn.commit()


    comments = c.execute("SELECT content FROM comments ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('dashboard.html', comments=comments)
@app.route('/admin')
def admin():
    # VULNERABILITY: Broken Access Control
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
  
    users = c.execute("SELECT username, password, role FROM users").fetchall()
    conn.close()

    return render_template('admin.html', users=users)


@app.route('/fake-malicious-site')
def fake_site():
    return render_template('warning.html')

# Running the Web

if __name__ == '__main__':
 
    app.run(debug=True, port=5000)
