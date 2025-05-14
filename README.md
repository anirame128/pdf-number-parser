# Largest Number Finder

Extracts all numeric values from a PDF and prints the largest one found.

## Features

- Handles integers, thousands-separators (`1,234`), and decimals (`3.14`).
- Detects "values are in millions" context and scales small numbers accordingly.
- Pure-Python; no external APIs.
- Includes unit tests with `pytest` and test PDFs via `reportlab`.

## Installation

```bash
git clone git@github.com:<you>/largest-number-finder.git
cd largest-number-finder
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python find_max_number.py /path/to/your/document.pdf
# → Largest number found: 4,554,915,000,000.00
```

## Running tests

```bash
pytest
```

## How it works

1. Uses pdfplumber to extract text page by page.
2. Applies a regex to find all number-like strings.
3. Normalizes them to float and keeps track of the maximum.
4. If the text mentions "in millions," scales sub-1000 numbers by 1e6. 