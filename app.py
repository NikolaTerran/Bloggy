from flask import Flask, render_template, request, session, redirect, url_for, flash
#import db_builder
import populateDB
#from passlib.hash import sha256_crypt
import time
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(8)

##command = "CREATE TABLE registration(username TEXT,password TEXT,email TEXT)"
##c.execute(command)    #run SQL statement
def checkApos(string):
    i = -1
    aposIndexes = []
    while True:
        i = string.find("'", i + 1)
        if i == -1: break
        aposIndexes.append(i)
    j = 0
    for index in aposIndexes:
        string = string[:index +j ] + "'" + string[index+ j:]
        j += 1
    return string


@app.route('/')
def home():
    ''' this function loads up home session, from where user can login and navigate through the website'''
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
    '''logs the user in by checking if their login info matches with registered user'''
    username = request.form['usr']
    password = request.form['pwd']
    user_exists = populateDB.findInfo('users', checkApos(username), 'username', fetchOne = True)
    print ('user_exists')
    print (user_exists)
    if user_exists:
        if user_exists[3] == password:
            session['user'] = username
            return redirect(url_for('home'))
        else:
            flash("password wrong")
            return render_template('home.html')
    flash("username wrong")
    return redirect(url_for('home'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    '''registers new account for user'''
    password = request.form['new_pwd'].strip()
    username= request.form['new_usr'].strip()
    pwdCopy = request.form['re_pwd'].strip()
    if username.find("'") == -1:
        try:
                if password == pwdCopy:
                    populateDB.insert('users', ['profilepic', username, password, ''])
                    flash("registration complete, please re-enter your login info");
                else:
                    flash('passwords do not match')
        except:  # as e syntax added in ~python2.5
            flash("your username is not unique; select a new one")
    else:
        flash("pick a username without apostrophes")
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    '''pops user from session, brings user back to home page'''
    #removes current session
    print ('logout...')
    print (session)
    session.pop('user')
    return redirect(url_for('home'))

#edit stuff interface
#don't know how to add those stuff to database
@app.route('/add_post', methods=['POST', 'GET'])
def add_post():
    '''allows the user to add more posts'''
    if 'user' in session:
        user = session['user']
        blog_id = request.form['add_post']
        # id = populateDB.findInfo('users', user, 2)[0]
        blog = populateDB.findInfo('blogs', blog_id, 'BlogID')
        posts = populateDB.findInfo('posts', blog_id, 'blogId')
        print ('blog clicked')
        print (blog[0])
        print (posts)
        return render_template('add_post.html',user = user, blog = blog[0], posts=posts[::-1])
    else:
        return redirect(url_for('home'))

@app.route('/edit_post', methods=['POST', 'GET'])
def edit_post():
    '''allows the user to edit existing posts'''
    if 'user' in session:
        user = session['user']
        user = populateDB.findInfo('users', user, 'Username', fetchOne =  True)
        user_id = user[0]
        if request.form.get('edit_id'):
            post_id = request.form['edit_id']
            print(post_id)
            # id = populateDB.findInfo('users', user, 2)[0]
            post = populateDB.findInfo('posts', post_id, 'postId')
            print ('post clicked')
            print (post)
            return render_template('edit_post.html',user = user, post=post[0])
        elif request.form.get('like_id'):
            post_id = request.form['like_id']
            postRec = populateDB.findInfo('posts', post_id, 'postID', fetchOne = True)
            votes = postRec[5]
            print ('liked')
            print (votes)
            postsLiked = populateDB.findInfo('users', user_id, 'UserID', fetchOne=True)[4]
            listLikedPosts = postsLiked.split(',')
            hasLiked = post_id in listLikedPosts

            if hasLiked:
                votes -= 1
                populateDB.modify('posts', 'VOTES', votes, 'PostID', post_id)
                listLikedPosts = postsLiked.split(',')
                listLikedPosts.remove(post_id)
                postsLiked = ""
                for p in listLikedPosts:
                    postsLiked += p + ','
                populateDB.modify('users', 'LikedPosts', postsLiked,'UserId', user_id)
            else:
                votes += 1
                populateDB.modify('posts', 'VOTES', votes, 'PostID', post_id)
                postsLiked += str(post_id) + ','
                populateDB.modify('users', 'LikedPosts', postsLiked,'UserId', user_id)

            blog = populateDB.findInfo('blogs', postRec[1], 'blogID', fetchOne =True)
            posts = populateDB.findInfo('posts', postRec[1], 'blogID')
            owner = populateDB.findInfo('users', blog[1], 'UserID', fetchOne = True)
            # viewerID = viewer[0]
            is_owner = user_id == blog[1]
            return render_template('blog.html', username = owner[2], viewerPostLiked = postsLiked, blog = blog, posts=posts[::-1], owner=is_owner)
        else:
            post_id = request.form['delete_id']
            postRec = populateDB.findInfo('posts', post_id, 'postID', fetchOne = True)
            blog = populateDB.findInfo('blogs', postRec[1], 'blogID', fetchOne =True)
            owner = populateDB.findInfo('users', blog[1], 'UserID', fetchOne = True)
            is_owner = user_id in blog
            users = populateDB.findInfo('users', 0, "UserID", notEqual =True)
            for user in users:
                user_id = users[0]
                postsLiked = user[4]
                listLikedPosts = postsLiked.split(',')
                listLikedPosts.remove(post_id)
                postsLiked = ""
                for p in listLikedPosts:
                        postsLiked += p + ','
                populateDB.modify('users', 'LikedPosts', postsLiked,'UserId', user_id)
            populateDB.delete('posts', 'PostID', post_id)
            posts = populateDB.findInfo('posts', postRec[1], 'blogID')
            postsLiked = populateDB.findInfo('users', user_id, 'UserID', fetchOne=True)[4]
            populateDB.modify('users', 'LikedPosts', postsLiked,'UserId', user_id)
            return render_template('blog.html', username = owner[2], viewerPostLiked = postsLiked, blog = blog, posts=posts[::-1], owner=is_owner)
    else:
        return redirect(url_for('home'))

@app.route('/create')
def create():
    '''loads html for adding blog to profile'''
    return render_template('createBlog.html', user = session['user'])

@app.route('/makeblog', methods =['POST', 'GET'])
def make():
    '''adds blog based on input from user to db'''
    user = session['user']
    head = checkApos(request.form['blogTitle'])
    des = checkApos(request.form['blogDes'])
    cat = request.form['blogCat']
    print(head)
    print(des)
    print(cat)
    user_id = populateDB.findInfo('users', user, 'username', fetchOne = True)[0]
    blogstuff = [user_id, str(user_id), head, des, cat]
    populateDB.insert('blogs',blogstuff)
    return redirect(url_for('profile'))


##displays user's homepage, which shows the blog that was just created
@app.route('/post', methods=['POST', 'GET'])
def post():
    '''adds a post'''
    print ('submit called...')
    head = checkApos(request.form['heading'])
    text = checkApos(request.form['text'])

    blog_id = request.form['blog_id']
    user = session['user']
    user_all = populateDB.findInfo('users', user, 'username', fetchOne = True)
    user_id = user_all[0]
    posts_liked = user_all[4]

    poststuff = [blog_id, user_id, text, str(time.asctime( time.localtime(time.time()))), 0, head]
    populateDB.insert('posts', poststuff)
    blog = populateDB.findInfo('blogs', blog_id, 'blogID', fetchOne =True)
    posts = populateDB.findInfo('posts', blog_id, 'blogID')
    # viewerID = user_all[0]
    is_owner = user_id in blog
    return render_template('blog.html', username = user_all[2], viewerPostLiked = posts_liked, blog = blog, posts=posts[::-1], owner=is_owner)

@app.route('/edit', methods=['POST', 'GET'])
def edit():
    '''edits a post'''
    print ('edit called...')
    user = session['user']
    viewer = populateDB.findInfo('users', user, 'username', fetchOne = True)
    posts_liked = viewer[4]
    text = checkApos(request.form['text'])
    print(text)
    post_id = request.form['post_id']
    populateDB.modify('posts', 'Content', text, 'PostID', post_id)
    populateDB.modify('posts', 'Timestamp', str(time.asctime( time.localtime(time.time()))), 'PostID', post_id)
    blog_id = populateDB.findInfo('posts', post_id, 'postID', fetchOne =True)[1]
    blog = populateDB.findInfo('blogs', blog_id, 'blogID', fetchOne =True)
    posts = populateDB.findInfo('posts', blog_id, 'blogID')
    viewerID = viewer[0]
    is_owner = viewerID in blog
    return render_template('blog.html', username = viewer[2], viewerPostLiked = posts_liked, blog = blog, posts=posts[::-1], owner=is_owner)

@app.route('/search', methods =['POST', 'GET'])
def look():
    name = request.form['search_value']
    type = request.form['searchtype']
    return render_template("search.html", typer = type, searcher = name)
#If you want to put pic in db, make sure to add a pic field in db table
#PM should ask mr. brown whether is ok use openCV:
#stackoverflow://to.com/questions/41586429/opencv-saving-images-to-a-particular-folder-of-choice/41587740

    #pic = request.form['pic']

    # print ('blog_id')
    # print (blog_id)
    # print ('des')
    # blog_id = populateDB.findInfo('blogs', user_id, 2)[0][0]
    # print (blog_id)
    # post_id = populateDB.findInfo('posts', user_id, 2)
    # populateDB.insert('posts', [blog_id, user_id, des, str(time.asctime( time.localtime(time.time()))), 0, head])

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


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    '''displays home page for user, which includes all the blogs the user made'''
    print ('profile')
    try:
        request.form['user_id']
        id = request.form['user_id']
        user = populateDB.findInfo('users', id, 'UserID', fetchOne = True)[2]
        is_owner = False
        print ('user here')
        print (user)
    except:
        user = session['user']
        id = populateDB.findInfo('users', user, 'username', fetchOne =  True)[0]
        is_owner = True
    print(id)
    blogs = populateDB.findInfo('blogs', id, 'ownerID')
    print(blogs)
    return render_template('profile.html', username = user, blogs=blogs[::-1], owner = is_owner)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    '''displays each blog for user'''
    user = session['user']
    blog_id = request.form['blog_id']
    blog = populateDB.findInfo('blogs', blog_id, 'blogID',fetchOne=True)
    user_id = blog[1]
    userInfo = populateDB.findInfo('users', user_id, 'UserID', fetchOne = True)
    viewer = populateDB.findInfo('users', user, 'username', fetchOne = True)
    viewerID = viewer[0]
    posts = populateDB.findInfo('posts', blog_id, 'blogId')
    is_owner = viewerID in blog
    print ('blog')
    print (blog[3])
    print(posts[::-1])
    return render_template('blog.html', username = userInfo[2], viewerPostLiked = viewer[4], blog = blog, posts=posts[::-1], owner=is_owner)

@app.route('/delete_blog', methods=['POST', 'GET'])
def delete():
    blog_id = request.form['blog_id']
    users = populateDB.findInfo('users', 0, "UserID", notEqual =True)
    for user in users:
        user_id = users[0]
        postsLiked = user[4]
        listLikedPosts = postsLiked.split(',')
        postsLiked = ""
        for p in listLikedPosts:
            blog_origin = populateDB.findInfo('posts', p, 'postID', fetchOne=True)[1]
            if blog_id != blog_origin:
                postsLiked += p + ','
        populateDB.modify('users', 'LikedPosts', postsLiked,'UserId', user_id)
    populateDB.delete('posts', 'BlogID', blog_id)
    populateDB.delete('blogs', 'BlogID', blog_id)
    return redirect(url_for('profile'))

# def like():
#     user = session['user']
#     user_id = populateDB.findInfo('users', user, 'Username', fetchOne =  True)[0]
#     post_id = request.form['post_id']
#     votes = findInfo('posts', post_id, postID, fetchOnethOne=True)[1]
#     print ('liked')
#     #modify('posts', )

@app.route('/usernav', methods=['POST', 'GET'])
def users():
    '''displays every user with their blogs'''
    user = session['user']
    users = populateDB.findInfo('users',user,'Username', notEqual = True)
    print (users)
    return render_template('users.html', users=users)


#link this to database
@app.route('/photo')
def photo():
    return request.form['pic']

@app.route('/food')
def food():
    blogs = populateDB.findInfo('blogs','Food','Category')
    return render_template('food.html', blogs=blogs)

@app.route('/tech')
def tech():
    blogs = populateDB.findInfo('blogs','Tech','Category')
    return render_template('tech.html', blogs=blogs)

@app.route('/sports')
def sports():
    blogs = populateDB.findInfo('blogs','Sports','Category')
    return render_template('sports.html', blogs=blogs)

@app.route('/news')
def news():
    blogs = populateDB.findInfo('blogs','News','Category')
    return render_template('news.html', blogs=blogs)

@app.route('/life')
def life():
    blogs = populateDB.findInfo('blogs','Life','Category')
    return render_template('life.html', blogs=blogs)

@app.route('/music')
def music():
    blogs = populateDB.findInfo('blogs','Music','Category')
    return render_template('music.html', blogs=blogs)

@app.route('/miscellaneous')
def miscellaneous():
    blogs = populateDB.findInfo('blogs','Miscellaneous','Category')
    return render_template('miscellaneous.html', blogs=blogs)
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
