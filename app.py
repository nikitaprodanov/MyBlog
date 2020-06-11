from flask import Flask
from flask import render_template, request, redirect, url_for, jsonify, send_from_directory, flash, session

from functools import wraps

from database import DB
from user import User

app = Flask(__name__)
app.secret_key = "blog and posts"

def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return func(*args, **kwargs)
    return wrapper

@app.route('/')
def main_page():
    if session.get('logged_in'):
        return redirect('/posts_logged_in')
    return redirect('/posts')

@app.route('/posts_logged_in')
@require_login
def posts_logged_in():
    posts = Post.all()
    images = {}
    if posts:
       for post in posts:
            directory = os.listdir(post.file_path) 
            file_path = post.file_path
            images.update({file_path : directory[0]})
    return render_template('posts_logged_in.html', username = User.find_by_id(session['USERNAME']), posts = posts, images = images)

@app.route('/posts')
def list_posts():
    if session.get('logged_in'):
        return redirect('/posts_logged_in')
    posts = Post.all()
    images = {}
    if posts:
        for post in posts:
            directory = os.listdir(post.file_path) 
            file_path = post.file_path
            images.update({file_path : directory[0]})
    return render_template('posts.html') #, posts = posts, images = images)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        if User.find_by_username(username):
            flash('This username is already registered!')
            # logging.info('Someone tried to register with already existing username: %s', username)
            return render_template('register.html')
        elif not request.form['password'] == request.form['confirmpassword']:
            flash('Incorrect password confirmation!')
            # logging.info('Someone didnt confirm his password properly')
            return render_template('register.html')
        elif User.find_by_email(email):
            flash('This email is already registered!')
            # logging.info('Someone tied to register with already existing email: %s', email)
            return render_template('register.html')
        values = (
            None,
            username,
            User.hash_password(request.form['password']),
            email
        )
        User(*values).create()
        user = User.find_by_username(username)
        session['logged_in'] = True
        session['USERNAME'] = user.id
        return redirect('/')  

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        user = User.find_by_username(username)
        if not user or not user.verify_password(password):
            flash('Incorrect login information!')
            # logging.info('Someone tried to login with wrong login information')
            return render_template('login.html')
        elif not user.verify_password(confirmpassword) == user.verify_password(password):
            flash('Incorrect login information!')
            # logging.info('Someone tried to login with wrong login information')
            return render_template('login.html')
        session['logged_in'] = True
        session['USERNAME'] = user.id

        # logging.info('%s with id: %s successfully logged in', User.find_by_id(session['USERNAME']), session['USERNAME'])

        return redirect('/')

@app.route('/user_info')
@require_login
def user_info():
    username = User.find_by_id(session['USERNAME'])
    return render_template('user_info.html', user = User.find_by_username(username))

@app.route('/edit_user_username', methods=['POST'])
def edit_user_username():
    if request.method == 'POST':
        username = User.find_by_id(session['USERNAME'])
        user = User.find_by_username(username)
        edit_username = request.form['username']
        if User.find_by_username(edit_username):
            flash('This username is already registered!')
            return redirect('/user_info')
        edit_oldpassword = request.form['oldpassword']
        if not user or not user.verify_password(edit_oldpassword):
            flash('Incorrect password!')
            return redirect('/user_info')
        user.username = edit_username
        
        # logging.info('%s with id: %s changed his username to %s', User.find_by_id(session['USERNAME']), session['USERNAME'], edit_username)
        
        User.save_username(user)

        return redirect('/user_info')

@app.route('/edit_user_email', methods=['POST'])
def edit_user_email():
    if request.method == 'POST':
        username = User.find_by_id(session['USERNAME'])
        user = User.find_by_username(username)
        edit_email = request.form['email']
        if User.find_by_email(edit_email):
            flash('This email is already registered!')
            return redirect('/user_info')
        edit_oldpassword = request.form['oldpassword']
        if not user or not user.verify_password(edit_oldpassword):
            flash('Incorrect password!')
            return redirect('/user_info')
        user.email = edit_email
        User.save_email(user)
        
        # logging.info('%s with id: %s changed his email to %s', User.find_by_id(session['USERNAME']), session['USERNAME'], edit_email)
        
        return redirect('/user_info')

@app.route('/edit_user_password', methods=['POST'])
def edit_user_password():
    if request.method == 'POST':
        username = User.find_by_id(session['USERNAME'])
        user = User.find_by_username(username)
        edit_oldpassword = request.form['oldpassword']
        if not user or not user.verify_password(edit_oldpassword):
            flash('Incorrect password!')
            return redirect('/user_info')
        edit_password = request.form['password']
        edit_confirmpassword = request.form['confirmpassword']
        if not edit_password == edit_confirmpassword:
            flash('Incorrect password confirmation!')
            return redirect('/user_info')
        user.password = User.hash_password(request.form['password'])
        User.save_password(user)
        
        # logging.info('%s with id: %s changed his password', User.find_by_id(session['USERNAME']), session['USERNAME'])
        
        return redirect('/user_info')

@app.route('/log_out', methods=['GET','POST'])
@require_login
def log_out():
    # logging.info('%s with id: %s logged out', User.find_by_id(session['USERNAME']), session['USERNAME'])
    
    session['USERNAME'] = None
    session['logged_in'] = False

    return redirect('/')

# TODO ADD POSTS ARTICLES AND COMMENTS FUNCTIONALITY


if __name__ == '__main__':
    app.run(debug=True)
