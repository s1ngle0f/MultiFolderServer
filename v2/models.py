# from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP, BigInteger
# from sqlalchemy.orm import relationship
#
# from database import Base
from peewee import *


db = PostgresqlDatabase('multifolder', user='postgres', password='6010', host='localhost', port=5432)

class BaseModel(Model):
    class Meta:
        database = db
        order_by = 'id'

class User(BaseModel):
    id = BigAutoField(primary_key=True, unique=True)
    login = CharField(max_length=128, null=False)
    password = CharField(max_length=64, null=False)

    class Meta:
        table_name = 'users'

class Directory(BaseModel):
    id = BigAutoField(primary_key=True, unique=True)
    name = CharField(max_length=128, null=False)
    user_id = ForeignKeyField(User, field='id')

    class Meta:
        table_name = 'directories'

class File(BaseModel):
    id = BigAutoField(primary_key=True, unique=True)
    directory_id = ForeignKeyField(Directory, field='id')
    name = CharField(max_length=512, null=False)
    path = CharField(max_length=512, null=False)
    timestamp = TimestampField(null=False)
    size = BigIntegerField()
    data = BlobField()

    class Meta:
        table_name = 'files'

# class User(Base):
#     __tablename__ = 'users'
#
#     id = Column(BigInteger, primary_key=True, index=True)
#     login = Column(String(128), nullable = False)
#     password = Column(String(64), nullable = False)
#
#     directories = relationship('Directory', back_populates='user')
#
# class Directory(Base):
#     __tablename__ = 'directories'
#
#     id = Column(BigInteger, primary_key=True, index=True)
#     name = Column(String(128), nullable = False)
#     user_id = Column(BigInteger, ForeignKey('users.id'))
#
#     user = relationship('User', back_populates='directories')
#
#     files = relationship('File', back_populates='directory')
#
# class File(Base):
#     __tablename__ = 'files'
#     id = Column(BigInteger, primary_key=True, index=True)
#     directory_id = Column(BigInteger, ForeignKey('directories.id'))
#     path = Column(String(512), nullable=False)
#     timestamp = Column(TIMESTAMP, nullable=False)
#     size = Column(BigInteger, nullable=False)
#
#     directory = relationship('Directory', back_populates='files')
