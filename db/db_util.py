import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import db_api
from . import db_table


DATABASE_URL = None


class DBConnector:

    def __init__(self, db_url, timeout=1):
        self.engine = create_engine(
            db_url,
            connect_args={
                "connect_timeout": timeout,
            },
        )
        self.DBSession = sessionmaker(bind=self.engine)

    def connect(self):
        """
        Returns:
            str: None if OK or returns err message.
        """
        try:
            self.engine.connect()
        except Exception as e:  # Can not connect.
            return e.message

        self.DBSession = sessionmaker(bind=self.engine)

    def execute(self, cmd):
        """ Execute SQL cmd. """
        return self.engine.execute(cmd)

    def session(self):
        return self.DBSession()


def session(timeout=5):
    db_connector = DBConnector(DATABASE_URL, timeout=timeout)
    return db_connector.session()


def engine(timeout=5):
    db_connector = DBConnector(DATABASE_URL, timeout=timeout)
    return db_connector.engine


@contextmanager
def session_context(timeout=5):
    db_connector = DBConnector(DATABASE_URL, timeout=timeout)
    s = db_connector.session()
    try:
        yield s
        s.commit()
    except:
        s.rollback()
        raise
    finally:
        s.close()