import os
import pandas as pd
import glob
from tqdm import tqdm

"""
Data Preparation Script v3.0: Maximum Coverage Strategy
1. Ensures EVERY .jpg in the 'train/' folder is represented in the database.
2. If images > text rows in a category, text rows are cycled.
3. If text rows > images in a category, images are cycled.
4. Resulting dataset 'fused_dataset_v3_final.csv' will contain at least one row per image.
"""

def get_category_from_premis(premis, available_folders):
    premis = str(premis).lower()
    for folder in available_folders:
        if folder in premis:
            return folder
    return "other"  # Fallback

def main():
    print("--- Phase 3: Maximum Coverage Mapping Engine ---")
    
    train_dir = "train"
    csv_path = "fused_dataset_v2.csv" # Base dataset
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
    
    if not os.path.exists(train_dir):
        print(f"Error: {train_dir} directory not found.")
        return

    # 1. Load Original Dataset
    df_original = pd.read_csv(csv_path)
    
    # 2. Identify Available Image Folders
    # Filter for directories and normalize names to lowercase
    available_folders = [f.name.lower() for f in os.scandir(train_dir) if f.is_dir()]
    print(f"Found {len(available_folders)} spatial categories in '{train_dir}/'.")

    # 3. Categorize CSV Rows
    # We create a mapping of Folder Name -> List of Dataframes (rows)
    df_original['mapped_category'] = df_original['Premis'].apply(lambda x: get_category_from_premis(x, available_folders))
    
    # 4. Process Categories and Cycle
    final_rows = []
    category_summary = {}

    for category in tqdm(available_folders, desc="Processing Categories"):
        # Get all images for this category
        cat_path = os.path.join(train_dir, category)
        images = glob.glob(os.path.join(cat_path, "*.jpg"))
        
        # Get all text rows assigned to this category
        cat_df = df_original[df_original['mapped_category'] == category].copy()
        
        # Fallback: If no rows mapped to this folder, use 'other' or a random slice
        if cat_df.empty:
            cat_df = df_original.sample(n=min(10, len(df_original)))
            
        text_rows = cat_df.to_dict('records')
        
        num_images = len(images)
        num_text = len(text_rows)
        
        # Determine the target count (The larger of the two sets)
        target_count = max(num_images, num_text)
        
        # Core Cycling Logic
        # We zip the lists, using cycling to ensure coverage
        for i in range(target_count):
            img_path = images[i % num_images]
            text_data = text_rows[i % num_text].copy()
            
            # Update the image path and cleanup
            text_data['Crime_Scene_Image_Path'] = img_path
            # Optional: Add flag to track if this was a primary or cycled row
            text_data['mapping_coverage_id'] = i 
            
            final_rows.append(text_data)
        
        category_summary[category] = target_count

    # 5. Compile and Save
    df_final = pd.DataFrame(final_rows)
    
    # Clean up internal columns
    if 'mapped_category' in df_final.columns:
        df_final = df_final.drop(columns=['mapped_category'])

    output_path = "fused_dataset_v3_final.csv"
    df_final.to_csv(output_path, index=False)

    # 6. Verification Summary
    print("\n" + "="*50)
    print("MAXIMUM COVERAGE VERIFICATION")
    print(f"Original Row Count: {len(df_original)}")
    print(f"Final Row Count:    {len(df_final)}")
    print(f"Unique Images Used: {df_final['Crime_Scene_Image_Path'].nunique()}")
    print("-" * 50)
    print("Rows per Category:")
    for cat, count in category_summary.items():
        print(f" - {cat.upper():<15}: {count}")
    print("="*50)
    print(f"Database Refresh: Ready. Use '{output_path}' with build_database.py")

if __name__ == "__main__":
    main()
