import base64
import html
from datetime import date

import requests
import streamlit as st


st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


BACKEND_URL = st.sidebar.text_input(
    "Backend URL",
    value="http://127.0.0.1:8000",
).rstrip("/")


st.markdown(
    """
    <style>

    .hero {
        padding: 1.7rem;
        border-radius: 18px;
        background:
            linear-gradient(
                135deg,
                #111827,
                #1f2937
            );
        color: white;
        margin-bottom: 1.2rem;
    }

    .hero h1 {
        margin: 0;
    }

    .hero p {
        margin-top: 6px;
        color: #d1d5db;
    }

    .preview {
        background: #111827;
        color: #f9fafb;
        padding: 1.5rem;
        border-radius: 14px;
        border: 1px solid #374151;
        max-height: 620px;
        overflow-y: auto;
        white-space: pre-wrap;
        font-family: Georgia, serif;
        line-height: 1.7;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    """
    <div class="hero">
        <h1>⚖️ LegalEase</h1>
        <p>
            AI-powered legal document drafting,
            editing and export.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


if "document" not in st.session_state:

    st.session_state.document = ""


if "demo_mode" not in st.session_state:

    st.session_state.demo_mode = False


left, right = st.columns(
    [1, 1.25],
    gap="large"
)


with left:

    st.subheader(
        "Document Details"
    )

    document_type = st.selectbox(
        "Document Type",
        [
            "Employment Contract",
            "Non-Disclosure Agreement (NDA)",
            "Lease Agreement",
            "Freelance Work Contract",
            "Service Agreement",
            "Employment Offer Letter",
            "Custom Agreement",
        ]
    )

    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Example: Jane Doe "
            "(Service Provider), "
            "TechNova Inc. (Client)"
        ),
        height=110,
    )

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Separate clauses using semicolons.\n\n"
            "Example:\n"
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Either party may terminate with "
            "15 days notice"
        ),
        height=180,
    )

    effective_date = st.date_input(
        "Effective Date",
        value=date.today()
    )

    logo = st.file_uploader(
        "Optional Logo",
        type=[
            "png",
            "jpg",
            "jpeg"
        ],
    )

    generate = st.button(
        "✨ Generate Document",
        type="primary",
        use_container_width=True,
    )

    if generate:

        if (
            not parties.strip()
            or not terms.strip()
        ):

            st.error(
                "Please enter parties and terms."
            )

        else:

            payload = {

                "document_type":
                    document_type,

                "parties":
                    parties,

                "terms":
                    terms,

                "effective_date":
                    effective_date.isoformat(),
            }

            try:

                with st.spinner(
                    "Generating document..."
                ):

                    response = requests.post(
                        f"{BACKEND_URL}/generate",
                        json=payload,
                        timeout=120,
                    )

                if response.ok:

                    data = response.json()

                    st.session_state.document = (
                        data["content"]
                    )

                    st.session_state.demo_mode = (
                        data["demo_mode"]
                    )

                    if data["demo_mode"]:

                        st.warning(
                            "Demo mode is active. "
                            "Add GEMINI_API_KEY to "
                            "generate with Gemini."
                        )

                    else:

                        st.success(
                            "AI document generated."
                        )

                else:

                    st.error(
                        response.text
                    )

            except requests.RequestException as error:

                st.error(
                    f"Backend connection failed: {error}"
                )


with right:

    st.subheader(
        "Editable Document"
    )

    if st.session_state.document:

        st.session_state.document = (
            st.text_area(
                "Edit your document",
                value=st.session_state.document,
                height=560,
                label_visibility="collapsed",
            )
        )

        st.markdown(
            "**Document Preview**"
        )

        preview = html.escape(
            st.session_state.document
        ).replace(
            "\n",
            "<br>"
        )

        st.markdown(
            f"""
            <div class="preview">
                {preview}
            </div>
            """,
            unsafe_allow_html=True
        )

        logo_base64 = None

        if logo is not None:

            logo_base64 = (
                "data:"
                + logo.type
                + ";base64,"
                + base64.b64encode(
                    logo.getvalue()
                ).decode()
            )

        export_payload = {

            "content":
                st.session_state.document,

            "document_type":
                document_type,

            "logo_base64":
                logo_base64,
        }

        st.divider()

        st.markdown(
            "**Export Document**"
        )

        col1, col2, col3 = st.columns(3)

        if col1.button(
            "TXT",
            use_container_width=True
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/export/txt",
                    json=export_payload,
                    timeout=60,
                )

                if response.ok:

                    st.download_button(
                        "Save TXT",
                        response.content,
                        file_name=(
                            "legalease_document.txt"
                        ),
                        mime="text/plain",
                        use_container_width=True,
                    )

                else:

                    st.error(
                        response.text
                    )

            except requests.RequestException as error:

                st.error(str(error))

        if col2.button(
            "DOCX",
            use_container_width=True
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/export/docx",
                    json=export_payload,
                    timeout=60,
                )

                if response.ok:

                    st.download_button(
                        "Save DOCX",
                        response.content,
                        file_name=(
                            "legalease_document.docx"
                        ),
                        mime=(
                            "application/"
                            "vnd.openxmlformats-officedocument."
                            "wordprocessingml.document"
                        ),
                        use_container_width=True,
                    )

                else:

                    st.error(
                        response.text
                    )

            except requests.RequestException as error:

                st.error(str(error))

        if col3.button(
            "PDF",
            use_container_width=True
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/export/pdf",
                    json=export_payload,
                    timeout=60,
                )

                if response.ok:

                    st.download_button(
                        "Save PDF",
                        response.content,
                        file_name=(
                            "legalease_document.pdf"
                        ),
                        mime="application/pdf",
                        use_container_width=True,
                    )

                else:

                    st.error(
                        response.text
                    )

            except requests.RequestException as error:

                st.error(str(error))

    else:

        st.info(
            "Generate a document to see "
            "the editable preview here."
        )


st.divider()

st.caption(
    "LegalEase is a drafting aid and not "
    "a substitute for advice from a qualified lawyer."
)