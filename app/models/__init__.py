from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData
metadata = MetaData()
# Esto se importa de alembic/env.py para mapear los modelos a tablas y autogenerar las migrations
Base = declarative_base(metadata=metadata)
