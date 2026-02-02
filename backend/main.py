import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.apis import router

# App Initialize
app = FastAPI(title="Enterprise RAG System", version="1.0")

# --- CORS SETUP (Bahut Important) ---
# Iske bina Frontend (Port 8501) Backend (Port 8000) se baat nahi kar payega.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Real project mein yahan specific domain hota hai
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes ko app mein jodo
app.include_router(router)

@app.get("/")
def root():
    return {"message": "RAG System is Running! 🚀"}

# Server Start Logic
if __name__ == "__main__":
    # Host 0.0.0.0 matlab local network pe accessible
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)