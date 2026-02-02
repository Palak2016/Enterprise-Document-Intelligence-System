import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from backend.rag_engine import RAGEngine # Humare logic engine ko import kar rahe hain

router=APIRouter()
engine=RAGEngine()

class QueryInput(BaseModel):
    query: str

@router.post("/ingest")
async def ingest_document(file: UploadFile = File(...)):
    """
    1. Uploaded file ko receive karo.
    2. Usse disk par 'data/docs' mein save karo.
    3. Engine ko bolo ki isse process (chunk/embed) kare.
    """
    try:
        # File save karne ke liye folder banao agar nahi hai
        os.makedirs("data/docs", exist_ok=True)
        file_path = f"data/docs/{file.filename}"
        
        # File ko disk par write karo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # RAG Engine ko kaam pe lagao
        num_chunks = engine.ingest_file(file_path)
        
        return {
            "message": "File processed successfully", 
            "filename": file.filename, 
            "chunks_added": num_chunks
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask")
async def ask_query(request: QueryInput):
    """
    User ka question lo aur answer return karo.
    """
    try:
        # Engine se answer maango
        response = engine.ask_question(request.query)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
