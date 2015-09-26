from flask import Flask, url_for, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return 'index'


@app.route('/projects/')
def projects():
    return 'The project page'


@app.route('/about')
def about():
    return 'The about page'


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)
