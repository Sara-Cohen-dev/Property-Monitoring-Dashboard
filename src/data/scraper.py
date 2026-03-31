import time
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from functools import lru_cache
from .parsing import LAHDParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


BASE_URL = "https://housingapp.lacity.org"

class LAHDScraper(LAHDParser):
    """Scraper class to retrieve property and case info from LAHD site."""

    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url

    @lru_cache(maxsize=64)
    def fetch_html(self, url: str) -> str:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        try:
            time.sleep(0.5)
            logger.info(f"Fetching URL: {url}")
            response = requests.get(url, headers=headers, verify=False, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as exc:
            logger.error(f"Failed to fetch URL {url}: {exc}")
            return ""

    def get_deep_details(self, apn: str, case_no: str, case_type: str):
        """Extract deeper case details including smart deadline selection."""
        type_id = self._case_type_id(case_type)
        details_url = f"{self.base_url}/reportviolation/Pages/PublicPropertyActivityReport?APN={apn}&CaseType={type_id}&CaseNo={case_no}"
        html = self.fetch_html(details_url)
        if not html:
            return None, None, None, "N/A", "N/A"

        soup = BeautifulSoup(html, "html.parser")
        nature = self._parse_nature(soup)
        events, found_deadlines = self._parse_events(soup)

        if not events:
            return None, None, None, nature, "N/A"

        events.sort(key=lambda item: item[0], reverse=True)

        complaint_received_dt = next((dt for dt, status in events if "Complaint Received" in status), None)    
        if complaint_received_dt:
            opened_dt = complaint_received_dt
        else:
           opened_dt = min(dt for dt, _ in events)
        last_act = events[0][0]
        last_step = events[0][1]
        final_deadline = self._choose_deadline(found_deadlines)

        return opened_dt, last_act, final_deadline, nature, last_step

    def scrape_lahd_data(self, apn: str):
        """Main scraper entry point for a property APN."""
        main_url = f"{self.base_url}/reportviolation/Pages/PropAtivityCases?APN={apn}&Source=ActivityReport"
        html = self.fetch_html(main_url)
        if not html:
            return None, []

        soup = BeautifulSoup(html, "html.parser")
        prop_info = {
            "address": self._find_prop_data(soup, "Official Address"),
            "total_units": self._find_prop_data(soup, "Total Units"),
            "regional_office": self._find_prop_data(soup, "Code Regional Area")
        }

        cases = []
        table = next((t for t in soup.find_all("table") if "Case Number" in t.text), None)

        if table:
            rows = table.find_all("tr")[1:]
            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 4:
                    continue

                c_type = cols[1].get_text(strip=True)
                c_no = cols[2].get_text(strip=True)
                closed_val = cols[3].get_text(strip=True)
                opened, last, deadln, nat, step = self.get_deep_details(apn, c_no, c_type)

                cases.append({
                    "case_number": c_no,
                    "type": c_type,
                    "status": "Closed" if closed_val else "Open",
                    "opened_date": opened,
                    "last_activity": last,
                    "closed_date": closed_val if closed_val else None,
                    "deadline_date": deadln,
                    "nature": nat,
                    "current_step": step
                })

        return prop_info, cases
