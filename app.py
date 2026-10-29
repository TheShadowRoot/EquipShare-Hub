import streamlit as st
import pandas as pd
import os
import re

CSV_FILE = "requests.csv"
ADMIN_PASSWORD = "admin"

# Equipment Inventory Stock Management
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
        return pd.DataFrame(columns=["id", "user", "student_id", "university", "equipment", "reason", "skill_id", "proof_info", "status"])

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

role = st.sidebar.radio("Select Portal Access:", ["Student / Researcher Portal", "Lab Manager (Owner)", "Audit & Compliance Log"])

df_requests = load_data()

# Calculate available stock dynamically based on approved requests
def get_available_stock():
    stock = EQUIPMENT_STOCK.copy()
    if not df_requests.empty:
        approved_df = df_requests[df_requests["status"] == "Approved"]
        for eq in approved_df["equipment"]:
            if eq in stock and stock[eq] > 0:
                stock[eq] -= 1
    return stock

if role == "Student / Researcher Portal":
    st.subheader("🎓 Student Authentication & Verification")
    
    with st.expander("🔐 Student Login (Required to Access Portal)", expanded="authenticated_student" not in st.session_state):
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

    if "authenticated_student" in st.session_state:
        st.markdown("---")
        current_student_id = st.session_state["authenticated_student"]
        current_student_name = st.session_state["student_name"]

        # LIVE INVENTORY STOCK DISPLAY FOR STUDENTS
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
        # LIVE NOTIFICATIONS
        st.subheader("🔔 Live Notification & Request Status")
        my_reqs = df_requests[df_requests["student_id"] == current_student_id] if not df_requests.empty else pd.DataFrame()

        if not my_reqs.empty:
            for idx, row in my_reqs.iterrows():
                status = row["status"]
                eq = row["equipment"]
                req_id = row["id"]
                proof = row.get("proof_info", "No file uploaded")
                
                if status == "Approved":
                    st.markdown(f"""
                        <div class="status-approved">
                            <b>✅ Request #{req_id} APPROVED!</b><br>
                            Your booking for <b>{eq}</b> has been approved. Condition Proof Log: <i>{proof}</i>
                        </div>
                    """, unsafe_allow_html=True)
                elif status == "Rejected":
                    st.markdown(f"""
                        <div class="status-rejected">
                            <b>❌ Request #{req_id} REJECTED!</b><br>
                            Your booking for <b>{eq}</b> was declined by the Lab Manager.
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
            
            # Condition proof attachment info for pickup/return tracking
            proof_file_info = st.text_input("Upload/Attach Photo/Video Proof Filename (Handover Condition Check):", placeholder="e.g., condition_check_img_01.jpg")
            
            submitted = st.form_submit_button("🚀 Submit Verified Request")
            
            if submitted:
                clean_uni = university.strip()
                clean_reason = reason.strip()
                clean_proof = proof_file_info.strip()
                words = clean_reason.split()

                current_stock = get_available_stock()
                if current_stock.get(equipment, 0) <= 0:
                    st.error(f"⚠️ Sorry! '{equipment}' is currently out of stock (All units are allocated/approved).")
                elif len(clean_uni) < 3:
                    st.error("⚠️ Please enter a valid University / Institution name.")
                elif len(words) < 5 or len(clean_reason) < 25:
                    st.error("⚠️ Reason is too short! Please provide a proper project description.")
                elif len(max(words, key=len)) > 20:
                    st.error("⚠️ Meaningless junk text detected in reason!")
                elif not clean_proof:
                    st.error("⚠️ Please provide condition photo/video proof filename for safety tracking.")
                else:
                    new_id = int(df_requests["id"].max() + 1) if not df_requests.empty else 1
                    new_row = pd.DataFrame([{
                        "id": new_id,
                        "user": current_student_name,
                        "student_id": current_student_id,
                        "university": clean_uni,
                        "equipment": equipment,
                        "reason": clean_reason,
                        "skill_id": skill_id,
                        "proof_info": clean_proof,
                        "status": "Pending"
                    }])
                    df_requests = pd.concat([df_requests, new_row], ignore_index=True)
                    save_data(df_requests)
                    st.success("✅ Secure booking request submitted with condition proof! Status updated above.")
                    st.rerun()

        st.subheader("📋 My Request Records")
        if not my_reqs.empty:
            st.dataframe(my_reqs, use_container_width=True)
    else:
        st.warning("🔒 Please verify your Student Roll No / ID above to unlock the booking dashboard.")

elif role == "Lab Manager (Owner)":
    st.subheader("🔒 Lab Manager Control Center")
    password = st.text_input("Enter Lab Manager Password:", type="password", placeholder="Enter admin password...")
    
    if password == ADMIN_PASSWORD:
        st.success("🔓 Access Granted!")
        st.write("Review incoming verified student requests, manage equipment stock, and oversee lab resource allocation.")
        
        pending_df = df_requests[df_requests["status"] == "Pending"] if not df_requests.empty else pd.DataFrame()
        current_stock = get_available_stock()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Equipment Types", len(EQUIPMENT_STOCK))
        with col2:
            st.metric("Pending Approvals", len(pending_df) if not pending_df.empty else 0)
        
        st.markdown("---")
        st.subheader("📊 Current Live Stock Status")
        for eq_name, qty in current_stock.items():
            st.write(f"- **{eq_name}**: `{qty}` available out of `{EQUIPMENT_STOCK[eq_name]}` total units.")

        st.markdown("---")
        st.subheader("📋 Pending & Active System Requests")
        if not df_requests.empty:
            st.dataframe(df_requests, use_container_width=True)
            
            req_ids = df_requests["id"].tolist()
            selected_id = st.selectbox("Select Request ID to Update Status:", req_ids) if req_ids else None
            
            if selected_id:
                action = st.radio("Action:", ["Approve", "Reject"], horizontal=True)
                if st.button("Update Request Status"):
                    # Check stock if approving
                    selected_row = df_requests[df_requests["id"] == selected_id].iloc[0]
                    eq_item = selected_row["equipment"]
                    
                    if action == "Approve" and current_stock.get(eq_item, 0) <= 0:
                        st.error(f"Cannot approve! '{eq_item}' is completely out of stock.")
                    else:
                        df_requests.loc[df_requests["id"] == selected_id, "status"] = "Approved" if action == "Approve" else "Rejected"
                        save_data(df_requests)
                        st.success(f"Request #{selected_id} updated to {action}ed!")
                        st.rerun()
        else:
            st.info("No pending requests to review.")
    elif password != "":
        st.error("❌ Incorrect Password! Only authorized Lab Managers can access this panel.")
    else:
        st.info("Please enter the administrator password to unlock control features.")

else:
    st.subheader("📜 Audit & Compliance Log")
    st.write("Complete institutional audit trail, stock logs, and return safety proofs.")
    if not df_requests.empty:
        st.dataframe(df_requests, use_container_width=True)
    else:
        st.info("No audit logs available.")
