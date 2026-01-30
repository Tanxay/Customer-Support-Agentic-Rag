from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from app.workflow.graph import app_graph

app = FastAPI(title="Customer Support Agent API")

class QueryRequest(BaseModel):
    question: str

class DocumentResponse(BaseModel):
    content: str
    source: str
    type: str

class QueryResponse(BaseModel):
    answer: str
    documents: List[DocumentResponse]
    datasource: str

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    print(f"Received query: {request.question}")
    try:
        # Run the graph
        final_state = app_graph.invoke({"question": request.question})
        
        # Extract results
        answer = final_state.get("generation", "No answer generated.")
        datasource = final_state.get("datasource", "unknown")
        docs = final_state.get("documents", [])
        
        doc_responses = []
        if docs:
            for doc in docs:
                doc_responses.append(DocumentResponse(
                    content=doc.page_content,
                    source=doc.metadata.get("source", "unknown"),
                    type=doc.metadata.get("type", "unknown")
                ))
        
        return QueryResponse(
            answer=answer,
            documents=doc_responses,
            datasource=datasource
        )
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
