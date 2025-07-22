# 📡 Network Modeling & Traffic Simulation Tool

A simple yet powerful Python tool for **network modeling, traffic flow simulation, link utilization analysis**, and **worst-case failure (WCF)** visualization. This tool mimics the basic functionality of commercial-grade network planners like Juniper's NorthStar Planner.

---

## 🚀 Features

- 📊 **Load network topology** from CSV.
- 📈 **Load traffic demands** from CSV.
- 🛣️ **Route traffic** using OSPF (Dijkstra’s Algorithm).
- 🔍 **Track link utilization** and detect overloaded paths.
- 💥 **Simulate single-link failures** and observe impact.
- 🎨 **Color-coded visualizations**:
   - 🟢 Safe links (≤80% load).
   - 🟠 Critical links (>80% load).
   - 🔴 Overloaded links (>100% load).
- 🗂️ **Generate reports** as CSV files.
- 🖼️ **Visual output** with graphs (normal operation + failures).

---

## 📂 Folder Structure

```plaintext
network-modeling-tool/
├── network_model.py            # Main simulation code
├── network.csv                 # Sample network topology CSV
├── traffic.csv                 # Sample traffic demands CSV
├── README.md                   # Project overview
├── requirements.txt            # Python package dependencies
├── outputs/                    # Optional folder for generated reports/images
└── LICENSE                     # Optional license file (MIT recommended)


