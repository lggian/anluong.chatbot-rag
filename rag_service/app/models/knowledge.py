from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, JSON, BigInteger, text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
from datetime import datetime
import sqlalchemy as sa

class KnowledgeBase(Base, TimestampMixin):
    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(LONGTEXT)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    documents = relationship("Document", back_populates="knowledge_base", cascade="all, delete-orphan")
    user = relationship("User", back_populates="knowledge_bases")
    processing_tasks = relationship("ProcessingTask", back_populates="knowledge_base")
    chunks = relationship("DocumentChunk", back_populates="knowledge_base", cascade="all, delete-orphan")
    document_uploads = relationship("DocumentUpload", back_populates="knowledge_base", cascade="all, delete-orphan")

class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50))
    kb_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False)
    
    knowledge_base = relationship("KnowledgeBase", back_populates="documents")
    processing_tasks = relationship("ProcessingTask", back_populates="document")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentUpload(Base, TimestampMixin):
    __tablename__ = "document_uploads"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    temp_path = Column(String(500), nullable=True) # Đã thêm độ dài
    file_size = Column(BigInteger)
    content_type = Column(String(100))
    file_hash = Column(String(64), index=True)
    status = Column(String(50), nullable=False, server_default="pending") # Đã thêm độ dài (50)
    error_message = Column(Text) # Kiểu Text thì OK, không cần độ dài
    kb_id = Column(Integer, sa.ForeignKey("knowledge_bases.id"), nullable=False)
    
    knowledge_base = relationship("KnowledgeBase", back_populates="document_uploads")

class ProcessingTask(Base):
    __tablename__ = "processing_tasks"

    id = Column(Integer, primary_key=True, index=True)
    kb_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    status = Column(String(50), default="pending") # Đã thêm độ dài (50)
    error_message = Column(Text, nullable=True)
    class TimestampMixin:
        created_at = Column(
            DateTime, 
            nullable=False, 
            server_default=text("CURRENT_TIMESTAMP")
        )   
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    knowledge_base = relationship("KnowledgeBase", back_populates="processing_tasks")
    document = relationship("Document", back_populates="processing_tasks")

class DocumentChunk(Base, TimestampMixin):
    __tablename__ = "document_chunks"

    id = Column(String(64), primary_key=True) 
    kb_id = Column(Integer, ForeignKey("knowledge_bases.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    chunk_metadata = Column(JSON, nullable=True)
    hash = Column(String(64), nullable=False, index=True)
    
    knowledge_base = relationship("KnowledgeBase", back_populates="chunks")
    document = relationship("Document", back_populates="chunks")
    
    __table_args__ = (
        sa.Index('idx_kb_file_name', 'kb_id', 'file_name'),
    ) 