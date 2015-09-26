import xmltodict
import urllib2
import gzip
import StringIO
import os
import boto3


class Clasher(object):
    def __init__(self, url):
        s3 = boto3.resource('s3')
        #bucket = s3.get_bucket('navishack', validate=False)
        if url.endswith('.gz'):
            response = urllib2.urlopen(url)
            compressed_file = StringIO.StringIO(response.read())
            decompressed_file = gzip.GzipFile(fileobj=compressed_file)
            self.data = xmltodict.parse(decompressed_file.read())
        else:
            self.data = xmltodict.parse(urllib2.urlopen(url))
