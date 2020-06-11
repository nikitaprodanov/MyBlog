from flask import Flask
from flask import render_template, request, redirect, url_for, jsonify, send_from_directory, flash, session

app = Flask(__name__)
app.secret_key = "blog and posts"

@app.route('/')
def main_page():
    return render_template('hello.html')


if __name__ == '__main__':
    app.run(debug=True)