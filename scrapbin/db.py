
import json

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative

from sqlalchemy import Column, Integer, String, DateTime

Base = sqlalchemy.ext.declarative.declarative_base()

session_fact = None
engine = None

def get_session():
    if session_fact is None:
        global engine
        engine = sqlalchemy.create_engine('sqlite:///scrapbin.db')
        global session_fact
        session_fact = sqlalchemy.orm.sessionmaker(bind=engine)

    return session_fact()


class Run(Base):
    __tablename__ = 'runs'

    id = Column(String, primary_key=True)
    status = Column(String)
    run_list = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    _data = Column('data', String)
    _resources = Column('resources', String)
    total_res_count = Column(Integer)
    node = Column(String)

    _attrs = ['id', 'status', 'run_list', 'start_time',
              'end_time', 'total_res_count', 'node',
              'data', 'resources']

    @property
    def resources(self):
        return json.loads(self._resources)

    @resources.setter
    def resources(self, value):
        self._resources = json.dumps(value)

    @property
    def data(self):
        return json.loads(self._data)

    @data.setter
    def data(self, value):
        self._data = json.dumps(value)

    def __init__(self, **kwargs):
        for attr in self._attrs:
            setattr(self, attr, kwargs.get(attr))

    def __repr__(self):
        return "<Run(id='%s', status='%s')>" % (self.id, self.status)

    def to_json(self):
        return { attr: getattr(self, attr) for attr in self._attrs }
