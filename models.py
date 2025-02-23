from sqlalchemy import Table, Column , MetaData
from sqlalchemy.sql.sqltypes import Boolean, Integer, String, Float
from database import engine

meta = MetaData()

Users = Table('Users', meta,
    Column('id', Integer, unique=True, primary_key=True),
    Column('username',String),
    Column('email', String),
    Column('is_superuser',Boolean),
    Column('password', String),
)

Cache = Table('cache', meta,
    Column("url", String, primary_key=True, unique=True, nullable=False),
    Column("left", Float),
    Column("center", Float),
    Column("right", Float),
)

meta.create_all(engine)