import streamlit as st
import pandas as pd
import os
import re

CSV_FILE = "requests.csv"
ADMIN_PASSWORD = "admin"  # Tum ise change kar sakti ho

# Authorized Skill IDs for institutional clearance
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
        return pd.DataFrame(columns=["id", "user", "university", "equipment", "reason", "skill_id", "status"])

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

st.set_page_config(page_title="EquipShare Hub", page_icon="⚙️", layout="wide")

st.title("⚙️ EquipShare Hub")
st.write("Trusted Institutional Resource & Equipment Sharing Platform")

role = st.sidebar.radio("Select Your Role:", ["Student / Researcher (User)", "Lab Manager (Owner)", "Audit & Compliance Log"])

df_requests = load_data()

if role == "Student / Researcher (User)":
    st.subheader("📝 Submit Booking Request")
    
    with st.form("booking_form"):
        user_name = st.text_input("Your Name / Roll No:")
        university = st.text_input("University / Institution Name:")
        equipment = st.selectbox("Select Equipment:", ["NVIDIA RTX 4090 GPU Server", "Industrial 3D Printer (Ultimaker)", "Oscilloscope 100MHz"])
        reason = st.text_area("Reason / Project Work Details (Minimum 20 characters):")
        
        skill_id = st.selectbox("Select Certified Skill Clearance ID:", VALID_SKILL_IDS)
        
        submitted = st.form_submit_button("🚀 Submit Request")
        
        if submitted:
            clean_name = user_name.strip()
            clean_uni = university.strip()
            clean_reason = reason.strip()

            # Strict Validations
            if len(clean_name) < 3 or not re.match("^[a-zA-Z\\s\\.]+$", clean_name):
                st.error("⚠️ Please enter a valid name (letters and spaces only).")
            elif len(clean_uni) < 3:
                st.error("⚠️ Please enter a valid University / Institution name.")
            elif len(clean_reason) < 20:
                st.error("⚠️ Reason is too short! Please provide a detailed project description (at least 20 characters).")
            else:
                new_id = int(df_requests["id"].max() + 1) if not df_requests.empty else 1
                new_row = pd.DataFrame([{
                    "id": new_id,
                    "user": clean_name,
                    "university": clean_uni,
                    "equipment": equipment,
                    "reason": clean_reason,
                    "skill_id": skill_id,
                    "status": "Pending"
                }])
                df_requests = pd.concat([df_requests, new_row], ignore_index=True)
                save_data(df_requests)
                st.success("✅ Booking request submitted successfully! Awaiting Lab Manager review.")

    st.subheader("📋 My Active Requests & Status")
    if not df_requests.empty:
        st.dataframe(df_requests)
    else:
        st.info("No requests submitted yet.")

elif role == "Lab Manager (Owner)":
    st.subheader("🔒 Lab Manager Control Center")
    
    password = st.text_input("Enter Lab Manager Password:", type="password")
    
    if password == ADMIN_PASSWORD:
        st.success("🔓 Access Granted!")
        st.write("Review incoming student requests, manage equipment status, and oversee lab resource allocation.")
        
        pending_df = df_requests[df_requests["status"] == "Pending"]
        
        col1, col2 = st.columns(2)
        col1.metric("Total Equipment Registered", "3")
        col2.metric("Pending Approvals", len(pending_df))
        
        st.subheader("Pending & Active Requests")
        if not df_requests.empty:
            st.dataframe(df_requests)
            
            req_ids = df_requests["id"].tolist()
            selected_id = st.selectbox("Select Request ID to Update:", req_ids) if req_ids else None
            
            if selected_id:
                action = st.radio("Action:", ["Approve", "Reject"])
                if st.button("Update Status"):
                    df_requests.loc[df_requests["id"] == selected_id, "status"] = "Approved" if action == "Approve" else "Rejected"
                    save_data(df_requests)
                    st.success(f"Request #{selected_id} has been {action.lower()}ed!")
                    st.rerun()
        else:
            st.info("No pending requests to review.")
    elif password != "":
        st.error("❌ Incorrect Password! Only Lab Managers are authorized.")
    else:
        st.info("Please enter the password to access the control panel.")

else:
    st.subheader("📜 Audit & Compliance Log")
    st.write("System audit logs and historical tracking.")
    if not df_requests.empty:
        st.dataframe(df_requests)
    else:
        st.info("No logs available.")
