import streamlit as st
import pandas as pd
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="EquipShare Hub",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS Styling for a Sleek, Futuristic Look ---
st.markdown("""
    <style>
    /* Main background & font styling */
    .main {
        background-color: #0e1117;
        color: #f0f2f6;
    }
    
    /* Custom Header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #8a99ad;
        margin-bottom: 2rem;
    }

    /* Card styling for Inventory */
    .eq-card {
        background-color: #1a1f2c;
        border: 1px solid #2d3748;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease;
    }
    .eq-card:hover {
        border-color: #4facfe;
        transform: translateY(-2px);
    }
    
    /* Sidebar customization */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #21262d;
    }
    
    /* Success / Info box tweaks */
    div.stAlert {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Initialize Session State for Inventory & Bookings ---
if "inventory" not in st.session_state:
    st.session_state.inventory = [
        {"id": 1, "name": "NVIDIA RTX 4090 GPU Server", "category": "Computing", "status": "Available", "specs": "24GB VRAM, CUDA 12.0"},
        {"id": 2, "name": "Industrial 3D Printer (Ultimaker)", "category": "Fabrication", "status": "Available", "specs": "PLA/ABS, Dual Extrusion"},
        {"id": 3, "name": "Digital Oscilloscope 100MHz", "category": "Electronics", "status": "In-Use", "specs": "2-Channel, 1GS/s"}
    ]

if "bookings" not in st.session_state:
    st.session_state.bookings = []

if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = []

# --- Sidebar Portal Navigation ---
st.sidebar.markdown("### 🔐 User Access Portal")
role = st.sidebar.radio(
    "Select Your Role:",
    ["Student / Researcher (User)", "Lab Manager (Owner)", "Audit & Compliance Log"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Use the sidebar to switch between roles for testing student requests and lab management approvals.")

# --- Main Application Header ---
st.markdown('<p class="main-header">EquipShare Hub</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Trusted Institutional Resource & Equipment Sharing Platform</p>', unsafe_allow_html=True)

# ==========================================
# 1. STUDENT / RESEARCHER VIEW
# ==========================================
if role == "Student / Researcher (User)":
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.markdown("### 📦 Available Inventory")
        search_query = st.text_input("🔍 Search equipment or spaces by name/category:", "")
        
        # Filter inventory
        filtered_items = [
            item for item in st.session_state.inventory 
            if search_query.lower() in item['name'].lower() or search_query.lower() in item['category'].lower()
        ]
        
        for item in filtered_items:
            status_color = "🟢" if item['status'] == "Available" else "🔴"
            st.markdown(f"""
                <div class="eq-card">
                    <h4>{status_color} {item['name']}</h4>
                    <p style="color: #a0aec0; margin: 2px 0;"><b>Category:</b> {item['category']} | <b>Specs:</b> {item['specs']}</p>
                    <p style="margin: 2px 0;"><b>Status:</b> <code>{item['status']}</code></p>
                </div>
            """, unsafe_allow_html=True)
            
    with col2:
        st.markdown("### 📝 Submit Booking Request")
        with st.form("booking_form"):
            user_name = st.text_input("Your Name / Roll No:")
            available_names = [item['name'] for item in st.session_state.inventory if item['status'] == "Available"]
            
            selected_eq = st.selectbox("Select Equipment:", available_names if available_names else ["No Equipment Available"])
            reason = st.text_area("Reason / Project Work Details:")
            skill_id = st.text_input("Enter Skill Certificate ID / Reference (Safety Clearance):")
            
            submitted = st.form_submit_button("🚀 Submit Request")
            
            if submitted:
                if not user_name or not reason or not skill_id:
                    st.warning("⚠️ Please fill in all fields before submitting.")
                elif not available_names:
                    st.error("❌ No equipment currently available for booking.")
                else:
                    new_booking = {
                        "id": len(st.session_state.bookings) + 1,
                        "user": user_name,
                        "equipment": selected_eq,
                        "reason": reason,
                        "skill_id": skill_id,
                        "status": "Pending Approval",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state.bookings.append(new_booking)
                    
                    # Log to audit
                    st.session_state.audit_logs.append({
                        "Action": "Booking Requested",
                        "User": user_name,
                        "Target": selected_eq,
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    st.success("🎉 Booking request submitted successfully! Awaiting Lab Manager review.")
                    st.balloons()

    # User's active status
    st.markdown("---")
    st.markdown("### 📋 My Active Requests & Status")
    if st.session_state.bookings:
        df_bookings = pd.DataFrame(st.session_state.bookings)
        st.dataframe(df_bookings, use_container_width=True)
    else:
        st.info("No active booking requests found.")

# ==========================================
# 2. LAB MANAGER (OWNER) VIEW
# ==========================================
elif role == "Lab Manager (Owner)":
    st.markdown("### 🛠️ Lab Manager Control Center")
    st.write("Review incoming student requests, manage equipment status, and oversee lab resource allocation.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Equipment Registered", value=len(st.session_state.inventory))
    with col2:
        pending_count = len([b for b in st.session_state.bookings if b['status'] == "Pending Approval"])
        st.metric(label="Pending Approvals", value=pending_count)
        
    st.markdown("---")
    st.markdown("### 📥 Pending & Active Requests")
    
    if st.session_state.bookings:
        for idx, booking in enumerate(st.session_state.bookings):
            with st.container():
                st.markdown(f"""
                    <div class="eq-card">
                        <h4>Request #{booking['id']} - {booking['equipment']}</h4>
                        <p><b>Requested By:</b> {booking['user']} | <b>Time:</b> {booking['timestamp']}</p>
                        <p><b>Reason:</b> {booking['reason']}</p>
                        <p><b>Safety Cert ID:</b> <code>{booking['skill_id']}</code> | <b>Current Status:</b> <b>{booking['status']}</b></p>
                    </div>
                """, unsafe_allow_html=True)
                
                if booking['status'] == "Pending Approval":
                    col_a, col_b = st.columns(2)
                    if col_a.button(f"✅ Approve #{booking['id']}", key=f"app_{idx}"):
                        booking['status'] = "Approved & Active"
                        # Update equipment status
                        for eq in st.session_state.inventory:
                            if eq['name'] == booking['equipment']:
                                eq['status'] = "In-Use"
                        st.session_state.audit_logs.append({
                            "Action": "Booking Approved",
                            "User": "Lab Manager",
                            "Target": booking['equipment'],
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        st.rerun()
                        
                    if col_b.button(f"❌ Reject #{booking['id']}", key=f"rej_{idx}"):
                        booking['status'] = "Rejected"
                        st.session_state.audit_logs.append({
                            "Action": "Booking Rejected",
                            "User": "Lab Manager",
                            "Target": booking['equipment'],
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
                        st.rerun()
                st.markdown("---")
    else:
        st.info("No pending requests to review.")

# ==========================================
# 3. AUDIT & COMPLIANCE LOG VIEW
# ==========================================
elif role == "Audit & Compliance Log":
    st.markdown("### 📊 Immutable Audit History & Activity Logs")
    st.write("Every important action (Approvals, Rejections, Check-ins, Returns) is recorded transparently for institutional governance.")
    
    if st.session_state.audit_logs:
        df_logs = pd.DataFrame(st.session_state.audit_logs)
        st.dataframe(df_logs, use_container_width=True)
    else:
        st.info("No activity recorded yet in the audit history.")