from flask import Flask, render_template, jsonify, redirect, url_for, request, Response
from web.clasher import Clasher, DATA_DIR_XML
import os
import logging
import StringIO
import tempfile
import re
from datetime import datetime


UPLOAD_FILE_FIELD_NAME = 'file'
date_re = re.compile('\d{4}')

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ

app.logger.addHandler(logging.StreamHandler())
if app.debug:
    app.logger.setLevel(logging.INFO)

clasher = Clasher(app.logger)

@app.route('/')
def index():
    return redirect('/list')


@app.route('/list')
def file_list():
    return jsonify(clasher.file_list_dict())


def _save_upload():
    fn_obj = request.files[UPLOAD_FILE_FIELD_NAME]
    tmp_file = tempfile.mktemp()
    app.logger.info('Files: %s %s tmp %s', fn_obj.mimetype, fn_obj, tmp_file)
    fn_obj.save(tmp_file)
    return tmp_file, fn_obj.filename


def _upload_file(tmp_file, projectname, date):
    dest_path = os.path.join(DATA_DIR_XML, projectname, date.replace('-', '/'), '1.xml')
    real_dest_path = clasher.upload_file(tmp_file, dest_path)
    os.unlink(tmp_file)
    return real_dest_path


@app.route('/xml/<projectname>', methods=['POST', ])
def upload_xml_no_date(projectname):
    tmp_file, fn_name = _save_upload()
    date = clasher.get_new_date(projectname)
    return _upload_file(tmp_file, projectname, date)


@app.route('/xml/<projectname>/<date>', methods=['POST', ])
def upload_xml(projectname, date):
    tmp_file, fn_name = _save_upload()
    return _upload_file(tmp_file, projectname, date)


def get_clash_test(building_name, date):
    app.logger.info('Building: %s, date: %s' % (building_name, date))
    clash_data = clasher.get_xml(building_name, date, '1.xml')
    app.logger.info('Class_data %s', type(clash_data))
    try:
        return clash_data['exchange']['batchtest']['clashtests']['clashtest']
    except Exception as ex:
        app.logger.warn('Error parsing %s', ex)
        return None


@app.route('/projects')
def list_projects():
    projects = clasher.file_list_dict()['projects']
    project_names = sorted([_['project'] for _ in projects])
    return Response('\r\n'.join(project_names), mimetype='text/plain')


@app.route('/clash/<buildingname>/<date>')
def clash_by_number(buildingname, date):
    clash_info = get_clash_test(buildingname, date)
    return jsonify(clash_info[0])


@app.route('/time')
@app.route('/time/')
def time_series():
    data_url = '/static/test-data.json'
    return render_template('clash-summary-over-time.html', data_url=data_url)
