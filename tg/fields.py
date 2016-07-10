import os

import redis


if 'REDIS_URL' in os.environ:
    redis = redis.from_url(os.environ['REDIS_URL'])
else:
    redis = redis.Redis()


class Field(object):

    def __init__(self, initial):
        self.initial = initial

    def get(self, obj, key):
        ret = redis.get('tg:%s:%s' % (obj.chat_id, key))
        if ret is None:
            ret = self.initial
            self.set(obj, key, ret)
        return ret

    def set(self, obj, key, value):
        redis.set('tg:%s:%s' % (obj.chat_id, key), value)
        return value


class Integer(Field):

    def get(self, obj, key):
        return int(super().get(obj, key))

    def set(self, obj, key, value):
        super().set(obj, key, int(value))
