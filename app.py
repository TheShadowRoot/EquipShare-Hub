import streamlit as st
import pandas as pd
import os
import re

CSV_FILE = "requests.csv"
ADMIN_PASSWORD = "admin"

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
        return pd.DataFrame(columns=["id", "user", "student_id", "university", "equipment", "reason", "skill_id", "status"])

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

st.set_page_config(page_title="EquipShare Hub", page_icon="⚙️", layout="wide")

# Professional UI Styling with Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    h1 {
        color: #00adb5;
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        background-color: #00adb5;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #00818a;
        color: #ffffff;
    }
    .metric-card {
        background-color: #1f2833;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #283747;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚙️ EquipShare Hub")
st.markdown("### *Trusted Institutional Resource & Equipment Sharing Platform*")
st.markdown("---")

role = st.sidebar.radio("Select Portal Access:", ["Student / Researcher Portal", "Lab Manager (Owner)", "Audit & Compliance Log"])

df_requests = load_data()

if role == "Student / Researcher Portal":
    st.subheader("🎓 Student Authentication & Verification")
    
    # Mandatory Student Login / Verification step to prevent spam
    with st.expander("🔐 Student Login (Required to Unlock Booking Form)", expanded=True):
        student_id_input = st.text_input("Enter Official Student Roll No / ID (e.g., ST-2026-001):", placeholder="ST-...")
        student_name_input = st.text_input("Your Full Name:")
        
        login_clicked = st.button("Verify & Proceed to Form")

    if login_clicked:
        clean_sid = student_id_input.strip().upper()
        clean_sname = student_name_input.strip()
        
        if not clean_sid.startswith("ST-") or len(clean_sid) < 6:
            st.error("⚠️ Invalid Student ID format! It must start with 'ST-' (e.g., ST-2026-01).")
        elif len(clean_sname) < 3:
            st.error("⚠️ Please enter a valid full name.")
        else:
            st.session_state["authenticated_student"] = clean_sid
            st.session_state["student_name"] = clean_sname
            st.success(f"✅ Welcome, {clean_sname} ({clean_sid})! Form unlocked below.")

    # Show booking form only if authenticated
    if "authenticated_student" in st.session_state:
        st.markdown("---")
        st.subheader("📝 Submit Equipment Booking Request")
        
        with st.form("secure_booking_form"):
            st.info(f"Logged in as: **{st.session_state['student_name']}** ({st.session_state['authenticated_student']})")
            
            university = st.text_input("University / Institution Name:")
            equipment = st.selectbox("Select Equipment:", ["NVIDIA RTX 4090 GPU Server", "Industrial 3D Printer (Ultimaker)", "Oscilloscope 100MHz"])
            reason = st.text_area("Reason / Project Work Details (Minimum 20 characters):")
            skill_id = st.selectbox("Select Certified Skill Clearance ID:", VALID_SKILL_IDS)
            
            submitted = st.form_submit_button("🚀 Submit Verified Request")
            
            if submitted:
                clean_uni = university.strip()
                clean_reason = reason.strip()

                if len(clean_uni) < 3:
                    st.error("⚠️ Please enter a valid University / Institution name.")
                elif len(clean_reason) < 20:
                    st.error("⚠️ Reason is too short! Please provide a detailed project description (at least 20 characters).")
                else:
                    new_id = int(df_requests["id"].max() + 1) if not df_requests.empty else 1
                    new_row = pd.DataFrame([{
                        "id": new_id,
                        "user": st.session_state["student_name"],
                        "student_id": st.session_state["authenticated_student"],
                        "university": clean_uni,
                        "equipment": equipment,
                        "reason": clean_reason,
                        "skill_id": skill_id,
                        "status": "Pending"
                    }])
                    df_requests = pd.concat([df_requests, new_row], ignore_index=True)
                    save_data(df_requests)
                    st.success("✅ Secure booking request submitted successfully! Awaiting Lab Manager review.")

        st.subheader("📋 My Active Requests & Status")
        if not df_requests.empty:
            my_reqs = df_requests[df_requests["student_id"] == st.session_state["authenticated_student"]]
            if not my_reqs.empty:
                st.dataframe(my_reqs, use_container_width=True)
            else:
                st.info("You have not submitted any requests yet.")
        else:
            st.info("No requests in the system.")
    else:
        st.warning("🔒 Please verify your Student ID above to access the booking form.")

elif role == "Lab Manager (Owner)":
    st.subheader("🔒 Lab Manager Secure Control Center")
    
    password = st.text_input("Enter Lab Manager Password:", type="password", placeholder="Enter admin password...")
    
    if password == ADMIN_PASSWORD:
        st.success("🔓 Access Granted!")
        st.write("Review incoming verified student requests, manage equipment status, and oversee institutional lab allocation.")
        
        pending_df = df_requests[df_requests["status"] == "Pending"]
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Equipment Registered", "3")
        with col2:
            st.metric("Pending Approvals", len(pending_df))
        
        st.markdown("---")
        st.subheader("📋 Pending & Active System Requests")
        if not df_requests.empty:
            st.dataframe(df_requests, use_container_width=True)
            
            req_ids = df_requests["id"].tolist()
            selected_id = st.selectbox("Select Request ID to Update Status:", req_ids) if req_ids else None
            
            if selected_id:
                action = st.radio("Action:", ["Approve", "Reject"], horizontal=True)
                if st.button("Update Request Status"):
                    df_requests.loc[df_requests["id"] == selected_id, "status"] = "Approved" if action == "Approve" else "Rejected"
                    save_data(df_requests)
                    st.success(f"Request #{selected_id} has been {action.lower()}ed successfully!")
                    st.rerun()
        else:
            st.info("No pending requests to review.")
    elif password != "":
        st.error("❌ Incorrect Password! Only authorized Lab Managers can access this panel.")
    else:
        st.info("Please enter the administrator password to unlock control features.")

else:
    st.subheader("📜 Audit & Compliance Log")
    st.write("Complete institutional audit trail and historical logs.")
    if not df_requests.empty:
        st.dataframe(df_requests, use_container_width=True)
    else:
        st.info("No audit logs available.")
