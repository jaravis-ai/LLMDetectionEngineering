# 🔬 LLM in Detection Engineering 
# LLM in Detection Engineering – Jarvis Agent

## 🔎 Short Working Brief

**Jarvis Agent** is an AI-powered system designed to revolutionize **Detection Engineering** by automating the generation of high-quality detection rules across multiple cybersecurity platforms.

- **Ingestion**: Pulls and normalizes threat intelligence reports directly from **AlienVault OTX**.
- **Mapping**: Correlates ingested threat intelligence with **MITRE ATT&CK** techniques, tactics, and procedures (TTPs).
- **Rule Generation**: Automatically generates detection rules tailored for diverse cyber defense platforms (e.g., SIEMs, EDRs, IDS/IPS).
- **Repository Management**: Stores and organizes generated rules in a structured repository for rapid deployment and version control.

The goal is to **reduce manual detection engineering efforts by 80%**, enabling faster, more accurate, and consistent threat detection across enterprise security ecosystems.

---

## ⚙️ Setup Instructions

Follow the steps below to set up **Jarvis Agent** locally:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/jaravis-ai/LLMDetectionEngineering.git
   cd LLMDetectionEngineering

2. **Install Poetry (if not already installed)**
pip install poetry

3. **Install Dependencies from pyproject.toml**
poetry install

This will:
- Create a virtual environment
- Install all dependencies specified in `pyproject.toml`

4. **Set Up Environment Variables**
cp .env.example .env





