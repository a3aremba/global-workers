# coding: utf-8

import sqlalchemy
import collections

from sqlalchemy.orm import Query
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from core.db.exc import NotFoundException
from sqlalchemy.ext.declarative import declarative_base

__all__ = ('create_engine', 'create_session', 'DatabaseConfig',
           'AuthModel', 'HistoryModel', 'CustomQuery')

AuthModel = declarative_base()
HistoryModel = declarative_base()


def create_engine(config):
    """
    :config should be config instance: of `config.DatabaseConfig`
    :return: Instance of `sqlalchemy.Engine`
    """
    return sqlalchemy.create_engine(config.url)


def create_session(bind):
    """
    Returns scoped `sqlalchemy.Session` factory
    """
    return scoped_session(sessionmaker(bind=bind, query_cls=CustomQuery))


class DatabaseConfig(collections.namedtuple('DatabaseConfig', ['url'])):
    """
    :param url: `sqlalchemy` connection url
    """
    __slots__ = ()


class CustomQuery(Query):
    """
    Extends `sqlalchemy.orm.Query` to add custom methods to session's query
    """

    def get_or_raise(self, _id):
        """
        Similar to `get`, but raises `NotFoundException` if no result found.
        """
        res = super(CustomQuery, self).get(_id)
        if not res:
            raise NotFoundException
        return res

    def first_or_raise(self):
        """
        Similar to `first`, but raises `NotFoundException` if no result found.
        """
        res = super(CustomQuery, self).first()
        if not res:
            raise NotFoundException
        return res
