import tempfile
import os
import pytest
from reportlab.pdfgen import canvas
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))
from find_max_number import find_max_in_pdf

def make_pdf(text: str) -> str:
    """Create a temp PDF with one page containing `text`, return its filepath."""
    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    c = canvas.Canvas(path)
    # Draw text at (100, 750)
    for i, line in enumerate(text.split("\n")):
        c.drawString(100, 800 - i*15, line)
    c.save()
    return path

def test_simple_integers():
    path = make_pdf("Numbers: 10, 500, 42")
    assert find_max_in_pdf(path) == 500.0

def test_decimals_and_commas():
    path = make_pdf("Revenue: 1,234.56\nExpense: 2,000.00")
    assert find_max_in_pdf(path) == pytest.approx(2000.0)

def test_millions_scaling():
    text = "All figures are in millions.\nBudget: 3.15, 450"
    path = make_pdf(text)
    # 3.15→3.15e6 ; 450→450e6 → max is 450e6
    assert find_max_in_pdf(path) == pytest.approx(450e6)

def test_no_numbers():
    path = make_pdf("No numeric content here.")
    assert find_max_in_pdf(path) == 0.0 