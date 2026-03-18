import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from config import settings
from app.models.knowledge import KnowledgeBase, Document
from app.processors.document_chunks import User 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_test_data():
    engine = create_engine(settings.get_database_url)
    
    with Session(engine) as session:
        try:
            logger.info("--- Đang tạo mẫu dữ liệu ---")
            
            # 1. Tạo User admin (ID=1)
            user = session.get(User, 1)
            if not user:
                user = User(
                    id=1, 
                    username="admin", 
                    email="admin@example.com", 
                    hashed_password="123" # Pass giả lập
                )
                session.add(user)
                logger.info("[+] Đã tạo User ID 1")

            # 2. Tạo Knowledge Base (ID=1)
            kb = session.get(KnowledgeBase, 1)
            if not kb:
                kb = KnowledgeBase(
                    id=1, 
                    name="Kho tri thuc Test", 
                    user_id=1
                )
                session.add(kb)
                logger.info("[+] Đã tạo KnowledgeBase ID 1")

            # 3. Tạo Document (ID=1)
            doc = session.get(Document, 1)
            if not doc:
                doc = Document(
                    id=1, 
                    file_name="huong_dan_su_dung.pdf", 
                    file_path="huong_dan_su_dung.pdf", 
                    kb_id=1
                )
                session.add(doc)
                logger.info("[+] Đã tạo Document ID 1")

            session.commit()
            logger.info("--- Tạo mẫu dữ liệu THÀNH CÔNG ---")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Lỗi khi tạo mẫu dữ liệu: {e}")

if __name__ == "__main__":
    seed_test_data()