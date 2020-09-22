# - coding: utf-8 -

from sqlalchemy import MetaData, create_engine, Column, String, Date, Integer, UniqueConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib
import datetime


metadata = MetaData()
engine = create_engine('mssql+pymssql://sa:{}@localhost:1433/clouddb'.format(urllib.parse.quote_plus('1835rd@')))
Base = declarative_base()
db_session = sessionmaker(bind=engine)()


class PigIll(Base):
    __tablename__ = 'pig_ill'
    __table_args__ = {"extend_existing": True}
    damagestartdate = Column(String, primary_key=True)
    damagestartplace = Column(String, primary_key=True)
    cunlan = Column(Integer)
    items = Column(Integer)
    damage_items = Column(Integer)
    region = Column(String)


class User(Base):
    __tablename__ = 'meteo_users'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    username = Column(String(128), nullable=False, index=True)
    password = Column(String(128), nullable=False)
    region = Column(String(128), nullable=False)
    iconPath = Column(String(256), nullable=True)
    UniqueConstraint(username, region, name='PK_User_username_region')


class Document(Base):
    __tablename__ = 'meteo_doc'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    publish_datetime = Column(DateTime, nullable=False)
    filePath = Column(String(500), nullable=False)
    region = Column(String(128), nullable=False)


Base.metadata.create_all(engine)

def get_records():
    return db_session.query(PigIll)

def get_loss_times(record):
    days = int(record.damagestartdate)-1
    startdate = datetime.date(1900,1,1)
    return startdate + datetime.timedelta(days=days) ## problem excel

def get_cunlan(record):
    return record.cunlan

def get_loss(record):
    return record.items

def get_damage(record):
    return record.damage_items

def get_place(record):
    return record.region, record.damagestartplace

data = get_records()
CITIES = [get_place(r) for r in data]

def get_users():
    return db_session.query(User)

users = get_users()
