import streamlit as st
import psutil
import os
import sys
import json
import time
import platform

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
# 3. MOBILE-RESPONSIVE CSS (SINGLE-LINE FIX)
# ==========================================
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Ensure application handles mobile boundaries correctly */
    .stApp {
        max-width: 100%;
        overflow-x: hidden;
    }
    
    /* Title sizing designed to dynamically scale and stay on 1 line */
    .main-title-text {
        color: #667eea; 
        margin-bottom: 0.2rem;
        font-weight: bold;
        font-size: calc(1.8rem + 1.5vw) !important;
        white-space: nowrap !important;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .main-subtitle-text {
        color: #764ba2; 
        margin-top: 0px;
        font-size: calc(0.9rem + 0.3vw) !important;
    }
    
    /* Custom card styling */
    .custom-card, .custom-card-critical, .custom-card-high, .custom-card-medium {
        background-color: #0e1117;
        border-radius: 0.5rem;
        padding: 1.5rem;
        border: 1px solid #2d2d2d;
        margin-bottom: 1rem;
        word-wrap: break-word;
    }
    
    .custom-card-critical { border-left: 4px solid #ff4b4b; }
    .custom-card-high { border-left: 4px solid #ffa500; }
    .custom-card-medium { border-left: 4px solid #00ff00; }
    
    /* Metric container styling */
    .metric-container {
        background-color: #0e1117;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
        border: 1px solid #2d2d2d;
        margin-bottom: 0.5rem;
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
    
    .badge-critical { background-color: #ff4b4b; color: white; }
    .badge-high { background-color: #ffa500; color: white; }
    .badge-medium { background-color: #00ff00; color: black; }

    /* Media query targeting mobile viewports */
    @media (max-width: 768px) {
        .metric-value {
            font-size: 1.5rem;
        }
        .metric-label {
            font-size: 0.75rem;
        }
        .custom-card, .custom-card-critical, .custom-card-high, .custom-card-medium {
            padding: 1rem;
        }
        .card-header-flex {
            flex-direction: column !important;
            align-items: start !important;
        }
        .card-badge-container {
            text-align: left !important;
            margin-top: 0.5rem;
        }
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
st.markdown("""
<div style="text-align: center; padding: 0 10px;">
    <h1 class="main-title-text">🛡️ SPECTERHUNTER</h1>
    <h4 class="main-subtitle-text">Autonomous Host Forensics & Threat Isolation</h4>
    <p style="color: #9ca3af; font-size: 0.9rem;">Real-time process monitoring, file system analysis, and automated threat neutralization</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ==========================================
# 6. METRICS ROW (MOBILE FRIENDLY 2x2 GRID)
# ==========================================
m_col1, m_col2 = st.columns(2)

with m_col1:
    threat_count = len(st.session_state['threats'])
    threat_color = "#ff4b4b" if threat_count > 0 else "#00ff00"
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">⚠️ THREAT INDICATORS</div>
        <div class="metric-value" style="color: {threat_color};">{threat_count}</div>
        <div class="metric-label" style="font-size: 0.75rem;">{'ACTION REQUIRED' if threat_count > 0 else 'HOST CLEAR'}</div>
    </div>
    """, unsafe_allow_html=True)

with m_col2:
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-label">📊 TELEMETRY ELEMENTS</div>
        <div class="metric-value" style="color: #00ff00;">{st.session_state['total_scanned']}</div>
        <div class="metric-label" style="font-size: 0.75rem;">MEMORY & DISK MAPPED</div>
    </div>
    """, unsafe_allow_html=True)

m_col3, m_col4 = st.columns(2)

with m_col3:
    st.markdown("""
    <div class="metric-container">
        <div class="metric-label">🤖 AGENT PROFILE</div>
        <div class="metric-value" style="color: #00ff00;">ACTIVE</div>
        <div class="metric-label" style="font-size: 0.75rem;">SELF-HEALING READY</div>
    </div>
    """, unsafe_allow_html=True)

with m_col4:
    st.markdown("""
    <div class="metric-container">
        <div class="metric-label">🔍 THREAT INTEL</div>
        <div class="metric-value" style="color: #00ff00;">REAL-TIME</div>
        <div class="metric-label" style="font-size: 0.75rem;">HEURISTIC ANALYSIS</div>
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
        
        threats = []
        scanned = 0
        
        progress_bar.progress(10, text="📡 Analyzing network connections...")
        time.sleep(0.5)
        
        active_network_pids = set()
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'ESTABLISHED' and conn.pid:
                    active_network_pids.add(conn.pid)
        except:
            pass
        
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
                        for file in files[:100]:  
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
    filtered_threats = [t for t in st.session_state['threats'] if t['Severity'] in severity_filter]
    
    if filtered_threats:
        st.markdown("### 🎯 DETECTED THREATS")
        st.markdown(f"**Found {len(filtered_threats)} threat(s) matching filters**")
        st.markdown("---")
        
        for idx, threat in enumerate(filtered_threats):
            severity_class = f"custom-card-{threat['Severity'].lower()}"
            
            st.markdown(f"""
            <div class="{severity_class}">
                <div class="card-header-flex" style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h3 style="margin: 0; color: white;">{threat['Name']}</h3>
                        <p style="margin: 5px 0; color: #9ca3af;"><b>Type:</b> {threat['Type']}</p>
                        <p style="margin: 5px 0; font-size: 0.85rem; word-break: break-all;"><b>📍 Path:</b> {threat['Path']}</p>
                        <p style="margin: 5px 0; font-size: 0.85rem;"><b>🔍 Details:</b> {threat['Details']}</p>
                    </div>
                    <div class="card-badge-container" style="text-align: right; min-width: 100px;">
                        <span class="badge badge-{threat['Severity'].lower()}">{threat['Severity']}</span>
                        <p style="margin-top: 10px; font-size: 0.8rem; color: #9ca3af;">PID: {threat['PID']}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if threat['PID'] != "N/A":
                if st.button(f"⚠️ Neutralize Action (PID {threat['PID']})", key=f"neutralize_{idx}_{threat['PID']}", use_container_width=True):
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
            st.markdown("<br>", unsafe_allow_html=True)
        
        # Export functionality
        st.markdown("---")
        if st.button("📥 Generate Forensic Report (JSON)", use_container_width=True):
            report_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_scanned": st.session_state['total_scanned'],
                "threats_found": len(filtered_threats),
                "threats": filtered_threats
            }
            st.download_button(
                label="💾 Download JSON Manifest",
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

console_container = st.container()
with console_container:
    console_text = "\n".join(st.session_state['console_history'][-20:])
    st.text_area("", console_text, height=180, disabled=True, label_visibility="collapsed")

if st.button("🗑️ Clear Console Logs", use_container_width=True):
    st.session_state['console_history'] = ["[SYSTEM] Console cleared"]
    st.rerun()

# ==========================================
# 10. FOOTER
# ==========================================
st.markdown("---")
st.caption(f"🛡️ SpecterHunter v2.0 | Active Incident Response Engine | {time.strftime('%Y-%m-%d')}")
