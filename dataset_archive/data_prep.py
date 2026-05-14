import os
import requests
import time

# 1. Paste your Unsplash Access Key here
UNSPLASH_ACCESS_KEY = 'vH9PqhNsc7x8ETD9_1FNrd4CWKeOqGwk5co8-qvAoNE'

# 2. Define the categories you need to match your Crime CSV
# We will download 10 images for each of these categories
categories = [
    'parking_lot',
    'street',
    'alley',
    'apartment_building',
    'bedroom', 
    'gas_station',
    'park',
    'restaurant',
    'motel'
]

IMAGES_PER_CATEGORY = 10
BASE_DIR = './train/'

print("Starting lightweight image download...")

for category in categories:
    # Create the folder if it doesn't exist (e.g., ./train/alley/)
    folder_path = os.path.join(BASE_DIR, category)
    os.makedirs(folder_path, exist_ok=True)
    
    print(f"Downloading images for: {category}...")
    
    # Use the Unsplash API to search for random images matching the category
    # Note: We replace underscores with spaces for the search query
    search_query = category.replace('_', ' ')
    url = f"https://api.unsplash.com/photos/random?query={search_query}&count={IMAGES_PER_CATEGORY}&client_id={UNSPLASH_ACCESS_KEY}"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        for i, img_data in enumerate(data):
            # Grab the regular-sized image URL
            img_url = img_data['urls']['regular']
            
            # Download the actual image file
            img_response = requests.get(img_url)
            
            if img_response.status_code == 200:
                # Save it as 001.jpg, 002.jpg, etc.
                file_name = f"{str(i+1).zfill(3)}.jpg"
                file_path = os.path.join(folder_path, file_name)
                
                with open(file_path, 'wb') as f:
                    f.write(img_response.content)
            
            # Pause for half a second so Unsplash doesn't block us for spamming
            time.sleep(0.5) 
            
        print(f"✓ Saved {IMAGES_PER_CATEGORY} images to {folder_path}")
    else:
        print(f"Failed to fetch {category}. Error: {response.status_code}")

print("\nSuccess! You now have a lightweight image dataset.")