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
import redis
import urlparse

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

def project_logo_file(projectname):
    return os.path.join(PROJECT_META_DIR, projectname, 'logo.jpg')




def date_matcher_func(fn):
    m = DATE_RE.search(fn)
    return date_parser.parse(m.groups(1)[0]) if m else None


class Clasher(object):
    def __init__(self, logger=None):
        self.logger = logger if logger else logging
        self.file_service = RedisHelper()

    def get_new_date(self, projectname):
        dates = sorted(self.file_service.project_files(projectname, PARE_DOWN_DIR, date_matcher_func))
        last_date = dates[-1] if dates else datetime.now()
        return (last_date + relativedelta(days=+1)).strftime('%Y-%m-%d')

    def pare_down_xml(self, projectname, date, xml_reader):
        project_json = self.get_json(project_metadata_file(projectname))
        parser = SingleDayParser(project_json)
        ac = parser.clashes_of(xml_reader, date)
        output_file = project_single_file(projectname, date)
        self.upload_file(output_file, json.dumps(ac))
        self.combine_single_jsons(projectname)
        return output_file

    def save_project_metadata(self, projectname, reader):
        return self.upload_file(project_metadata_file(projectname), reader.read())

    def get_project_metadata(self, projectname):
        return self.get_json(project_metadata_file(projectname))

    def get_clash(self, projectname):
        return self.get_json(project_combo_file(projectname))

    def combine_single_jsons(self, projectname):
        key_names = self.file_service.project_files(projectname, PARE_DOWN_DIR)
        single_datas = [self.get_json(_) for _ in key_names]
        self.logger.info("SD1: %s", single_datas[0])
        acc = combine_readers((StringIO.StringIO(json.dumps(_)) for _ in single_datas))
        self.upload_file(project_combo_file(projectname), json.dumps(acc))

    def upload_file(self, local_data, dest_path):
        return self.file_service.upload_file(local_data, dest_path)

    def list_projects(self):
        def get_middle_section(key):
            return key.split('/')[1]
        projects = set(self.file_service.project_files(None, PROJECT_META_DIR, get_middle_section))
        if '' in projects:
            projects.remove('')
        return sorted(projects)

    def get_file(self, fn):
        return self.file_service.get_file(fn)

    def get_json(self, s3_key):
        data = self.get_file(s3_key)
        try:
            return json.loads(data)
        except Exception as ex:
            raise Exception('Error json parsing data from S3 %s' % (s3_key, ), ex)

    def upload_logo(self, projectname, reader):
        return self.file_service.upload_file(project_logo_file(projectname), reader.read())

    def get_logo(self, projectname):
        return self.get_file(project_logo_file(projectname))
