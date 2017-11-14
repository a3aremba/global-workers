# coding: utf-8


import logging
import logstash

from celery import signals

from core.app import task_dump
from core.dump import Task
from core.app import config

logger = logging.getLogger(__name__)


@signals.task_failure.connect
def failed_task(task_id, exception, args, kwargs, sender):
    t = Task(task_id, sender.name, args, kwargs, str(exception))
    logger.info('Going to dump failed task: {}'.format(t))
    task_dump().dump(t)


@signals.after_setup_logger.connect
@signals.after_setup_task_logger.connect
def after_setup_logger_handler(logger=None):
    logger.addHandler(logstash.TCPLogstashHandler(host=config.logstash.host,
                                                  port=config.logstash.port,
                                                  version=1))
