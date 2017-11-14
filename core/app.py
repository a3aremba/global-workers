# coding: utf-8

from celery import Celery

from core import db
from core import dump
from core import notify
from core.config import load_config

__all__ = ('app', 'task_dump', 'user_event_notifier', 'AuthSession',
           'HistorySession')

config = load_config()

app = Celery('core')
app.config_from_object(config.celery)

_redis_pool = dump.create_redis_pool(config.dump)
_amqp_pool = notify.create_amqp_pool(config.rabbitmq)
_aws_session = notify.create_aws_session(config.aws)
auth_db = db.create_engine(config.auth_db)
history_db = db.create_engine(config.history_db)

AuthSession = db.create_session(auth_db)
HistorySession = db.create_session(history_db)


# TODO(ak): consider factory
def task_dump(pool=_redis_pool):
    return dump.RedisDump(dump.create_redis(pool), prefix='tasks',
                          set_key='tasks:all')


def notify_dump(pool=_redis_pool):
    return dump.RedisDump(dump.create_redis(pool), prefix='notification',
                          set_key='notification:all')


# TODO(ak): consider factory
def user_event_notifier(pool=_amqp_pool):
    return notify.RabbitMQEventNotifier(pool, config.rabbitmq.routing_key,
                                        notify.create_exchange(
                                            config.rabbitmq.exchange,
                                            config.rabbitmq.exchange_type),
                                        dict(
                                            type=config.rabbitmq.message_type
                                        ))


def system_event_notifier(session=_aws_session):
    return notify.EmailEventNotifier(notify.create_sns(session),
                                     topic=config.sns.topic,
                                     subject=config.sns.subject,
                                     message_type=config.sns.message_type)


if __name__ == '__main__':
    app.worker_main()
