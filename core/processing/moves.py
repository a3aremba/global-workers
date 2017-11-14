# coding: utf-8


from __future__ import absolute_import

import datetime

import moves

from core import db
from core import app
from core.processing import BaseProcessing

__all__ = ('MovesProcessing',)

current_day_start = lambda: datetime.datetime.utcnow().replace(
    hour=0, minute=0, second=0, microsecond=0
)
current_day_end = lambda: datetime.datetime.utcnow().replace(
    hour=23, minute=59, second=59, microsecond=999
)


class MovesProcessing(BaseProcessing):
    DATE_FORMAT = '%Y%m%d'

    def process(self):
        self._check_and_add_final_data_collection()
        super(MovesProcessing, self).process()

    @property
    def _moves(self):
        connection = self._user_connection
        return moves.MovesClient(client_id=connection.access_token,
                                 client_secret=connection.access_token_secret,
                                 access_token=connection.oauth_token)

    def _call_api(self):
        try:
            day = self._request.processing_time
        except AttributeError:
            day = datetime.datetime.now()
        return self._moves.user_summary_daily(day.strftime(self.DATE_FORMAT))

    def _check_and_add_final_data_collection(self):
        request = self._request

        try:
            self._history_session.query(db.HistoricalData).filter(
                db.HistoricalData.user_id == request.user_id,
                db.HistoricalData.device_type_id == request.device_type,
                db.HistoricalData.real_event_type_name == request.event_type,
                db.HistoricalData.event_time.between(
                    current_day_start(), current_day_end()
                )
            ).first_or_raise()
        except db.NotFoundException:
            try:
                time = request.processing_time
            except AttributeError:
                time = datetime.datetime.now()
            eta = time.replace(day=time.day + 1, hour=2)

            kw = dict(user_id=request.user_id,
                      seq_id=request.sequence_id,
                      device_type=request.device_type,
                      event_type=request.event_type,
                      processing_timestamp=time.isoformat())
            app.app.send_task('core.tasks.process_event', kwargs=kw, eta=eta)
