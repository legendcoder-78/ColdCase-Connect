import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from PIL import Image
from tqdm import tqdm
import os

"""
Phase 1: Multi-Modal Cold Case Intelligence Platform - Vectorization Pipeline
This script processes structured case data from a CSV, generates embeddings for both
textual descriptions and crime scene images, and stores them in a local ChromaDB instance.
"""

def main():
    # ---------------------------------------------------------
    # 1. Initialization: Loading Models & DB
    # ---------------------------------------------------------
    print("--- Phase 1: Initializing Pipeline ---")
    
    print("Loading Text Model (all-MiniLM-L6-v2)...")
    # used for processing 'Premis' text descriptions
    text_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Loading Image Model (clip-ViT-B-32)...")
    # CLIP model used for generating multi-modal image embeddings
    image_model = SentenceTransformer('clip-ViT-B-32')

    print("Initializing ChromaDB Client (./cold_case_db)...")
    # Persistent client ensures the database is saved to disk
    client = chromadb.PersistentClient(path="./cold_case_db")

    # Creating separate collections for modular retrieval
    print("Creating collections...")
    text_collection = client.get_or_create_collection(name="text_cases")
    image_collection = client.get_or_create_collection(name="image_cases")

    # ---------------------------------------------------------
    # 2. Data Loading & Cleaning
    # ---------------------------------------------------------
    csv_path = 'fused_dataset_800.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    print(f"Loading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)

    # Clean data: Drop rows with missing critical information
    initial_count = len(df)
    df = df.dropna(subset=['DR_NO', 'Premis', 'Crime_Scene_Image_Path'])
    final_count = len(df)
    
    if initial_count != final_count:
        print(f"Dropped {initial_count - final_count} rows with missing values.")

    # ---------------------------------------------------------
    # 3. Vectorization Loop: Text and Image Pipelines
    # ---------------------------------------------------------
    print(f"Starting Vectorization of {final_count} cases...")
    
    # Iterate through each row to populate the vector database
    for index, row in tqdm(df.iterrows(), total=final_count, desc="Processing Cases"):
        case_id = str(row['DR_NO'])
        premis_text = row['Premis']
        image_path = row['Crime_Scene_Image_Path']

        # --- Text Pipeline ---
        # Generate embedding for the crime scene location description
        text_embedding = text_model.encode(premis_text).tolist()
        
        # Add to text collection with metadata for traceability
        text_collection.add(
            embeddings=[text_embedding],
            documents=[premis_text],
            metadatas=[{"case_id": case_id, "text_summary": premis_text}],
            ids=[case_id]
        )

        # --- Image Pipeline ---
        try:
            # Check if image exists before processing
            if os.path.exists(image_path):
                # Load image using PIL
                img = Image.open(image_path)
                
                # Generate embedding using the CLIP model
                img_embedding = image_model.encode(img).tolist()
                
                # Add to image collection
                image_collection.add(
                    embeddings=[img_embedding],
                    metadatas=[{"case_id": case_id, "image_path": image_path}],
                    ids=[case_id]
                )
            else:
                print(f"\nWarning: Image not found for Case ID {case_id} at {image_path}")
        except Exception as e:
            # Silent fail or brief warning as per requirements to keep the loop running
            print(f"\nError processing image for Case ID {case_id}: {e}")
            continue

    # ---------------------------------------------------------
    # 4. Output: Success Confirmation
    # ---------------------------------------------------------
    print("\n" + "="*50)
    print("SUCCESS: Vectorization Pipeline Phase 1 Complete.")
    print(f"Database successfully saved to: {os.path.abspath('./cold_case_db')}")
    print(f"Text Collection Count: {text_collection.count()}")
    print(f"Image Collection Count: {image_collection.count()}")
    print("="*50)

if __name__ == "__main__":
    main()
