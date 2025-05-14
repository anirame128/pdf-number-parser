import PyPDF2
import re
from typing import List, Tuple

class PDFNumberParser:
    def __init__(self):
        pass

    def extract_text(self, path: str) -> str:
        """Extract full text from the PDF."""
        text = []
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text() or "")
        return "\n".join(text)

    def find_largest_number(self, path: str) -> Tuple[float, str]:
        """Find and return the largest numeric value and its context."""
        text = self.extract_text(path)

        # Match numbers with optional commas and decimal points
        pattern = r'-?\d{1,3}(?:,\d{3})*(?:\.\d+)?'
        numbers: List[Tuple[float, re.Match]] = []
        
        for m in re.finditer(pattern, text):
            raw_str = m.group().replace(',', '')
            try:
                raw_val = float(raw_str)
                numbers.append((raw_val, m))
            except ValueError:
                continue

        if not numbers:
            raise ValueError("No valid numeric values found.")

        # Find the largest number
        largest_val, match = max(numbers, key=lambda x: x[0])
        
        # Get some context around the number
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        context = text[start:end].strip()
        
        return largest_val, context

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python pdf_number_parser.py <path_to_pdf>")
        sys.exit(1)

    parser = PDFNumberParser()
    path = sys.argv[1]
    try:
        largest, context = parser.find_largest_number(path)
        print(f"Largest number found: {largest:,.2f}")
        print("Context:", context)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
