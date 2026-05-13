import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from PIL import Image
from tqdm import tqdm
import os

"""
Phase 2: Forensic-Enhanced Cold Case Intelligence Platform - Vectorization Pipeline
This script processes the fused dataset, generates gritty image embeddings using CLIP,
and text embeddings using SBERT, storing them in a refreshed ChromaDB instance.
"""

def main():
    # ---------------------------------------------------------
    # 1. Initialization: Loading Models & DB
    # ---------------------------------------------------------
    print("--- Phase 2: Initializing Forensic Pipeline ---")
    
    print("Loading Text Model (SBERT: all-MiniLM-L6-v2)...")
    text_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Loading Image Model (CLIP: clip-ViT-B-32)...")
    image_model = SentenceTransformer('clip-ViT-B-32')

    print("Initializing ChromaDB Client (./cold_case_db)...")
    client = chromadb.PersistentClient(path="./cold_case_db")

    # Wipe existing collections to ensure a clean slate for gritty forensic data
    print("Wiping existing collections...")
    collections_to_delete = ["text_cases", "image_cases", "forensic_enhanced", "forensic_text"]
    for col_name in collections_to_delete:
        try:
            client.delete_collection(name=col_name)
            print(f"Deleted old collection: {col_name}")
        except Exception:
            # Skip if collection doesn't exist
            pass

    # Creating fresh forensic-enhanced collections
    print("Creating new forensic collections...")
    image_collection = client.create_collection(name="forensic_enhanced")
    text_collection = client.create_collection(name="forensic_text")

    # ---------------------------------------------------------
    # 2. Data Loading & Cleaning
    # ---------------------------------------------------------
    csv_path = 'fused_dataset_v2.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Please run mapping.py first.")
        return

    print(f"Loading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)

    # Clean data: Drop rows with missing critical information
    df = df.dropna(subset=['DR_NO', 'Premis', 'Crime_Scene_Image_Path'])
    final_count = len(df)
    
    # ---------------------------------------------------------
    # 3. Vectorization Loop: Text and Image Pipelines
    # ---------------------------------------------------------
    print(f"Starting Vectorization of {final_count} forensic cases...")
    
    for index, row in tqdm(df.iterrows(), total=final_count, desc="Processing Cases"):
        case_id = str(row['DR_NO'])
        premis_text = row['Premis']
        image_path = row['Crime_Scene_Image_Path']

        # --- Text Pipeline (SBERT) ---
        text_embedding = text_model.encode(premis_text).tolist()
        text_collection.add(
            embeddings=[text_embedding],
            documents=[premis_text],
            metadatas=[{"case_id": case_id, "text_summary": premis_text}],
            ids=[case_id]
        )

        # --- Image Pipeline (CLIP) ---
        try:
            if os.path.exists(image_path):
                img = Image.open(image_path)
                img_embedding = image_model.encode(img).tolist()
                
                image_collection.add(
                    embeddings=[img_embedding],
                    metadatas=[{"case_id": case_id, "image_path": image_path, "text_summary": premis_text}],
                    ids=[case_id]
                )
            else:
                print(f"\nWarning: Image not found for Case ID {case_id} at {image_path}")
        except Exception as e:
            print(f"\nError processing image for Case ID {case_id}: {e}")
            continue

        # Optimization: Track progress every 50 rows
        if (index + 1) % 50 == 0:
            print(f"\n>>> Progress Update: Completed {index + 1} rows. CLIP embedding generation is active.")

    # ---------------------------------------------------------
    # 4. Output: Success Confirmation
    # ---------------------------------------------------------
    print("\n" + "="*50)
    print("SUCCESS: Forensic Vectorization Pipeline Complete.")
    print(f"Text Collection ('forensic_text') Count: {text_collection.count()}")
    print(f"Image Collection ('forensic_enhanced') Count: {image_collection.count()}")
    print("="*50)

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
