# coding: utf-8

from core import dump
from celery import Celery
from core.config import load_config

__all__ = ('app', 'task_dump')

config = load_config()

app = Celery('core')
app.config_from_object(config.celery)

_redis_pool = dump.create_redis_pool(config.dump)


# TODO: consider factory
def task_dump(pool=_redis_pool):
    return dump.RedisDump(dump.create_redis(pool), prefix='tasks',
                          set_key='tasks:all')


def notify_dump(pool=_redis_pool):
    return dump.RedisDump(dump.create_redis(pool), prefix='notification',
                          set_key='notification:all')


if __name__ == '__main__':
    app.worker_main()
