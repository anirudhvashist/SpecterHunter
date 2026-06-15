# 🛡️ SpecterHunter

SpecterHunter is an autonomous incident response platform designed to detect, analyze, and neutralize volatile threats in real-time. Built for high-speed threat hunting, it allows security teams to identify process masquerading, hidden C2 beacons, and directory anomalies without the operational lag of traditional forensic tools.

## 🚀 Key Features
- **Deep Live Triage:** Audits RAM execution threads, network socket endpoints, and user-space pathways (`AppData`, `ProgramData`, `Temp`).
- **Autonomous Threat Neutralization:** Tactical kill-switch to immediately terminate malicious PIDs directly from the interface.
- **Forensic Manifests:** Automatically compiles telemetry data into certified, exportable JSON audit logs.
- **Low-Latency UI:** Built with a tactical, neon-cyber aesthetic for high-density data visualization in high-pressure scenarios.

## 🛠️ Tech Stack
- **Engine:** Python (`psutil`, `os`, `sys`)
- **Interface:** Streamlit (Custom CSS/HTML injection)
- **Environment:** Windows-Native (x64)

## 📦 Getting Started

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/anirudhvashist/SpecterHunter.git](https://github.com/anirudhvashist/SpecterHunter.git)
   cd SpecterHunter
