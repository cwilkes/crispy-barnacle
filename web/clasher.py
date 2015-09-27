import xmltodict
import urllib2
import gzip
import StringIO
import os
import boto3
from datetime import datetime


S3_BUCKET_NAME = 'navishack'
DATA_DIR_XML = 'xml'

class Clasher(object):
    def __init__(self):
        self.s3 = boto3.resource('s3')

    def _list_xml_files(self, prefix='xml'):
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

    def list_projects(self):
        projects = set([_.split('/')[1] for _ in self._list_xml_files()])
        projects.remove('')
        return sorted(projects)

    def list_dates(self, project):
        dates = set()
        for fn in self._list_xml_files(os.path.join(DATA_DIR_XML, project)):
            try:
                year, month, day = [int(_) for _ in fn.split('/')[2:5]]
                dates.add('%04d-%02d-%02d' % (year, month, day))
            except:
                pass
        return sorted(dates)

    def list_files(self, project, date):
        files = set()
        for fn in self._list_xml_files(os.path.join(DATA_DIR_XML, project, date.replace('-', '/'))):
            files.add(fn.split('/')[-1])
        return sorted(files)

    def get_xml(self, project, date, name):
        fn = os.path.join(DATA_DIR_XML, project, date.replace('-', '/'), name)
        print 'fn', fn
        key = self.s3.Object(S3_BUCKET_NAME, fn)
        raw_data = StringIO.StringIO(key.get()['Body'].read())
        if fn.endswith('.gz'):
            decompressed_file = gzip.GzipFile(fileobj=raw_data)
            return xmltodict.parse(decompressed_file.read())
        else:
            return xmltodict.parse(raw_data)
