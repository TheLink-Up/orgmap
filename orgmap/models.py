from pyramid.security import Allow, Everyone
import json

from sqlalchemy import (
    Column,
    Integer,
    Text,
    Float
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(
    sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Org(Base):
    __tablename__ = 'org'
    uid = Column(Integer, primary_key=True)
    name = Column(Text)
    city = Column(Text)
    state = Column(Text)
    url = Column(Text)
    lat = Column(Float)
    lng = Column(Float)

    def __getitem__(self, item):
        return getattr(self, item)

    def __json__(self, request):
        return self.to_json()

    def to_json(self):
        _json = {k:v for k,v in self.__dict__.items() if k != '_sa_instance_state'}
        return json.dumps(_json, sort_keys=True)
