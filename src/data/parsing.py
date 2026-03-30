from bs4 import BeautifulSoup
from datetime import datetime

class LAHDParser:
    """Static methods for parsing LAHD data."""

    @staticmethod
    def _find_prop_data(soup: BeautifulSoup, label: str) -> str:
        lbl = soup.find(string=lambda t: label in t if t else False)
        return lbl.find_next().get_text(strip=True) if lbl else "N/A"

    @staticmethod
    def _case_type_id(case_type: str) -> int:
        type_map = {
            "Complaint": 1,
            "Systematic Code Enforcement Program": 2,
            "Case Management": 3,
            "Rent Escrow Account Program": 4,
            "Hearing": 5,
            "Property Management Training Program": 10,
            "Legal": 11,
            "Emergency": 13,
            "Out Reach Case": 14
        }
        return type_map.get(case_type, 1)

    @staticmethod
    def _parse_nature(soup: BeautifulSoup) -> str:
        nature_span = soup.find("span", {"id": "lblComplaintNature"})
        return nature_span.get_text(strip=True) if nature_span else "N/A"

    @staticmethod
    def _parse_events(soup: BeautifulSoup):
        deadline_keywords = [
            "Schedule Council Removal Date",
            "Notice of General Manager Hearing",
            "Positive Outreach Report Date",
            "Compliance Date"
        ]
        found_deadlines = {}
        events = []

        for row in soup.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 2:
                continue
            try:
                date_raw = cols[0].get_text(strip=True).split(" ")[0]
                status_text = cols[1].get_text(strip=True)
                dt = datetime.strptime(date_raw, "%m/%d/%Y")
                events.append((dt, status_text))
                for kw in deadline_keywords:
                    if kw in status_text:
                        found_deadlines[kw] = dt
            except Exception:
                continue

        return events, found_deadlines

    @staticmethod
    def _choose_deadline(found_deadlines: dict):
        priority = [
            "Schedule Council Removal Date",
            "Notice of General Manager Hearing",
            "Positive Outreach Report Date",
            "Compliance Date"
        ]
        for kw in priority:
            if kw in found_deadlines:
                return found_deadlines[kw]
        return None