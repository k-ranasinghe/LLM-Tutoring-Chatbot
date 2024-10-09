from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, String, DateTime, LargeBinary
from sqlalchemy.sql.sqltypes import Integer
from datetime import datetime, timezone
import os

# Load environment variables
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DB = os.getenv("MYSQL_DB")

# Create SQLAlchemy engine
engine = create_engine(f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}")

# Define metadata
meta = MetaData()

# Connect to the database
conn = engine.connect()

# Define tables
lecture_materials = Table(
    'lecture_materials', meta,
    Column('id', Integer, primary_key=True),
    # Column('file', String(255)), 
    Column('file_name', String(255)),  
    Column('file_type', String(255)), 
    Column('uploaded_at', DateTime, default=lambda: datetime.now(timezone.utc))
)

# Create all tables in the database
meta.create_all(engine)