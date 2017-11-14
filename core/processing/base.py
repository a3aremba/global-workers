# coding: utf-8


import abc
import enum
import datetime
from collections import namedtuple

from core import db
from core.app import user_event_notifier
from core.notify import UserEvent

__all__ = ('BaseProcessing', 'ProcessingRequest', 'TimedProcessingRequest',
           'Device')

ProcessingRequest = namedtuple('ProcessingRequest', ['user_id',
                                                     'sequence_id',
                                                     'device_type',
                                                     'event_type'])
TimedProcessingRequest = namedtuple('TimedProcessingRequest',
                                    ProcessingRequest._fields +
                                    ('processing_time',))

current_day_start = lambda: datetime.datetime.utcnow().replace(
    hour=0, minute=0, second=0, microsecond=0
)
current_day_end = lambda: datetime.datetime.utcnow().replace(
    hour=23, minute=59, second=59, microsecond=999
)


@enum.unique
class Device(enum.Enum):
    Fitbit = 1
    HumanApi = 3
    Moves = 6


class BaseProcessing(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, request, auth_session, history_session):
        """
        :param request: Instance of `core.processing.ProcessingRequest`
        """
        self._request = request
        self._auth_session = auth_session
        self._history_session = history_session

    def process(self):
        """
        Runs processing chain for specified provider.
        """
        data_from_api = self._call_api()
        self._save_to_historic_db(data_from_api)
        self._notify()

    @abc.abstractmethod
    def _call_api(self):
        """
        Performs call to API.
        :return: raw data
        """
        raise NotImplementedError

    def _save_to_historic_db(self, raw_data):
        event_type = self._history_session.query(db.EventType).filter(
            db.EventType.name == 'raw'
        ).first_or_raise()
        try:
            record = self._history_session.query(db.HistoricalData).filter(
                db.HistoricalData.user_id == self._request.user_id,
                db.HistoricalData.device_type_id == self._request.device_type,
                db.HistoricalData.real_event_type_name == self._request.event_type,  # noqa
                db.HistoricalData.event_time.between(
                    current_day_start(), current_day_end()
                )
            ).first_or_raise()
            record.event = raw_data
        except db.NotFoundException:
            record = db.HistoricalData(
                sequence_id=self._request.sequence_id,
                user_id=self._request.user_id,
                device_type_id=self._request.device_type,
                real_event_type_name=self._request.event_type,
                event_type=event_type,
                event=raw_data
            )
            self._history_session.add(record)
        self._history_session.commit()

    def _notify(self):
        user_event_notifier().send(UserEvent(dict(
            sequence_id=self._request.sequence_id,
            device_type=self._request.device_type,
            event_type=self._request.event_type
        ), 1))  # TODO(ak): fix hardcode

    @property
    def _user_connection(self):
        return (self._auth_session.query(db.UserConnection).filter_by(
            user_id=self._request.user_id).first_or_raise())
