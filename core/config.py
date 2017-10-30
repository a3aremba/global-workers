# coding: utf-8


import os
from collections import namedtuple

from core import utils
from core.db import DatabaseConfig
from core.dump import DumpConfig

__all__ = ('load_config', 'AWSConfig', 'RabbitMQConfig')

AWSConfig = namedtuple('AWSConfig', 'access_key, access_key_secret, region')
SNSConfig = namedtuple('SNSConfig', 'topic, subject, message_type')


def raise_or_return(prop, prop_name):
    """
    Raises `ValueError` if `prop` is None. Returns it otherwise.
    """
    utils.raise_on(prop is not None, "'{}' is None".format(prop_name))
    return prop


def load_config():
    """
    Returns config object with default values that can be overridden by
    env variables.
    """
    return Config(
        celery_broker_url=os.getenv('CELERY_BROKER_URL', 'redis://'),
        celery_result_backend_url=os.getenv('CELERY_RESULT_URL', 'redis://'),
        auth_db_url=os.getenv('AUTH_DB_URL',
                              'postgresql+pg8000://core:core@/user_auth_test'),
        history_db_url=os.getenv('HISTORY_DB_URL',
                                 'postgresql+pg8000://core:core@/history_test'),
        dump_url=os.getenv('DUMP_URL', 'redis://'),
        rabbitmq_url=os.getenv('NOTIFICATION_URL',
                               'amqp://guest:guest@localhost:5672//'),
        rabbitmq_exchange='Burrow.Exchange',
        rabbitmq_exchange_type='headers',
        rabbitmq_routing_key='TestCommunicationMessage',
        rabbitmq_message_type=('SocialWellth_Integrations_OAsis_Models'
                               '_TestCommunicationMessage:SocialWellth'
                               '_Integrations_OAsis')
    )


class Config(object):
    def __init__(self,
                 celery_broker_url=None, celery_result_backend_url=None,
                 auth_db_url=None, history_db_url=None, dump_url=None,
                 rabbitmq_url=None, rabbitmq_exchange=None,
                 rabbitmq_exchange_type=None,
                 rabbitmq_routing_key=None,
                 rabbitmq_message_type=None
                 ):

        self._celery_broker_url = raise_or_return(
            celery_broker_url, 'celery_broker_url')
        self._celery_result_backend_url = raise_or_return(
            celery_result_backend_url, 'celery_result_backend_url')
        self._auth_db_url = raise_or_return(auth_db_url, 'auth_db_url')
        self._history_db_url = raise_or_return(history_db_url,
                                               'history_db_url')
        self._dump_url = raise_or_return(dump_url, 'dump_url')
        self._rabbitmq_url = raise_or_return(rabbitmq_url,
                                             'rabbitmq_url')
        self._rabbitmq_exchange = raise_or_return(rabbitmq_exchange,
                                                  'rabbitmq_exchange')
        self._rabbitmq_exchange_type = raise_or_return(
            rabbitmq_exchange_type, 'rabbitmq_exchange_type')
        self._rabbitmq_routing_key = raise_or_return(
            rabbitmq_routing_key, 'rabbitmq_routing_key')
        self._rabbitmq_message_type = raise_or_return(
            rabbitmq_message_type, 'rabbitmq_message_type')

    @property
    def celery(self):
        return dict(
            BROKER_URL=self._celery_broker_url,
            CELERY_RESULT_BACKEND=self._celery_result_backend_url,
            CELERY_ENABLE_UTC=True,
            CELERY_ACCEPT_CONTENT=('json',),
            CELERY_TASK_SERIALIZER='json',
            CELERY_RESULT_SERIALIZER='json',
            CELERYD_TASK_SOFT_TIME_LIMIT=60,
            CELERYD_TASK_TIME_LIMIT=120,
            CELERY_MESSAGE_COMPRESSION='gzip',
            CELERY_DISABLE_RATE_LIMITS=True,
            CELERY_IMPORTS=('core.tasks', 'core.signals')
        )

    @property
    def auth_db(self):
        return DatabaseConfig(self._auth_db_url)

    @property
    def history_db(self):
        return DatabaseConfig(self._history_db_url)

    @property
    def dump(self):
        return DumpConfig(self._dump_url)
