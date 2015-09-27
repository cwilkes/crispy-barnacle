from flask import Flask, render_template, jsonify, redirect, request, Response
from web.clasher import Clasher, DATA_DIR_XML, PROJECT_META_DIR, COMBO_DIR
import os
import logging
import tempfile
import re


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
    tmp_file = tempfile.mktemp(suffix='.tmp', prefix='navis')
    app.logger.info('Files: %s %s tmp %s', fn_obj.mimetype, fn_obj, tmp_file)
    fn_obj.save(tmp_file)
    return tmp_file, fn_obj.filename


def _upload_any_file(tmp_file, projectname, prefix, file_name):
    dest_path = os.path.join(prefix, projectname, file_name)
    real_dest_path = clasher.upload_file(tmp_file, dest_path)
    os.unlink(tmp_file)
    return real_dest_path


def _upload_file_xml(tmp_file, projectname, date):
    dest_path = os.path.join(DATA_DIR_XML, projectname, date.replace('-', '/'), '1.xml')
    real_dest_path = clasher.upload_file(tmp_file, dest_path)
    clasher.pare_down_xml(projectname, date)
    os.unlink(tmp_file)
    return real_dest_path


@app.route('/projects/<projectname>', methods=['POST', ])
def upload_project_meta(projectname):
    tmp_file, file_name = _save_upload()
    return _upload_any_file(tmp_file, projectname, PROJECT_META_DIR, 'util.json')


@app.route('/projects/<projectname>')
def get_project_meta(projectname):
    clasher.get_gzip_file(os.path.join())
    tmp_file, file_name = _save_upload()
    return _upload_any_file(tmp_file, projectname, PROJECT_META_DIR, 'util.json')


@app.route('/xml/<projectname>', methods=['POST', ])
def upload_xml_no_date(projectname):
    tmp_file, fn_name = _save_upload()
    date = clasher.get_new_date(projectname)
    return _upload_file_xml(tmp_file, projectname, date)


@app.route('/xml/<projectname>/<date>', methods=['POST', ])
def upload_xml(projectname, date):
    tmp_file, fn_name = _save_upload()
    return _upload_file_xml(tmp_file, projectname, date)


def get_clash_test(building_name, date):
    app.logger.info('Building: %s, date: %s' % (building_name, date))
    clash_data = clasher.get_xml(building_name, date, '1.xml')
    app.logger.info('Class_data %s', type(clash_data))
    try:
        return clash_data['exchange']['batchtest']['clashtests']['clashtest']
    except Exception as ex:
        app.logger.warn('Error parsing %s', ex)
        return None


@app.route('/plot/<projectname>/<date>')
def get_coords_html(projectname, date):
    coords=_get_coords(projectname, date)
    return render_template('building_plot.html', projectname=projectname, date=date, coords=coords)


def _get_coords(projectname, date):
    clash_data = clasher.get_xml(projectname, date, '1.xml')
    ret = list()
    for data in clash_data['exchange']['batchtest']['clashtests']['clashtest']:
        if data['clashresults'] is None:
            continue
        for d2 in data['clashresults']['clashresult']:
            x, y, z = [float(d2['clashpoint']['pos3f']['@%s' % (_, )]) for _ in ('x', 'y', 'z')]
            clash1, clash2 = [_['smarttags']['smarttag'][1]['value'] for _ in d2['clashobjects']['clashobject']]
            ret.append(dict(name1=clash1, name2=clash2, x=x, y=y, z=z))
            #app.logger.info('Added %s', ret[-1])
    return get_coords

@app.route('/coords/<projectname>/<date>')
def get_coords(projectname, date):
    return jsonify(dict(coords=_get_coords(projectname, date)))


@app.route('/projects')
def list_projects():
    projects = clasher.file_list_dict()['projects']
    project_names = sorted([_['project'] for _ in projects])
    return Response('\r\n'.join(project_names), mimetype='text/plain')


@app.route('/clash/<projectname>')
def clash_for_project(projectname):
    combo_json = clasher.get_json(os.path.join(COMBO_DIR, projectname, 'combo.json'))
    return jsonify(combo_json)


@app.route('/time')
@app.route('/time/')
def time_series():
    data_url = '/static/test-data.json'
    return render_template('clash-summary-over-time.html', data_url=data_url)
