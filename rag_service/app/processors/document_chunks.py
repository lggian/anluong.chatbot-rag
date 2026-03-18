import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.orm import relationship
from app.models.base import Base
# Import các model hiện có của bạn
from app.models.knowledge import KnowledgeBase, Document, DocumentChunk, DocumentUpload, ProcessingTask
from config import settings
from datetime import datetime

# --- KHAI BÁO BẢNG USERS Ở ĐÂY ---
# Vì KnowledgeBase tham chiếu đến 'users.id', chúng ta phải định nghĩa nó
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(
        DateTime, 
        nullable=False, 
        server_default=text("CURRENT_TIMESTAMP")
    )    
    # Khai báo quan hệ ngược lại để đồng bộ với models_knowledge
    knowledge_bases = relationship("KnowledgeBase", back_populates="user")

def create_tables():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Kết nối tới MySQL (Đảm bảo .env đã đổi thành localhost)
    engine = create_engine(settings.get_database_url)
    
    print("--- Đang khởi tạo toàn bộ cấu trúc database... ---")
    try:
        # Lệnh này sẽ tự động sắp xếp thứ tự: tạo 'users' trước, 'knowledge_bases' sau
        Base.metadata.create_all(bind=engine)
        print("[V] Chúc mừng! Đã tạo thành công tất cả các bảng (users, kbs, documents, chunks).")
    except Exception as e:
        print(f"[X] Lỗi nghiêm trọng: {e}")

if __name__ == "__main__":
    create_tables()