import fitz  # PyMuPDF
import io
import os
from PIL import Image
import google.generativeai as genai
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# --- Configuration ---

pdf_path = 'Your-PDF-Name.pdf'
output_file = 'Gemini_transliterated_output.txt'

# Gemini API key setup
GOOGLE_API_KEY = "Add-Your-Gemini_API"  # <-- put your Gemini API Key here

# Initialize Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash') # You can add the version of Gemini you want

# --- Script Logic ---

def extract_text_from_pdf(pdf_file):
    """Extracts text page by page, trying embedded text first, then Gemini OCR."""
    all_text_blocks = []
    doc = None
    print(f"Opening PDF: {pdf_file}")
    try:
        doc = fitz.open(pdf_file)
        # num_pages = min(doc.page_count, 3)
        num_pages = (doc.page_count)

        print(f"PDF has {num_pages} pages.")

        for page_num in range(num_pages):
            page_text = ""
            page = doc.load_page(page_num)
            print(f"\n--- Processing Page {page_num + 1}/{num_pages} ---")

            # Attempt 1: Try extracting embedded text
            print("Attempt 1: Extracting embedded text...")
            page_text = page.get_text("text", sort=True).strip()

            # Attempt 2: Gemini OCR if embedded text is insufficient
            if len(page_text) < 50:
                print(f"Attempt 1 yielded little text ({len(page_text)} chars). Trying Gemini OCR...")
                try:
                    # Render page to image
                    zoom = 2
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)
                    img_bytes = pix.tobytes("png")

                    # Open image
                    img = Image.open(io.BytesIO(img_bytes))

                    # Gemini OCR
                    response = model.generate_content(
                    [
                        {"mime_type": "image/png", "data": img_bytes},
                        "Please extract the Hindi text from this image."
                    ],
                    stream=False
                )
                    page_text = response.text.strip()
                    print("Gemini OCR successful.")
                except Exception as ocr_error:
                    print(f"!! Gemini OCR failed for page {page_num + 1}: {ocr_error}")
                    page_text = ""  # fallback to empty
            else:
                print("Attempt 1 successful (found embedded text).")

            all_text_blocks.append(f"--- PAGE {page_num + 1} ---\n{page_text}\n")

    except Exception as e:
        print(f"!! Error processing PDF: {e}")
    finally:
        if doc:
            doc.close()
            print("Closed PDF.")
    return all_text_blocks

def transliterate_blocks(text_blocks):
    """Transliterates a list of Devanagari text blocks to IAST."""
    print("\n--- Starting Transliteration ---")
    iast_blocks = []
    total_blocks = len(text_blocks)
    for i, block in enumerate(text_blocks):
        if block:  # Ensure block is not empty
            try:
                if block.startswith("--- PAGE"):
                    parts = block.split('\n', 1)
                    header = parts[0] + "\n"
                    devanagari_content = parts[1] if len(parts) > 1 else ""
                else:
                    header = ""
                    devanagari_content = block

                if devanagari_content.strip():
                    iast_text = transliterate(devanagari_content, sanscript.DEVANAGARI, sanscript.IAST)
                    iast_blocks.append(header + iast_text)
                else:
                    iast_blocks.append(header)
            except Exception as e:
                print(f"!! Error transliterating block {i+1}/{total_blocks}: {e}")
                iast_blocks.append(f"[ERROR DURING TRANSLITERATION]\n{block}")  # Keep original on error
        print(f"Transliterated block {i + 1}/{total_blocks}")
    print("--- Transliteration Complete ---")
    return iast_blocks

def write_to_file(filename, blocks):
    """Writes the processed blocks to a text file."""
    print(f"\nWriting output to: {filename}")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for block in blocks:
                f.write(block)
                f.write("\n")
        print("--- File Writing Complete ---")
    except Exception as e:
        print(f"!! Error writing to file: {e}")

# --- Main Execution ---

if __name__ == "__main__":
    if not os.path.exists(pdf_path):
        print(f"!! ERROR: PDF file not found at: {pdf_path}")
    else:
        devanagari_pages = extract_text_from_pdf(pdf_path)
        if devanagari_pages:
            iast_pages = transliterate_blocks(devanagari_pages)
            write_to_file(output_file, iast_pages)
            print(f"\nSuccess! Check the file '{output_file}' in the same folder as the script.")
        else:
            print("\nNo text could be extracted from the PDF.")

    print("\nScript finished.")
