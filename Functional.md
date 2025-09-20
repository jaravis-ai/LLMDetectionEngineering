# 🚀 Threat Intelligence to Detection Pipeline with OTX, MITRE ATT&CK, and LLMs

## 📌 Overview

This document describes a **functional working design** for integrating  
**Open Threat Exchange (OTX)** threat intelligence with **MITRE ATT&CK mapping**  
using **LLMs (Large Language Models)** to automate **Detection Engineering** workflows.  

The output of this pipeline includes **mapped techniques** and **auto-generated detection rules**,  
which can be version-controlled and shared via GitHub.

---

## 🎯 Goals

1. Fetch threat intelligence data from **OTX API** (pulses, IOCs, metadata).  
2. Use **LLM** to extract adversary behaviors from reports.  
3. Map extracted behaviors to **MITRE ATT&CK techniques**.  
4. Automatically generate **detection rules** (e.g., Sigma, EDR, IDS).  
5. Provide coverage insights & maintain continuous improvement.

---

## 🔑 OTX (Open Threat Exchange) API – Data You Can Retrieve

OTX is a **community-driven threat intelligence platform**. The API provides access to:

### 1. Pulses (Threat Reports)
- **Metadata**: Title, description, author, creation date, references, tags.  
- **Context**: Linked campaigns, malware families, attack categories.  
- **Community Info**: Followers, contributors, reliability.  

### 2. Indicators of Compromise (IOCs)
- Types: IPs, domains, URLs, file hashes (MD5/SHA1/SHA256), hostnames, CVEs.  
- Metadata: First seen, last seen, indicator type, related pulses.  
- Reputation & trust score.  

### 3. Submissions
- Upload files or URLs for sandbox/static analysis.  
- Retrieve results for malware behavior.  

### 4. Exports
- Bulk data in **JSON, STIX, CSV**.  
- Subscription-based feeds (DirectConnect).  

---

## ⚔️ Why Map to MITRE ATT&CK?

MITRE ATT&CK is a globally recognized **framework of adversary tactics & techniques**.

**Benefits of Mapping:**
- 📖 **Standardized language**: Speak the same vocabulary across teams & tools.  
- 🛡️ **Detection coverage analysis**: Identify **gaps** in your detection rules.  
- 🎯 **Prioritization**: Focus on high-risk techniques relevant to your org.  
- 🔁 **Reusability**: Share rules annotated with ATT&CK IDs across environments.  
- 🧑‍💻 **Threat hunting & incident response**: Pivot based on ATT&CK behaviors.  
- 📊 **Metrics & dashboards**: Visualize coverage across tactics/techniques.  

---

## 🔄 Functional Workflow

### Step 1. Data Ingestion
- **Source**: OTX API → Fetch pulses, indicators, metadata.  
- **Format**: JSON (parsed into structured schema).  

### Step 2. Behavior Extraction
- **Input**: Pulse descriptions, references, malware analysis notes.  
- **Process**: Use **LLM (or NLP)** to extract adversary actions.  
- **Output**: List of observed behaviors.  

Example:

### Step 3. Mapping to ATT&CK
- Match extracted behaviors to ATT&CK **techniques & sub-techniques**.  
- Use **LLM with ATT&CK technique catalog** for alignment.  
- Output structured JSON mapping:  

```json
{
  "techniques": [
    { "id": "T1566.001", "name": "Spearphishing Attachment" },
    { "id": "T1053.005", "name": "Scheduled Task" },
    { "id": "T1021.002", "name": "SMB/Windows Admin Shares" }
  ]
}

### Step 4. Rule Generation
- Use **mapped techniques + IOCs** to auto-generate detection rules.


## **Supported Rule Formats:**
- **Sigma** (SIEM-agnostic)  
- **YARA / Suricata / Snort** (network-focused)  
- **EDR rules** (endpoint telemetry)  

---

### Step 5. Validation & Testing
- Test generated rules in:
  - **Sandbox environments**  
  - **SIEM platforms**  
  - **EDR telemetry**  
- Iterate the rules to minimize:
  - **False Positives (FPs)**  
  - **False Negatives (FNs)**  

---

### Step 6. Monitoring & Coverage Tracking
Maintain a **dashboard of MITRE ATT&CK coverage** to ensure visibility and completeness.

## **Track the following:**
- ✅ Techniques **observed** in OTX pulses  
- 🛡️ Techniques **covered** by generated rules  
- ⚠️ **Coverage gaps** (techniques not yet addressed)  
