import streamlit as st
import pandas as pd
import os

CSV_FILE = "requests.csv"

# Load or initialize requests data file
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        # Initial empty structure
        return pd.DataFrame(columns=["id", "user", "equipment", "reason", "skill_id", "status"])

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

st.title("EquipShare Hub")
st.write("Trusted Institutional Resource & Equipment Sharing Platform")

# Sidebar for Role Selection
role = st.sidebar.radio("Select Your Role:", ["Student / Researcher (User)", "Lab Manager (Owner)", "Audit & Compliance Log"])

df_requests = load_data()

if role == "Student / Researcher (User)":
    st.subheader("Submit Booking Request")
    
    with st.form("booking_form"):
        user_name = st.text_input("Your Name / Roll No:")
        equipment = st.selectbox("Select Equipment:", ["NVIDIA RTX 4090 GPU Server", "Industrial 3D Printer (Ultimaker)", "Oscilloscope 100MHz"])
        reason = st.text_area("Reason / Project Work Details:")
        skill_id = st.text_input("Enter Skill Certificate ID / Reference (Safety Clearance):")
        
        submitted = st.form_submit_button("🚀 Submit Request")
        
        if submitted:
            if user_name and reason and skill_id:
                new_id = int(df_requests["id"].max() + 1) if not df_requests.empty else 1
                new_row = pd.DataFrame([{
                    "id": new_id,
                    "user": user_name,
                    "equipment": equipment,
                    "reason": reason,
                    "skill_id": skill_id,
                    "status": "Pending"
                }])
                df_requests = pd.concat([df_requests, new_row], ignore_index=True)
                save_data(df_requests)
                st.success("Booking request submitted successfully! Awaiting Lab Manager review.")
            else:
                st.error("Please fill in all fields.")

    st.subheader("📋 My Active Requests & Status")
    if not df_requests.empty:
        st.dataframe(df_requests)
    else:
        st.info("No requests submitted yet.")

elif role == "Lab Manager (Owner)":
    st.subheader("Lab Manager Control Center")
    st.write("Review incoming student requests, manage equipment status, and oversee lab resource allocation.")
    
    pending_df = df_requests[df_requests["status"] == "Pending"]
    
    col1, col2 = st.columns(2)
    col1.metric("Total Equipment Registered", "3")
    col2.metric("Pending Approvals", len(pending_df))
    
    st.subheader("Pending & Active Requests")
    if not df_requests.empty:
        st.dataframe(df_requests)
        
        # Simple action to approve/reject
        req_ids = df_requests["id"].tolist()
        selected_id = st.selectbox("Select Request ID to Update:", req_ids) if req_ids else None
        
        if selected_id:
            action = st.radio("Action:", ["Approve", "Reject"])
            if st.button("Update Status"):
                df_requests.loc[df_requests["id"] == selected_id, "status"] = "Approved" if action == "Approve" else "Rejected"
                save_data(df_requests)
                st.success(f"Request {selected_id} has been {action.lower()}ed!")
                st.rerun()
    else:
        st.info("No pending requests to review.")

else:
    st.subheader("Audit & Compliance Log")
    st.write("System audit logs and historical tracking.")
    if not df_requests.empty:
        st.dataframe(df_requests)
    else:
        st.info("No logs available.")
