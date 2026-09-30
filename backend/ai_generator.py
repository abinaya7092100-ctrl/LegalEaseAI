import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash",
).strip()

DEMO_MODE = (
    os.getenv("DEMO_MODE", "true").strip().lower()
    in {"true", "1", "yes", "on"}
)


def create_demo_document(
    document_type: str,
    parties: str,
    terms: str,
    effective_date: str,
) -> str:

    return f"""
{document_type.upper()}

Effective Date: {effective_date}

PARTIES

{parties}

AGREEMENT

This {document_type} is entered into between the parties
identified above and is effective from {effective_date}.

TERMS AND CONDITIONS

{terms}

GENERAL PROVISIONS

1. The parties agree to comply with the terms stated in
   this document.

2. Any amendment to this agreement should be made in writing
   and accepted by the relevant parties.

3. The parties should retain a copy of the final signed
   document for their records.

4. Applicable law and jurisdiction shall be determined
   according to the circumstances of the agreement.

5. This document is a draft and should be reviewed before
   signing or legal use.

SIGNATURES

PARTY 1

Name: ______________________________

Signature: _________________________

Date: ______________________________


PARTY 2

Name: ______________________________

Signature: _________________________

Date: ______________________________
""".strip()


def generate_with_gemini(
    document_type: str,
    parties: str,
    terms: str,
    effective_date: str,
) -> str:

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    prompt = f"""
You are a professional legal document drafting assistant.

Draft a clear and professional {document_type} using ONLY the
information provided below.

DOCUMENT TYPE:
{document_type}

EFFECTIVE DATE:
{effective_date}

PARTIES:
{parties}

TERMS AND CONDITIONS:
{terms}

Requirements:

- Create a professional legal-document structure.
- Include an appropriate title.
- Include party information.
- Include the effective date.
- Organize clauses using clear headings.
- Use professional and readable language.
- Do not invent names, dates, addresses, amounts, obligations,
  penalties, or facts that were not supplied.
- Include signature sections.
- Do not provide legal advice.
- End with a clear note that the draft should be reviewed by
  a qualified legal professional before use.

Return ONLY the document text.
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
            max_output_tokens=6000,
        ),
    )

    text = getattr(response, "text", None)

    if not text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return text.strip()


def generate_document(
    document_type: str,
    parties: str,
    terms: str,
    effective_date: str,
) -> str:

    if DEMO_MODE:
        return create_demo_document(
            document_type,
            parties,
            terms,
            effective_date,
        )

    try:
        return generate_with_gemini(
            document_type,
            parties,
            terms,
            effective_date,
        )

    except Exception:
        # Keep the application usable even when Gemini
        # is unavailable.
        return create_demo_document(
            document_type,
            parties,
            terms,
            effective_date,
        )