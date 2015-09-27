from flask import Flask, render_template, jsonify, redirect, url_for
from web.clasher import Clasher
import os

xml_file = 'PC-00-COMP-BBC.xml.gz'
clasher = Clasher()

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ


@app.route('/')
def index():
    return redirect('/clash/')


@app.route('/projects/')
def projects():
    return 'The project page'


@app.route('/meta/<project>')
def upload_metadata(project):
    pass

@app.route('/list')
def file_list():
    return jsonify(clasher.file_list_dict())


@app.route('/xml/<project>/<date>')
def upload_xml(project, date):
    pass


@app.route('/about')
def about():
    return 'The about page'


def get_clash_test():
    clash_data = clasher.get_xml('building1', '2015-04-01', '1.xml')
    return clash_data['exchange']['batchtest']['clashtests']['clashtest']


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
