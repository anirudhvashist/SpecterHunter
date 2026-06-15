import streamlit as st
import psutil
import os
import sys
import json
import time
import platform

# The rest of your code goes here...

# ==========================================
# 1. PAGE CONFIG - FIXED THEME SETUP
# ==========================================
st.set_page_config(
    page_title="SpecterHunter - Autonomous Security Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. INITIALIZE SESSION STATE
# ==========================================
if 'threats' not in st.session_state:
    st.session_state['threats'] = []
if 'total_scanned' not in st.session_state:
    st.session_state['total_scanned'] = 0
if 'scan_complete' not in st.session_state:
    st.session_state['scan_complete'] = False
if 'mitigated_pids' not in st.session_state:
    st.session_state['mitigated_pids'] = []
if 'console_history' not in st.session_state:
    st.session_state['console_history'] = ["[SYSTEM] Security Engine initialized. Awaiting host validation command..."]

# ==========================================
# 3. SIMPLIFIED CSS - REMOVED BROKEN THEMES
# ==========================================
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Custom card styling */
    .custom-card {
        background-color: #0e1117;
        border-radius: 0.5rem;
        padding: 1.5rem;
        border: 1px solid #2d2d2d;
        margin-bottom: 1rem;
    }
    
    .custom-card-critical {
        background-color: #0e1117;
        border-radius: 0.5rem;
        padding: 1.5rem;
        border-left: 4px solid #ff4b4b;
        border-top: 1px solid #2d2d2d;
        border-right: 1px solid #2d2d2d;
        border-bottom: 1px solid #2d2d2d;
        margin-bottom: 1rem;
    }
    
    .custom-card-high {
        background-color: #0e1117;
        border-radius: 0.5rem;
        padding: 1.5rem;
        border-left: 4px solid #ffa500;
        border-top: 1px solid #2d2d2d;
        border-right: 1px solid #2d2d2d;
        border-bottom: 1px solid #2d2d2d;
        margin-bottom: 1rem;
    }
    
    .custom-card-medium {
        background-color: #0e1117;
        border-radius: 0.5rem;
        padding: 1.5rem;
        border-left: 4px solid #00ff00;
        border-top: 1px solid #2d2d2d;
        border-right: 1px solid #2d2d2d;
        border-bottom: 1px solid #2d2d2d;
        margin-bottom: 1rem;
    }
    
    /* Metric styling */
    .metric-container {
        background-color: #0e1117;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
        border: 1px solid #2d2d2d;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Console styling */
    .console-log {
        background-color: #000000;
        color: #00ff00;
        font-family: 'Courier New', monospace;
        padding: 1rem;
        border-radius: 0.5rem;
        height: 400px;
        overflow-y: auto;
        font-size: 0.85rem;
        border: 1px solid #00ff00;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    
    .main-header p {
        color: #e0e0e0;
        margin-top: 0.5rem;
    }
    
    /* Threat row styling */
    .threat-row {
        margin-bottom: 1rem;
        padding: 0;
    }
    
    /* Fix for Streamlit default spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    
    /* Custom button styling */
    .stButton > button {
        width: 100%;
        font-weight: bold;
    }
    
    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.75rem;
        font-weight: bold;
    }
    
    .badge-critical {
        background-color: #ff4b4b;
        color: white;
    }
    
    .badge-high {
        background-color: #ffa500;
        color: white;
    }
    
    .badge-medium {
        background-color: #00ff00;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR CONFIGURATION
# ==========================================
with st.sidebar:
    st.markdown("## 🖥️ SYSTEM CONTROLS")
    st.markdown("---")
    
    st.markdown("**Engine Status:**")
    st.success("🟢 ACTIVE")
    
    st.markdown("**Platform:**")
    st.info(f"{platform.system()} {platform.release()}")
    
    st.markdown("---")
    
    severity_filter = st.multiselect(
        "🎯 Threat Filter",
        options=["Critical", "High", "Medium"],
        default=["Critical", "High", "Medium"],
        help="Select severity levels to display"
    )
    
    st.markdown("---")
    st.markdown("### 📊 Statistics")
    
    total_threats = len(st.session_state['threats'])
    mitigated = len(st.session_state['mitigated_pids'])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Threats", total_threats)
    with col2:
        st.metric("Neutralized", mitigated)
    
    st.markdown("---")
    st.caption("SpecterHunter v2.0 | Autonomous Security Agent")

# ==========================================
# 5. MAIN HEADER
# ==========================================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style="text-align: center;">
        <h1 style="color: #667eea;">🛡️ SPECTERHUNTER</h1>
        <h3 style="color: #764ba2;">Autonomous Host Forensics & Threat Isolation</h3>
        <p style="color: #9ca3af;">Real-time process monitoring, file system analysis, and automated threat neutralization</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 6. METRICS ROW
# ==========================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    threat_count = len(st.session_state['threats'])
    threat_color = "#ff4b4b" if threat_count > 0 else "#00ff00"
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">⚠️ THREAT INDICATORS</div>
        <div class="metric-value" style="color: {threat_color};">{threat_count}</div>
        <div class="metric-label">{'ACTION REQUIRED' if threat_count > 0 else 'HOST CLEAR'}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">📊 TELEMETRY ELEMENTS</div>
        <div class="metric-value" style="color: #00ff00;">{st.session_state['total_scanned']}</div>
        <div class="metric-label">MEMORY & DISK MAPPED</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-container">
        <div class="metric-label">🤖 AGENT PROFILE</div>
        <div class="metric-value" style="color: #00ff00;">ACTIVE</div>
        <div class="metric-label">SELF-HEALING READY</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-container">
        <div class="metric-label">🔍 THREAT INTEL</div>
        <div class="metric-value" style="color: #00ff00;">REAL-TIME</div>
        <div class="metric-label">HEURISTIC ANALYSIS</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 7. SCAN BUTTON
# ==========================================
scan_button = st.button("🚀 ENGAGE AUTOMATED THREAT HUNT", type="primary", use_container_width=True)

if scan_button:
    with st.spinner("🔍 Scanning system for threats..."):
        progress_bar = st.progress(0)
        
        # Simulated scan with progress
        threats = []
        scanned = 0
        
        # Step 1: Network analysis
        progress_bar.progress(10, text="📡 Analyzing network connections...")
        time.sleep(0.5)
        
        active_network_pids = set()
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'ESTABLISHED' and conn.pid:
                    active_network_pids.add(conn.pid)
        except:
            pass
        
        # Step 2: Process analysis
        progress_bar.progress(30, text="🔍 Scanning running processes...")
        time.sleep(0.5)
        
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                scanned += 1
                p_name = proc.info['name'].lower() if proc.info['name'] else ""
                p_exe = proc.info['exe'] if proc.info['exe'] else ""
                p_pid = proc.info['pid']
                
                if p_pid in st.session_state['mitigated_pids']:
                    continue
                
                net_status = "🌐 ACTIVE" if p_pid in active_network_pids else ""
                
                # Threat detection
                if "rainmeter" in p_name:
                    threats.append({
                        "PID": p_pid,
                        "Name": proc.info['name'],
                        "Path": p_exe,
                        "Severity": "High",
                        "Details": f"Suspicious user-space execution {net_status}",
                        "Type": "Memory Hook"
                    })
                elif "svchost" in p_name and p_exe and "system32" not in p_exe.lower():
                    threats.append({
                        "PID": p_pid,
                        "Name": proc.info['name'],
                        "Path": p_exe,
                        "Severity": "Critical",
                        "Details": f"Process masquerading detected {net_status}",
                        "Type": "Masquerading"
                    })
            except:
                continue
        
        progress_bar.progress(70, text="📁 Scanning file system...")
        time.sleep(0.5)
        
        # Step 3: File system analysis
        paths_to_scan = []
        if platform.system() == "Windows":
            paths_to_scan = [
                os.environ.get("APPDATA", ""),
                os.environ.get("PROGRAMDATA", ""),
                os.path.join(os.environ.get("TEMP", ""), "")
            ]
        else:
            paths_to_scan = ["/tmp", "/var/tmp"]
        
        for base_path in paths_to_scan:
            if base_path and os.path.exists(base_path):
                try:
                    for root, dirs, files in os.walk(base_path):
                        if root.count(os.sep) - base_path.count(os.sep) > 2:
                            continue
                        for file in files[:100]:  # Limit for performance
                            if file.endswith(('.exe', '.dll', '.xlsm')):
                                scanned += 1
                                if "update" in file.lower():
                                    threats.append({
                                        "PID": "N/A",
                                        "Name": file,
                                        "Path": os.path.join(root, file),
                                        "Severity": "Critical",
                                        "Details": "Suspicious file in user directory",
                                        "Type": "File Anomaly"
                                    })
                except:
                    continue
        
        progress_bar.progress(100, text="✅ Scan complete!")
        time.sleep(0.5)
        
        st.session_state['threats'] = threats
        st.session_state['total_scanned'] = scanned
        st.session_state['scan_complete'] = True
        st.session_state['console_history'].append(f"[{time.strftime('%H:%M:%S')}] Scan completed. Found {len(threats)} threats.")
        
        progress_bar.empty()
        st.rerun()

# ==========================================
# 8. MAIN CONTENT - THREAT DISPLAY
# ==========================================
if st.session_state['scan_complete']:
    # Filter threats based on sidebar selection
    filtered_threats = [t for t in st.session_state['threats'] if t['Severity'] in severity_filter]
    
    if filtered_threats:
        st.markdown("### 🎯 DETECTED THREATS")
        st.markdown(f"**Found {len(filtered_threats)} threat(s) matching filters**")
        st.markdown("---")
        
        for idx, threat in enumerate(filtered_threats):
            severity_class = f"custom-card-{threat['Severity'].lower()}"
            
            with st.container():
                st.markdown(f"""
                <div class="{severity_class}">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h3 style="margin: 0; color: white;">{threat['Name']}</h3>
                            <p style="margin: 5px 0; color: #9ca3af;">Type: {threat['Type']}</p>
                            <p style="margin: 5px 0; font-size: 0.85rem;">📍 {threat['Path'][:80]}...</p>
                            <p style="margin: 5px 0; font-size: 0.85rem;">🔍 {threat['Details']}</p>
                        </div>
                        <div style="text-align: right;">
                            <span class="badge badge-{threat['Severity'].lower()}">{threat['Severity']}</span>
                            <p style="margin-top: 10px; font-size: 0.8rem;">PID: {threat['PID']}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if threat['PID'] != "N/A":
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col2:
                        if st.button(f"⚠️ Neutralize", key=f"neutralize_{idx}_{threat['PID']}"):
                            try:
                                proc = psutil.Process(threat['PID'])
                                proc.terminate()
                                time.sleep(1)
                                if proc.is_running():
                                    proc.kill()
                                st.success(f"✅ Process {threat['PID']} terminated successfully")
                                st.session_state['mitigated_pids'].append(threat['PID'])
                                st.session_state['console_history'].append(f"[{time.strftime('%H:%M:%S')}] Terminated PID {threat['PID']}")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to terminate: {str(e)}")
        
        # Export button
        st.markdown("---")
        if st.button("📥 Export Threat Report (JSON)", use_container_width=True):
            report_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_scanned": st.session_state['total_scanned'],
                "threats_found": len(filtered_threats),
                "threats": filtered_threats
            }
            st.download_button(
                label="💾 Download Report",
                data=json.dumps(report_data, indent=2),
                file_name=f"specterhunter_report_{time.strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.success("🎉 No threats detected matching the selected filters!")
        st.balloons()
        
        if st.button("🔄 Start New Scan", use_container_width=True):
            st.session_state['scan_complete'] = False
            st.session_state['threats'] = []
            st.rerun()

# ==========================================
# 9. CONSOLE LOG
# ==========================================
st.markdown("---")
st.markdown("### 📟 System Console")

# Console with auto-scroll
console_container = st.container()
with console_container:
    console_text = "\n".join(st.session_state['console_history'][-20:])
    st.text_area("", console_text, height=200, disabled=True, label_visibility="collapsed")

col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🗑️ Clear Console", use_container_width=True):
        st.session_state['console_history'] = ["[SYSTEM] Console cleared"]
        st.rerun()

# ==========================================
# 10. FOOTER
# ==========================================
st.markdown("---")
st.caption(f"🛡️ SpecterHunter v2.0 | Active Protection | Last Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")