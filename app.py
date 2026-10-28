import streamlit as st
import pandas as pd
import os

CSV_FILE = "requests.csv"
# Lab Manager Key / Password
ADMIN_PASSWORD = "admin"  # Tum ise apne hisab se change kar sakti ho

# Load or initialize requests data file
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        return pd.DataFrame(columns=["id", "user", "equipment", "reason", "skill_id", "status"])

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

st.set_page_config(page_title="EquipShare Hub", page_icon="⚙️", layout="wide")

st.title("⚙️ EquipShare Hub")
st.write("Trusted Institutional Resource & Equipment Sharing Platform")

# Sidebar for Role Selection
role = st.sidebar.radio("Select Your Role:", ["Student / Researcher (User)", "Lab Manager (Owner)", "Audit & Compliance Log"])

df_requests = load_data()

if role == "Student / Researcher (User)":
    st.subheader("📝 Submit Booking Request")
    
    with st.form("booking_form"):
        user_name = st.text_input("Your Name / Roll No:")
        equipment = st.selectbox("Select Equipment:", ["NVIDIA RTX 4090 GPU Server", "Industrial 3D Printer (Ultimaker)", "Oscilloscope 100MHz"])
        reason = st.text_area("Reason / Project Work Details (Minimum 10 characters):")
        skill_id = st.text_input("Enter Skill Certificate ID / Reference (Safety Clearance - e.g., SK-101):")
        
        submitted = st.form_submit_button("🚀 Submit Request")
        
        if submitted:
            # Proper Validation Check
            clean_name = user_name.strip()
            clean_reason = reason.strip()
            clean_skill = skill_id.strip()

            if len(clean_name) < 3:
                st.error("⚠️ Please enter a valid name or roll number (at least 3 characters).")
            elif len(clean_reason) < 10:
                st.error("⚠️ Please provide a detailed reason for booking (at least 10 characters).")
            elif len(clean_skill) < 3:
                st.error("⚠️ Please enter a valid Skill Certificate ID / Reference Code.")
            else:
                new_id = int(df_requests["id"].max() + 1) if not df_requests.empty else 1
                new_row = pd.DataFrame([{
                    "id": new_id,
                    "user": clean_name,
                    "equipment": equipment,
                    "reason": clean_reason,
                    "skill_id": clean_skill,
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
    
    # Password Protection
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
            
            # Action to approve/reject
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
        st.error("❌ Incorrect Password! Only Lab Managers are authorized to view this section.")
    else:
        st.info("Please enter the password to access the control panel.")

else:
    st.subheader("📜 Audit & Compliance Log")
    st.write("System audit logs and historical tracking.")
    if not df_requests.empty:
        st.dataframe(df_requests)
    else:
        st.info("No logs available.")
