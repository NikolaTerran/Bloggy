from flask import Flask, render_template, request, session, redirect, url_for, flash
import os

app = Flask(__name__)
app.secret_key = os.urandom(8)

@app.route('/')
def home():
    #checks if there is a session
    if "username" in session:
        #if there is then just show the welcome screen
        return render_template('welcome.html',user = session['username'])
    else:
        #if not just ask for info
        return render_template('home.html')

@app.route('/login')
def login():
    #Login: Alan Smith PW: password12345678, checks if it is correct
    if request.args['usr'] == 'Alan Smith' and request.args['pwd']=='password12345678':
        session['username'] = "Alan Smith"
        return redirect(url_for('home'))
    # if either is wrong then it returns an error message
    elif request.args['usr'] == 'Alan Smith' and request.args['pwd']!='password12345678':
        flash("password wrong")
        return render_template('home.html')
    else:
        flash("username wrong")
        return render_template('home.html')

@app.route('/logout')
def logout():
    #removes current session
    session.pop('username',"Alan Smith")
    return redirect(url_for('home'))

#edit stuff interface
#don't know how to add those stuff to database
@app.route('/edit')
def edit():
	if "username" in session:
		return render_template('edit.html',user = session['username'])
	else:
		return redirect(url_for('home'))

@app.route('/username')
def profile():
    user = "Alan Smith"
    blogposts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('profile.html', username = user, blogs = blogposts)



if __name__ == "__main__":
    app.run(debug=True)
