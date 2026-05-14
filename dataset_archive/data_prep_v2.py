import os
import pandas as pd
import random
from PIL import Image
from glob import glob
from tqdm import tqdm

"""
Data Preparation Script v2.1: Priority Real-Image Mapping
1. PNG Conversion: Converts all .png to .jpg with 'real_' prefix (strips alpha).
2. Priority Mapping: Ensures 'real_' images are used first for each category.
3. Verification: Summary of Real vs Unsplash distribution.
"""

def convert_png_to_jpg(train_dir):
    print("--- Step 1: Converting PNG Screenshots to Real JPGs ---")
    stats = {"converted": 0}
    
    # walk through all subdirectories
    for root, dirs, files in os.walk(train_dir):
        for file in files:
            if file.lower().endswith('.png'):
                png_path = os.path.join(root, file)
                # Create new filename: real_original.jpg
                filename_no_ext = os.path.splitext(file)[0]
                new_filename = f"real_{filename_no_ext}.jpg"
                jpg_path = os.path.join(root, new_filename)
                
                try:
                    with Image.open(png_path) as img:
                        # Convert to RGB (removes alpha channel from screenshots)
                        rgb_img = img.convert('RGB')
                        rgb_img.save(jpg_path, "JPEG", quality=95)
                    
                    # Delete original PNG
                    os.remove(png_path)
                    stats["converted"] += 1
                except Exception as e:
                    print(f"Error converting {png_path}: {e}")
                    
    print(f"Conversion Complete: {stats['converted']} PNGs converted to 'real_' JPGs.")

def create_priority_mapping(train_dir, csv_path):
    print("\n--- Step 2: Creating Priority Hybrid Mapping ---")
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)
    
    # 1. Map subfolders by category name
    subfolders = {f.name.lower(): f.path for f in os.scandir(train_dir) if f.is_dir()}
    
    # 2. Group available images in each folder
    folder_images = {}
    for cat_name, path in subfolders.items():
        all_jpgs = glob(os.path.join(path, "*.jpg"))
        real = [img for img in all_jpgs if os.path.basename(img).startswith("real_")]
        unsplash = [img for img in all_jpgs if not os.path.basename(img).startswith("real_")]
        
        # Shuffle for variety
        random.shuffle(real)
        random.shuffle(unsplash)
        
        folder_images[cat_name] = {
            "real": real,
            "unsplash": unsplash,
            "real_idx": 0
        }

    # 3. Mapping Logic
    mapped_paths = []
    image_types = []
    
    # Identify which folder matches which Premis
    # Pre-calculate to avoid nested loops
    def get_best_folder(premis_text):
        premis_text = str(premis_text).lower()
        for cat_name in folder_images.keys():
            if cat_name in premis_text:
                return cat_name
        return random.choice(list(folder_images.keys()))

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Assigning Images"):
        target_folder = get_best_folder(row['Premis'])
        img_data = folder_images[target_folder]
        
        # PRIORITY RULE: Use 'real' images first
        if img_data["real_idx"] < len(img_data["real"]):
            img_path = img_data["real"][img_data["real_idx"]]
            img_data["real_idx"] += 1
            source_type = "Real"
        else:
            # Fallback to random unsplash
            if img_data["unsplash"]:
                img_path = random.choice(img_data["unsplash"])
                source_type = "Unsplash"
            else:
                # Extreme fallback if folder is empty (shouldn't happen with Unsplash base)
                img_path = "N/A"
                source_type = "None"
        
        mapped_paths.append(img_path)
        image_types.append(source_type)

    df['Crime_Scene_Image_Path'] = mapped_paths
    df['Image_Source_Type'] = image_types
    
    # Save the final dataset
    output_csv = 'fused_dataset_v3_final.csv'
    df.to_csv(output_csv, index=False)
    
    # --- Step 3: Verification Summary ---
    print("\n" + "="*50)
    print("MAPPING VERIFICATION SUMMARY")
    print(f"Total Rows Processed: {len(df)}")
    print(df['Image_Source_Type'].value_counts())
    print(f"Results saved to: {output_csv}")
    print("="*50)

if __name__ == "__main__":
    TRAIN_DIR = "train"
    # Using the latest fused dataset as base
    INPUT_CSV = "fused_dataset_v2.csv" 
    
    if os.path.exists(TRAIN_DIR):
        convert_png_to_jpg(TRAIN_DIR)
        create_priority_mapping(TRAIN_DIR, INPUT_CSV)
    else:
        print(f"Error: '{TRAIN_DIR}' directory not found.")
