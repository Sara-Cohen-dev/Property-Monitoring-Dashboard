import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://housingapp.lacity.org"

# Map for internal rating (Case Type ID)
CASE_TYPE_MAP = {
    "Complaint": 1, "Systematic Code Enforcement Program": 2, "Case Management": 3,
    "Rent Escrow Account Program": 4, "Hearing": 5, "Property Management Training Program": 10,
    "Legal": 11, "Emergency": 13, "Out Reach Case": 14
}

def fetch_html(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        time.sleep(0.5)
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        return response.text
    except: return ""

def get_deep_details(apn, case_no, case_type):
    """Extracting deep data including smart deadline identification"""
    type_id = CASE_TYPE_MAP.get(case_type, 1)
    details_url = f"{BASE_URL}/reportviolation/Pages/PublicPropertyActivityReport?APN={apn}&CaseType={type_id}&CaseNo={case_no}"
    html = fetch_html(details_url)
    if not html: return None, None, None, "N/A", "N/A"
    
    soup = BeautifulSoup(html, "html.parser")
    nature = "N/A"
    nature_span = soup.find("span", {"id": "lblComplaintNature"})
    if nature_span: nature = nature_span.get_text(strip=True)

    events = []
    # Deadline priority order: Council is the most critical for closure
    deadline_keywords = [
        "Schedule Council Removal Date",
        "Notice of General Manager Hearing",
        "Positive Outreach Report Date",
        "Compliance Date"
    ]
    found_deadlines = {}

    rows = soup.find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            try:
                date_raw = cols[0].text.strip().split(" ")[0]
                status_text = cols[1].text.strip()
                dt = datetime.strptime(date_raw, "%m/%d/%Y")
                events.append((dt, status_text))
                
                for kw in deadline_keywords:
                    if kw in status_text:
                        found_deadlines[kw] = dt
            except: continue

    if not events: return None, None, None, nature, "N/A"
    
    events.sort(key=lambda x: x[0], reverse=True)
    opened_dt = min(d for d, _ in events)
    last_act = events[0][0]
    last_step = events[0][1]
    
    # Choosing the most relevant deadline
    final_deadline = next((found_deadlines[kw] for kw in deadline_keywords if kw in found_deadlines), None)
    
    return opened_dt, last_act, final_deadline, nature, last_step

def apply_business_logic(df):
    """Business logic that works directly with DB names"""
    if df.empty: return df
    today = datetime.now()
    
    # Converting date columns
    for col in ['opened_date', 'last_activity', 'deadline_date']:
        df[col] = pd.to_datetime(df[col], errors='coerce')

    def calc_urgency(row):
      
      if row['status'] == 'Closed': 
        return 'Safe'
    
      today = datetime.now()
      # Checking if the date has passed
      is_overdue = pd.notnull(row['deadline_date']) and row['deadline_date'] < today
      # Checking if the type is dangerous
      is_high_risk = row['type'] in ['Emergency', 'Legal', 'REAP', 'Hearing']
    
      if is_high_risk:
        return 'Critical'
    
      if is_overdue:
        return 'Overdue'
    
      return 'Active'

    df['urgency'] = df.apply(calc_urgency, axis=1)
    
    # Identifying new cases (14 days)
    df['is_new'] = df['opened_date'].apply(
        lambda x: 1 if pd.notnull(x) and (today - x).days <= 14 else 0
    )
    
    return df.sort_values(by=['case_number', 'last_activity'], ascending=[False, False])

def scrape_lahd_data(apn):
    """The main function - collects data and activates logic"""
    main_url = f"{BASE_URL}/reportviolation/Pages/PropAtivityCases?APN={apn}&Source=ActivityReport"
    html = fetch_html(main_url)
    if not html: return None, pd.DataFrame()
    
    soup = BeautifulSoup(html, "html.parser")
    
    def find_prop_data(label):
        lbl = soup.find(string=lambda t: label in t if t else False)
        return lbl.find_next().get_text(strip=True) if lbl else "N/A"

    prop_info = {
        "address": find_prop_data("Official Address"),
        "total_units": find_prop_data("Total Units"),
        "regional_office": find_prop_data("Code Regional Area")
    }

    cases = []
    table = next((t for t in soup.find_all("table") if "Case Number" in t.text), None)
    
    if table:
        rows = table.find_all("tr")[1:]
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 4:
                c_type = cols[1].text.strip()
                c_no = cols[2].text.strip()
                closed_val = cols[3].text.strip()
                
                opened, last, deadln, nat, step = get_deep_details(apn, c_no, c_type)
                
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

    df = pd.DataFrame(cases)
    if not df.empty:
        df = apply_business_logic(df)
    
    return prop_info, df