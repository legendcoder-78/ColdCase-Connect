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
├── build_database.py    # Phase 1: Vectorization Pipeline
├── mapping.py           # Maps crime premises to image categories
├── data_prep.py         # Downloads scene images from Unsplash
├── index.html           # Professional Dashboard structure
├── style.css            # Tactical UI/UX and Animations
├── script.js            # Frontend Logic and API Bridge
├── cold_case_db/        # Persistent ChromaDB Vector Store (auto-generated)
├── train/               # Historical Crime Scene Image Archive (from train.zip)
├── fused_dataset_v2.csv # Fused dataset with image paths (auto-generated)
├── dataset_800.csv      # Core structured case data
└── .env                 # Secure API Configuration (you create this)
```

---

## ⚙️ Setup & Installation

Follow these steps in order to get the project running on your local machine.

### Prerequisites

- **Python 3.9+** installed ([download here](https://www.python.org/downloads/))
- **Git** installed
- A **Google Gemini API Key** (get one free at [Google AI Studio](https://aistudio.google.com/apikey))

### Step 1 — Clone the Repository

```bash
git clone <your-repo-url>
cd ColdCase
```

### Step 2 — Unzip the Training Images

The repository includes a `train.zip` file containing all the historical crime scene images used by the AI models. You **must** unzip this before running the project.

```bash
# macOS / Linux
unzip train.zip

# Windows (PowerShell)
Expand-Archive -Path train.zip -DestinationPath .
```

After unzipping, you should see a `train/` folder with sub-directories like `alley/`, `street/`, `parking_lot/`, etc., each containing `.jpg` images.

```text
train/
├── alley/
├── apartment_building/
├── bedroom/
├── gas_station/
├── motel/
├── park/
├── parking_lot/
├── restaurant/
└── street/
```

### Step 3 — Create a Virtual Environment

```bash
# Create the virtual environment
python3 -m venv venv

# Activate it
# macOS / Linux:
source venv/bin/activate

# Windows (PowerShell):
.\venv\Scripts\Activate
```

### Step 4 — Install Dependencies

```bash
pip install fastapi uvicorn chromadb sentence-transformers pillow google-generativeai python-dotenv pandas tqdm
```

### Step 5 — Set Up the `.env` File

Create a file named `.env` in the **project root directory** (same level as `main.py`):

```bash
touch .env    # macOS / Linux
```

Open the `.env` file and add your **Google Gemini API Key**:

```env
GEMINI_API_KEY="your_google_gemini_api_key_here"
```

> **How to get your API key:**
> 1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
> 2. Sign in with your Google account
> 3. Click **"Create API Key"**
> 4. Copy the key and paste it into the `.env` file

⚠️ **Important:** Never commit your `.env` file to Git. It is already listed in `.gitignore`, so it will be excluded automatically.

### Step 6 — Build the Vector Database

This is a **one-time setup** step. It processes the CSV dataset and images, generates vector embeddings, and stores them in ChromaDB. This may take a few minutes depending on your machine.

```bash
python3 build_database.py
```

You should see a progress bar and a success message like:

```
SUCCESS: Forensic Vectorization Pipeline Complete.
Text Collection ('forensic_text') Count: 800
Image Collection ('forensic_enhanced') Count: 800
```

> **Note:** The `fused_dataset_v2.csv` and `cold_case_db/` folder are generated automatically by this step. If you need to rebuild the database from scratch, delete the `cold_case_db/` folder and re-run.

### Step 7 — Start the Backend Server

```bash
python3 -m uvicorn main:app --reload
```

The API will start at **`http://127.0.0.1:8000`**. You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

You can verify it's working by visiting `http://127.0.0.1:8000` in your browser — you should see:
```json
{"message": "ColdSync AI is active. Multi-image fusion enabled."}
```

### Step 8 — Launch the Frontend

Open `index.html` using a local web server. The easiest options:

**Option A — VS Code Live Server (Recommended):**
1. Install the [Live Server extension](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) in VS Code
2. Right-click `index.html` → **"Open with Live Server"**
3. Dashboard opens at `http://127.0.0.1:5500`

**Option B — Python HTTP Server:**
```bash
# In a new terminal (keep the backend running in the first one)
python3 -m http.server 5500
```
Then open `http://127.0.0.1:5500` in your browser.

---

## 🧪 Investigative Workflow

Once both the backend and frontend are running:

1. **Upload Evidence:** Drag and drop one or multiple crime scene photos into the "Evidence Upload" zone.
2. **Enter Narrative:** Type the M.O. details (e.g., *"Forced entry via rear window, target: electronics, signature: graffiti left on wall"*).
3. **Run Analysis:** Click **Run Investigative Analysis**.
4. **Review Results:** Analyze the **AI Forensic Synthesis** and explore the top 5 matches. Pay close attention to **Red Pulsing Cards**, which indicate high-divergence anomalies.

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Make sure your virtual environment is activated (`source venv/bin/activate`) and all dependencies are installed (Step 4) |
| `GEMINI_API_KEY not found` | Ensure the `.env` file exists in the project root with the correct key |
| Archived match images not loading | Make sure you unzipped `train.zip` (Step 2) and the `train/` folder is in the project root |
| CORS errors in browser console | Ensure the frontend is running on port `5500` (the backend allows this origin) |
| `chromadb` collection errors | Delete the `cold_case_db/` folder and re-run `python3 build_database.py` |

---

## 📜 Pipeline Overview (For Contributors)

The data flows through these scripts in order:

```
data_prep.py → mapping.py → build_database.py → main.py (serves the API)
```

| Script | Purpose |
|---|---|
| `data_prep.py` | Downloads crime scene images from Unsplash into `train/` (already done — images are in `train.zip`) |
| `mapping.py` | Maps each crime record's "Premis" field to an image category and produces `fused_dataset_v2.csv` |
| `build_database.py` | Reads the fused CSV, generates SBERT + CLIP embeddings, and stores them in ChromaDB |
| `main.py` | FastAPI server — handles queries, runs multi-modal fusion search, and calls Gemini for forensic synthesis |

> **For teammates:** You only need to run **Step 6** (`build_database.py`) — the images and CSV are already prepared. `data_prep.py` and `mapping.py` were used during initial dataset creation and do **not** need to be re-run.

---

**Developed for the 2026 Forensic Intelligence Hackathon.**
*Note: This platform is a prototype designed for investigative research.*
# ColdCase-Connect
An AI-powered multimodal forensic intelligence system that semantically matches crime cases across text and images to uncover hidden patterns, serial links, and staged crimes.
