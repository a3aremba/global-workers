# coding: utf-8


from __future__ import absolute_import

import abc
import datetime

import fitbit
from fitbit.exceptions import HTTPTooManyRequests


from core.processing import BaseProcessing
from core.processing.exc import (
    ProcessingDelayedException,
    ProcessingRetryLimitException
)

__all__ = ('FitbitActivitiesProcessing', 'FitbitBodyProcessing',
           'FitbitSleepProcessing')


class BaseFitbitProcessing(BaseProcessing):
    __metaclass__ = abc.ABCMeta

    def _call_api(self):
        now = datetime.datetime.now()
        user_connection = self._user_connection

        if user_connection.delay_till and user_connection.delay_till > now:
            raise ProcessingDelayedException

        try:
            return self._call_fitbit()
        except HTTPTooManyRequests as e:
            user_connection.delay_till = now + datetime.timedelta(
                seconds=e.retry_after_secs)
            self._auth_session.commit()
            raise ProcessingRetryLimitException(retry=e.retry_after_secs)

    @property
    def _fitbit(self):
        user = self._user_connection
        client = fitbit.Fitbit(user.access_token, user.access_token_secret,
                               resource_owner_key=user.q_token,
                               resource_license_plate=rollout_plate,
                               resource_owner_secret=user.oauth_token_secret)
        return client

    @abc.abstractmethod
    def _call_fitbit(self):
        raise NotImplementedError


class FitbitActivitiesProcessing(BaseFitbitProcessing):
    def _call_fitbit(self):
        return self._fitbit.activities()


class FitbitBodyProcessing(BaseFitbitProcessing):
    def _call_fitbit(self):
        return self._fitbit.bp()


class FitbitSleepProcessing(BaseFitbitProcessing):
    def _call_fitbit(self):
        return self._fitbit.sleep()
