import re
import pdfplumber
import pytesseract
import numpy as np
import cv2

from pdf2image import convert_from_bytes
from PIL import Image
from django.conf import settings


# ==============================
# 🔹 1. TEXT PDF EXTRACTION
# ==============================

def extract_text_from_pdf(file_obj):
    text = ""
    with pdfplumber.open(file_obj) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


# ==============================
# 🔹 2. PDF → IMAGES (OCR)
# ==============================

def convert_pdf_to_images_for_ocr(pdf_file_obj):
    try:
        pdf_bytes = pdf_file_obj.read()
        poppler_path = getattr(settings, 'POPPLER_PATH', None)

        print("DEBUG POPPLER PATH:", poppler_path)  # 👈 ADD THIS

        images = convert_from_bytes(
            pdf_bytes,
            dpi=300,
            poppler_path=poppler_path
        )

        return images

    except Exception as e:
        print(f"❌ Error converting PDF to images: {e}")
        raise

# ==============================
# 🔹 3. IMAGE PREPROCESSING
# ==============================

def preprocess_image(pil_image):
    img = np.array(pil_image)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Thresholding improves OCR accuracy
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    return Image.fromarray(thresh)


# ==============================
# 🔹 4. OCR FUNCTION
# ==============================

def apply_ocr_to_image(image: Image.Image) -> str:
    try:
        # Set path if needed
        if hasattr(settings, "TESSERACT_PATH"):
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH

        config = r'--oem 3 --psm 6'

        text = pytesseract.image_to_string(image, config=config)

        return text

    except Exception as e:
        print(f"❌ OCR Error: {e}")
        raise


# ==============================
# 🔹 5. OCR TEXT CLEANING
# ==============================

def clean_ocr_text(text: str) -> str:
    text = text.replace('\f', '')

    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)

    lines = [line.strip() for line in text.split('\n')]

    return "\n".join(lines).strip()


# ==============================
# 🔹 6. NORMALIZATION (VERY IMPORTANT)
# ==============================

def normalize_text(text):
    # Fix common OCR mistakes
    text = text.replace("|", "I")
    text = text.replace("0)", "D)")
    text = text.replace("O)", "D)")

    # Normalize options format
    text = re.sub(r'([A-D])\s*\)', r'\1)', text)

    return text


# ==============================
# 🔹 7. OCR PIPELINE
# ==============================

def extract_text_from_scanned_pdf(pdf_file_obj) -> str:
    full_text = []

    images = convert_pdf_to_images_for_ocr(pdf_file_obj)

    for image in images:
        processed = preprocess_image(image)

        page_text = apply_ocr_to_image(processed)

        cleaned = clean_ocr_text(page_text)

        full_text.append(cleaned)

    return "\n\n".join(full_text)


# ==============================
# 🔹 8. AUTO DETECT (TEXT vs OCR)
# ==============================

def extract_text(file_obj):
    text = extract_text_from_pdf(file_obj)

    # If text is too small → use OCR
    if len(text.strip()) < 50:
        print("📸 Switching to OCR...")
        file_obj.seek(0)
        text = extract_text_from_scanned_pdf(file_obj)

    return text


# ==============================
# 🔹 9. MCQ PARSER (ROBUST 🔥)
# ==============================

def parse_mcqs_from_text(text):
    pattern = re.compile(
        r"(?P<index>\d+)[\.\)]\s*(?P<question>.*?)\s+"
        r"A[\.\)\:]*\s*(?P<option_a>.*?)\s+"
        r"B[\.\)\:]*\s*(?P<option_b>.*?)\s+"
        r"C[\.\)\:]*\s*(?P<option_c>.*?)\s+"
        r"D[\.\)\:]*\s*(?P<option_d>.*?)\s+"
        r"(Answer|Ans|Correct)\s*[:\-]?\s*(?P<correct_answer>[A-D])",
        re.DOTALL | re.IGNORECASE
    )

    questions = []

    for match in pattern.finditer(text):
        data = match.groupdict()

        questions.append({
            "question": data["question"].strip(),
            "option_a": data["option_a"].strip(),
            "option_b": data["option_b"].strip(),
            "option_c": data["option_c"].strip(),
            "option_d": data["option_d"].strip(),
            "correct_answer": data["correct_answer"].upper().strip()
        })

    return questions


# ==============================
# 🔹 10. MAIN PIPELINE
# ==============================

def process_pdf(file_obj):
    text = extract_text(file_obj)

    text = clean_ocr_text(text)

    text = normalize_text(text)

    print("🔍 Extracted Text Preview:\n", text[:1000])  # Debug

    questions = parse_mcqs_from_text(text)

    return questions