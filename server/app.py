from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
from flask import redirect
from flask import session
from flask_argon2 import Argon2

import secrets
import json
import sqlite3
import os
import random
import string
import bleach

app = Flask(__name__,static_folder='static', static_url_path='')
hasher = Argon2(app)
# set the app secret key to something cryptographically random
app.secret_key = secrets.token_hex(32)

# add some extra randomness to passwords
# this means that each time the server is restarted, it essentially runs
# a different hashing algorithm. Therefore password/hash pairs cannot
# be reused between runs
password_pepper = ''.join(random.choices(string.printable, k=5))

def generate_password_hash(password):
    password = password + password_pepper
    return hasher.generate_password_hash(password)

def check_password_hash(hsh,password):
    password = password + password_pepper
    return hasher.check_password_hash(hsh,password)

# the admin password is random 14-character password of non-whitespace characters
admin_password = ''.join(random.choices(string.ascii_letters+string.digits+string.punctuation, k=14))
admin_password_hash = generate_password_hash(admin_password)

app.logger.debug(f"admin password: {admin_password}")

def init_database():
    if os.path.isfile("database.db"):
        raise Exception("Database already exists!")
    
    connection = sqlite3.connect("database.db")
    sql = """
                DROP TABLE IF EXISTS users;
                CREATE TABLE users ( 
                id INTEGER IDENTITY PRIMARY KEY, 
                username VARCHAR(64),
                phone VARCHAR(64),
                password VARCHAR(100));
                INSERT INTO users (username, phone, password) VALUES ("admin", "+61383445080", "%s");
                DROP TABLE IF EXISTS messages;
                CREATE TABLE messages (
                id INTEGER IDENTITY PRIMARY KEY,
                postedby VARCHAR(64),
                content VARCHAR(140),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
              """ % (admin_password_hash)
    cursor = connection.cursor()
    cursor.executescript(sql)
    connection.close()

# re-initialise the database on app startup
init_database()

@app.route('/')
def index():
    if 'username' in session:
        connection = sqlite3.connect("database.db")
        sql = "SELECT * FROM messages;"
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        messages = []
        for r in result:
            msg = {"postedby": r[1], "content": r[2], "timestamp": r[3]}
            messages.append(msg)

        return render_template('app.html', session=session,messages=messages)
    else:    
        return render_template("login.html")

@app.route('/post', methods=['POST'])
def post():
    if 'username' in session and request.form['msg']:
        username = session['username']
        msg = request.form['msg']
        # sanitise all non-admin messages
        if username != "admin":
            msg = bleach.clean(msg)
        if len(msg) <= 140:
            
            connection = sqlite3.connect("database.db")
            sql = 'INSERT INTO messages (postedby, content) VALUES (?, ?);'
            cursor = connection.cursor()
            cursor.execute(sql,[username,msg])
            connection.commit()
            connection.close()
            return redirect('/')
    if 'username' not in session:
        return f"Log in first.", 401
    else:
        return "No msg provided", 400
        
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    user = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = sqlite3.connect("database.db")
        sql = "SELECT username,password FROM users WHERE username='" + username + "';"
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        connection.close()
        if len(result) != 0:
            if check_password_hash(result[0][1],password):
                # sensitive info should not be stored in the session cookie
                # see e.g. https://blog.miguelgrinberg.com/post/how-secure-is-the-flask-user-session
                # so don't put the phone number in here
                session['username'] = result[0][0]
                return redirect('/')
        return render_template('login.html', error=True, user=None), 401
    else:
        return render_template('login.html',error=False,user=None), 200


@app.route('/userexists', methods=['GET'])
def userexists():
    if request.args.get('username'):
        connection = sqlite3.connect("database.db")
        sql = "SELECT * FROM users WHERE username='" + request.args['username'] + "'"
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        connection.close()
        if len(result) > 0:
            return "User already exists", 200
        else:
            return "User doesn't exist", 404
    return "No user specified. Try adding a ?username=blah parameter", 400

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        phone = request.form['phone']
        
        password_hash = generate_password_hash(password)
        
        connection = sqlite3.connect("database.db")
        sql = "SELECT * FROM users WHERE username='" + username + "'"
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        connection.close()
        if len(result) > 0:
            # user already exists
            return render_template('signup.html', error=True), 400
        else:
            connection = sqlite3.connect("database.db")
            sql = 'INSERT INTO users (username, phone, password) VALUES (?, ?, ?);'
            cursor = connection.cursor()
            cursor.execute(sql,[username,phone,password_hash])
            connection.commit()
            connection.close()
            return redirect('login')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    # Clear the session cookie
    session.pop('username', None)
    session.pop('role', None)
    return redirect('/')

if __name__ == "__main__":
    # when debug=True, use_reloader needs to be False to prevent the
    # initialisation code (which generates the admin password, etc.)
    # from being executed more than once
    app.run(debug=True,host='0.0.0.0',port=80,use_reloader=False)
