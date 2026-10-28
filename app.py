import streamlit as st
import datetime
import pandas as pd

st.set_page_config(page_title="EquipShare Hub", page_icon="🔬", layout="wide")

# Local Data Initialization
if 'resources' not in st.session_state:
    st.session_state.resources = [
        {"id": 101, "name": "NVIDIA RTX 4090 GPU Server", "category": "Computing", "prereq": "Python & CUDA Certificate", "owner": "AI Lab Dept", "status": "Available"},
        {"id": 102, "name": "Industrial 3D Printer (Ultimaker)", "category": "Fabrication", "prereq": "3D CAD Training", "owner": "Makerspace", "status": "Available"},
        {"id": 103, "name": "Digital Oscilloscope 100MHz", "category": "Electronics", "prereq": "Basic Electronics Lab Passed", "owner": "ECE Dept", "status": "Available"}
    ]

if 'bookings' not in st.session_state:
    st.session_state.bookings = []

if 'audit_logs' not in st.session_state:
    st.session_state.audit_logs = []

def log_action(user, action, details):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.audit_logs.append({"Timestamp": timestamp, "User": user, "Action": action, "Details": details})

# App Header
st.title("🔬 EquipShare Hub")
st.caption("Trusted Institutional Resource & Equipment Sharing Platform")

# Sidebar Role Switcher
st.sidebar.title("🔐 User Access Portal")
role = st.sidebar.radio("Select Your Role:", ["Student / Researcher (User)", "Lab Manager (Owner)", "Audit & Compliance Log"])

# ----------------- ROLE 1: USER VIEW -----------------
if role == "Student / Researcher (User)":
    st.header("📋 Discover & Request Resources")
    
    # 1. Resource Search & Discovery
    search = st.text_input("Search equipment or spaces by name/category:")
    filtered_items = [r for r in st.session_state.resources if search.lower() in r['name'].lower() or search.lower() in r['category'].lower()]
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Available Inventory")
        for item in filtered_items:
            with st.expander(f"⚙️ {item['name']} ({item['category']})"):
                st.write(f"**Owner:** {item['owner']}")
                st.write(f"**Prerequisites:** {item['prereq']}")
                st.write(f"**Status:** {item['status']}")
                
    with col2:
        st.subheader("Submit Booking Request")
        user_name = st.text_input("Your Name / Roll No:")
        selected_item = st.selectbox("Select Equipment:", [item['name'] for item in st.session_state.resources])
        purpose = st.text_area("Reason / Project Work Details:")
        qualification_proof = st.text_input("Enter Skill Certificate ID / Reference:")
        
        if st.button("Submit Request"):
            if user_name and qualification_proof:
                req_id = len(st.session_state.bookings) + 1
                new_booking = {
                    "req_id": req_id,
                    "user": user_name,
                    "item": selected_item,
                    "purpose": purpose,
                    "proof": qualification_proof,
                    "status": "Pending Verification",
                    "checkin_notes": "Not Checked In",
                    "return_notes": "Not Returned"
                }
                st.session_state.bookings.append(new_booking)
                log_action(user_name, "Requested Resource", f"Requested {selected_item}")
                st.success(f"Request #{req_id} submitted! Sent to Lab Manager for Approval.")
            else:
                st.warning("Please fill all details and qualification proof.")

    st.markdown("---")
    st.subheader("🔄 My Active Lifecycle & Check-In Status")
    for b in st.session_state.bookings:
        if b['user'] == user_name:
            st.info(f"**Booking #{b['req_id']}** for `{b['item']}` | Status: **{b['status']}**")
            if b['status'] == "Approved":
                c1, c2 = st.columns(2)
                with c1:
                    notes = st.text_input(f"Check-in Condition Note (#{b['req_id']}):", "Equipment looks scratch-free and working.")
                    if st.button(f"Mark Check-In (#{b['req_id']})"):
                        b['status'] = "Checked-In"
                        b['checkin_notes'] = notes
                        log_action(user_name, "Check-In Completed", f"Initial Note: {notes}")
                        st.rerun()
            elif b['status'] == "Checked-In":
                notes_ret = st.text_input(f"Return Condition Note (#{b['req_id']}):", "Returned in original working condition.")
                if st.button(f"Mark Return (#{b['req_id']})"):
                    b['status'] = "Returned & Closed"
                    b['return_notes'] = notes_ret
                    log_action(user_name, "Item Returned", f"Final Note: {notes_ret}")
                    st.rerun()

# ----------------- ROLE 2: OWNER VIEW -----------------
elif role == "Lab Manager (Owner)":
    st.header("🛡️ Owner & Manager Dashboard")
    
    st.subheader("1. Add New Institutional Resource")
    with st.form("add_resource"):
        res_name = st.text_input("Resource / Equipment Name:")
        res_cat = st.selectbox("Category:", ["Computing", "Fabrication", "Electronics", "Testing Space"])
        res_prereq = st.text_input("Eligibility Requirement (e.g. Mandatory Training):")
        submitted = st.form_submit_button("List Resource")
        if submitted and res_name:
            new_id = 100 + len(st.session_state.resources) + 1
            st.session_state.resources.append({"id": new_id, "name": res_name, "category": res_cat, "prereq": res_prereq, "owner": "Lab Manager", "status": "Available"})
            log_action("Lab Manager", "Added Resource", f"Listed {res_name}")
            st.success("Resource Listed Successfully!")

    st.markdown("---")
    st.subheader("2. Review Pending Booking Requests")
    if not st.session_state.bookings:
        st.write("No requests submitted yet.")
    else:
        for b in st.session_state.bookings:
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a:
                st.write(f"**Request #{b['req_id']}** by `{b['user']}` for **{b['item']}**")
                st.write(f"*Purpose:* {b['purpose']} | *Proof ID:* {b['proof']}")
                st.write(f"*Current Status:* `{b['status']}`")
            with col_b:
                if b['status'] == "Pending Verification":
                    if st.button(f"Approve #{b['req_id']}"):
                        b['status'] = "Approved"
                        log_action("Lab Manager", "Approved Booking", f"Approved for {b['user']}")
                        st.rerun()
            with col_c:
                if b['status'] == "Pending Verification":
                    if st.button(f"Reject #{b['req_id']}"):
                        b['status'] = "Rejected"
                        log_action("Lab Manager", "Rejected Booking", f"Rejected for {b['user']}")
                        st.rerun()

# ----------------- ROLE 3: AUDIT LOG VIEW -----------------
elif role == "Audit & Compliance Log":
    st.header("📜 Immutable Audit History & Activity Logs")
    st.write("Every important action (Approvals, Rejections, Check-ins, Returns) is recorded transparently.")
    
    if st.session_state.audit_logs:
        df_logs = pd.DataFrame(st.session_state.audit_logs)
        st.dataframe(df_logs, use_container_width=True)
    else:
        st.info("No activity recorded yet in the audit history.")