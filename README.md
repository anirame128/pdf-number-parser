# PDF Number Parser

This tool finds the largest number in a PDF document, taking into account natural language context about units and scales (e.g., millions, billions, etc.).

## Features

- Extracts text from PDF documents
- Finds the largest numerical value
- Handles comma-separated numbers
- Considers natural language context for unit multipliers
- Filters out implausibly large values
- Provides context around the largest number found

## Requirements

- Python 3.8+
- PyPDF2

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/pdf-number-parser.git
cd pdf-number-parser
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the script with a PDF file as an argument:

```bash
python pdf_number_parser.py path/to/your/document.pdf
```

The script will output:
- The largest number found in the document
- The context around that number
- Any unit multipliers applied based on the context

## How it Works

1. The script extracts text from the PDF using PyPDF2
2. It finds all numerical values in the text, including comma-separated numbers
3. Filters out implausibly large values that are likely outliers
4. For the largest number found, it analyzes the surrounding context
5. Determines if there are any unit multipliers (e.g., millions, billions)
6. The final value is calculated by applying any relevant multipliers

## Notes

- The script is optimized for finding budget and financial numbers
- Processing time is fast and efficient
- The script handles common unit multipliers like million, billion, trillion, etc.
- Context windows are expanded to better detect unit multipliers