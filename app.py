import streamlit as st
import pandas as pd
import os
import re

CSV_FILE = "requests.csv"
ADMIN_PASSWORD = "admin"

EQUIPMENT_STOCK = {
    "NVIDIA RTX 4090 GPU Server": 3,
    "Industrial 3D Printer (Ultimaker)": 5,
    "Oscilloscope 100MHz": 4
}

VALID_SKILL_IDS = [
    "SK-101 (AI Safety & Ethics)", 
    "SK-102 (Advanced GPU Cluster Safety)", 
    "SK-103 (Industrial Hardware Handling)", 
    "SK-104 (Lab Compliance & Protocols)"
]

def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=["id", "user", "student_id", "university", "equipment", "reason", "skill_id", "proof_filename", "status"])

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

st.set_page_config(page_title="EquipShare Hub", page_icon="⚙️", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #00adb5; font-family: 'Inter', sans-serif; }
    .stButton>button {
        background-color: #00adb5; color: white; border-radius: 8px;
        padding: 0.5em 1em; font-weight: bold; border: none;
    }
    .stButton>button:hover { background-color: #00818a; color: #ffffff; }
    .status-approved { background-color: #1e4620; color: #4caf50; padding: 15px; border-radius: 10px; border: 1px solid #4caf50; margin-bottom: 10px; }
    .status-rejected { background-color: #4a1e1e; color: #f44336; padding: 15px; border-radius: 10px; border: 1px solid #f44336; margin-bottom: 10px; }
    .status-pending { background-color: #4a3b1e; color: #ffeb3b; padding: 15px; border-radius: 10px; border: 1px solid #ffeb3b; margin-bottom: 10px; }
    .inventory-card { background-color: #1f2833; padding: 12px; border-radius: 8px; border: 1px solid #283747; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ EquipShare Hub")
st.markdown("### *Trusted Institutional Resource & Equipment Sharing Platform*")
st.markdown("---")

# Secure Role Selection: Audit log option removed from public view
role = st.sidebar.radio("Select Portal Access:", ["Student / Researcher Portal", "Lab Manager (Owner)"])

df_requests = load_data()

def get_available_stock():
    stock = EQUIPMENT_STOCK.copy()
    current_df = load_data()
    if not current_df.empty:
        approved_df = current_df[current_df["status"].isin(["Approved", "Handed Over"])]
        for eq in approved_df["equipment"]:
            if eq in stock and stock[eq] > 0:
                stock[eq] -= 1
    return stock

if role == "Student / Researcher Portal":
    st.subheader("🎓 Student Authentication & Verification")
    
    if "authenticated_student" not in st.session_state:
        with st.expander("🔐 Student Login (Required to Access Portal)", expanded=True):
            student_id_input = st.text_input("Enter Official Roll No / Student ID:", placeholder="e.g., 2026/AIML/01 or BTECH1024")
            student_name_input = st.text_input("Your Full Name:")
            login_clicked = st.button("Verify & Open Student Dashboard")

        if login_clicked:
            clean_sid = student_id_input.strip()
            clean_sname = student_name_input.strip()
            
            if len(clean_sid) < 3:
                st.error("⚠️ Please enter a valid University Roll No or Student ID.")
            elif len(clean_sname) < 3 or not re.match("^[a-zA-Z\\s\\.]+$", clean_sname):
                st.error("⚠️ Please enter a valid full name (letters only).")
            else:
                st.session_state["authenticated_student"] = clean_sid
                st.session_state["student_name"] = clean_sname
                st.success(f"✅ Welcome, {clean_sname} (ID: {clean_sid})!")
                st.rerun()

    if "authenticated_student" in st.session_state:
        current_student_id = st.session_state["authenticated_student"]
        current_student_name = st.session_state["student_name"]
        
        if st.sidebar.button("🚪 Logout Student"):
            del st.session_state["authenticated_student"]
            del st.session_state["student_name"]
            st.rerun()

        st.markdown("---")
        st.subheader("📊 Live Equipment Availability & Stock")
        current_stock = get_available_stock()
        cols = st.columns(len(current_stock))
        for i, (eq_name, avail_qty) in enumerate(current_stock.items()):
            with cols[i]:
                total_qty = EQUIPMENT_STOCK[eq_name]
                st.markdown(f"""
                    <div class="inventory-card">
                        <b>{eq_name}</b><br>
                        Available: <span style="color: #00adb5; font-size: 1.2em;">{avail_qty}</span> / {total_qty}
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("🔔 Live Notification & Request Status")
        latest_df = load_data()
        my_reqs = latest_df[latest_df["student_id"] == current_student_id] if not latest_df.empty else pd.DataFrame()

        if not my_reqs.empty:
            for idx, row in my_reqs.iterrows():
                status = row["status"]
                eq = row["equipment"]
                req_id = row["id"]
                proof = row.get("proof_filename", "None")
                
                if status in ["Approved", "Handed Over"]:
                    st.markdown(f"""
                        <div class="status-approved">
                            <b>✅ Request #{req_id} - Status: {status}</b><br>
                            Your booking for <b>{eq}</b> is active. Safety Proof File: <i>{proof}</i>
                        </div>
                    """, unsafe_allow_html=True)
                elif status == "Returned":
                    st.markdown(f"""
                        <div class="status-approved">
                            <b>📦 Request #{req_id} - RETURNED SAFELY</b><br>
                            Equipment <b>{eq}</b> has been successfully returned and verified.
                        </div>
                    """, unsafe_allow_html=True)
                elif status == "Rejected":
                    st.markdown(f"""
                        <div class="status-rejected">
                            <b>❌ Request #{req_id} REJECTED!</b><br>
                            Your booking for <b>{eq}</b> was declined by the manager.
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="status-pending">
                            <b>⏳ Request #{req_id} PENDING REVIEW</b><br>
                            Your booking for <b>{eq}</b> is under review.
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("ℹ️ You have no active requests. Submit a booking below.")

        st.markdown("---")
        st.subheader("📝 Submit New Equipment Booking Request")
        
        with st.form("secure_booking_form"):
            st.info(f"Logged in as: **{current_student_name}** (ID: {current_student_id})")
            
            university = st.text_input("University / Institution Name:")
            equipment = st.selectbox("Select Equipment:", list(EQUIPMENT_STOCK.keys()))
            reason = st.text_area("Reason / Project Work Details (Must be meaningful, at least 5 words):")
            skill_id = st.selectbox("Select Certified Skill Clearance ID:", VALID_SKILL_IDS)
            
            submitted = st.form_submit_button("🚀 Submit Request")
            
            if submitted:
                clean_uni = university.strip()
                clean_reason = reason.strip()
                words = clean_reason.split()

                current_stock = get_available_stock()
                if current_stock.get(equipment, 0) <= 0:
                    st.error(f"⚠️ Sorry! '{equipment}' is currently out of stock.")
                elif len(clean_uni) < 3:
                    st.error("⚠️ Please enter a valid University / Institution name.")
                elif len(words) < 5 or len(clean_reason) < 25:
                    st.error("⚠️ Reason is too short! Please provide a proper project description.")
                elif len(max(words, key=len)) > 20:
                    st.error("⚠️ Meaningless junk text detected in reason!")
                else:
                    live_df = load_data()
                    new_id = int(live_df["id"].max() + 1) if not live_df.empty else 1
                    new_row = pd.DataFrame([{
                        "id": new_id,
                        "user": current_student_name,
                        "student_id": current_student_id,
                        "university": clean_uni,
                        "equipment": equipment,
                        "reason": clean_reason,
                        "skill_id": skill_id,
                        "proof_filename": "Awaiting Handover",
                        "status": "Pending"
                    }])
                    updated_df = pd.concat([live_df, new_row], ignore_index=True)
                    save_data(updated_df)
                    st.success("✅ Booking request submitted successfully! Status updated above.")
                    st.rerun()

        st.subheader("📋 My Request Records")
        if not my_reqs.empty:
            st.dataframe(my_reqs, use_container_width=True)
    else:
        st.warning("🔒 Please verify your Student Roll No / ID above to access the booking dashboard.")

else:
    # SECURE LAB MANAGER PORTAL (Contains Control Center & Audit Log restricted behind password)
    st.subheader("🔒 Lab Manager Secure Control Center")
    password = st.text_input("Enter Lab Manager Password:", type="password", placeholder="Enter admin password...")
    
    if password == ADMIN_PASSWORD:
        st.success("🔓 Access Granted!")
        
        # Use tabs inside secure manager view for clean organization
        mgr_tab, audit_tab = st.tabs(["⚡ Request Management & Stock", "📜 Audit & Compliance Log"])
        
        manager_df = load_data()
        current_stock = get_available_stock()
        
        with mgr_tab:
            st.write("Review incoming requests instantly, manage stock, and upload condition proofs.")
            
            st.markdown("---")
            st.subheader("📊 Current Live Stock Status")
            for eq_name, qty in current_stock.items():
                st.write(f"- **{eq_name}**: `{qty}` available out of `{EQUIPMENT_STOCK[eq_name]}` total units.")

            st.markdown("---")
            st.subheader("📋 Pending & Active System Requests")
            if not manager_df.empty:
                st.dataframe(manager_df, use_container_width=True)
                
                req_ids = manager_df["id"].tolist()
                selected_id = st.selectbox("Select Request ID to Manage:", req_ids) if req_ids else None
                
                if selected_id:
                    selected_row = manager_df[manager_df["id"] == selected_id].iloc[0]
                    st.write(f"**Selected Request:** Student: {selected_row['user']} | Equipment: {selected_row['equipment']} | Status: {selected_row['status']}")
                    
                    action = st.selectbox("Select Action / Status Update:", ["Approve & Hand Over (Upload Proof)", "Reject", "Mark as Returned & Verify Condition"])
                    uploaded_proof = st.file_uploader("Upload Condition Photo/Video Proof (Handover / Return):", type=["png", "jpg", "jpeg", "mp4"])
                    
                    if st.button("Confirm Status & Save Proof"):
                        proof_name = uploaded_proof.name if uploaded_proof is not None else "No File Uploaded"
                        latest_fresh_df = load_data()
                        
                        if "Approve" in action:
                            if current_stock.get(selected_row['equipment'], 0) <= 0:
                                st.error("Cannot approve! Equipment is out of stock.")
                            else:
                                latest_fresh_df.loc[latest_fresh_df["id"] == selected_id, "status"] = "Handed Over"
                                latest_fresh_df.loc[latest_fresh_df["id"] == selected_id, "proof_filename"] = f"Handover: {proof_name}"
                                save_data(latest_fresh_df)
                                st.success(f"Request #{selected_id} approved and marked as Handed Over with proof!")
                                st.rerun()
                        elif "Reject" in action:
                            latest_fresh_df.loc[latest_fresh_df["id"] == selected_id, "status"] = "Rejected"
                            latest_fresh_df.loc[latest_fresh_df["id"] == selected_id, "proof_filename"] = "Rejected"
                            save_data(latest_fresh_df)
                            st.success(f"Request #{selected_id} has been rejected.")
                            st.rerun()
                        elif "Returned" in action:
                            latest_fresh_df.loc[latest_fresh_df["id"] == selected_id, "status"] = "Returned"
                            latest_fresh_df.loc[latest_fresh_df["id"] == selected_id, "proof_filename"] = f"Return Verified: {proof_name}"
                            save_data(latest_fresh_df)
                            st.success(f"Equipment for Request #{selected_id} marked as Returned safely with condition proof!")
                            st.rerun()
            else:
                st.info("No requests to review.")
                
        with audit_tab:
            st.subheader("📜 Institutional Audit Trail & Compliance Records")
            st.write("Complete secured history of all user requests, allocations, and safety proofs.")
            if not manager_df.empty:
                st.dataframe(manager_df, use_container_width=True)
            else:
                st.info("No audit logs available.")
                
    elif password != "":
        st.error("❌ Incorrect Password! Unauthorized access denied.")
    else:
        st.info("Please enter the administrator password to unlock secure manager features.")
