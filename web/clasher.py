import xmltodict
import urllib2
import gzip
import StringIO
import os
import boto3


S3_BUCKET_NAME = 'navishack'

class Clasher(object):
    def __init__(self, fn):
        s3 = boto3.resource('s3')
        key = s3.Object(S3_BUCKET_NAME, fn)
        raw_data = StringIO.StringIO(key.get()['Body'].read())
        if fn.endswith('.gz'):
            decompressed_file = gzip.GzipFile(fileobj=raw_data)
            self.data = xmltodict.parse(decompressed_file.read())
        else:
            self.data = xmltodict.parse(raw_data)
