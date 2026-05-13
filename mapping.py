import pandas as pd
import os
import random

# 1. Load your existing 800-row CSV file
df = pd.read_csv('dataset_800.csv')

# 2. Define the path to where your forensic images are stored
PLACES_DIR = './train/' 

# 3. Create the Mapping Dictionary based on the unique values in your CSV
category_map = {
    # Streets & Alleys
    'STREET': 'street',
    'SIDEWALK': 'street',
    'DRIVEWAY': 'street',
    'ALLEY': 'alley',
    'UNDERPASS/BRIDGE*': 'street',
    'TRAIN TRACKS': 'street',
    
    # Residential
    'SINGLE FAMILY DWELLING': 'bedroom', 
    'CONDOMINIUM/TOWNHOUSE': 'bedroom',
    'GROUP HOME': 'bedroom',
    'MULTI-UNIT DWELLING (APARTMENT, DUPLEX, ETC)': 'apartment_building',
    
    # Commercial & Lodging
    'MOTEL': 'motel',
    'HOTEL': 'motel',
    'CLOTHING STORE': 'restaurant',      # Using 'restaurant' as a generic indoor store proxy
    'CELL PHONE STORE': 'restaurant',
    'DEPARTMENT STORE': 'restaurant',
    'JEWELRY STORE': 'restaurant',
    'OTHER STORE': 'restaurant',
    
    # Open Areas & Vehicles
    'PARKING LOT': 'parking_lot',
    'PARK/PLAYGROUND': 'park',
    'GARAGE/CARPORT': 'parking_lot'
}

# 4. Function to grab a random forensic image
def get_random_image(premises_type):
    # Allowed forensic image extensions
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    
    # Check if the police premises exists in our map
    if premises_type in category_map:
        folder_name = category_map[premises_type]
        folder_path = os.path.join(PLACES_DIR, folder_name)
        
        # Check if the folder actually exists on your drive
        if os.path.exists(folder_path):
            # List all matching forensic images
            images = [img for img in os.listdir(folder_path) 
                     if img.lower().endswith(valid_extensions)]
            if images:
                # Pick one random image and return its full path
                random_image = random.choice(images)
                return os.path.join(folder_path, random_image)
    
    # For unmatched types, default to a generic street forensic image
    default_path = os.path.join(PLACES_DIR, 'street')
    if os.path.exists(default_path):
        images = [img for img in os.listdir(default_path) 
                 if img.lower().endswith(valid_extensions)]
        if images:
            return os.path.join(default_path, images[0])
            
    return "No_Image_Found"

print("Fusing gritty forensic images to crime cases...")

# 5. Apply the function to the 'Premis' column
df['Crime_Scene_Image_Path'] = df['Premis'].apply(get_random_image)

# 6. Save the final fused dataset as v2
output_filename = 'fused_dataset_v2.csv'
df.to_csv(output_filename, index=False)
print(f"Success! Forensic image paths attached and saved to {output_filename}")