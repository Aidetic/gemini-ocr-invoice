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
# UI
# -------------------------------------------------
st.title("Invoice OCR → ERPNext")

st.write(
    "Upload invoice images, analyze them using AI, "
    "and automatically store the invoice and OCR data in ERPNext."
)


# -------------------------------------------------
# Upload images
# -------------------------------------------------
uploaded_files = st.file_uploader(
    "Upload invoice images",
    type=["png", "jpg", "jpeg", "webp", "bmp", "tiff"],
    accept_multiple_files=True,
)

# -------------------------------------------------
# Preview images
# -------------------------------------------------
if uploaded_files:
    cols = st.columns(min(4, len(uploaded_files)))
    for idx, f in enumerate(uploaded_files):
        with cols[idx % len(cols)]:
            st.image(f, caption=f"Invoice {idx + 1}", use_container_width=True)


# -------------------------------------------------
# SINGLE ACTION: Analyze + Upload + Save
# -------------------------------------------------
if uploaded_files and st.button("Analyze & Save to ERPNext"):
    with st.spinner("Analyzing invoice(s) and saving to ERPNext..."):

        # ----------------------------------
        # Save uploaded images to temp files
        # ----------------------------------
        image_paths = []
        for uploaded_file in uploaded_files:
            ext = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(uploaded_file.getbuffer())
                image_paths.append(tmp.name)

        # ----------------------------------
        # Run OCR / AI extraction
        # ----------------------------------
        analysis_result = analyze_invoice_images(image_paths)

        st.subheader("OCR / Extracted Output")
        safe_display(analysis_result)

        # ----------------------------------
        # Normalize OCR output → dict ONLY
        # ----------------------------------
        if isinstance(analysis_result, dict):
            ocr_json = analysis_result
        elif isinstance(analysis_result, str):
            try:
                ocr_json = json.loads(analysis_result)
            except json.JSONDecodeError:
                st.error("OCR output is not valid JSON")
                st.stop()
        else:
            st.error(f"Unsupported OCR output type: {type(analysis_result)}")
            st.stop()

        # ----------------------------------
        # Extract invoice number (guaranteed)
        # ----------------------------------
        invoice_number = ocr_json.get("invoice_number")
        if not invoice_number:
            st.error("Invoice number not found in OCR output")
            st.stop()

        # ----------------------------------
        # Upload images to ERPNext
        # ----------------------------------
        uploaded_erp_files = []
        for local_path, uploaded_file in zip(image_paths, uploaded_files):
            info = upload_file_to_erpnext(
                file_path=local_path,
                filename=uploaded_file.name,
                is_private=1,
            )
            uploaded_erp_files.append(info)

        # ----------------------------------
        # Create Invoice OCR Record(s)
        # ----------------------------------
        records = []
        for file_info in uploaded_erp_files:
            record = create_invoice_ocr_record(
                file_url=file_info["file_url"],
                invoice_number=invoice_number,
            )
            records.append(record)

        # ----------------------------------
        # Final output
        # ----------------------------------
        st.success("Invoice analyzed and saved to ERPNext successfully")

        st.json({
            "invoice_number": invoice_number,
            "erp_files": uploaded_erp_files,
            "ocr_records": records
        })


# -------------------------------------------------
# Footer
# -------------------------------------------------
st.markdown("---")
st.caption(
    "Files are stored in ERPNext → File. "
    "OCR data is stored in ERPNext → Invoice OCR Record."
)
