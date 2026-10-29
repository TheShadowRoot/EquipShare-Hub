import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime, timedelta

CSV_FILE = "requests.csv"
UPLOAD_DIR = "uploads"
ADMIN_PASSWORD = "admin"

os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:
        try:
            df = pd.read_csv(CSV_FILE)
        except Exception:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    expected_cols = ["id", "user", "student_id", "university", "equipment", "reason", "skill_id", "proof_filename", "return_deadline", "shipping_info", "status"]
    
    if df.empty or not all(col in df.columns for col in expected_cols):
        df = pd.DataFrame([{
            "id": 1,
            "user": "Sneha",
            "student_id": "27894560",
            "university": "Tech Institute",
            "equipment": "NVIDIA RTX 4090 GPU Server",
            "reason": "Deep Learning Model Training and Research Project",
            "skill_id": "SK-102 (Advanced GPU Cluster Safety)",
            "proof_filename": "No Proof Uploaded",
            "return_deadline": "2026-11-05",
            "shipping_info": "Campus Pickup",
            "status": "Handed Over"
        }])
        df.to_csv(CSV_FILE, index=False)

    text_cols = ["user", "student_id", "university", "equipment", "reason", "skill_id", "proof_filename", "return_deadline", "shipping_info", "status"]
    for col in text_cols:
        if col not in df.columns:
            df[col] = ""
        else:
            df[col] = df[col].astype(str)
    return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

st.set_page_config(page_title="EquipShare Hub", page_icon="⚙️", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    div[data-testid="stToolbar"] {visibility: hidden;}
    
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

role = st.sidebar.radio("Select Portal Access:", ["Student / Researcher Portal", "Lab Manager (Owner)"])

def get_available_stock():
    stock = EQUIPMENT_STOCK.copy()
    current_df = load_data()
    if not current_df.empty:
        approved_df = current_df[current_df["status"].isin(["Approved", "Handed Over", "Dispatched via Courier", "Return Requested"])]
        for eq in approved_df["equipment"]:
            if eq in stock and stock[eq] > 0:
                stock[eq] -= 1
    return stock

if role == "Student / Researcher Portal":
    st.subheader("🎓 Student Authentication & Dashboard")
    
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
                proof = str(row.get("proof_filename", "")).strip().replace("\\", "/")
                deadline = row.get("return_deadline", "N/A")
                shipping = row.get("shipping_info", "N/A")
                
                if status in ["Approved", "Handed Over"]:
                    st.markdown(f"""
                        <div class="status-approved">
                            <b>✅ Request #{req_id} - Active Allocation (Campus Pickup)</b><br>
                            Equipment: <b>{eq}</b> | <b>Return Deadline: {deadline}</b>
                        </div>
                    """, unsafe_allow_html=True)
                    if proof and proof != "No Proof Uploaded" and os.path.exists(proof):
                        st.image(proof, caption=f"Manager Handover Proof for Request #{req_id}", width=300)
                elif status == "Dispatched via Courier":
                    st.markdown(f"""
                        <div class="status-approved">
                            <b>🚚 Request #{req_id} - DISPATCHED VIA SECURE COURIER</b><br>
                            Equipment: <b>{eq}</b> | <b>Tracking Details: {shipping}</b><br>
                            <b>Return Deadline: {deadline}</b>
                        </div>
                    """, unsafe_allow_html=True)
                    if proof and proof != "No Proof Uploaded" and os.path.exists(proof):
                        st.image(proof, caption=f"Manager Dispatch Proof for Request #{req_id}", width=300)
                elif status == "Return Requested":
                    st.markdown(f"""
                        <div class="status-pending">
                            <b>📦 Request #{req_id} - Return Verification Pending</b><br>
                            You have submitted your return proof for <b>{eq}</b>. Awaiting Lab Manager approval.
                        </div>
                    """, unsafe_allow_html=True)
                    if proof and proof != "No Proof Uploaded" and os.path.exists(proof):
                        st.image(proof, caption=f"Your Return Proof for Request #{req_id}", width=300)
                elif status == "Returned":
                    st.markdown(f"""
                        <div class="status-approved">
                            <b>📦 Request #{req_id} - RETURNED SAFELY & CLOSED</b><br>
                            Equipment <b>{eq}</b> return has been verified and approved by the manager.
                        </div>
                    """, unsafe_allow_html=True)
                elif status == "Rejected":
                    st.markdown(f"""
                        <div class="status-rejected">
                            <b>❌ Request #{req_id} REJECTED!</b><br>
                            Your booking for <b>{eq}</b> was declined.
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

        active_handovers = my_reqs[my_reqs["status"].isin(["Handed Over", "Dispatched via Courier"])] if not my_reqs.empty else pd.DataFrame()
        if not active_handovers.empty:
            st.markdown("---")
            st.subheader("🔄 Return Allocated Equipment")
            return_req_id = st.selectbox("Select Active Request ID to Return:", active_handovers["id"].tolist())
            
            return_proof_file = st.file_uploader("Upload Mandatory Return Condition Proof (Photo/Video required):", type=["png", "jpg", "jpeg", "mp4"], key="student_return_proof")
            
            if st.button("📤 Submit Return Request with Proof"):
                if return_proof_file is None:
                    st.error("⚠️ Mandatory Error: You cannot submit a return request without uploading condition proof (photo/video)!")
                else:
                    r_proof_path = os.path.join(UPLOAD_DIR, return_proof_file.name).replace("\\", "/")
                    with open(r_proof_path, "wb") as f:
                        f.write(return_proof_file.getbuffer())
                    
                    fresh_df = load_data()
                    fresh_df.loc[fresh_df["id"] == return_req_id, "status"] = "Return Requested"
                    fresh_df.loc[fresh_df["id"] == return_req_id, "proof_filename"] = r_proof_path
                    save_data(fresh_df)
                    st.success(f"✅ Return request submitted with mandatory proof for item #{return_req_id}! Awaiting Lab Manager approval.")
                    st.rerun()

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
                        "return_deadline": "N/A",
                        "shipping_info": "N/A",
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
    st.subheader("🔒 Lab Manager Secure Control Center")
    password = st.text_input("Enter Lab Manager Password:", type="password", placeholder="Enter admin password...")
    
    if password == ADMIN_PASSWORD:
        st.success("🔓 Access Granted!")
        
        req_tab, return_tab, audit_tab = st.tabs(["⚡ Pending Requests", "🔄 Return Requests Queue", "📜 Audit & Compliance Log"])
        
        manager_df = load_data()
        current_stock = get_available_stock()
        
        with req_tab:
            st.subheader("📥 New Student Booking Requests")
            pending_df = manager_df[manager_df["status"] == "Pending"] if not manager_df.empty else pd.DataFrame()
            
            if not pending_df.empty:
                st.dataframe(pending_df, use_container_width=True)
                req_ids = pending_df["id"].tolist()
                selected_p_id = st.selectbox("Select Pending Request ID to Approve/Reject:", req_ids, key="pend_sel")
                
                if selected_p_id:
                    sel_row = pending_df[pending_df["id"] == selected_p_id].iloc[0]
                    st.write(f"**Student:** {sel_row['user']} | **Equipment:** {sel_row['equipment']} | **Reason:** {sel_row['reason']}")
                    
                    p_action = st.radio("Action:", ["Approve for Campus Handover", "Approve & Dispatch via Secure Courier", "Reject Request"], key="p_act")
                    
                    courier_tracking = ""
                    if "Courier" in p_action:
                        courier_tracking = st.text_input("Enter Courier Partner & Tracking/Consignment ID:", placeholder="e.g., Blue Dart - AW109283475")

                    manager_proof = st.file_uploader("Upload Handover/Dispatch Slip Proof (Optional):", type=["png", "jpg", "jpeg", "mp4"], key="p_proof")
                    
                    if st.button("Confirm Approval & Action"):
                        p_path = "No Proof Uploaded"
                        if manager_proof is not None:
                            p_path = os.path.join(UPLOAD_DIR, manager_proof.name).replace("\\", "/")
                            with open(p_path, "wb") as f:
                                f.write(manager_proof.getbuffer())
                        
                        fresh_df = load_data()
                        if "Campus Handover" in p_action:
                            if current_stock.get(sel_row['equipment'], 0) <= 0:
                                st.error("Cannot approve! Equipment is out of stock.")
                            else:
                                due_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                                fresh_df.loc[fresh_df["id"] == selected_p_id, "status"] = "Handed Over"
                                fresh_df.loc[fresh_df["id"] == selected_p_id, "return_deadline"] = due_date
                                fresh_df.loc[fresh_df["id"] == selected_p_id, "proof_filename"] = p_path
                                fresh_df.loc[fresh_df["id"] == selected_p_id, "shipping_info"] = "Campus Pickup"
                                save_data(fresh_df)
                                st.success(f"Request #{selected_p_id} approved for campus handover! 7-day return deadline set ({due_date}).")
                                st.rerun()
                        elif "Courier" in p_action:
                            if current_stock.get(sel_row['equipment'], 0) <= 0:
                                st.error("Cannot dispatch! Equipment is out of stock.")
                            elif len(courier_tracking.strip()) < 3:
                                st.error("⚠️ Please enter a valid Courier Name & Tracking ID!")
                            else:
                                due_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
                                fresh_df.loc[fresh_df["id"] == selected_p_id, "status"] = "Dispatched via Courier"
                                fresh_df.loc[fresh_df["id"] == selected_p_id, "return_deadline"] = due_date
                                fresh_df.loc[fresh_df["id"] == selected_p_id, "proof_filename"] = p_path
                                fresh_df.loc[fresh_df["id"] == selected_p_id, "shipping_info"] = courier_tracking.strip()
                                save_data(fresh_df)
                                st.success(f"Request #{selected_p_id} dispatched via courier with tracking ID: {courier_tracking}!")
                                st.rerun()
                        else:
                            fresh_df.loc[fresh_df["id"] == selected_p_id, "status"] = "Rejected"
                            fresh_df.loc[fresh_df["id"] == selected_p_id, "return_deadline"] = "N/A"
                            fresh_df.loc[fresh_df["id"] == selected_p_id, "proof_filename"] = "Rejected"
                            fresh_df.loc[fresh_df["id"] == selected_p_id, "shipping_info"] = "N/A"
                            save_data(fresh_df)
                            st.success(f"Request #{selected_p_id} rejected.")
                            st.rerun()
            else:
                st.info("No pending booking requests right now.")

        with return_tab:
            st.subheader("🔄 Student Equipment Return Queue")
            return_df = manager_df[manager_df["status"] == "Return Requested"] if not manager_df.empty else pd.DataFrame()
            
            if not return_df.empty:
                st.dataframe(return_df, use_container_width=True)
                return_req_ids = return_df["id"].tolist()
                selected_r_id = st.selectbox("Select Return Request ID to Verify:", return_req_ids, key="ret_sel")
                
                if selected_r_id:
                    # Clean assignment to prevent syntax truncation
                    selected_ret_row = return_df[return_df["id"] == selected_r_id].iloc[0]
                    st.write(f"**Student:** {selected_ret_row['user']} | **Equipment:** {selected_ret_row['equipment']} | **Delivery Type:** {selected_ret_row['shipping_info']}")
                    
                    proof_file_path = str(selected_ret_row['proof_filename']).strip().replace("\\", "/")
                    if proof_file_path and proof_file_path != "No Proof Uploaded" and os.path.exists(proof_file_path):
                        st.image(proof_file_path, caption=f"Student's Mandatory Return Proof for Request #{selected_r_id}", width=350)
                    else:
                        st.warning(f"⚠️ Warning: No valid proof file found at path '{proof_file_path}'!")
                    
                    ret_action = st.radio("Manager Return Action:", ["Approve Return & Restore Stock", "Reject Return (Issue with condition)"], key="ret_act")
                    
                    if st.button("Confirm Return Decision"):
                        fresh_df = load_data()
                        if "Approve" in ret_action:
                            fresh_df.loc[fresh_df["id"] == selected_r_id, "status"] = "Returned"
                            save_data(fresh_df)
                            st.success(f"Return for Request #{selected_r_id} approved successfully! Stock restored.")
                            st.rerun()
                        else:
                            fresh_df.loc[fresh_df["id"] == selected_r_id, "status"] = "Handed Over"
                            fresh_df.loc[fresh_df["id"] == selected_r_id, "proof_filename"] = f"Return Rejected: Resubmit Proof"
                            save_data(fresh_df)
                            st.warning(f"Return request #{selected_r_id} rejected. Student will need to resubmit valid proof.")
                            st.rerun()
            else:
                st.info("No pending equipment return requests from students.")

        with audit_tab:
            st.subheader("📜 Institutional Audit Trail & Compliance Records")
            st.write("Complete secured history of all user requests, allocations, and safety proofs.")
            if not manager_df.empty:
                st.dataframe(manager_df, use_container_width=True)
            else:
                st.info("No audit logs available.")
                
    elif password != "":
        st.error("❌ Incorrect Password!")
    else:
        st.info("Please enter the administrator password.")
