# coding: utf-8


import uuid
import datetime

import iso8601

from core.app import app
from core.app import notify_dump
from core.app import system_event_notifier
from core.notify import SystemEvent
from core.processing import TimedProcessingRequest
from core.processing import create_processing
from core.processing.exc import ProcessingRetryLimitException


__all__ = ('process_event', 'notify_error')


@app.task
def process_event(user_id=None, seq_id=None, device_type=None,
                  event_type=None, processing_timestamp=None):
    try:
        processing_time = iso8601.parse_date(processing_timestamp)
    except iso8601.ParseError:
        processing_time = datetime.datetime.now()

    request = TimedProcessingRequest(user_id, seq_id, device_type,
                                     event_type, processing_time)

    try:
        with create_processing(request) as processing:
            processing.process()
    except ProcessingRetryLimitException as e:
        process_event.retry(countdown=e.retry, exc=e)


@app.task
def notify_error(time, err_type, message):
    event = SystemEvent(str(uuid.uuid4()), time, err_type, message)
    try:
        system_event_notifier().send(event)
    except Exception as exc:
        raise notify_error.retry(countdown=10, exc=exc, max_retry=3)

    notify_dump().dump(event)
