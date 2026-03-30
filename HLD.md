# 📑 High-Level Design (HLD) - LA Property Monitor

## 1. Background & Motivation
Property Management in Los Angeles requires strict adherence to LAHD (Housing Department) standards. Manually tracking fragmented data leads to delayed responses and high legal risks. 

**The Goal:** A modular, automated system that transforms raw municipal data into a prioritized executive dashboard, ensuring no compliance deadline is missed.

---

## 2. System Architecture (Solid Separation of Concerns)
The project is built on **Clean Architecture** principles, specifically implementing the **Open/Closed Principle**. Each layer is decoupled, allowing the system to be extended (e.g., new data fields, new UI themes) without modifying the core logic.

### 🏗️ Layered Breakdown:
* **Data Acquisition Layer (`src/data/`):**
    * `scraper.py`: Dedicated strictly to network requests and portal navigation.
    * `parsing.py`: Pure logic for HTML DOM extraction. 
* **Business Logic Layer (`processor.py`):**
    * The "Business Brain" that enriches raw data. It calculates urgency, maps case types, and flags "New" entries.
* **Persistence Layer (`database.py`):**
    * Implements the **Repository Pattern** to abstract SQLite operations.
* **UI Layer (`src/ui/`):**
    * `ui_utils.py`: Reusable UI components and AgGrid configurations (DRY).
* **Entry Point (`app.py`):**
    * The orchestrator that manages data flow and Streamlit state.

---

## 3. Sequence Diagram: Data Refresh Flow
1. **User** ➔ Triggers "Refresh" in the `App` (Streamlit).
2. **App** ➔ Calls `Scraper` to fetch raw HTML from LAHD.
3. **Scraper** ➔ Delegates to `Parser` to extract structured data.
4. **App** ➔ Sends structured data to `Processor` for **Enrichment** (Urgency/New flags).
5. **App** ➔ Passes enriched data to `Repository` (Database) for persistence.
6. **App** ➔ Requests `UI Utils` to render the interactive grid.

---

## 4. Database Schema
The system utilizes **SQLite** for local, persistent data management.

### **Table: `properties`** (Master Data)
`apn`, `address`, `total_units`, `regional_office`, `last_updated`

### **Table: `cases`** (Transactional Data)
`case_number`, `property_apn`, `type`, `status`, `nature`, `current_step`, `opened_date`, `deadline_date`, `last_activity`, `closed_date`, `urgency`, `is_new`

---

## 5. Component Design & Terminology
* **APN (Assessor Parcel Number):** Unique property identifier in LA.
* **Enrichment Logic:** A 14-day rolling window for "New" flags and a lookup-table for "Urgency" mapping.
* **Interactive Grids:** Client-side filtering and sorting via `AgGrid` with custom CSS-in-JS for conditional row styling.

---

## 6. Implementation & QA Strategy
* **Extensibility:** Configuration-driven explanations via `type_explanations.json`.
* **Testing:** * **Unit Tests:** Parsing accuracy via local HTML mocks.
    * **Integration Tests:** End-to-end flow from Scraping to DB persistence.
    * **UI Tests:** Date formatting and search filter verification in `ui_utils`.

## 7. Design Decisions & Trade-offs
* **Flat vs. Grouped View:** During the data analysis phase, I evaluated grouping records by Case Number to provide a unified lifecycle. However, I identified edge cases where multiple active processes exist for a single ID. To ensure 100% transparency and prevent data loss, I chose a Granular Flat View. A hierarchical "Parent-Child" UI is planned for future versions to balance clarity and detail.