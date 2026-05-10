# 🔍 ColdSync AI: Multi-Modal Cold Case Intelligence Platform

**ColdSync AI** is a professional-grade forensic tool designed to assist investigators in cross-referencing new crime scene evidence against vast historical cold case archives. By fusing **Deep Computer Vision** with **Semantic Language Models** and **Generative AI**, the platform identifies hidden patterns that standard database searches often miss.

---

## 🌌 Project Vision: "The Midnight Tactical" Command Center
The platform features a custom-built, high-fidelity dashboard designed for low-light forensic environments. It moves beyond standard web aesthetics to provide a "hardware-integrated" feel with real-time investigative feedback.

### 🚀 Key Capabilities
- **Multi-Modal Vector Search:** Simultaneously cross-references textual M.O. (Modus Operandi) narratives and visual crime scene evidence.
- **"Best Evidence" Fusion:** Supports multiple image uploads, automatically selecting the highest visual match (Max Pooling) to represent the case.
- **AI Forensic Synthesis:** Uses **Gemini 2.5 Flash** to analyze patterns between current investigations and top historical matches, providing a bulleted forensic report.
- **Divergence Detection:** Automatically flags cases where visual evidence contradicts the textual narrative—a critical signal for **staged crime scenes** or copycat behavior.
- **Pixel-Scanning UI:** Productive friction via a custom "pixel-scanner" animation that visualizes the AI's deep analysis of evidence.

---

## 🛠 The Tech Stack

### **Backend (The Investigative Engine)**
- **FastAPI:** High-performance asynchronous API framework.
- **ChromaDB:** A persistent vector database for low-latency similarity search.
- **Sentence-Transformers (SBERT):** `all-MiniLM-L6-v2` for encoding textual investigative narratives.
- **OpenAI CLIP (Vision Transformer):** `clip-ViT-B-32` for multi-modal image vectorization.
- **Google Generative AI:** Gemini 2.5 Flash for advanced forensic reasoning and synthesis.

### **Frontend (The Command Center)**
- **Custom HTML5/JS/CSS3:** Built from scratch for a high-performance, immersive experience.
- **Tailwind CSS:** For the "Midnight Tactical" (`#0B0E14`) aesthetic and responsive layouts.
- **Lucide Icons:** Technical, thin-stroke iconography.
- **CORS-Compliant Fetch:** Real-time asynchronous communication with the FastAPI engine.

---

## 📂 Project Architecture

```text
ColdCase/
├── main.py              # FastAPI Backend (Scoring, Fusion, LLM)
├── index.html           # Professional Dashboard structure
├── style.css            # Tactical UI/UX and Animations
├── script.js            # Frontend Logic and API Bridge
├── build_database.py    # Phase 1: Vectorization Pipeline
├── cold_case_db/        # Persistent ChromaDB Vector Store
├── train/               # Historical Crime Scene Image Archive
├── fused_dataset_800.csv # Core structured case data
└── .env                 # Secure API Configuration
```

---

## ⚙️ Setup & Installation

### 1. Environment Configuration
Create a `.env` file in the root directory:
```bash
GEMINI_API_KEY=your_google_gemini_api_key
```

### 2. Backend Initialization
Install dependencies and start the investigative engine:
```bash
# Activate your environment
source venv/bin/activate

# Install requirements
pip install fastapi uvicorn chromadb sentence-transformers pillow google-generativeai python-dotenv

# Run the API
python3 -m uvicorn main:app --reload
```

### 3. Frontend Activation
Open `index.html` using a local web server (e.g., VS Code "Live Server" or `python -m http.server 5500`). Access the dashboard at `http://127.0.0.1:5500`.

---

## 🧪 Investigative Workflow
1. **Data Ingest:** Drag and drop one or multiple crime scene photos into the "Evidence Upload" zone.
2. **Narrative Entry:** Type the M.O. details (e.g., *"Forced entry via rear window, target: electronics, signature: graffiti left on wall"*).
3. **Execution:** Click **Run Investigative Analysis**.
4. **Review:** Analyze the **AI Forensic Synthesis** and explore the top 5 matches. Pay close attention to **Red Pulsing Cards**, which indicate high-divergence anomalies.

---

**Developed for the 2026 Forensic Intelligence Hackathon.** 
*Note: This platform is a prototype designed for investigative research.*
