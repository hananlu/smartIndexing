import streamlit as st
from PIL import Image
import pytesseract
import re
import os
import numpy as np
import cv2

#pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


st.set_page_config(page_title="Smart Indexing", page_icon="🔍")

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


# Base Function
# def extract_text_from_image(image_path: str) -> str:
#     if not os.path.exists(image_path):
#         raise FileNotFoundError(f"Image not found: {image_path}")
#     image = Image.open(image_path)
#     text = pytesseract.image_to_string(image)
#     return text.strip()


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from an image using Tesseract OCR with adaptive auto-enhancement.
    Automatically adjusts contrast and threshold based on image brightness.
    """

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    try:
        # --- Load image ---
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # --- Step 1: Adaptive contrast enhancement (CLAHE) ---
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # --- Step 2: Estimate brightness ---
        mean_brightness = np.mean(enhanced)

        # --- Step 3: Adaptive thresholding based on brightness ---
        if mean_brightness < 90:
            # Dark image → brighten and invert if needed
            enhanced = cv2.convertScaleAbs(enhanced, alpha=1.5, beta=40)
            thresh = cv2.adaptiveThreshold(
                enhanced, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 31, 10
            )
        elif mean_brightness > 170:
            # Overexposed → darken slightly
            enhanced = cv2.convertScaleAbs(enhanced, alpha=0.8, beta=-30)
            thresh = cv2.adaptiveThreshold(
                enhanced, 255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY, 31, 10
            )
        else:
            # Normal brightness → standard adaptive threshold
            thresh = cv2.adaptiveThreshold(
                enhanced, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 31, 2
            )

        # --- Step 4: Morphological cleanup (remove noise) ---
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # --- Step 5: Resize small images for better OCR ---
        height, width = cleaned.shape
        if width < 1000:
            cleaned = cv2.resize(cleaned, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # --- Step 6: Convert back to PIL & run OCR ---
        processed_image = Image.fromarray(cleaned)
        config = r'--oem 3 --psm 6'  # LSTM OCR engine, treat image as block of text
        text = pytesseract.image_to_string(processed_image, config=config)

        return text.strip()

    except Exception as e:
        raise RuntimeError(f"OCR failed: {e}")

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
    st.info("👆 Upload an image file to start Check ISO.")

