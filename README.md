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
* **Live Data Acquisition:** Multi-layered Data Acquisition: Automated navigation through the LAHD portal to retrieve both high-level case summaries and deep-dive historical activity.
* **Smart Urgency Mapping:** Automated classification of cases into visual statuses: `Critical` (Emergency/Legal), `Overdue`, or `Active`.
* **Color-Coded Priority System:** High-visibility table cells (Red/Orange/Gray/Green) for instant risk identification.
* **Deep-Dive Case Details:** Interactive rows reveal the nature of the violation, the current procedural step, and the full activity history.
* **Deadline Management:** Clear visibility of due dates to prevent fines and legal sanctions.

---

## 🏗️ System Architecture
The project follows **Clean Architecture** principles, ensuring a strict separation of concerns:

* **Data Layer (`src/data/`):**
    * `scraper.py`: Handles network requests and navigation logic.
    * `parsing.py`: Pure logic for extracting data from HTML structures.
    * `processor.py`: The "Business Brain" – calculates urgency, flags new cases, and enriches data.
    * `database.py`: Repository pattern for SQLite persistence and change tracking.
* **UI Layer (`src/ui/`):**
    * `ui_utils.py`: Reusable UI components and AgGrid configurations (DRY principle).
* **Entry Point (`app.py`):** A streamlined Streamlit interface orchestrating the data flow and visualization.

---

## 📁 Project Structure
```text
├── src/
│   ├── data/
│   │   ├── database.py      # Persistence Layer (SQLite & Repository Pattern)
│   │   ├── parsing.py       # HTML Extraction & Scraping Logic
│   │   ├── processor.py     # Business Logic, Urgency Mapping & Enrichment
│   │   └── scraper.py       # Network Requests & LAHD Portal Navigation
│   └── ui/
│       └── ui_utils.py      # Reusable UI Components & AgGrid Configurations
│
├── tests/                   # Automated Testing Suite (Pytest)
│   ├── test_database.py     # Data integrity & SQL persistence validation
│   ├── test_parsing.py      # Validation of HTML extraction accuracy
│   ├── test_processor.py    # Verification of urgency & "New" flag logic
│   ├── test_scraper.py      # Mocked network request & API behavior tests
│   └── test_ui_utils.py     # UI data formatting & search filter tests
├── app.py                   # Main Dashboard Entry Point (Streamlit)
├── requirements.txt         # Project Dependencies
└── property_monitoring.db   # Local SQLite Database (Auto-generated)
```
---

## 🛠 Tech Stack
* **Frontend:** Streamlit – For a fast, modern, and responsive user interface.
* **Data Grid:** Streamlit-AgGrid – Powering interactive tables with conditional formatting and advanced filtering.
* **Scraping:** BeautifulSoup4 & Requests – For precise data extraction from complex HTML structures.
* **Database:** SQLite – Local, persistent data management.
* **Tests:** Pytest

---
## 🚀 Getting Started
Follow these steps to get the dashboard up and running on your local machine:

### 1. Clone the Repository
Open your terminal and run:
```bash
git clone https://github.com/Sara-Cohen-dev/Property-Monitoring-Dashboard.git
cd Property-Monitoring-Dashboard
```

### 2. Create and Activate a Virtual Environment (Recommended)
```bash
# Create environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

### 3. Install Dependencies:
```bash
pip install -r requirements.txt
```

### 4. Run the Dashboard:
```bash
python -m streamlit run app.py
```
### 5. Run the Tests (Optional)
To ensure data integrity and scraping logic accuracy, run the automated test suite:
```bash
python -m pytest tests
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
* **Case Consolidation Logic:** Developed to handle complex legal lifecycles (e.g., SCEP inspections transitioning into REAP). The system groups related activities by Case Number to provide a single, unified status for each legal proceeding.

---

### 💡 Smart Notification Logic
* **Current Implementation:** Automatically flags cases opened within the last 14 days as **"New"** for immediate visibility.
* **Future Roadmap:** Implementing **Field-Level Delta-Checks**. This will track updates to existing cases (status changes, new steps, or shifted deadlines), as a procedural update is often as critical as a new case.

### Future Improvements & Scalability:
* **Sensitive Change Detection:** Flagging updates to existing cases as "New" to ensure immediate attention rather than just tracking new cases.
* **Auto-Sync Engine:** A background process (Scheduled Task) to periodically scan all APNs in the database and update records automatically.
* **Real-Time Alerts:** Integration with WhatsApp/Email to push notifications the moment a critical change is detected.
* **Multi-Property Portfolio View:** A global dashboard featuring an aggregated "Health Score" per asset.

---

## 🏗️ Production-Grade Scaling
If this project were to be scaled for a high-volume enterprise environment, the following architecture shifts would be implemented:

* **Architecture:** Transition from a monolithic Streamlit app to a **Decoupled Architecture**:
    * **Frontend:** A modern **React.js** or **Next.js** application for a highly responsive, custom user experience.
    * **Backend:** A high-performance **FastAPI** or **Node.js** REST API to manage data flow and business logic.
* **Database:** Migration to **PostgreSQL** to support high concurrency, complex relationships, and multi-user access.
* **Task Queue:** Implementation of **Celery & Redis** to manage asynchronous background scraping tasks for thousands of properties simultaneously.
* **Authentication:** Integration with **Auth0** or AWS Cognito to ensure secure, multi-tenant access for different management teams.
* **Deployment:** Containerization via **Docker** and orchestration with **Kubernetes** for seamless scaling and high availability on cloud providers (AWS/GCP).

---

### 👩‍💻 Developed by
**Sara Cohen** - Full Stack Developer & Data Enthusiast
