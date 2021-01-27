from sqlalchemy import Column, Integer, String, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ReplySetting(Base):
    __tablename__ = 'replysetting'

    stickerreply = Column(BOOLEAN, primary_key=True)


class PushMessageSetting(Base):
    __tablename__ = 'pushmsgsetting'

    targetid = Column(String, primary_key=True)
    push     = Column(BOOLEAN)
    desc     = Column(String)
