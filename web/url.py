from flask import Flask, render_template, jsonify, redirect, request, Response
from web.clasher import Clasher
import os
import logging


UPLOAD_FILE_FIELD_NAME = 'file'

app = Flask(__name__)
app.debug = 'DEBUG' in os.environ

app.logger.addHandler(logging.StreamHandler())
if app.debug:
    app.logger.setLevel(logging.INFO)

clasher = Clasher(app.logger)

@app.route('/')
def index():
    return redirect('/time')


@app.route('/projects')
def list_projects():
    return Response('\r\n'.join(clasher.list_projects()), mimetype='text/plain')


@app.route('/projects/<projectname>', methods=['POST', ])
def upload_project_meta(projectname):
    upload_file = request.files[UPLOAD_FILE_FIELD_NAME]
    location = clasher.save_project_metadata(projectname, upload_file.stream)
    upload_file.close()
    return location


@app.route('/projects/<projectname>')
def get_project_meta(projectname):
    return jsonify(clasher.get_project_metadata(projectname))


@app.route('/xml/<projectname>', methods=['POST', ])
def upload_xml_no_date(projectname):
    return upload_xml(projectname, clasher.get_new_date(projectname))


@app.route('/xml/<projectname>/<date>', methods=['POST', ])
def upload_xml(projectname, date):
    upload_file = request.files[UPLOAD_FILE_FIELD_NAME]
    saved_location = clasher.pare_down_xml(projectname, date, upload_file.stream)
    upload_file.close()
    return saved_location


@app.route('/clash/<projectname>')
def clash_for_project(projectname):
    return jsonify(clasher.get_clash(projectname))


@app.route('/projects/<projectname>/logo', methods=['POST', ])
def upload_logo(projectname):
    upload_file = request.files[UPLOAD_FILE_FIELD_NAME]
    loc = clasher.upload_logo(projectname, upload_file.stream)
    upload_file.close()
    return loc


@app.route('/projects/<projectname>/logo')
def get_logo(projectname):
    return Response(clasher.get_logo(projectname), mimetype='image/jpg')


@app.route('/time')
def time_series():
    try:
        projectname = request.args['project']
        data_url=os.path.join('/clash', projectname)
    except:
        projectname = "test"
        data_url = '/static/test-data.json'
    logo_url = os.path.join('/projects', projectname, 'logo')
    return render_template('clash-summary-over-time.html', projectname=projectname, data_url=data_url, logo_url=logo_url)
