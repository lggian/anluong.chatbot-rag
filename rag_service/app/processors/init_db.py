import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.orm import relationship
from app.models.base import Base
# Import tất cả các model để SQLAlchemy nhận diện được các bảng
from app.models.knowledge import KnowledgeBase, Document, DocumentChunk, DocumentUpload, ProcessingTask
from config import settings
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    chats = relationship("Chat", back_populates="user")
    knowledge_bases = relationship("KnowledgeBase", back_populates="user")

def init_database():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Đảm bảo DATABASE_URL trong config trỏ đúng tới MySQL của bạn
    engine = create_engine(settings.get_database_url)
    
    try:
        logger.info("--- Đang khởi tạo cấu trúc database RAG ---")
        # metadata.create_all sẽ quét tất cả class kế thừa từ Base đã được import
        Base.metadata.create_all(bind=engine)
        logger.info("[V] Thành công! Đã tạo xong: users, chats, messages, knowledge_bases, documents...")
        
    except Exception as e:
        logger.error(f"[X] Lỗi khi tạo bảng: {e}")

if __name__ == "__main__":
    init_database()