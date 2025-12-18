import os
import tempfile
import json
import streamlit as st

from invoice_app import analyze_invoice_images
from erpnext_client import upload_file_to_erpnext


# -------------------------------------------------
# Helper: Safe display (TEXT or JSON)
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

if "erp_uploaded" not in st.session_state:
    st.session_state.erp_uploaded = False

if "key_counter" not in st.session_state:
    st.session_state.key_counter = 0


# -------------------------------------------------
# Reset
# -------------------------------------------------
if st.button("🔄 Start New Analysis"):
    st.session_state.uploaded_files = None
    st.session_state.image_paths = []
    st.session_state.analysis_result = None
    st.session_state.erp_uploaded = False
    st.session_state.key_counter += 1
    st.rerun()


# -------------------------------------------------
# UI
# -------------------------------------------------
st.title("Invoice Scanner")

st.write(
    "Upload invoice images. Images are automatically uploaded to ERPNext "
    "after analysis."
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
# Analyze + AUTO UPLOAD IMAGE TO ERPNext
# -------------------------------------------------
if uploaded_files and st.button("Analyze Invoice(s)"):
    with st.spinner("Analyzing invoice(s) and uploading to ERPNext..."):

        image_paths = []

        # Save temp images
        for uploaded_file in uploaded_files:
            ext = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(uploaded_file.getbuffer())
                image_paths.append(tmp.name)

        st.session_state.image_paths = image_paths

        # Run OCR / analysis (even if you don't use result now)
        result = analyze_invoice_images(image_paths)
        st.session_state.analysis_result = result

        # Upload images to ERPNext (ONCE)
        if not st.session_state.erp_uploaded:
            for local_path, uploaded_file in zip(image_paths, uploaded_files):
                upload_file_to_erpnext(
                    file_path=local_path,
                    filename=uploaded_file.name,
                    is_private=1,
                )

            st.session_state.erp_uploaded = True
            st.success("Invoice image(s) uploaded to ERPNext successfully")


# -------------------------------------------------
# Show OCR Output (Optional, UI only)
# -------------------------------------------------
if st.session_state.analysis_result is not None:
    st.subheader("OCR Output (Preview Only)")
    safe_display(st.session_state.analysis_result)


# -------------------------------------------------
# Footer
# -------------------------------------------------
st.markdown("---")
st.caption("Invoice images are stored in ERPNext → File")
