import os
import base64
import sys
import json, urllib, collections
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base
#URL

from xml.etree import ElementTree
from configparser import SafeConfigParser
from data_models import *


CONFIG_PATH = str(os.path.realpath(__file__))
CONFIG_PATH = CONFIG_PATH.replace("data.pyc", "")
CONFIG_PATH = CONFIG_PATH.replace("data.pyo", "")
CONFIG_PATH = CONFIG_PATH.replace("data.py", "")
CONFIG_PATH = CONFIG_PATH.replace("classes\managers","")
CONFIG_PATH = CONFIG_PATH + "../../config/"


def eout(e, message=""):
    print("Error in " + message, e)
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)


class Connection:
    def __init__(self):
        try:
            print("-----------------------------------------")
            print(" * Reading Config")
            config = SafeConfigParser()
            CONFIG_FILE = "config.ini"
            config.read(os.path.join(CONFIG_PATH, CONFIG_FILE))
            self.config = config
        except Exception as e:
            eout(e, message="Reading config: ")
        finally:
            print("-----------------------------------------")
            print(" * PostGres Connection Init")
            print("-----------------------------------------")

    def _build_cert(self, name, bfr):
        fh = open(name, "wb")
        fh.write(base64.b64decode(bfr))
        fh.close()
        return name

    def postgres(self):
        connection = None
        postgres = dict(self.config.items("pg_config", {}))
        # db_string = "postgresql+pygresql://" + user + ":" + password + "@" + host + ":" + port + "/" + database
        # connection = "postgresql://"":""@" + postgres.get("host") + "/" + postgres.get("db")
        connection = "postgresql://" + postgres.get("user") + ":" + postgres.get("passwd") + "@" + postgres.get("host") + "/" + postgres.get("db")

        return connection


class DataManager:
    def __init__(self, app):
        try:
            def getSession(postgres_connection):
                engine = create_engine(postgres_connection, poolclass=NullPool)
                engine.dialect.supports_sane_rowcount = engine.dialect.supports_sane_multi_rowcount = False
                db_session = scoped_session(sessionmaker(
                    autocommit=False,
                    autoflush=True,
                    expire_on_commit=False,
                    bind=engine
                ))
                Base = declarative_base()
                Base.query = db_session.query_property()

                Session = sessionmaker(bind=engine)
                conn = engine.connect()
                session = Session(bind=conn)
                return session
            self.pg_connection_string =     Connection().postgres()
        except Exception as e:
            self.eout(e, message="DataManager")

    def getSession(self):
        postgres_connection = self.get_pg_connection_string()
        engine = create_engine(postgres_connection, poolclass=NullPool)
        engine.dialect.supports_sane_rowcount = engine.dialect.supports_sane_multi_rowcount = False
        db_session = scoped_session(sessionmaker(
            autocommit=False,
            autoflush=True,
            expire_on_commit=False,
            bind=engine
        ))
        Base = declarative_base()
        Base.query = db_session.query_property()
        Session = sessionmaker(bind=engine)
        conn = engine.connect()
        session = Session(bind=conn)
        return session

    def closeSession(self, session):
        print("Closing Session")
        try:
            session.bind.close()
            session.close()
            print("Session Closed")
        except Exception as e:
            print('Error:', e)
            pass

    def get_pg_connection_string(self):
        return self.pg_connection_string

    def create_key(self, url, params):
        _key = [url]
        for key in params:
            _key.append(key)
            node = params[key]
            if type(node) is dict:
                for key1 in node:
                    _key.append(key1)
                    _key.append(str(node[key1]))
            else:
                _key.append(str(node))
        _key.sort()

        return ("_").join(_key).lower()

    def convert(self, data):
        if isinstance(data, basestring):
            return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(self.convert, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(self.convert, data))
        else:
            return data

    def eout(self, e, message=""):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(message, e)

    def getdictresult(self, labels, query_result):
        result = []

        for node in query_result:
            row = {}
            for key, value in zip(labels, node):
                row.setdefault(str(key), str(value))
            result.append(row)
        return result

    def get_settings(self):
        pg = self.getSession()
        period_date = ""
        self.settings_value = {}
        query_result = pg.query(ATTRIBUTES.field, ATTRIBUTES.value).all()

        labels = ("field", "value")
        setting_result = self.getdictresult(labels, query_result)
        #
        for node in setting_result:
            self.settings_value[node["field"]] = node["value"]
            if node["field"] == "Period":
                period_date = node["value"]

        self.closeSession(pg)
        return {'period': period_date}
