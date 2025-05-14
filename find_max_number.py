#!/usr/bin/env python3
"""
find_max_number.py

Extracts all numeric values from a PDF and prints the largest ones found.
Handles natural language context for unit multipliers (e.g., "values in millions").
"""

import re
import sys
import pdfplumber
from dataclasses import dataclass
from typing import List, Tuple, Optional
from collections import defaultdict

# Regex: matches 1–3 digits, optional commas groups, optional decimal part
NUMBER_RE = re.compile(r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b')

# Patterns for detecting unit multipliers in text
UNIT_PATTERNS = [
    # Millions patterns
    (re.compile(r'\b(all|these|the|values|figures|amounts|numbers|totals|budgets?|costs?)\s+(?:are|is|in|listed|stated|shown|expressed|reported|presented)\s+(?:in|as)\s+millions?\b', re.IGNORECASE), 1e6),
    (re.compile(r'\b(?:in|as)\s+millions?\s+(?:of\s+dollars?)?\b', re.IGNORECASE), 1e6),
    (re.compile(r'\$M\b', re.IGNORECASE), 1e6),
    (re.compile(r'\bM\$\b', re.IGNORECASE), 1e6),
    
    # Billions patterns
    (re.compile(r'\b(all|these|the|values|figures|amounts|numbers|totals|budgets?|costs?)\s+(?:are|is|in|listed|stated|shown|expressed|reported|presented)\s+(?:in|as)\s+billions?\b', re.IGNORECASE), 1e9),
    (re.compile(r'\b(?:in|as)\s+billions?\s+(?:of\s+dollars?)?\b', re.IGNORECASE), 1e9),
    (re.compile(r'\$B\b', re.IGNORECASE), 1e9),
    (re.compile(r'\bB\$\b', re.IGNORECASE), 1e9),
    
    # Thousands patterns
    (re.compile(r'\b(all|these|the|values|figures|amounts|numbers|totals|budgets?|costs?)\s+(?:are|is|in|listed|stated|shown|expressed|reported|presented)\s+(?:in|as)\s+thousands?\b', re.IGNORECASE), 1e3),
    (re.compile(r'\b(?:in|as)\s+thousands?\s+(?:of\s+dollars?)?\b', re.IGNORECASE), 1e3),
    (re.compile(r'\$K\b', re.IGNORECASE), 1e3),
    (re.compile(r'\bK\$\b', re.IGNORECASE), 1e3),
]

@dataclass
class NumberContext:
    value: float
    raw_text: str
    page_num: int
    context: str
    multiplier: float
    confidence: float

def get_context(text: str, position: int, window: int = 100) -> str:
    """Extract context around a position in text."""
    start = max(0, position - window)
    end = min(len(text), position + window)
    return text[start:end].strip()

def detect_unit_multiplier(text: str) -> Tuple[float, float]:
    """
    Detect unit multiplier from text and return (multiplier, confidence).
    Confidence is a value between 0 and 1.
    """
    max_confidence = 0.0
    best_multiplier = 1.0
    
    for pattern, multiplier in UNIT_PATTERNS:
        matches = list(pattern.finditer(text))
        if matches:
            # Calculate confidence based on:
            # 1. Number of matches
            # 2. Proximity to numbers
            # 3. Pattern specificity
            confidence = min(1.0, len(matches) * 0.3)  # Base confidence
            if 'all' in pattern.pattern or 'these' in pattern.pattern:
                confidence += 0.2  # More specific patterns get higher confidence
            if confidence > max_confidence:
                max_confidence = confidence
                best_multiplier = multiplier
    
    return best_multiplier, max_confidence

def find_numbers_in_pdf(path: str, top_n: int = 5) -> List[NumberContext]:
    """
    Opens `path`, extracts text, finds all numbers with context,
    applies unit multipliers based on natural language context,
    and returns the top N largest values.
    """
    numbers_found = []
    text_by_page = []

    # 1) Read every page's text
    with pdfplumber.open(path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            text_by_page.append((page_num, text))

    # 2) Detect unit multiplier from the entire document
    full_text = "\n".join(text for _, text in text_by_page)
    base_multiplier, base_confidence = detect_unit_multiplier(full_text)
    if base_confidence > 0:
        print(f"[INFO] Detected unit multiplier: {base_multiplier:,.0f} (confidence: {base_confidence:.1%})")

    # 3) Find numbers in each page with context
    for page_num, page_text in text_by_page:
        # Check for page-specific unit context
        page_multiplier, page_confidence = detect_unit_multiplier(page_text)
        # Use page-specific multiplier if it has higher confidence
        multiplier = page_multiplier if page_confidence > base_confidence else base_multiplier
        confidence = max(page_confidence, base_confidence)
        
        for match in NUMBER_RE.finditer(page_text):
            raw = match.group(0)
            # Remove commas, convert to float
            value = float(raw.replace(",", ""))
            
            # Apply multiplier if confidence is high enough
            if confidence > 0.3:  # Only apply if we're reasonably confident
                value *= multiplier
            
            context = get_context(page_text, match.start())
            numbers_found.append(NumberContext(
                value=value,
                raw_text=raw,
                page_num=page_num,
                context=context,
                multiplier=multiplier,
                confidence=confidence
            ))

    # Sort by value and return top N
    return sorted(numbers_found, key=lambda x: x.value, reverse=True)[:top_n]

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path/to/document.pdf>")
        sys.exit(1)
    pdf_path = sys.argv[1]
    try:
        top_numbers = find_numbers_in_pdf(pdf_path)
        print("\nTop 5 largest numbers found:")
        print("-" * 80)
        for i, num in enumerate(top_numbers, 1):
            print(f"\n{i}. Value: {num.value:,.2f}")
            print(f"   Raw text: {num.raw_text}")
            print(f"   Page: {num.page_num}")
            print(f"   Context: ...{num.context}...")
            if num.multiplier != 1.0:
                print(f"   Unit multiplier: {num.multiplier:,.0f} (confidence: {num.confidence:.1%})")
        print("-" * 80)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(2)

if __name__ == "__main__":
    main() 