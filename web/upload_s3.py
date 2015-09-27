import sys
import boto3
import os


S3_BUCKET_NAME = 'navishack'
DATA_DIR_XML = 'xml'


def main():
    fn, date = sys.argv[1], sys.argv[2]
    s3 = boto3.resource('s3')
    s3_file_name = os.path.join(DATA_DIR_XML, 'building1', date.replace('-', '/'), '1.xml')
    print 'uploading', fn, 'to', s3_file_name
    s3.Object(S3_BUCKET_NAME, s3_file_name).put(Body=open(fn, 'rb'))


if __name__ == '__main__':
    sys.exit(main())
