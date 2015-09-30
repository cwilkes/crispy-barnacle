import os
import urlparse
import redis


def blank(target):
    return '' if target is None else target


def redis_connection(url=None):
    if url:
        pass
    else:
        if 'REDISCLOUD_URL' in os.environ:
            url = os.environ.get('REDISCLOUD_URL')
        else:
            url = 'redis://redis:6379'
    url = urlparse.urlparse(url)
    return redis.Redis(host=url.hostname, port=url.port, password=url.password)


class RedisHelper(object):
    def __init__(self, input_url=None):
        self.r = redis_connection(input_url)

    def all_files(self, prefix=None):
        if prefix is None:
            return self.r.keys()
        else:
            return self.r.keys(os.path.join(prefix, '*'))

    def project_files(self, projectname, category, match_func=None):
        for fn in self.all_files(os.path.join(blank(category), blank(projectname))):
            if match_func:
                ret = match_func(fn)
                if ret is not None:
                    yield ret
            else:
                yield fn

    def upload_file(self, dest_path, value):
        self.r.set(dest_path, value)
        return dest_path

    def get_file(self, fn):
        return self.r.get(fn)
