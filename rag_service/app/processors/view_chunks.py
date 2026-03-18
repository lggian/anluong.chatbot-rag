import json
from sqlalchemy import create_engine, text

# Kết nối DB
engine = create_engine("mysql+mysqlconnector://ragwebui:ragwebui@localhost:3306/ragwebui")

with engine.connect() as conn:
    result = conn.execute(text("SELECT chunk_metadata FROM document_chunks LIMIT 5"))
    for i, row in enumerate(result):
        # Chuyển string sang Dict
        meta = json.loads(row[0]) if isinstance(row[0], str) else row[0]
        
        print(f"\n--- CHUNK {i+1} ---")
        # In ra tất cả các key để xem key nào chứa nội dung
        print(f"Các phím (Keys) có trong metadata: {list(meta.keys())}")
        
        # Thử tìm nội dung trong các key phổ biến
        content = meta.get('page_content') or meta.get('text') or "Không tìm thấy nội dung văn bản!"
        print(f"Nội dung trích đoạn: {str(content)[:200]}...")