import shutil
import sys
import os
import httpx
import database
try:
    import ollama
except ImportError:
    ollama = None
import logging
from typing import List
from pathlib import Path
import uvicorn

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse


from document_processor import process_document
from services.vector_store.factory import VectorStoreFactory
from services.embedding.embedding_factory import EmbeddingsFactory
from config import settings
from app.core.llm_client import call_llm
from app.core.minio import get_minio_client
from chat_service import generate_response
from database.session import get_db



# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Mount các thư mục cần thiết
app.mount("/img", StaticFiles(directory="img"), name="img")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo Vector Store để dùng cho việc tìm kiếm (Chat)
# Giả sử dùng kb_id mặc định là 1 để test
embeddings = EmbeddingsFactory.create()
vector_store = VectorStoreFactory.create(
    store_type=settings.VECTOR_STORE_TYPE,
    collection_name="kb_1",
    embedding_function=embeddings,
)

@app.get("/")   
async def serve_ui():
    return FileResponse("index.html")

# Thư mục lưu file tạm trên server
UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    size: int = 800,
    overlap: int = 100
):
    client = get_minio_client()

    total_chunks = 0
    for file in files:
        temp_path = UPLOAD_DIR / file.filename
        try:
            # 1. Lưu file vào thư mục dataset (để process_document có thể đọc)
            with temp_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            # Chuẩn hóa tên file cho Windows (thay \ bằng /)
            object_name = str(temp_path).replace('\\', '/')

            client.fput_object(
                bucket_name=settings.MINIO_BUCKET_NAME,
                object_name=object_name,
                file_path=str(temp_path)
            )

            # 2. Gọi hàm process_document từ file document_processor.py của bạn
            # Hàm này đã bao gồm: Load -> Split -> Embed -> Save to ChromaDB
            new_chunks = await process_document(
                file_path=str(temp_path),
                file_name=file.filename,
                kb_id=1,        # ID mặc định
                document_id=1,  # ID mặc định
                chunk_size=size,
                chunk_overlap=overlap
            )
            total_chunks += len(new_chunks)
            
        except Exception as e:
            logger.error(f"Lỗi xử lý file {file.filename}: {str(e)}")
            continue
        finally:
            if temp_path.exists():
                temp_path.unlink()

    return {"message": f"Thành công! Đã xử lý {len(files)} file, tạo ra {total_chunks} đoạn."}

class ChatRequest(BaseModel):
    message: str
    chat_id: int = 1
    kb_id: List[int] = [1]
    history: List[dict] = []  # Có thể chứa các message trước đó nếu cần thiết

@app.post("/ask")
async def ask(q: str):
    answer = await call_llm(q)
    return {"answer": answer}

@app.post("/chat")
async def handle_chat(req: ChatRequest):
    try:
        messages_payload ={
            "message": req.history + [{"role": "user", "content": req.message}]
        }
        
        return StreamingResponse(
            generate_response(
                query=req.message,
                messages=messages_payload,
                kb_ids=req.kb_id,
                chat_id=req.chat_id,
                db= get_db()
                ), 
            media_type="text/event-stream",
            )
        # # 1. Tìm kiếm context liên quan từ Vector Store
        # # Sử dụng phương thức similarity_search có sẵn trong LangChain VectorStore
        # docs = vector_store.similarity_search(req.message, k=3)
        # context_text = "\n---\n".join([doc.page_content for doc in docs])

        # # 2. Tạo Prompt chuyên nghiệp
        # full_prompt = f"""
        # Bạn là một trợ lý HR chuyên nghiệp. Hãy dựa vào tài liệu dưới đây để trả lời câu hỏi.
        # Nếu tài liệu không có thông tin, hãy nói bạn không biết, đừng tự chế câu trả lời.

        # TÀI LIỆU:
        # {context_text}

        # CÂU HỎI: {req.message}
        # """

        # # # 3. Gọi Ollama
        # # response = ollama.generate(model='llama3', prompt=full_prompt)
        # # return {"response": response['response']}
    
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         "http://localhost:8002/generate", 
        #         json={"prompt": full_prompt},
        #         timeout=180.0
        #     )
            
        #     # if response.status_code != 200:
        #     #     return {"response": f"AI Service lỗi (Code: {response.status_code})"}
            
        #     result = response.json()
        #     return {"response": result["response"]}
            
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return {"response": "Xin lỗi, đã có lỗi xảy ra trong quá trình truy vấn."}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)