import fitz  # PyMuPDF
import io
import os
import sys
from PIL import Image
import google.generativeai as genai
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# --- Get PDF path from argument ---
if len(sys.argv) < 2:
    print("Usage: python script.py <input_pdf_path>")
    sys.exit(1)

pdf_path = sys.argv[1]
input_filename = os.path.splitext(os.path.basename(pdf_path))[0]

# Output file names
extracted_output_file = f"Extraction_Data_{input_filename}.txt"
transliterated_output_file = f"Gemini_transliterated_{input_filename}.txt"

# --- Gemini API Key ---
GOOGLE_API_KEY = "Your_API_Key"  # Replace with your Gemini Key
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-flash')

# --- Extract Text ---
def extract_text_from_pdf(pdf_file):
    all_text_blocks = []
    doc = None
    print(f"Opening PDF: {pdf_file}")
    try:
        doc = fitz.open(pdf_file)
        num_pages = doc.page_count
        print(f"PDF has {num_pages} pages.")

        for page_num in range(num_pages):
            page = doc.load_page(page_num)
            print(f"\n--- Processing Page {page_num + 1}/{num_pages} ---")
            page_text = page.get_text("text", sort=True).strip()

            if len(page_text) < 50:
                print(f"Low text found ({len(page_text)} chars). Using Gemini OCR...")
                try:
                    zoom = 2
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)
                    img_bytes = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_bytes))

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
                    page_text = ""
            else:
                print("Embedded text found.")

            all_text_blocks.append(f"--- PAGE {page_num + 1} ---\n{page_text}\n")

    except Exception as e:
        print(f"!! Error processing PDF: {e}")
    finally:
        if doc:
            doc.close()
            print("Closed PDF.")
    return all_text_blocks

# --- Transliterate Text ---
def transliterate_blocks(text_blocks):
    print("\n--- Starting Transliteration ---")
    iast_blocks = []
    for i, block in enumerate(text_blocks):
        try:
            if block.startswith("--- PAGE"):
                parts = block.split('\n', 1)
                header = parts[0] + "\n"
                devanagari = parts[1] if len(parts) > 1 else ""
            else:
                header = ""
                devanagari = block

            if devanagari.strip():
                iast_text = transliterate(devanagari, sanscript.DEVANAGARI, sanscript.IAST)
                iast_blocks.append(header + iast_text)
            else:
                iast_blocks.append(header)
        except Exception as e:
            print(f"!! Error transliterating block {i + 1}: {e}")
            iast_blocks.append(f"[TRANSLITERATION ERROR]\n{block}")
        print(f"Transliterated block {i + 1}/{len(text_blocks)}")
    print("--- Transliteration Complete ---")
    return iast_blocks

# --- Write Output ---
def write_to_file(filename, blocks):
    print(f"\nWriting output to: {filename}")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            for block in blocks:
                f.write(block + "\n")
        print("File writing complete.")
    except Exception as e:
        print(f"!! Error writing to file: {e}")

# --- Main ---
if __name__ == "__main__":
    if not os.path.exists(pdf_path):
        print(f"!! ERROR: File not found: {pdf_path}")
        sys.exit(1)

    devanagari_text = extract_text_from_pdf(pdf_path)

    if devanagari_text:
        write_to_file(extracted_output_file, devanagari_text)
        iast_text = transliterate_blocks(devanagari_text)
        write_to_file(transliterated_output_file, iast_text)
        print(f"\n✅ Extraction saved to: {extracted_output_file}")
        print(f"✅ Transliteration saved to: {transliterated_output_file}")
    else:
        print("!! No text was extracted from the PDF.")
