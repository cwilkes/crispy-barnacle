import xmltodict
import StringIO
import os
import boto3
from datetime import datetime
import redis
import urlparse
import zlib
import logging
from dateutil import parser as date_parser
import re
from dateutil.relativedelta import relativedelta
from web.single_day_parser import SingleDayParser
import simplejson as json
from compile_days import combine_readers


S3_BUCKET_NAME = 'navishack'
DATA_DIR_XML = 'xml'
PROJECT_META_DIR = 'project'
PARE_DOWN_DIR = 'single_json'
COMBO_DIR = 'combo_json'


DATE_RE = re.compile('(\d{4}.\d{2}.\d{2})')

class Clasher(object):
    def __init__(self, logger=None):
        self.logger = logger if logger else logging
        self.s3 = boto3.resource('s3')
        url = urlparse.urlparse(os.environ.get('REDISCLOUD_URL'))
        self.r = redis.Redis(host=url.hostname, port=url.port, password=url.password)

    def _list_files(self, prefix='xml'):
        bucket = self.s3.Bucket(S3_BUCKET_NAME)
        col = bucket.objects.filter(Prefix=prefix)
        ret = list(col)
        try:
            iter(ret)
            return [_.key for _ in ret]
        except:
            return [ret.key, ]

    def file_list_dict(self):
        p1 = self.list_projects()
        p3 = list()
        for project in p1:
            dates = list()
            for date in self.list_dates(project):
                files = list()
                for fn in self.list_files(project, date):
                    files.append(fn)
                dates.append(dict(date=date, files=files))
            p3.append(dict(project=project, dates=dates))
        return dict(projects=p3)

    def get_new_date(self, projectname):
        bucket = self.s3.Bucket(S3_BUCKET_NAME)
        col = bucket.objects.filter(Prefix=os.path.join(DATA_DIR_XML, projectname))
        # xml/cjw/2014/07/24/1.xml
        dates = list()
        for fn in (_.key for _ in col):
            m = DATE_RE.search(fn)
            dates.append(date_parser.parse(m.groups(1)[0]))
        if dates:
            last_date = sorted(dates)[-1]
        else:
            last_date = datetime.now()
        ret_date = last_date + relativedelta(days=+1)
        return ret_date.strftime('%Y-%m-%d')

    def pare_down_xml(self, projectname, date):
        project_json = self.get_json(os.path.join(PROJECT_META_DIR, projectname, 'util.json'))
        parser = SingleDayParser(project_json)
        xml = self.get_xml_string(projectname, date, '1.xml')
        ac = parser.accumulate_clashes(StringIO.StringIO(xml))
        self.upload_file(StringIO.StringIO(json.dumps(ac)), os.path.join(PARE_DOWN_DIR, projectname, date + '.json'))
        self.combine_single_jsons(projectname)

    def combine_single_jsons(self, projectname):
        key_names = self._list_files(os.path.join(PARE_DOWN_DIR, projectname))
        single_datas = [self.get_json(_) for _ in key_names]
        self.logger.info("SD1: %s", single_datas[0])
        acc = combine_readers((StringIO.StringIO(json.dumps(_)) for _ in single_datas))
        self.upload_file(StringIO.StringIO(json.dumps(acc)), os.path.join(COMBO_DIR, projectname, 'combo.json'))

    def upload_file(self, local_data, dest_path):
        body = open(local_data, 'rb') if type(local_data) == str else local_data
        self.s3.Object(S3_BUCKET_NAME, dest_path).put(Body=body)
        return dest_path

    def list_projects(self):
        projects = set([_.split('/')[1] for _ in self._list_files()])
        projects.remove('')
        return sorted(projects)

    def list_dates(self, project):
        dates = set()
        for fn in self._list_files(os.path.join(DATA_DIR_XML, project)):
            try:
                year, month, day = [int(_) for _ in fn.split('/')[2:5]]
                dates.add('%04d-%02d-%02d' % (year, month, day))
            except:
                pass
        return sorted(dates)

    def list_files(self, project, date):
        files = set()
        for fn in self._list_files(os.path.join(DATA_DIR_XML, project, date.replace('-', '/'))):
            files.add(fn.split('/')[-1])
        return sorted(files)

    def get_gzip_file(self, fn):
        self.logger.info('get gzip file %s', fn)
        raw_data = self.r.get(fn)
        if raw_data is not None:
            self.logger.info('From cache %s size: %d', fn, len(raw_data))
            try:
                return zlib.decompress(raw_data)
            except Exception as ex:
                self.logger.warn('Error parsing compressed file %s', ex)
                raise ex
        key = self.s3.Object(S3_BUCKET_NAME, fn)
        self.logger.info('Reading s3 key %s', key)
        raw_data = StringIO.StringIO(key.get()['Body'].read()).read()
        if fn.endswith('.gz'):
            self.r.set(fn, raw_data)
            return zlib.decompress(raw_data)
        else:
            self.r.set(fn, zlib.compress(raw_data, 9))
            return raw_data

    def get_json(self, s3_key):
        return json.loads(self.get_gzip_file(s3_key))

    def get_xml_string(self, project, date, name):
        fn = os.path.join(DATA_DIR_XML, project, date.replace('-', '/'), name)
        self.logger.info('fetching %s', fn)
        return self.get_gzip_file(fn)

    def get_xml(self, project, date, name):
        xml = self.get_xml_string(project, date, name)
        self.logger.info('XML: %s', xml[:100])
        return xmltodict.parse(xml)
