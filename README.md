⚙️ EquipShare Hub
*Trusted Institutional Resource & Equipment Sharing Platform*

---

## 📌 About the Project
EquipShare Hub is a comprehensive web-based institutional resource and equipment sharing platform designed for academic and research institutions. It streamlines the borrowing, tracking, approval, and secure return lifecycle for high-end laboratory hardware (such as NVIDIA RTX 4090 GPU Servers, Industrial 3D Printers, and Oscilloscopes).

---

## 🚀 Key Features
* **Role-Based Access Control (RBAC):** Separate portals tailored for Students/Researchers and Lab Managers (Owners).
* **Live Inventory & Stock Tracking:** Real-time availability calculation and stock counters.
* **Secure Booking & Validation:** Form validation featuring anti-junk text filters and certified safety skill ID clearances (`SK-101` to `SK-104`).
* **Condition Proof & Audit Trail:** Mandatory photo/video upload support for campus handovers, secure courier dispatches, and return verification.

---

## 🛠️ Technical Stack
* **Core Language:** Python 3.x
* **UI Framework:** Streamlit
* **Data Management & Persistence:** Pandas library utilizing flat-file CSV storage (`requests.csv`)
* **Media Storage:** Local directory (`uploads/`) for normalized condition-proof assets

---

## 📂 Project Directory Structure
```text
equipshare-hub/
│
├── app.py              # Main Streamlit application file containing UI and logic
├── requests.csv        # Persistent transaction and state management data log
├── requirements.txt    # Project dependencies list
└── uploads/            # Directory storing handover, dispatch, and return condition proofs



⚙️ How to Run Locally
1.Clone the repository:git clone [https://github.com/TheShadowRoot/EquipShare-Hub.git](https://github.com/TheShadowRoot/EquipShare-Hub.git)
cd EquipShare-Hub

2.Install dependencies:pip install -r requirements.txt

3.Run the Streamlit application:streamlit run app.py
