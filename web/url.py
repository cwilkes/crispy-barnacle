from flask import Flask, render_template, jsonify, redirect, url_for, request
from web.clasher import Clasher, DATA_DIR_XML
import os
import logging
import StringIO
import tempfile

UPLOAD_FILE_FIELD_NAME = 'file'

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ

app.logger.addHandler(logging.StreamHandler())
if app.debug:
    app.logger.setLevel(logging.INFO)

clasher = Clasher(app.logger)

@app.route('/')
def index():
    return redirect('/list')


@app.route('/projects/')
def projects():
    return 'The project page'


@app.route('/list')
def file_list():
    return jsonify(clasher.file_list_dict())


@app.route('/xml/<projectname>/<date>', methods=['POST', ])
def upload_xml(projectname, date):
    fn_obj = request.files[UPLOAD_FILE_FIELD_NAME]
    tmp_file = tempfile.mktemp()
    app.logger.info('Files: %s %s tmp %s', fn_obj.mimetype, fn_obj, tmp_file)
    fn_obj.save(tmp_file)
    dest_path = os.path.join(DATA_DIR_XML, projectname, date.replace('-', '/'), '1.xml')
    clasher.upload_file(tmp_file, dest_path)
    os.unlink(tmp_file)
    return dest_path



def get_clash_test(building_name, date):
    app.logger.info('Building: %s, date: %s' % (building_name, date))
    clash_data = clasher.get_xml(building_name, date, '1.xml')
    app.logger.info('Class_data %s', type(clash_data))
    try:
        return clash_data['exchange']['batchtest']['clashtests']['clashtest']
    except Exception as ex:
        app.logger.warn('Error parsing %s', ex)
        return None


@app.route('/clash/<buildingname>/<date>')
def clash_by_number(buildingname, date):
    clash_info = get_clash_test(buildingname, date)
    return jsonify(clash_info[0])


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)


@app.route('/time')
@app.route('/time/')
def time_series():
    data_url = '/static/test-data.json'
    return render_template('clash-summary-over-time.html', data_url=data_url)
