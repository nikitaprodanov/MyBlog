from flask import Flask
from flask import render_template, request, redirect, url_for, jsonify, send_from_directory, flash, session

from database import DB
from user import User

app = Flask(__name__)
app.secret_key = "blog and posts"

@app.route('/')
def main_page():
    if session.get('logged_in'):
        return redirect('/posts_logged_in')
    return redirect('/posts')

@app.route('/posts_logged_in')
# @require_login
def posts_logged_in():
    # posts = Post.all()
    # images = {}
    # if posts:
    #     for post in posts:
    #         directory = os.listdir(post.file_path) 
    #         file_path = post.file_path
    #         images.update({file_path : directory[0]})
    return render_template('posts_logged_in.html') #''', posts = posts, username = User.find_by_id(session['USERNAME']), images = images''')

@app.route('/posts')
def list_posts():
    if session.get('logged_in'):
        return redirect('/posts_logged_in')
    # posts = Post.all()
    # images = {}
    # if posts:
    #     for post in posts:
    #         directory = os.listdir(post.file_path) 
    #         file_path = post.file_path
    #         images.update({file_path : directory[0]})
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

# TODO ADD POSTS ARTICLES AND COMMENTS FUNCTIONALITY


if __name__ == '__main__':
    app.run(debug=True)