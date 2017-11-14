# coding: utf-8


import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Sequence,
    DateTime,
    ForeignKeyConstraint,
    PrimaryKeyConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB

from core.db import AuthModel
from core.db import HistoryModel

__all__ = ('UserConnection', 'HumanApiConnection',
           'EventType', 'HistoricalData')

current_datetime = lambda: datetime.datetime.utcnow()


class UserConnection(AuthModel):
    __tablename__ = 'user_connection'
    __table_args__ = (
        PrimaryKeyConstraint(name='user_connection_pkey'),
    )

    id = Column('user_connection_id', Integer,
                Sequence('user_connection_user_connection_id_seq'),
                primary_key=True)
    user_id = Column(String(50))
    access_token = Column(String(64))
    access_token_secret = Column(String(50))
    oauth_token = Column(String(64))
    oauth_token_secret = Column(String(50))
    delay_till = Column(DateTime())
    device_type_id = Column(Integer)

    def __init__(self, user_id, oauth_token, oauth_token_secret,
                 access_token, access_token_secret, delay_till=None):
        self.user_id = user_id
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.delay_till = delay_till

    def __repr__(self):
        return "<UserConnection(user_id='{.user_id}')>".format(self)


class HumanApiConnection(AuthModel):
    __tablename__ = 'human_api_connection'
    __table_args__ = (
        PrimaryKeyConstraint(name='human_api_connection_pkey'),
    )

    id = Column('human_api_connection_id', Integer,
                Sequence('human_api_connection_human_api_connection_id_seq'),
                primary_key=True)
    human_id = Column(String(64))
    access_token = Column(String(500))
    public_token = Column(String(64))
    client_id = Column(String(64))
    client_user_id = Column(String(64))
    person_id = Column(Integer)


class EventType(HistoryModel):
    __tablename__ = 'lookup_event_type'
    __table_args__ = (
        PrimaryKeyConstraint(name='lookup_event_type_pkey'),
    )

    id = Column('event_type_id', Integer, primary_key=True)
    name = Column(String(50))

    def __init__(self, event_type_id, name):
        self.id = event_type_id
        self.name = name


class HistoricalData(HistoryModel):
    __tablename__ = 'historical_data'
    __table_args__ = (
        PrimaryKeyConstraint(name='historical_data_pkey'),
        ForeignKeyConstraint(['event_type_id'],
                             ['lookup_event_type.event_type_id'],
                             name='event_type_FK')
    )

    id = Column('historical_data_id', Integer,
                Sequence('historical_data_historical_data_id_seq'),
                primary_key=True)
    user_id = Column(String(50))
    device_type_id = Column(Integer)
    event = Column(JSONB)
    sequence_id = Column(String(70))
    real_event_type_name = Column(String(50))
    event_type_id = Column(Integer, nullable=False)
    event_time = Column('datetime', DateTime, default=current_datetime,
                        onupdate=current_datetime)

    event_type = relationship('EventType')

    def __init__(self, sequence_id, user_id, device_type_id,
                 real_event_type_name, event_type, event):
        self.sequence_id = sequence_id
        self.user_id = user_id
        self.device_type_id = device_type_id
        self.real_event_type_name = real_event_type_name
        self.event_type = event_type
        self.event = event

    def __repr__(self):
        return ("<HistoricalData("
                "user_id='{.user_id}', "
                "sequence_id='{.sequence_id}', "
                "device_type_id='{.device_type_id}', "
                "event_type_id='{.event_type_id}', "
                "event_type_name='{.real_event_type_name}')>".format(self))
