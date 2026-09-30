from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from backend.ai_core.gemini_generator import GeminiDocumentGenerator
from backend.models.schemas import (
    DocumentRequest,
    DocumentResponse,
    ExportRequest,
)
from backend.services.document_service import (
    format_txt,
    format_docx,
    format_pdf,
)
from backend.core.config import settings


router = APIRouter()

generator = GeminiDocumentGenerator()


@router.post(
    "/generate",
    response_model=DocumentResponse
)
def generate_document(request: DocumentRequest):

    try:
        generated_text = generator.generate_document(request)

        return DocumentResponse(
            document_type=request.document_type,
            content=generated_text,
            model=(
                settings.gemini_model
                if settings.gemini_api_key
                else "demo-template"
            ),
            demo_mode=not bool(settings.gemini_api_key),
        )

    except Exception as error:

        raise HTTPException(
            status_code=502,
            detail=f"Document generation failed: {error}"
        )


@router.post("/export/txt")
def export_txt(request: ExportRequest):

    content = format_txt(request.content)

    return Response(
        content=content,
        media_type="text/plain",
        headers={
            "Content-Disposition":
                'attachment; filename="legalease_document.txt"'
        },
    )


@router.post("/export/docx")
def export_docx(request: ExportRequest):

    try:

        file_data = format_docx(
            request.content,
            request.document_type,
            request.logo_base64,
        )

        return Response(
            content=file_data,
            media_type=(
                "application/"
                "vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            headers={
                "Content-Disposition":
                    'attachment; filename="legalease_document.docx"'
            },
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"DOCX export failed: {error}"
        )


@router.post("/export/pdf")
def export_pdf(request: ExportRequest):

    try:

        file_data = format_pdf(
            request.content,
            request.document_type,
            request.logo_base64,
        )

        return Response(
            content=file_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition":
                    'attachment; filename="legalease_document.pdf"'
            },
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"PDF export failed: {error}"
        )