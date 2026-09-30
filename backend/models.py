from typing import Optional

from pydantic import BaseModel, Field


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=1)
    parties: str = Field(..., min_length=1)
    terms: str = Field(..., min_length=1)
    effective_date: str = Field(..., min_length=1)


class DocumentResponse(BaseModel):
    document: str
    document_type: str
    mode: str


class ExportRequest(BaseModel):
    document: str = Field(..., min_length=1)
    logo_base64: Optional[str] = None