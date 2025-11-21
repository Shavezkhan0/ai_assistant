from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.agents.router_agent import router_agent
from app.database.postgres_db import get_db
from sqlalchemy.orm import Session

router = APIRouter(tags=["chat"])

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    sources: list = []
    pdf_files: list = []
    has_pdfs: bool = False
    agent: str = "notes_agent"
    result_data: Optional[dict] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Chat endpoint that routes to appropriate agent and returns response"""
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Use router agent to route to appropriate agent
        result = router_agent.route_query(request.message, db)
        
        return ChatResponse(
            response=result.get('response', ''),
            sources=result.get('sources', []),
            pdf_files=result.get('pdf_files', []),
            has_pdfs=result.get('has_pdfs', False),
            agent=result.get('agent', 'notes_agent'),
            result_data=result.get('result_data') or {}
        )
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")