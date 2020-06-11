from flask import Flask
from flask import render_template, request, redirect, url_for, jsonify, send_from_directory, flash, session

app = Flask(__name__)
app.secret_key = "blog and posts"

@app.route('/')
def main_page():
    if session.get('logged_in'):
        return redirect('/posts_logged_in')
    return redirect('/posts')

@app.route('/posts_logged_in')
@require_login
def posts_logged_in():
    # posts = Post.all()
    # images = {}
    # if posts:
    #     for post in posts:
    #         directory = os.listdir(post.file_path) 
    #         file_path = post.file_path
    #         images.update({file_path : directory[0]})
    return render_template('posts_logged_in.html' ''', posts = posts, username = User.find_by_id(session['USERNAME']), images = images''')

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
    return render_template('posts.html' ''', posts = posts, images = images''')

# TODO ADD POSTS ARTICLES AND COMMENTS FUNCTIONALITY


if __name__ == '__main__':
    app.run(debug=True)