import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama


# configuration
VECTOR_DB_PATH="./data/vector_db"
EMBEDDING_MODEL=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

LLM_MODEL=Ollama(model="llama3")

class RAGEngine:
    def __init__(self):
        # Jab class start ho, toh Vector DB load kar lo
        self.vector_db = Chroma(
            persist_directory=VECTOR_DB_PATH,
            embedding_function=EMBEDDING_MODEL
        )
    
    def ingest_file(self, file_path: str):

        # load pdf
        loader=PyPDFLoader(file_path)
        documents=loader.load()

        # split text
        text_splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks=text_splitter.split_documents(documents)

        # store in vector db
        self.vector_db.add_documents(chunks)
        self.vector_db.persist()
        return len(chunks)
    
    def ask_question(self, query: str, history: list = []):
        """
        Modified to include Chat History
        """
        # 1. Format History (Convert list of dicts to string)
        # History format expected: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        chat_history_str = ""
        for msg in history[-4:]: # Only keep last 4 messages to save context window
            role = "User" if msg["role"] == "user" else "Assistant"
            chat_history_str += f"{role}: {msg['content']}\n"

        # 2. Retrieval
        results = self.vector_db.similarity_search(query, k=3)
        context_text = "\n\n".join([doc.page_content for doc in results])
        
        # 3. Prompt with History
        prompt = f"""
        You are an expert enterprise assistant. Answer based on Context and Chat History.
        
        Context:
        {context_text}
        
        Chat History:
        {chat_history_str}
        
        Current Question:
        {query}
        
        Answer:
        """
        
        response = LLM_MODEL.invoke(prompt)
        
        sources = [{"text": doc.page_content, "page": doc.metadata.get("page", 0)} for doc in results]
        
        return {
            "answer": response,
            "sources": sources
        }
if __name__=="__main__":
    engine=RAGEngine()
    engine.ingest_file("sample.pdf") # Uncomment to test ingestion
    print(engine.ask_question("What is the policy?"))