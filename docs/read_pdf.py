import sys
from pypdf import PdfReader

def read_pdf(pdf_path, out_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
        
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)

if __name__ == "__main__":
    read_pdf(sys.argv[1], sys.argv[2])
