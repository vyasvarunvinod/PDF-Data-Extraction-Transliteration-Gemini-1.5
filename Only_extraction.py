import fitz  # PyMuPDF
import google.generativeai as genai
from PIL import Image
import io
import os

# --- Configuration ---
pdf_path = 'Your_PDF_Name.pdf'
output_file = 'Your_Output_File_Name.txt'
checkpoint_file = 'checkpoint.txt' # to get have a checkpoint in case of Internet breakdown

# Gemini API Key
genai.configure(api_key="Add-Your-API-Key")

# Initialize Gemini model only once
gemini_model = genai.GenerativeModel("gemini-1.5-flash")    # you can chnage the gemini version here


def gemini_ocr(img):
    """Uses Gemini Pro Vision to OCR a single image."""
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()

    response = gemini_model.generate_content([
        {"mime_type": "image/png", "data": img_bytes},
        "Please extract the full Hindi text from this page accurately. Do not translate or summarize."
    ])
    return response.text.strip()


def get_checkpoint():
    """Reads the checkpoint file to get the last completed page."""
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            try:
                return int(f.read().strip())
            except:
                return 0
    return 0


def update_checkpoint(page_num):
    """Writes the current page number to the checkpoint file."""
    with open(checkpoint_file, 'w') as f:
        f.write(str(page_num))


def extract_text_from_pdf(pdf_file):
    """Extracts text page by page, uses embedded text or Gemini OCR, and saves progress."""
    doc = fitz.open(pdf_file)
    num_pages = doc.page_count
    print(f"PDF has {num_pages} pages.")

    start_page = get_checkpoint()
    print(f"Resuming from page {start_page + 1}...")

    for page_num in range(start_page, num_pages):
        page_text = ""
        page = doc.load_page(page_num)
        print(f"\n--- Processing Page {page_num + 1}/{num_pages} ---")

        # Try extracting embedded text
        print("Attempt 1: Extracting embedded text...")
        page_text = page.get_text("text", sort=True).strip()

        if len(page_text) < 50:
            print(f"Embedded text weak ({len(page_text)} chars). Trying Gemini OCR...")
            try:
                zoom = 2
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                img_bytes = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_bytes))

                ocr_text = gemini_ocr(img)
                page_text = ocr_text if ocr_text else page_text
                print("Gemini OCR successful.")
            except Exception as ocr_error:
                print(f"!! Gemini OCR failed for page {page_num + 1}: {ocr_error}")
        else:
            print("Embedded text extraction successful.")

        # Write this page to output file
        try:
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(f"--- PAGE {page_num + 1} ---\n{page_text}\n\n")
        except Exception as e:
            print(f"!! Error writing page {page_num + 1} to file: {e}")

        # Update checkpoint
        update_checkpoint(page_num + 1)

    doc.close()
    print("\n✅ Extraction complete.")


# --- Main Execution ---
if __name__ == "__main__":
    if not os.path.exists(pdf_path):
        print(f"!! ERROR: PDF file not found at: {pdf_path}")
    else:
        extract_text_from_pdf(pdf_path)
        print(f"\n✅ Done! Check '{output_file}' for extracted text.")
        print("📌 You can delete 'checkpoint.txt' once you're fully done.")
