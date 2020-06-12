from functools import wraps

from flask import Flask
from flask import render_template, request, redirect, url_for, jsonify, send_from_directory, flash, session
import os, shutil, string, random

from database import DB
from user import User
from comment import Comment
from post import Post
from article import Article

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

@app.route('/user_info')
@require_login
def user_info():
    username = User.find_by_id(session['USERNAME'])
    return render_template('user_info.html', user = User.find_by_username(username))


#postS METHODS
@app.route('/posts/user_posts')
@require_login
def user_posts():
    posts = Post.find_by_user_id(session['USERNAME'])
    username = User.find_by_id(session['USERNAME'])
    images = {}
    for post in posts:
        directory = os.listdir(post.file_path) 
        file_path = post.file_path
        images.update({file_path : directory[0]})
    return render_template('library.html', posts = posts, images = images, username = username)

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
    return render_template('posts_logged_in.html', posts = posts, username = User.find_by_id(session['USERNAME']), images = images)

@app.route('/posts/search', methods=['POST'])
def search_post():
    if request.method == 'POST':
        keyword = request.form['keyword']
        with DB() as db:
            rows = db.execute('''SELECT * FROM posts WHERE 
            (name LIKE ? OR name LIKE ?) ''', ("%" + keyword + "%", "%" + keyword + "%",)).fetchall()
            posts = [Post(*row) for row in rows]
            images = {}
            for post in posts:
                directory = os.listdir(post.file_path) 
                file_path = post.file_path
                images.update({file_path : directory}) 
            return render_template('searched_posts.html', posts = posts, images = images)

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
    return render_template('posts.html', posts = posts, images = images)

@app.route('/posts/<int:id>')
def show_post(id):
    post = Post.find(id)
    images = os.listdir(post.file_path)
    post.file_path = '/' + post.file_path
    user_id = session['USERNAME']
    username = User.find_by_id(post.user_id)
    user = User.find_by_username(username)
    email = user.email
    return render_template('post.html', post = post, images = images, user_id = user_id, username = username, email = email)

@app.route('/posts/new', methods=['GET', 'POST'])
@require_login
def new_post():
    if request.method == 'GET':
        return render_template('new_post.html', articles = Article.all())
    elif request.method == 'POST':
        letters = string.ascii_lowercase
        direc_path = random.choice(letters)
        direc = request.form['name']
        images = request.files.getlist("file")
        os.mkdir("static/images/" + direc + User.find_by_id(session['USERNAME']) + direc_path)
        for img in images:
            img_path = 'static/images/' + direc + User.find_by_id(session['USERNAME']) + direc_path + "/"
            img.save(img_path + img.filename)
        article = Article.find(request.form['article_id'])
        values = (
            None,
            request.form['name'],
            request.form['description'],
            article,
            img_path,
            session['USERNAME']
        )
        Post(*values).create()

        #logging.info('%s with id: %s added new post', User.find_by_id(session['USERNAME']), session['USERNAME'])

        return redirect('/')

@app.route('/posts/<int:id>/delete', methods=['POST'])
@require_login
def delete_post(id):
    post = Post.find(id)
    shutil.rmtree(post.file_path)
    with DB() as db:
        db.execute('DELETE FROM comments WHERE post_id = ?', (post.id,))
    post.delete()
    #logging.info('%s with id: %s deleted post %s', User.find_by_id(session['USERNAME']), session['USERNAME'], post.id)
    return redirect('/')

@app.route('/posts/<int:id>/edit', methods=['GET', 'POST'])
@require_login
def edit_post(id):
    post = Post.find(id)
    if request.method == 'GET':
        return render_template('edit_post.html', post = post, articles = Article.all())
    elif request.method == 'POST':
        post.name = request.form['name']
        post.description = request.form['description']
        post.article = Article.find(request.form['article_id'])
        images = request.files.getlist("file")
        shutil.rmtree(post.file_path)
        letters = string.ascii_lowercase
        direc_path = random.choice(letters)
        direc = request.form['name']
        os.mkdir("static/images/" + direc + User.find_by_id(session['USERNAME']) + direc_path)
        for img in images:
            img_path = 'static/images/' + direc + User.find_by_id(session['USERNAME']) + direc_path + "/"
            img.save(img_path + img.filename)
        post.file_path = img_path
        post.save()

        #logging.info('%s with id: %s edited post %s', User.find_by_id(session['USERNAME']), session['USERNAME'], post.id)
        
        return redirect(url_for('show_post', id = post.id))


#articles METHODS
@app.route('/articles')
def get_articles():
    return render_template("articles.html", articles=Article.all())

@app.route('/articles/new', methods=['GET', 'POST'])
def new_article():
    if request.method == "GET":
        return render_template("new_article.html")
    elif request.method == "POST":
        article = Article(None, request.form["name"])
        article.create()

        #logging.info('%s with id: %s added new categoty %s named %s', User.find_by_id(session['USERNAME']), session['USERNAME'], article.id, article.name)
        
        return redirect("/articles")


@app.route('/articles/<int:id>')
def get_article(id):
    return render_template("article.html", article=Article.find(id))


@app.route('/articles/<int:id>/delete')
def delete_article(id):
    Article.find(id).delete()

   #logging.info('%s with id: %s deleted categoty %s named %s', User.find_by_id(session['USERNAME']), session['USERNAME'], article.id, article.name)


    return redirect("/articles")


#COMMENTS METHODS
@app.route('/comments/new', methods=['GET', 'POST'])
@require_login
def new_comment():
    if request.method == 'POST':
        post = Post.find(request.form['post_id'])
        user_id = session['USERNAME']
        username = User.find_by_id(user_id)
        if not request.form['message']:
            flash('You entered empty comment!')
            return redirect(url_for('show_post', id=post.id))
        else:
            values = (None, post, request.form['message'], user_id, username)
            Comment(*values).create()

        #logging.info('%s with id: %s commented %s on post %s', User.find_by_id(session['USERNAME']), session['USERNAME'], request.form['message'], post.id)

        return redirect(url_for('show_post', id=post.id))

@app.route('/comments/<int:id>/delete', methods=['POST'])
@require_login
def del_comment(id):
    Comment.delete(id)
    post = Post.find(request.form['post_id'])

    #logging.info('%s with id: %s deleted comment on post %s', User.find_by_id(session['USERNAME']), session['USERNAME'], post.id)


    return redirect(url_for('show_post',id = post.id))

@app.route('/comments/<int:id>/edit', methods=['POST'])
@require_login
def edit_comment(id):
    if not request.form['message']:
        Comment.delete(id)
    else:
        Comment.save(request.form['message'], id)
    post = Post.find(request.form['post_id'])

    #logging.info('%s with id: %s edited comment on post %s with: %s', User.find_by_id(session['USERNAME']), session['USERNAME'], post.id, request.form['message'])


    return redirect(url_for('show_post',id = post.id))    


#REGISTRATION/LOGIN METHODS
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
        
        #logging.info('%s with id: %s changed his username to %s', User.find_by_id(session['USERNAME']), session['USERNAME'], edit_username)
        
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
        
        #logging.info('%s with id: %s changed his email to %s', User.find_by_id(session['USERNAME']), session['USERNAME'], edit_email)
        
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
        
        #logging.info('%s with id: %s changed his password', User.find_by_id(session['USERNAME']), session['USERNAME'])
        
        return redirect('/user_info')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        if User.find_by_username(username):
            flash('This username is already registered!')
            #logging.info('Someone tried to register with already existing username: %s', username)
            return render_template('register.html')
        elif not request.form['password'] == request.form['confirmpassword']:
            flash('Incorrect password confirmation!')
            #logging.info('Someone didnt confirm his password properly')
            return render_template('register.html')
        elif User.find_by_email(email):
            flash('This email is already registered!')
            #logging.info('Someone tied to register with already existing email: %s', email)
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
            #logging.info('Someone tried to login with wrong login information')
            return render_template('login.html')
        elif not user.verify_password(confirmpassword) == user.verify_password(password):
            flash('Incorrect login information!')
            #logging.info('Someone tried to login with wrong login information')
            return render_template('login.html')
        session['logged_in'] = True
        session['USERNAME'] = user.id

        #logging.info('%s with id: %s successfully logged in', User.find_by_id(session['USERNAME']), session['USERNAME'])

        return redirect('/')

@app.route('/log_out', methods=['GET','POST'])
@require_login
def log_out():
    #logging.info('%s with id: %s logged out', User.find_by_id(session['USERNAME']), session['USERNAME'])
    
    session['USERNAME'] = None
    session['logged_in'] = False

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
