import os
import tempfile

import streamlit as st

from invoice_app import analyze_invoice_images

# --- Session states ---
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = None
if "key_counter" not in st.session_state:
    st.session_state.key_counter = 0

if st.button("🔄 Start New Analysis"):
    st.session_state.uploaded_files = None
    st.session_state.key_counter += 1
    st.rerun()

st.title("Invoice Scanner")

st.write(
    "Upload **invoice image(s)** (scanned, photo, etc.) for automatic extraction and analytics."
)

uploaded_files = st.file_uploader(
    "Upload invoice images (jpg, png, etc.)",
    type=["png", "jpg", "jpeg", "webp", "bmp", "tiff"],
    accept_multiple_files=True,
    key=f"file_uploader_{st.session_state.key_counter}",
)

st.session_state.uploaded_files = uploaded_files

# Require at least one image
if st.session_state.uploaded_files:
    if len(st.session_state.uploaded_files) < 1:
        st.error("Please upload at least one invoice image.")
    else:
        cols = st.columns(min(4, len(st.session_state.uploaded_files)))
        for idx, uploaded_file in enumerate(st.session_state.uploaded_files):
            with cols[idx % len(cols)]:
                st.image(
                    uploaded_file,
                    caption=f"Invoice {idx + 1}",
                    use_container_width=True,
                )

        if st.button("Analyze Invoice(s)"):
            with st.spinner("Analyzing invoice image(s)..."):
                image_paths = []
                # Save each uploaded image to a temp file
                for uploaded_file in st.session_state.uploaded_files:
                    ext = os.path.splitext(uploaded_file.name)[1]
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=ext
                    ) as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        image_paths.append(tmp_file.name)

                # Call your Gemini analysis function
                result = analyze_invoice_images(image_paths)

                st.write(result)
