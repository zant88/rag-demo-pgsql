"""Knowledge API endpoints for manual knowledge input."""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.knowledge import KnowledgeCreate, KnowledgeResponse
from app.services.knowledge_service import KnowledgeService

# Create router
router = APIRouter()


def get_knowledge_service(db: Session = Depends(get_db)):
    """Dependency to get knowledge service instance."""
    return KnowledgeService(db)


@router.post("/manual-entry", response_model=KnowledgeResponse)
async def create_manual_knowledge(
    knowledge_data: KnowledgeCreate,
    db: Session = Depends(get_db)
):
    """Create knowledge entries from manual input."""
    try:
        knowledge_service = KnowledgeService(db)
        knowledge_entry = await knowledge_service.create_manual_knowledge(knowledge_data)
        return knowledge_entry
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create knowledge entry: {str(e)}")


@router.get("/entries", response_model=List[KnowledgeResponse])
async def list_knowledge_entries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all knowledge entries."""
    try:
        knowledge_service = KnowledgeService(db)
        entries = knowledge_service.get_knowledge_entries(skip=skip, limit=limit)
        return entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve knowledge entries: {str(e)}")


@router.get("/entry/{entry_id}", response_model=KnowledgeResponse)
async def get_knowledge_entry(
    entry_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific knowledge entry by ID."""
    try:
        knowledge_service = KnowledgeService(db)
        entry = knowledge_service.get_knowledge_entry(entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Knowledge entry not found")
        return entry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve knowledge entry: {str(e)}")


@router.delete("/entry/{entry_id}")
async def delete_knowledge_entry(
    entry_id: int,
    db: Session = Depends(get_db)
):
    """Delete a knowledge entry by ID."""
    try:
        knowledge_service = KnowledgeService(db)
        success = knowledge_service.delete_knowledge_entry(entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Knowledge entry not found")
        return {"message": "Knowledge entry deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete knowledge entry: {str(e)}")
