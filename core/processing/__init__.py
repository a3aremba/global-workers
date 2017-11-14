# coding: utf-8


import contextlib

from core import app
from core.processing.exc import (
    ProcessingException,
    UnknownProcessingTypeException
)
from core.processing.base import (
    Device,
    BaseProcessing,
    ProcessingRequest,
    TimedProcessingRequest
)
from core.processing.fitbit import (
    FitbitActivitiesProcessing,
    FitbitBodyProcessing,
    FitbitSleepProcessing
)
from core.processing.moves import MovesProcessing
from core.processing.human import HumanApiActivitiesProcessing

__all__ = ('get_processing', 'create_processing', 'Device',
           'ProcessingException', 'UnknownProcessingTypeException',
           'BaseProcessing', 'FitbitActivitiesProcessing',
           'FitbitBodyProcessing', 'FitbitSleepProcessing',
           'MovesProcessing', 'ProcessingRequest', 'TimedProcessingRequest')

device_event_processing_mapping = {
    (Device.Fitbit.value, 'activities'): FitbitActivitiesProcessing,
    (Device.Fitbit.value, 'bp'): FitbitBodyProcessing,
    (Device.Fitbit.value, 'sleep'): FitbitSleepProcessing,
    (Device.HumanApi.value, 'update'): HumanApiActivitiesProcessing,  # TODO: fix
    (Device.Moves.value, 'DataUpload'): MovesProcessing
}


def get_processing(device_type, event_type):
    """
    Returns processing class that can process specified type.
    Raises UnknownProcessingTypeException if type is unknown
    :param device_type:
    :param event_type:
    :return:
    :raises: UnknownProcessingTypeException
    """
    try:
        return device_event_processing_mapping[(device_type, event_type)]
    except KeyError:
        raise UnknownProcessingTypeException("Unable to create processing for "
                                             "device_type '{}' and "
                                             "event_type '{}'"
                                             .format(device_type, event_type))


@contextlib.contextmanager
def create_processing(request, auth_session=app.AuthSession,
                      history_session=app.HistorySession):
    """
    :param request: Instance of `core.processing.ProcessingRequest`
    :param auth_session: Factory of auth db `sqlalchemy.Session`
    :param history_session: Factory of history db `sqlalchemy.Session`
    :return: subclass of `core.processing.BaseRequest`
    """
    if not request:
        raise ValueError("Processing requires not null 'request' arg")
    if not request.user_id:
        raise ValueError("Processing requires not null 'user_id'")
    if not request.sequence_id:
        raise ValueError("Processing requires not null 'sequence_id'")
    processing = get_processing(request.device_type, request.event_type)
    yield processing(request, auth_session(), history_session())
