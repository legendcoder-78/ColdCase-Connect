import os
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sentence_transformers import SentenceTransformer
import chromadb
from PIL import Image
import io
import math
from typing import List, Dict, Any

from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file (e.g., GEMINI_API_KEY)
load_dotenv()

"""
Phase 4: Multi-Modal Cold Case Intelligence Platform - LLM Enhanced Investigative Engine
UPDATE: Added CORS Middleware and Multi-Image "Best Evidence" Fusion.
"""

# Configure Google Generative AI with API Key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Initialize FastAPI App
app = FastAPI(title="ColdSync AI - Investigative Engine (Pro Dashboard Backend)")

# --- Resolve CORS Hurdle ---
# This allows our local frontend (e.g., Port 5500) to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://[::]:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static File Serving ---
# This allows the browser to access images in the 'train' directory
# via URLs like http://127.0.0.1:8000/train/...
app.mount("/train", StaticFiles(directory="train"), name="train")

# ---------------------------------------------------------
# 1. Initialization: Models & Database Connection
# ---------------------------------------------------------

print("--- Loading Intelligence Models ---")
# Text Model: Encodes investigative summaries
text_model = SentenceTransformer('all-MiniLM-L6-v2')
# Image Model: Encodes uploaded crime scene photos using CLIP
image_model = SentenceTransformer('clip-ViT-B-32')

print("--- Connecting to Persistent Vector Store ---")
client = chromadb.PersistentClient(path="./cold_case_db")
text_collection = client.get_or_create_collection(name="forensic_text")
image_collection = client.get_or_create_collection(name="forensic_enhanced")

# ---------------------------------------------------------
# 2. Helper Functions
# ---------------------------------------------------------

def distance_to_score(distance: float) -> float:
    """
    Converts ChromaDB distance (Euclidean/Cosine) to a 0-100 percentage score.
    Formula: 100 - (distance * 30), clamped between 0 and 100.
    """
    score = 100.0 - (distance * 30)
    return round(max(0.0, min(100.0, score)), 2)

# ---------------------------------------------------------
# 3. API Endpoints
# ---------------------------------------------------------

@app.post("/analyze")
async def analyze_case(
    text_summary: str = Form(...),
    scene_images: List[UploadFile] = File(...)
):
    """
    Advanced multi-modal endpoint supporting multi-image evidence fusion.
    Uses 'Best Evidence' Max Pooling to identify patterns across multiple visual inputs.
    """
    try:
        # --- Vectorization of Input ---
        # 1. Process Text Input
        text_vector = text_model.encode(text_summary).tolist()

        # 2. Process Multiple Image Inputs
        query_image_embeddings = []
        for scene_image in scene_images:
            image_bytes = await scene_image.read()
            pil_image = Image.open(io.BytesIO(image_bytes))
            img_vector = image_model.encode(pil_image).tolist()
            query_image_embeddings.append(img_vector)

        # --- Querying the Collections ---
        # Text Query: Returns top 60 textual matches
        text_results = text_collection.query(
            query_embeddings=[text_vector],
            n_results=60,
            include=["documents", "metadatas", "distances"]
        )

        # Multi-Image Query: Returns lists of results (one per uploaded image)
        image_results = image_collection.query(
            query_embeddings=query_image_embeddings,
            n_results=60,
            include=["metadatas", "distances"]
        )

        # --- Debugging: Log Raw Distances ---
        print("\n--- DEBUG: RAW IMAGE MATCH DISTANCES ---")
        for idx, dist_list in enumerate(image_results['distances']):
            print(f"Image {idx+1} Top 5 Distances: {dist_list[:5]}")

        # ---------------------------------------------------------
        # 4. Max Pooling (Best Evidence Fusion)
        # ---------------------------------------------------------
        # We consolidate matches from all uploaded images, keeping only the 
        # HIGHEST visual score for any given case ID.
        best_visual_matches = {}
        
        # image_results['ids'] is a list of lists: [[results_for_img1], [results_for_img2], ...]
        for img_idx in range(len(image_results['ids'])):
            ids = image_results['ids'][img_idx]
            distances = image_results['distances'][img_idx]
            metadatas = image_results['metadatas'][img_idx]
            
            for i in range(len(ids)):
                case_id = ids[i]
                dist = distances[i]
                score = distance_to_score(dist)
                path = metadatas[i].get("image_path", "")
                
                # If case seen before, take the MAX score (Best Evidence)
                if case_id not in best_visual_matches or score > best_visual_matches[case_id]["visual_score"]:
                    best_visual_matches[case_id] = {
                        "visual_score": score,
                        "image_path": path
                    }

        # --- Scoring & Intersect Logic ---
        merged_matches = {}

        # Process Text Matches (Primary candidates)
        for i in range(len(text_results['ids'][0])):
            case_id = text_results['ids'][0][i]
            dist = text_results['distances'][0][i]
            metadata = text_results['metadatas'][0][i]
            
            # Initialize with textual data
            merged_matches[case_id] = {
                "case_id": case_id,
                "text_score": distance_to_score(dist),
                "visual_score": 0.0,
                "text_summary": metadata.get("text_summary", ""),
                "image_path": ""
            }
            
            # Intersect with Best Evidence from visual queries
            if case_id in best_visual_matches:
                merged_matches[case_id]["visual_score"] = best_visual_matches[case_id]["visual_score"]
                # Use the path from the visual match if available
                merged_matches[case_id]["image_path"] = best_visual_matches[case_id]["image_path"]

        # Add visual-only matches that weren't in the top 60 text results
        for case_id, visual_data in best_visual_matches.items():
            if case_id not in merged_matches:
                merged_matches[case_id] = {
                    "case_id": case_id,
                    "text_score": 0.0,
                    "visual_score": visual_data["visual_score"],
                    "text_summary": "N/A (Visual Match Only)",
                    "image_path": visual_data["image_path"]
                }

        # --- Final Calculation & Filtering ---
        raw_results = []
        for case_id, data in merged_matches.items():
            combined_score = (data["text_score"] + data["visual_score"]) / 2
            divergence_delta = abs(data["visual_score"] - data["text_score"])
            
            # --- Smarter Divergence Logic ---
            # 1. High-Score Exception: If combined > 70%, no flag (high evidence consistency)
            # 2. Minimum Text Floor: Only trigger if text_score < 30% while visual is high
            # 3. Threshold Adjustment: Increase delta sensitivity from 40 to 50
            divergence_flag = False
            if combined_score <= 70.0:
                if divergence_delta > 50.0 and data["text_score"] < 30.0:
                    divergence_flag = True

            # Confidence Threshold Check (15%)
            if combined_score < 15.0:
                continue

            # --- Robust Path Sanitization ---
            # Stored paths like './train/cat/img.jpg' or 'train/cat/img.jpg'
            # need to be served via /train/ mount.
            raw_path = data["image_path"]
            web_image_path = ""
            if raw_path:
                # Remove leading dots/slashes and isolate the 'train/' portion
                sanitized = raw_path.replace("\\", "/").lstrip("./")
                if "train/" in sanitized:
                    web_image_path = sanitized[sanitized.find("train/"):]
                else:
                    web_image_path = f"train/{sanitized}"

            raw_results.append({
                "case_id": case_id,
                "combined_score": round(combined_score, 2),
                "text_score": data["text_score"],
                "visual_score": data["visual_score"],
                "divergence_delta": round(divergence_delta, 2),
                "divergence_flag": divergence_flag,
                "text_summary": data["text_summary"],
                "image_path": web_image_path
            })

        # Sort by combined score descending
        raw_results.sort(key=lambda x: x["combined_score"], reverse=True)

        # --- De-duplication Filter ---
        final_unique_results = []
        seen_combinations = set()

        for match in raw_results:
            signature = f"{match['text_summary']}_{match['image_path']}"
            if signature not in seen_combinations:
                seen_combinations.add(signature)
                final_unique_results.append(match)
            if len(final_unique_results) == 5:
                break

        # --- AI Forensic Synthesis (Gemini Integration) ---
        generated_text = "Forensic synthesis unavailable. Please check API connection."
        if final_unique_results:
            top_match = final_unique_results[0]
            historical_summary = top_match["text_summary"]
            
            prompt = (
                f"Act as a forensic analyst. Read these two case summaries.\n\n"
                f"Case 1 (New Case): {text_summary}\n"
                f"Case 2 (Historical Match): {historical_summary}\n\n"
                f"In exactly 3 short bullet points, explain the shared Modus Operandi (M.O.) "
                f"and forensic similarities between them."
            )

            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content(prompt)
                if response and response.text:
                    generated_text = response.text.strip()
            except Exception as ai_error:
                print(f"Gemini API Error: {ai_error}")

        return {
            "status": "success",
            "forensic_synthesis": generated_text,
            "top_matches": final_unique_results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis engine error: {str(e)}")

@app.get("/")
async def root():
    return {"message": "ColdSync AI is active. Multi-image fusion enabled."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
