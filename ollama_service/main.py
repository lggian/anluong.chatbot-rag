# ollama_service/main.py
from fastapi import FastAPI
import ollama
import uvicorn
from pydantic import BaseModel

class ChatInput(BaseModel):
    prompt: str
app = FastAPI()

@app.post("/generate")
async def generate(input: ChatInput):
    res = ollama.generate(model="llama3", prompt=input.prompt)
    return {"response": res["response"]}
    
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)