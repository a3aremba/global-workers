# coding: utf-8

import logging

from celery import signals
from core.app import task_dump
from core.dump import Task

logger = logging.getLogger(__name__)


@signals.task_failure.connect
def failed_task(task_id, exception, args, kwargs, sender, **kw):
    t = Task(task_id, sender.name, args, kwargs, str(exception))
    logger.info('Going to dump failed task: {}'.format(t))
    task_dump().dump(t)
