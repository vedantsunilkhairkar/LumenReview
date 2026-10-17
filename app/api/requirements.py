"""FastAPI router for requirements upload, parsing, and listing."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.agents.nodes.ingest import parse_requirements_text
from app.api.deps import verify_api_key
from app.db.models import RequirementRecord
from app.db.session import get_db

router = APIRouter(prefix="/requirements", tags=["Requirements"])


class RequirementUploadRequest(BaseModel):
    raw_text: str = Field(..., description="Raw requirement statements or CSV text")
    category: str | None = Field(default="Lighting", description="Subsystem category")


class ParsedRequirement(BaseModel):
    req_id: str
    text: str
    category: str


class UploadResponse(BaseModel):
    status: str
    count: int
    requirements: list[ParsedRequirement]


@router.post("/upload", response_model=UploadResponse, dependencies=[Depends(verify_api_key)])
async def upload_requirements(
    file: UploadFile | None = File(default=None),
    raw_text: str | None = Form(default=None),
):
    """Upload requirements via pasted text, CSV file, or document."""
    content = ""
    if file:
        content_bytes = await file.read()
        try:
            content = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            content = content_bytes.decode("latin-1")
    elif raw_text:
        content = raw_text.strip()

    if not content:
        raise HTTPException(status_code=400, detail="No requirements text or file provided.")

    parsed = parse_requirements_text(content)
    if not parsed:
        raise HTTPException(
            status_code=400, detail="Could not extract any valid requirements from the input."
        )

    return UploadResponse(
        status="success",
        count=len(parsed),
        requirements=[ParsedRequirement(**item) for item in parsed],
    )


@router.get("", dependencies=[Depends(verify_api_key)])
def list_requirements(limit: int = 100, db=Depends(get_db)):
    """List recent requirements from database."""
    records = (
        db.query(RequirementRecord).order_by(RequirementRecord.created_at.desc()).limit(limit).all()
    )
    return [
        {
            "id": r.id,
            "review_id": r.review_id,
            "req_id": r.req_id,
            "text": r.text,
            "category": r.category,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]
