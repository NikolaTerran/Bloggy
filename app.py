from flask import Flask, render_template, request, session, redirect, url_for, flash
from passlib.hash import sha256_crypt
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(8)

DB_FILE="bloggers.db"

db = sqlite3.connect("bloggers.db",check_same_thread=False) #open if file exists, otherwise create
c = db.cursor()               #facilitate db ops

##command = "CREATE TABLE registration(username TEXT,password TEXT,email TEXT)"
##c.execute(command)    #run SQL statement

@app.route('/')
def home():
    #checks if there is a session
    command3 = 'SELECT * FROM registration'
    c.execute(command3)
    print(c.fetchall())
    if 'user' in session:
        #if there is then just show the welcome screen
        print('user in!')
        return render_template('welcome.html', user=session['user'])
    else:
        #if not just ask for info
        return render_template('home.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    username = request.form['usr']
    password = request.form['pwd']
    command4 = "SELECT password FROM registration WHERE username = '" + username + "'"
    c.execute(command4)
    user_exists = c.fetchone()
    print ('user_exists')
    print (user_exists)
    if user_exists:
        if user_exists[0] == password:
            session['user'] = username
            return redirect(url_for('home'))
        else:
            flash("password wrong")
            return render_template('home.html')
    else:
        flash("username wrong")
        return render_template('home.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    password = request.form['new_pwd']
    username= request.form['new_usr']
    command2 = 'INSERT INTO registration VALUES("' + username + '", "' + password  + '", "' + request.form['email'] + '")'
    c.execute(command2)
    session['user'] = username
    command3 = 'SELECT * FROM registration'
    c.execute(command3)
    print(c.fetchall())
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    #removes current session
    session.pop('user')
    return redirect(url_for('home'))

	
if __name__ == "__main__":
    app.run(debug=True)
