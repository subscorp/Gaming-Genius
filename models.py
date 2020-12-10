import os
from playhouse.db_url import connect  # for heroku 


from peewee import ( 
    BareField, ForeignKeyField, IntegerField, Model,
    SqliteDatabase, TextField,
)

#database = SqliteDatabase('trivia_game.db')
db = connect(os.environ.get('DATABASE_URL')) # for heroku 


class UnknownField(object):
    def __init__(self, *_, **__): 
        pass


class BaseModel(Model):
    class Meta:
        database = db


class Users(BaseModel):
    email = TextField()
    password = TextField()
    username = TextField()

    class Meta:
        table_name = 'users'


class Achievements(BaseModel):
    achievement_name = TextField()
    uri = TextField()

    class Meta:
        table_name = 'achievements'


class EasterEggs(BaseModel):
    name = TextField()

    class Meta:
        table_name = 'easter_eggs'


class Leaderboard(BaseModel):
    user_id = ForeignKeyField(Users)
    name = TextField()
    score = IntegerField()

    class Meta:
        table_name = 'leaderboard'


class SqliteSequence(BaseModel):
    name = BareField(null=True)
    seq = BareField(null=True)

    class Meta:
        table_name = 'sqlite_sequence'
        primary_key = False


class UserAchievements(BaseModel):
    achievement_id = ForeignKeyField(Achievements)
    user_id = ForeignKeyField(Users)

    class Meta:
        table_name = 'user_achievements'


class UserEasterEggs(BaseModel):
    easter_egg_id = ForeignKeyField(EasterEggs)
    user_id = ForeignKeyField(Users)

    class Meta:
        table_name = 'user_easter_eggs'