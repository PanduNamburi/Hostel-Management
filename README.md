# StayInn | Premium Hostel Management Intelligence

StayInn is a high-performance, strategic management platform designed to streamline hostel operations for Wardens, Administrators, and Residents. Developed with a focus on "Strategic Command," the application replaces legacy manual tracking with real-time intelligence and visual analytics.

## 🚀 Key Functionalities

### 1. Executive Warden Dashboard
The central command center provides wardens with an immediate overview of hostel health.
- **Priority Feed**: Real-time alerts for pending complaints and outing requests.
- **Strategic Analytics**: High-level summaries of room occupancy and attendance trends.
- **Action Gateway**: Quick-access controls for managing daily operations.

### 2. Room Allocation Intelligence
A sophisticated visual engine for managing student housing.
- **Building Visualization**: A 5-floor interactive map (8 rooms per floor) showing real-time occupancy.
- **Optimal Filling Logic**: Ensures floor-by-floor room saturation (up to 4 students per room) to maintain hostel order.
- **Resident Mapping**: Direct links to resident portfolios for every allocated bed.

### 3. Attendance Auditing (2.0)
Advanced numerical tracking for precise student monitoring.
- **Period-Based Tracking**: Moves beyond simple "Present/Absent" to track specific periods attended vs. total held.
- **Historical Audit Feed**: A precision date-selector allows managers to audit attendance data for any specific day in the past.
- **Resident History**: Individual student portfolios showing cumulative presence statistics.

### 4. Complaint Evidence Dossier
A streamlined facility maintenance and resident satisfaction system.
- **Visual Evidence**: Students can upload high-resolution photo evidence with their complaints.
- **Warden Review Portal**: Wardens receive a "Verified Evidence" feed to prioritize repairs and facility issues.
- **Status Workflows**: Transparent tracking from "Pending" to "Resolved" with official resolution notes.

### 5. Access Control & Identity Enrollment
High-security entry points with a premium user experience.
- **Executive Portals**: Redesigned, high-impact Login and Registration gateways.
- **Role-Based Access**: Specialized views for Wardens (Control) and Students (Portability).

---

## 🛠 Tech Stack
- **Framework**: Django (Python)
- **Styling**: Tailwind CSS (Executive High-Contrast Palette)
- **Interactions**: Alpine.js & Vanilla JavaScript
- **Database**: SQLite / PostgreSQL
- **Media**: Integrated Photo Storage for Evidence & Profiles

## 📦 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/PanduNamburi/Hostel-Management.git
   ```

2. **Initialize Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Database Setup**:
   ```bash
   python manage.py migrate
   ```

4. **Launch Platform**:
   ```bash
   python manage.py runserver
   ```

---
*StayInn - Engineered for modern hostel excellence.*
