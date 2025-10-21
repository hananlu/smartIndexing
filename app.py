import streamlit as st
from PIL import Image
import pytesseract
import re
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


st.set_page_config(page_title="OCR ISO Detector", page_icon="🔍")

st.markdown(
    """
    <div style='font-size:20px; font-weight:bold; text-align:center; color:#0f4c81;'>
    🔍 Implementasi Sistem Cerdas berbasis AI untuk Indexing dan Rekomendasi Kinerja bagi Penyedia Layanan Internet Indonesia​
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("Silahkan upload dokumen ISO")

uploaded_file = st.file_uploader("📤 Upload an image", type=["jpg", "jpeg", "png"])

def extract_text_from_image(image_path: str) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text.strip()

def find_specific_iso_value(text: str) -> list:
    matches = re.findall(r'27001\s*:\s*\d{4}', text)
    return [match.strip() for match in matches]

if uploaded_file is not None:
    with open("uploaded_image.png", "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.image(uploaded_file, caption="Uploaded Image", use_container_width =True)
    # st.info("🔍 Extracting text...")
    extracted_text = extract_text_from_image("uploaded_image.png")

    # st.subheader("📝 Extracted Text:")
    # st.text_area("OCR Result", extracted_text, height=200)

    specific_iso_value = find_specific_iso_value(extracted_text)
    st.markdown("Nomor ISO")
    if specific_iso_value:
        for val in specific_iso_value:
            st.success(val)
    else:
        st.warning("❌ Specific ISO value not found.")
else:
    st.info("👆 Upload an image file to start OCR.")
