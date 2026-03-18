from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, text
from datetime import datetime

Base = declarative_base()

class TimestampMixin:
    created_at = Column(
        DateTime, 
        nullable=False, 
        server_default=text("CURRENT_TIMESTAMP")
    )    
updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False) 