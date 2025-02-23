import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Table, Column, Text, Float, MetaData, select, insert
from sqlalchemy.orm import sessionmaker
from database import engine, SessionLocal  # Ensure correct import

metadata = MetaData()

# Define the Cache table
website_cache = Table(
    "Cache", metadata,
    Column("url", Text, primary_key=True, unique=True, nullable=False),
    Column("left", Float, nullable=False),
    Column("center", Float, nullable=False),
    Column("right", Float, nullable=False)
)

# Ensure table is created
metadata.create_all(engine)

# Initialize API router
cache = APIRouter()

# Request model
class CacheRequest(BaseModel):
    url: str
    left: float
    center: float
    right: float

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@cache.post("/cache")
async def check_and_insert_cache(request: CacheRequest, db=Depends(get_db)):
    """Checks if the URL exists in the cache. If not, inserts it."""
    query = select(website_cache.c.url, website_cache.c.left, website_cache.c.center, website_cache.c.right).where(website_cache.c.url == request.url)
    result = db.execute(query).fetchone()

    if result:
        return {"message": "Data retrieved from cache", "bias_analysis": {"Left": result[1], "Middle": result[2], "Right": result[3]}}

    # Insert new data
    try:
        db.execute(insert(website_cache).values(url=request.url, left=request.left, center=request.center, right=request.right))
        db.commit()
        return {"message": "Data inserted into cache", "bias_analysis": request.dict()}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
