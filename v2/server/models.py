from peewee import *


# db = PostgresqlDatabase('multifolder', user='postgres', password='6010', host='db', port=5432)
db = PostgresqlDatabase('multifolder', user='postgres', password='6010', host='45.141.103.92', port=5431)

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

class LastTimeModification(BaseModel):
    id = BigAutoField(primary_key=True, unique=True)
    directory_id = ForeignKeyField(Directory, field='id')
    timestamp = TimestampField(null=False)

    class Meta:
        table_name = 'last_time_modification'

class File(BaseModel):
    id = BigAutoField(primary_key=True, unique=True)
    directory_id = ForeignKeyField(Directory, field='id')
    name = CharField(max_length=512, null=False)
    path = CharField(max_length=512, null=False)
    timestamp = TimestampField(null=False)
    size = BigIntegerField()
    # data = BlobField()

    class Meta:
        table_name = 'files'

class Tokens(BaseModel):
    token = CharField(primary_key=True, unique=True, max_length=64)
    user_id = ForeignKeyField(User, field='id', null=False)

    class Meta:
        table_name = 'tokens'