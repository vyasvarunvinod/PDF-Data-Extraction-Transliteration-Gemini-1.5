# Hindi PDF Text Extractor and Transliterator

This Python script extracts Hindi text from a PDF file (either from embedded text or using Gemini OCR) and saves two output files:

1. **Extracted Devanagari Text** – Saved as `Extraction_Data_<input_filename>.txt`
2. **Transliterated Text (IAST)** – Saved as `Gemini_transliterated_<input_filename>.txt`

---

## 🛠 Requirements

Install dependencies using `pip`:

```bash
pip install PyMuPDF Pillow google-generativeai indic-transliteration

```

You also need a Google Gemini API Key. You can get it from https://makersuite.google.com/app.

📁 File Structure
Copy
Edit
.
├── script.py
├── part2.pdf
├── Extraction_Data_part2.txt
├── Gemini_transliterated_part2.txt
└── README.md

🚀 How to Run ?
Run this command in your VScode Terminal :
```
python Devnagri_and_IAST_Output.py.py part2.pdf
```

📄 Output Files
Given an input file part2.pdf, the script will generate:

Extraction_Data_part2.txt – Raw extracted Hindi text (page by page)
Gemini_transliterated_part2.txt – IAST transliteration of the same text

🔐 Environment
It's recommended to use environment variables or a .env file to store your Gemini API key for security. Currently, the script uses:

python
Copy
Edit
GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
Replace with your key or refactor to use os.environ.

🤖 Features
Automatically chooses between embedded PDF text and OCR for best results.

Gemini OCR integration ensures accuracy on image-only PDFs.

Supports transliteration from Devanagari to IAST using indic_transliteration.

🧪 Example Page Output Format
diff
Copy
Edit
--- PAGE 1 ---
राम रामेति रमंे रामे रमे मनोरमे।
सहस्रनाम तत्तुल्यं रामनाम वरानने।।
Transliterated:

perl
Copy
Edit
--- PAGE 1 ---
rāma rāmeti ramaṁe rāme rame manōrame।
sahasranāma tattulyaṁ rāmanāma varānane।।
🧹 To-Do (Optional Enhancements)
Add JSON/CSV output format.

GUI for selecting files and setting options.

Store API key securely via .env.

👨‍💻 Author
Script maintained by Varun Vyas. Built with ❤️ for Hindi Kirtan digitization.
