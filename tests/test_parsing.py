import pytest
from bs4 import BeautifulSoup
from src.data.parsing import LAHDParser

def test_parse_nature():
    html = '<span id="lblComplaintNature">Plumbing Issue</span>'
    soup = BeautifulSoup(html, "html.parser")
    result = LAHDParser._parse_nature(soup)
    assert result == "Plumbing Issue"

def test_case_type_id():
    assert LAHDParser._case_type_id("Complaint") == 1
    assert LAHDParser._case_type_id("Emergency") == 13