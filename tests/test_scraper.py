import pytest
import requests
from src.data.scraper import LAHDScraper

@pytest.fixture
def scraper():
    return LAHDScraper()

def test_fetch_html_success(monkeypatch, scraper):
    class DummyResponse:
        status_code = 200
        text = "<html></html>"
        def raise_for_status(self): pass

    def dummy_get(*args, **kwargs):
        return DummyResponse()
    
    monkeypatch.setattr("requests.get", dummy_get)
    
    html = scraper.fetch_html("http://fake.url")
    assert html == "<html></html>"

def test_fetch_html_failure(monkeypatch, scraper):
    def dummy_get_error(*args, **kwargs):
        raise requests.exceptions.RequestException("Connection Error")
    
    monkeypatch.setattr("requests.get", dummy_get_error)
    
    html = scraper.fetch_html("http://fake.url")
    assert html == ""