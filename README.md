# 🏠 LA Property Monitoring Dashboard

### 📊 Transforming Raw Data into Actionable Real Estate Insights
A strategic management dashboard designed for Los Angeles property managers. This tool automates the monitoring of Housing Department (LAHD) inspections, identifies safety violations, and manages priorities in real-time.

---

## 🎯 The Business Challenge
Managing large-scale property portfolios requires tight oversight of municipal inspections. Currently, the process is flawed:
* **Information Fragmentation:** Data is hosted on external sites and requires manual, one-by-one verification.
* **Delayed Response:** Managers often discover safety violations or legal deadlines only when a physical letter arrives in the mail.
* **Capacity Management:** Difficulty distinguishing between routine inspections (SCEP) and emergency incidents or legal proceedings.

**The Solution:** This tool provides end-to-end automation for data collection from the LAHD portal, categorizes cases by urgency, and presents a "Property Health" executive summary.

---

## ✨ Key Features
* **Live Data Acquisition:** Fetch up-to-date information from the LAHD portal by APN at the click of a button.
* **Smart Urgency Mapping:** Automated classification of cases into visual statuses: `Critical` (Emergency/Legal), `Overdue`, or `Active`.
* **Color-Coded Priority System:** High-visibility table cells (Red/Orange/Gray/Green) for instant risk identification.
* **Deep-Dive Case Details:** Interactive rows reveal the nature of the violation, the current procedural step, and the full activity history.
* **Deadline Management:** Clear visibility of due dates to prevent fines and legal sanctions.

---

## 🛠 Tech Stack
* **Frontend:** Streamlit – For a fast, modern, and responsive user interface.
* **Data Grid:** Streamlit-AgGrid – Powering interactive tables with conditional formatting and advanced filtering.
* **Scraping:** BeautifulSoup4 & Requests – For precise data extraction from complex HTML structures.
* **Database:** SQLite – Local, persistent data management.
* **Tests:** Pytest

---
## 🚀 Getting Started
##  Installation & Execution

Follow these steps to get the dashboard up and running on your local machine:

### 1. Clone the Repository
Open your terminal and run:
```bash
git clone https://github.com/Sara-Cohen-dev/Property-Monitoring-Dashboard.git
cd Property-Monitoring-Dashboard
```

### 2. Install Dependencies:
```bash
pip install -r requirements.txt
```

### 3. Run the Dashboard:
```bash
streamlit run app.py
```
### 4. Run the Tests (Optional)
To ensure data integrity and scraping logic accuracy, run the automated test suite:
```bash
pytest tests
```

## 🔍 Data Strategy: What we track & Why
Every data field was selected to serve a specific business need:
* **Case Number & Type:** Provides unique identification and legal context.
* **Status (Open/Closed):** Separates historical records from the current active workload.
* **Deadlines:** The most critical field for preventing legal escalation and financial penalties.
* **Urgency:** Dynamically calculated based on case type and proximity to deadlines.
* **Nature of Case:** Allows the manager to understand the specific physical defect (e.g., plumbing or smoke detectors).
* **Current Step:** Indicates exactly where the case stands within the city bureaucracy.
* **Opening/Closing Dates:** For chronological tracking and performance auditing of resolution times.

---

## 💡 Implementation Insights & Future Roadmap
### Change Detection Logic
The vision for this tool goes beyond initial scraping. In a professional environment, **any change is an event**. I have planned for a system where any update to an existing case (status change, new procedural step, or shifted deadline) is flagged as "New," ensuring the manager never misses a development.

### Future Improvements & Scalability:
* **Sensitive Change Detection:** Flagging updates to existing cases as "New" to ensure immediate attention rather than just tracking new cases.
* **Auto-Sync Engine:** A background process (Scheduled Task) to periodically scan all APNs in the database and update records automatically.
* **Real-Time Alerts:** Integration with WhatsApp/Email to push notifications the moment a critical change is detected.
* **Multi-Property Portfolio View:** A global dashboard featuring an aggregated "Health Score" per asset.

---

## 🏗 Production-Grade Scaling
If this project were to be scaled for a high-volume enterprise environment, the following architecture shifts would be implemented:

* **Database:** Migration to **PostgreSQL** to support high concurrency and multi-user access.
* **Task Queue:** Implementation of **Celery & Redis** to manage background scraping tasks for thousands of properties simultaneously.
* **Authentication:** Integration with **Auth0** or AWS Cognito to ensure secure, multi-tenant access for different management teams.
* **Deployment:** Containerization via **Docker** for seamless deployment and scaling on cloud providers.

---

### 👩‍💻 Developed by
**Sara Cohen** - Full Stack Developer & Data Enthusiast
