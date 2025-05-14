import PyPDF2
import re
from typing import List, Tuple

class PDFNumberParser:
    def __init__(self):
        # Common unit multipliers for local context detection
        self.unit_multipliers = {
            'trillion': 1_000_000_000_000,
            'billion':  1_000_000_000,
            'million':  1_000_000,
            'thousand': 1_000,
            't':        1_000_000_000_000,
            'b':        1_000_000_000,
            'm':        1_000_000,
            'k':        1_000,
        }

    def extract_text(self, path: str) -> str:
        """Extract full text from the PDF."""
        text = []
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text() or "")
        return "\n".join(text)

    def is_likely_code(self, m: re.Match, text: str) -> bool:
        """Skip numbers embedded in words or codes (letters adjacent)."""
        s, e = m.span()
        # If letter immediately before or after, treat as code/ID
        if (s > 0 and text[s-1].isalpha()) or (e < len(text) and text[e].isalpha()):
            return True
        return False

    def detect_global_multiplier(self, text: str) -> float:
        """Detect a document-wide unit multiplier from headers like '(Dollars in Millions)'."""
        lower = text.lower()
        if 'dollars in millions' in lower or '( $m)' in lower:
            return 1_000_000
        if 'dollars in thousands' in lower or '( $k)' in lower:
            return 1_000
        return 1.0

    def detect_local_multiplier(self, context: str) -> float:
        """Detect unit multiplier in the given text context (e.g., 'million', '$B')."""
        lc = context.lower()
        for unit, mult in self.unit_multipliers.items():
            # match whole words or parenthetic shortcuts like ($M), allowing for plurals
            if re.search(rf"\b{unit}s?\b", lc) or re.search(rf"\(\s*\${unit[0].upper()}\s*\)", context):
                return mult
        return 1.0

    def find_largest_numbers(self, path: str) -> Tuple[float, str]:
        """Find and return the single largest numeric value and its context."""
        text = self.extract_text(path)
        global_mult = self.detect_global_multiplier(text)

        # Match numbers with at most four comma-groups (up to 13 digits before decimal)
        # Also require at least one digit after decimal point for better precision
        pattern = r'-?\d{1,3}(?:,\d{3}){0,3}\.\d+'
        numbers: List[Tuple[float, re.Match]] = []
        for m in re.finditer(pattern, text):
            if self.is_likely_code(m, text):
                continue
            raw_str = m.group().replace(',', '')
            try:
                raw_val = float(raw_str)
            except ValueError:
                continue
            # Discard implausibly large values (over 13 digits)
            if raw_val > 1e13:
                continue
            # Only consider numbers that appear in budget-related context
            context = text[max(0, m.start()-100):min(len(text), m.end()+100)]
            if any(keyword in context.lower() for keyword in ['budget', 'dollars', 'fund', 'million', 'thousand', 'revenue', 'expense', 'total']):
                numbers.append((raw_val, m))

        if not numbers:
            raise ValueError("No valid numeric values found.")

        # Identify the largest raw value
        raw_largest, match_largest = max(numbers, key=lambda x: x[0])
        s, e = match_largest.span()

        # Capture wide context for unit detection
        context = text[max(0, s-1000):min(len(text), e+1000)].replace("\n", " ")
        local_mult = self.detect_local_multiplier(context)

        # Final adjusted value (taking into account global and local multipliers)
        adjusted = raw_largest * global_mult * local_mult
        return adjusted, context.strip()


def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python pdf_number_parser.py <path_to_pdf>")
        sys.exit(1)

    parser = PDFNumberParser()
    path = sys.argv[1]
    try:
        largest, context = parser.find_largest_numbers(path)
        print(f"Largest number found: {largest:,.2f}")
        print("Context:", context)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
