import StringIO
import os
from datetime import datetime
import logging
from dateutil import parser as date_parser
import re
from dateutil.relativedelta import relativedelta
from web.single_day_parser import SingleDayParser
import simplejson as json
from compile_days import combine_readers


S3_BUCKET_NAME = 'navishack'
PROJECT_META_DIR = 'project'
PARE_DOWN_DIR = 'single_json'
COMBO_DIR = 'combo_json'


DATE_RE = re.compile('(\d{4}.\d{2}.\d{2})')


def project_metadata_file(projectname):
    return os.path.join(PROJECT_META_DIR, projectname, 'util.json')

def project_combo_file(projectname):
    return os.path.join(COMBO_DIR, projectname, 'combo.json')

def project_single_file(projectname, date):
    return os.path.join(PARE_DOWN_DIR, projectname, date + '.json')

def blank(target):
    return '' if target is None else target

class S3Helper(object):
    def __init__(self, access_key=None, secret_key=None):
        if access_key is None:
            import boto3
            self.s3 = boto3.resource('s3')
        else:
            from boto3.session import Session
            session = Session(access_key, secret_key, None)
            self.s3 = session.resource('s3')

    def all_files(self, prefix=None):
        bucket = self.s3.Bucket(S3_BUCKET_NAME)
        col = bucket.objects.filter(Prefix='/' if prefix is None else prefix)
        ret = list(col)
        try:
            # this is cheesy, list above returns an array
            # or if one item just that item
            iter(ret)
            return [_.key for _ in ret]
        except:
            return [ret.key, ]

    def project_files(self, projectname, category, match_func=None):
        for fn in self.all_files(os.path.join(blank(category), blank(projectname))):
            if match_func:
                ret = match_func(fn)
                if ret is not None:
                    yield ret
            else:
                yield fn

    def upload_file(self, local_data, dest_path):
        body = open(local_data, 'rb') if type(local_data) == str else local_data
        self.s3.Object(S3_BUCKET_NAME, dest_path).put(Body=body)
        return dest_path

    def get_file(self, fn):
        key = self.s3.Object(S3_BUCKET_NAME, fn)
        return StringIO.StringIO(key.get()['Body'].read()).read()


def date_matcher_func(fn):
    m = DATE_RE.search(fn)
    return date_parser.parse(m.groups(1)[0]) if m else None


class Clasher(object):
    def __init__(self, logger=None):
        self.logger = logger if logger else logging
        self.s3service = S3Helper()

    def get_new_date(self, projectname):
        dates = sorted(self.s3service.project_files(projectname, PARE_DOWN_DIR, date_matcher_func))
        last_date = dates[-1] if dates else datetime.now()
        return (last_date + relativedelta(days=+1)).strftime('%Y-%m-%d')

    def pare_down_xml(self, reader, projectname, date):
        project_json = self.get_json(project_metadata_file(projectname))
        parser = SingleDayParser(project_json)
        ac = parser.clashes_of(reader, date)
        output_file = project_single_file(projectname, date)
        self.upload_file(StringIO.StringIO(json.dumps(ac)), output_file)
        self.combine_single_jsons(projectname)
        return output_file

    def save_project_metadata(self, reader, projectname):
        return self.upload_file(reader, project_metadata_file(projectname))

    def get_project_metadata(self, projectname):
        return self.get_json(project_metadata_file(projectname))

    def get_clash(self, projectname):
        return self.get_json(project_combo_file(projectname))

    def combine_single_jsons(self, projectname):
        key_names = self.s3service.project_files(projectname, PARE_DOWN_DIR)
        single_datas = [self.get_json(_) for _ in key_names]
        self.logger.info("SD1: %s", single_datas[0])
        acc = combine_readers((StringIO.StringIO(json.dumps(_)) for _ in single_datas))
        self.upload_file(StringIO.StringIO(json.dumps(acc)), project_combo_file(projectname))

    def upload_file(self, local_data, dest_path):
        return self.s3service.upload_file(local_data, dest_path)

    def list_projects(self):
        def get_middle_section(key):
            return key.split('/')[1]
        projects = set(self.s3service.project_files(None, PARE_DOWN_DIR, get_middle_section))
        if '' in projects:
            projects.remove('')
        return sorted(projects)

    def get_file(self, fn):
        return self.s3service.get_file(fn)

    def get_json(self, s3_key):
        data = self.get_file(s3_key)
        try:
            return json.loads(data)
        except Exception as ex:
            raise Exception('Error json parsing data from S3 %s' % (s3_key, ), ex)
