# coding: utf-8


import abc
import collections

import kombu
import boto3.session
from kombu.messaging import Producer

from core.utils import json

__all__ = ('create_amqp_pool', 'create_exchange',
           'create_aws_session', 'create_sns',
           'UserEvent', 'SystemEvent',
           'EventNotifier',
           'RabbitMQEventNotifier',
           'SnsEventNotifier', 'EmailEventNotifier')

UserEvent = collections.namedtuple('UserEvent', ['body', 'priority'])
SystemEvent = collections.namedtuple('SystemEvent', ['id', 'time', 'type',
                                                     'message'])


def create_amqp_pool(config):
    """
    :param config: Instance of `core.config.NotificationConfig`
    :return: Instance of `kombu.ConnectionPool`
    """
    return kombu.Connection(config.url).Pool()


def create_exchange(name, _type):
    return kombu.Exchange(name=name, type=_type)


def create_aws_session(config):
    return boto3.session.Session(aws_access_key_id=config.access_key,
                                 aws_secret_access_key=config.access_key_secret,  # noqa
                                 region_name=config.region)


def create_sns(session):
    return session.client('sns')


class EventNotifier(object):
    """
    Used to send notify about events.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def send(self, event):
        """
        Sends `event` to specified broker.
        :param event object to be sent
        """
        raise NotImplementedError


class RabbitMQEventNotifier(EventNotifier):
    def __init__(self, pool, routing_key, exchange, extra_properties=None):
        """
        :param pool: Instance of `kombu.connection.ConnectionPool`
        :param routing_key: str
        :param exchange: Instance of `kombu.messaging.Exchange`
        :param extra_properties: dict
        """
        self._pool = pool
        self._exchange = exchange
        self._routing_key = routing_key
        self._extra_properties = extra_properties or {}

    def send(self, event):
        with self._pool.acquire() as conn:
            producer = Producer(conn)
            producer.publish(event.body,
                             exchange=self._exchange,
                             routing_key=self._routing_key,
                             declare=[self._exchange],
                             headers=dict(
                                 RoutingKey=self._routing_key,
                                 Priority=str(event.priority)
                             ),
                             **self._extra_properties)


class SnsEventNotifier(EventNotifier):
    def __init__(self, sns, topic, subject, message_type):
        self._sns = sns
        self._topic = topic
        self._subject = subject
        self._message_type = message_type

    def send(self, event):
        self._sns.publish(TopicArn=self._topic, Subject=self._subject,
                          MessageStructure=self._message_type,
                          Message=self._prepare(event))

    @abc.abstractmethod
    def _prepare(self, event):
        """
        Returns formatted message ready to be send to sns
        :param event:
        :return:
        """
        raise NotImplementedError


class EmailEventNotifier(SnsEventNotifier):
    DEFAULT_FORMAT = '[{m.type}] at {m.time}: {m.message}'
    EMAIL_FORMAT = DEFAULT_FORMAT

    def _prepare(self, event):
        return json.dumps(dict(
            default=self.DEFAULT_FORMAT.format(m=event),
            email=self.EMAIL_FORMAT.format(m=event)
        ))
