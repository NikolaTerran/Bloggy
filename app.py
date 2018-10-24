from flask import Flask, render_template, request, session, redirect, url_for, flash
#import db_builder
import populateDB
from passlib.hash import sha256_crypt
import time
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(8)

##command = "CREATE TABLE registration(username TEXT,password TEXT,email TEXT)"
##c.execute(command)    #run SQL statement

@app.route('/')
def home():
    #checks if there is a session
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
    user_exists = populateDB.findInfo('users', username, 2)
    print ('user_exists')
    print (user_exists)
    if user_exists:
        if user_exists[3] == password:
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
    pwdCopy = request.form['re_pwd']
#   command2 = 'INSERT INTO registration VALUES("' + username + '", "' + password  + '", "' + request.form['email'] + '")'
#   c.execute(command2)
    try:
        populateDB.insert('users', ['profilepic', username, password])
    except:  # as e syntax added in ~python2.5
        flash("your username is not unique; select a new one") #BUG GOT TO FIX THIS FOR UNIQUE USERNAME
        return redirect(url_for('home'))

    if password != pwdCopy:
        flash('passwords do not match')
        return redirect(url_for('home'))
    else:
        session['user'] = username
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    #removes current session
    print ('logout...')
    print (session)
    session.pop('user')
    return redirect(url_for('home'))

#edit stuff interface
#don't know how to add those stuff to database
@app.route('/edit')
def edit():
    if 'user' in session:
        user = session['user']
        id = populateDB.findInfo('users', user, 2)[0]
        blogs = populateDB.findInfo('blogs', id, 1)
        return render_template('edit.html',user = user, blogs=blogs)
    else:
		return redirect(url_for('home'))

@app.route('/create')
def create():
    return render_template('createBlog.html', user = session['user'])

@app.route('/makeblog', methods =['POST', 'GET'])
def make():
    user = session['user']
    head = request.form['blogTitle']
    des = request.form['blogDes']
    cat = request.form['blogCat']
    print(head)
    print(des)
    print(cat)
    user_id = populateDB.findInfo('users', user, 2)[0]
    blogstuff = [user_id, str(user_id), head, des, cat]
    populateDB.insert('blogs',blogstuff)
    return redirect(url_for('profile'))


##displays user's homepage, which shows the blog that was just created
@app.route('/submit', methods=['POST', 'GET'])
def submit():
    print ('submit called...')
    user = session['user']
    user_id = populateDB.findInfo('users', user, 2)[0]
    head = request.form['heading']
    des = request.form['text']
    print ('des')
    blog_id = populateDB.findInfo('blogs', user_id, 2)[0][0]
    print (blog_id)
    post_id = populateDB.findInfo('posts', user_id, 2)
    populateDB.insert('posts', [blog_id, user_id, des, str(time.asctime( time.localtime(time.time()))), 0])

    ### html_str = """
    ### <table border="2">
    ###     <tr>
    ###         <th>{{head}}</th>
    ###     </tr>
    ###     <tr>
    ###         <td>{{des}}</td>
    ###     </tr>
    ### </table>
    ### """
    return redirect(url_for('profile'))

@app.route('/profile')
def profile():
    user = session['user']
    print ('profile')
    id = populateDB.findInfo('users', user, 2)[0]
    print(id)
    blogs = populateDB.findInfo('blogs', id, 1)
    print(blogs)
    posts = populateDB.findInfo('posts', id, 2)
    print(posts[::-1])
    return render_template('profile.html', username = user, blogs=blogs[::-1], posts=posts[::-1])

#@app.route('/redirect')
#def findblog():


#@app.route('/usernamedf')
#def profile():
   # user = session.get('username')
   # defaultheading = 'Blog'
    #defaultpost = 'Information about cool stuff'
    #return render_template('profile.html', username = user, heading = defaultheading, blogs = defaultpost)


###enter user's info to database
##@app.route('/register')
##def register():
##	#if(request.args['usr'] != NULL):
##	#	db = sqlite3.connect("user_data.db")
##	#	c = db.cursor()
##	#	file = open('data/data.csv')
##	#	command = "CREATE TABLE users(name TEXT,password TEXT,id INTEGER)"
##	#	c.execute(command)
##	#	command2 = 'INSERT INTO users VALUES(?,?,?)'
##	#	c.execute(command,(request.args['usr'],request.args['pwd'],0))
##	#	return render_template('home.html')
##	#else:
##		return render_template('register.html')
if __name__ == "__main__":
    app.run(debug=True)
