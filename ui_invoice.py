import os
import tempfile
import json
import streamlit as st

from invoice_app import analyze_invoice_images
from erpnext_client import (
    upload_file_to_erpnext,
    create_invoice_ocr_record,
)

# -------------------------------------------------
# Helper: Safe display
# -------------------------------------------------
def safe_display(result):
    if isinstance(result, (dict, list)):
        st.json(result)
        return

    if isinstance(result, str):
        try:
            parsed = json.loads(result)
            st.json(parsed)
        except json.JSONDecodeError:
            st.write(result)
        return

    st.write(result)


# -------------------------------------------------
# Session state
# -------------------------------------------------
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = None

if "image_paths" not in st.session_state:
    st.session_state.image_paths = []

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "uploaded_erp_files" not in st.session_state:
    st.session_state.uploaded_erp_files = []

if "key_counter" not in st.session_state:
    st.session_state.key_counter = 0


# -------------------------------------------------
# Reset
# -------------------------------------------------
if st.button("🔄 Start New Analysis"):
    st.session_state.uploaded_files = None
    st.session_state.image_paths = []
    st.session_state.analysis_result = None
    st.session_state.uploaded_erp_files = []
    st.session_state.key_counter += 1
    st.rerun()


# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("Invoice OCR → ERPNext")

st.write(
    "Upload invoice images, extract OCR details using AI, "
    "and store both the file and extracted data in ERPNext."
)


# -------------------------------------------------
# Upload images
# -------------------------------------------------
uploaded_files = st.file_uploader(
    "Upload invoice images",
    type=["png", "jpg", "jpeg", "webp", "bmp", "tiff"],
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state.key_counter}",
)

st.session_state.uploaded_files = uploaded_files


# -------------------------------------------------
# Preview
# -------------------------------------------------
if uploaded_files:
    cols = st.columns(min(4, len(uploaded_files)))
    for idx, f in enumerate(uploaded_files):
        with cols[idx % len(cols)]:
            st.image(f, caption=f"Invoice {idx + 1}", use_container_width=True)


# -------------------------------------------------
# Analyze OCR
# -------------------------------------------------
if uploaded_files and st.button("Analyze Invoice(s)"):
    with st.spinner("Running OCR and extraction..."):
        image_paths = []

        for uploaded_file in uploaded_files:
            ext = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(uploaded_file.getbuffer())
                image_paths.append(tmp.name)

        st.session_state.image_paths = image_paths
        st.session_state.analysis_result = analyze_invoice_images(image_paths)


# -------------------------------------------------
# Show OCR Output
# -------------------------------------------------
if st.session_state.analysis_result is not None:
    st.subheader("OCR / Extracted Output")
    safe_display(st.session_state.analysis_result)


# -------------------------------------------------
# Upload invoice image(s) to ERPNext
# -------------------------------------------------
if st.session_state.image_paths and st.button("Upload Image(s) to ERPNext"):
    with st.spinner("Uploading invoice image(s) to ERPNext..."):
        uploaded_info = []

        for local_path, uploaded_file in zip(
            st.session_state.image_paths,
            st.session_state.uploaded_files,
        ):
            info = upload_file_to_erpnext(
                file_path=local_path,
                filename=uploaded_file.name,
                is_private=1,
            )
            uploaded_info.append(info)

        st.session_state.uploaded_erp_files = uploaded_info

        st.success("Invoice image(s) uploaded to ERPNext")
        st.json(uploaded_info)


# -------------------------------------------------
# Save OCR details to ERPNext (Custom DocType)
# -------------------------------------------------
if (
    st.session_state.uploaded_erp_files
    and st.session_state.analysis_result is not None
    and st.button("Save OCR Details to ERPNext")
):
    with st.spinner("Saving OCR details to ERPNext..."):

        # Raw OCR text
        ocr_raw = (
            st.session_state.analysis_result
            if isinstance(st.session_state.analysis_result, str)
            else json.dumps(st.session_state.analysis_result, indent=2)
        )

        # Structured JSON (only if valid)
        ocr_json = (
            st.session_state.analysis_result
            if isinstance(st.session_state.analysis_result, dict)
            else None
        )

        records = []

        for file_info in st.session_state.uploaded_erp_files:
            record = create_invoice_ocr_record(
                file_url=file_info["file_url"],
                ocr_raw=ocr_raw,
                ocr_json=ocr_json,
            )
            records.append(record)

        st.success("OCR data saved in ERPNext (Invoice OCR Record)")
        st.json(records)


# -------------------------------------------------
# Footer
# -------------------------------------------------
st.markdown("---")
st.caption(
    "Files are stored in ERPNext → File. "
    "OCR data is stored in ERPNext → Invoice OCR Record."
)
