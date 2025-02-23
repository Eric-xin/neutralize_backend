import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import Table, Column, Text, MetaData, select
from sqlalchemy.orm import sessionmaker
from database import conn, engine, SessionLocal

metadata = MetaData()

credit = APIRouter()

# Define the credits table
credits = Table(
    "Credits", metadata,
    Column("user", Text, primary_key=True, unique=True, nullable=False), 
    Column("credit", int, nullable=False),
)
