# coding: utf-8


import datetime

import humanapi

from core import db
from core.processing import BaseProcessing


__all__ = ('HumanApiActivitiesProcessing',)


start_of_day = lambda: datetime.datetime.utcnow().replace(
    hour=0, minute=0, second=0, microsecond=0
)


class HumanApiActivitiesProcessing(BaseProcessing):
    @property
    def _human_connection(self):
        return (self._auth_session.query(db.HumanApiConnection).filter(
            db.HumanApiConnection.human_id == self._request.user_id
        ).first_or_raise())

    def _call_api(self):
        human = self._human_connection
        api = humanapi.HumanAPI(accessToken=human.access_token)
        return api.call('/activities/summaries?updated_since={}'.format(
            start_of_day().strftime('%Y%m%dT%H%M%SZ')
        ))
