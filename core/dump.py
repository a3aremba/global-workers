# coding: utf-8

from __future__ import absolute_import

import abc
import redis
import logging
import collections

from core.utils import json

__all__ = ('create_redis', 'create_redis_pool', 'Task', 'Dump',
           'RedisDump', 'InvalidKeyError', 'DumpConfig')

logger = logging.getLogger(__name__)
DumpConfig = collections.namedtuple('Dump', 'url')


class Task(collections.namedtuple('Task', 'id name args kwargs exception')):
    """
    Failed task info to be dumped.

    :param id: failed task's id
    :param name: full name of task function
    :param args: args that were passed
    :param kwargs: kwargs that were passed
    :param exception: string representation of exception
    """

    __slots__ = ()

    def __new__(cls, id, name, args, kwargs, exception):
        return super(Task, cls).__new__(cls, id, name, args, kwargs,
                                        str(exception))


def create_redis(pool):
    """
    :param pool: Instance of `redis.ConnectionPool`
    :return: Instance of `redis.StrictRedis`
    """
    return redis.StrictRedis(connection_pool=pool)


def create_redis_pool(config):
    """
    :param config: Instance of `core.config.DumpConfig`
    :return: Instance of `redis.ConnectionPool`
    """
    return redis.ConnectionPool.from_url(config.url)


class DumpException(BaseException):
    pass


class InvalidKeyError(DumpException):
    pass


class Dump(object):
    """
    Allows to dump objects to external storage.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def dump(self, obj):
        """
        :param obj: Instance of `namedtuple`
        :raises: `AttributeError` if no `obj.id` or `task._asdict()` are found
        """
        raise NotImplementedError


class RedisDump(Dump):
    """
    Redis-based implementation of `Dump`.

    Object's `id` is a key to hash.

    Hash key is build according to format `prefix:id`.
    Set key is used if provided. `prefix:all` otherwise
    """

    def __init__(self, redis, prefix, set_key=None):
        super(RedisDump, self).__init__()

        self._redis = redis
        self._prefix = prefix
        self._set_key = set_key or '{}:all'.format(self._prefix)

    def dump(self, obj):
        """
        :raises: `InvalidKeyError` if `task.id` matches `tasks_set_name`
        """
        pipe = self._redis.pipeline()
        hash_key = self._hash_key(obj.id)

        if hash_key == self._set_key:
            raise InvalidKeyError(("Hash key '{}' conflicts with set key '{}'"
                                   ).format(hash_key, self._set_key))

        pipe.hmset(hash_key, {k: json.dumps(v) for k, v in
                              obj._asdict().items()})
        pipe.sadd(self._set_key, hash_key)
        pipe.execute()

    # TODO: simple concatenation will be faster then .format() function
    def _hash_key(self, id):
        return '{}:{}'.format(self._prefix, id)
