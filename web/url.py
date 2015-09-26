from flask import Flask, url_for, render_template, jsonify, redirect
import os
import psycopg2
import urlparse
import xmltodict
import urllib2
import gzip
import StringIO


xml_file = 'https://s3.amazonaws.com/navishack/PC-00-COMP-BBC.xml.gz'

if xml_file.endswith('.gz'):
    response = urllib2.urlopen(xml_file)
    compressedFile = StringIO.StringIO(response.read())
    decompressedFile = gzip.GzipFile(fileobj=compressedFile)
    j = xmltodict.parse(decompressedFile.read())
else:
    j = xmltodict.parse(urllib2.urlopen(xml_file))



app = Flask(__name__)

urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])


@app.route('/')
def index():
    return redirect('/clash/')


@app.route('/projects/')
def projects():
    return 'The project page'


@app.route('/about')
def about():
    return 'The about page'

@app.route('/clash/')
def clash_index():
    number_clashes = len(j['exchange']['batchtest']['clashtests']['clashtest'])
    return render_template('clash_index.html', number_clashes=number_clashes)

@app.route('/clash/<int:number>')
def clash_by_number(number):
    clash_info = j['exchange']['batchtest']['clashtests']['clashtest'][number]
    return jsonify(clash_info)

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)
