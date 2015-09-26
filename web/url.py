from flask import Flask, render_template, jsonify, redirect, url_for
from web.clasher import Clasher
import os

xml_file = 'PC-00-COMP-BBC.xml.gz'
clash_data = None

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ


@app.route('/')
def index():
    return redirect('/clash/')


@app.route('/projects/')
def projects():
    return 'The project page'


@app.route('/about')
def about():
    return 'The about page'


def get_clash_test():
    global clash_data
    if clash_data is None:
        print 'loading'
        clash_data = Clasher(xml_file)
    return clash_data.data['exchange']['batchtest']['clashtests']['clashtest']

@app.route('/clash/')
def clash_index():
    number_clashes = len(get_clash_test())
    return render_template('clash_index.html', number_clashes=number_clashes)


@app.route('/clash/<int:number>')
def clash_by_number(number):
    clash_info = get_clash_test()[number]
    return jsonify(clash_info)


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)


@app.route('/time')
@app.route('/time/')
def time_series():
    data_url = '/static/test-data.json'
    return render_template('clash-summary-over-time.html', data_url=data_url)
