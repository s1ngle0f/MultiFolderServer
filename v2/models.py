from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP, BigInteger
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, index=True)
    login = Column(String(128), nullable = False)
    password = Column(String(64), nullable = False)

    directories = relationship('Directory', back_populates='user')

class Directory(Base):
    __tablename__ = 'directories'

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(128), nullable = False)
    user_id = Column(BigInteger, ForeignKey('users.id'))

    user = relationship('User', back_populates='directories')

    files = relationship('File', back_populates='directory')

class File(Base):
    __tablename__ = 'files'
    id = Column(BigInteger, primary_key=True, index=True)
    directory_id = Column(BigInteger, ForeignKey('directories.id'))
    path = Column(String(512), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)
    size = Column(BigInteger, nullable=False)

    directory = relationship('Directory', back_populates='files')
