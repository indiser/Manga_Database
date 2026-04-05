import json
import time
from curl_cffi import requests
import os
import img2pdf
import ctypes
import shutil
from PIL import Image
import argparse

def prevent_sleep():
    if os.name == 'nt':
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001)
        except: pass

prevent_sleep()

def create_folder(path):
        if not os.path.exists(path):
            os.makedirs(path)
        return path

def download_file(url, folder, filename):
        filepath = os.path.join(folder, filename)
        if os.path.exists(filepath): return # Skip if exists
        
        try:
            with requests.get(url, headers=HEADERS, stream=True) as r:
                r.raise_for_status()
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            time.sleep(1) # Be polite
        except Exception as e:
            print(f"  [ERROR] {url}: {e}")

def optimize_image(image_path):
        """
        Overwrites the image with an optimized version.
        1. if it's the cover (page 1/cover), keep color.
        2. If it's a body page, check if it's actually color.
        If mostly B&W, convert to Grayscale (L mode) -> 60% size drop.
        3. Save with optimize=True and quality=85 (Visual sweet spot).
        """
        try:
            with Image.open(image_path) as img:
                # Convert to RGB first to handle PNGs with transparency issues
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # OPTION: Brutal Grayscale for everything except Cover
                # This is the safest bet for Manga.
                # Assuming filenames are numbers (1.jpg, 2.jpg...)
                filename = os.path.basename(image_path)
                is_cover = "cover" in filename or filename.startswith("1.")
                
                if not is_cover:
                    # Convert to Grayscale (L)
                    # Manga is ink on paper. You don't need RGB channels.
                    img = img.convert("L")
                
                # Save it back over the original
                # quality=85 is the industry standard for "High" without bloat.
                img.save(image_path, "JPEG", quality=85, optimize=True)
                
        except Exception as e:
            print(f"  [Warning] Could not optimize {image_path}: {e}")


def make_pdf(folder_path, pdf_name):
    print(f"  [Packing] Optimizing images and creating PDF: {pdf_name}...")
        
    images = [i for i in os.listdir(folder_path) if i.endswith(('.jpg', '.png', '.jpeg', '.webp'))]
    images.sort(key=lambda x: int(os.path.splitext(x)[0]) if x[0].isdigit() else 0)
        
    image_paths = []
    for img_file in images:
        full_path = os.path.join(folder_path, img_file)
            
        optimize_image(full_path) 
            
        image_paths.append(full_path)

    pdf_path = os.path.join(DOWNLOAD_BASE, pdf_name)
    try:
        with open(pdf_path, "wb") as f:
            f.write(img2pdf.convert(image_paths))
        print(f"  [Success] PDF saved: {pdf_path}")
        return True
    except Exception as e:
        print(f"  [Error] PDF creation failed: {e}")
        return False

# def download_pdf(gallery_data):
#     safe_title = re.sub(r'[<>:"/\\|?*]', '', gallery_data['title']['english'])[:50]
#     temp_folder = os.path.join(DOWNLOAD_BASE, f"TEMP_{gallery_data['id']}")
#     create_folder(temp_folder)

#     print(f"Downloading {gallery_data['num_pages']} pages to temp folder...")
        
#     # Download Pages
#     ext_map = {'j': 'jpg', 'p': 'png', 'w': 'webp', 'g': 'gif'}
#     for i, page in enumerate(gallery_data['images']['pages'], start=1):
#         ext = ext_map.get(page['t'], 'jpg')
#         url = f"https://i.nhentai.net/galleries/{gallery_data['media_id']}/{i}.{ext}"
#         download_file(url, temp_folder, f"{i}.{ext}")

#         # 3. CONVERT TO PDF
#     pdf_filename = f"{gallery_data['id']} - {safe_title}.pdf"
#     success = make_pdf(temp_folder, pdf_filename)
        
#         # 4. CLEANUP (Delete the messy folder)
#     if success:
#         print("  [Cleanup] Deleting temp images...")
#         shutil.rmtree(temp_folder)
#         print("Done.")
#     else:
#         print("Warning: PDF failed, keeping images.")

def saveid(filename,manga_id):
    with open(filename,"a") as filp:
        filp.write(f"{manga_id}\n")

script_dir=os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_BASE = os.path.join(script_dir,"manga_library")
filepath=os.path.join(script_dir,"manga.jsonl")
good_ids_filepath=os.path.join(script_dir,"good_id.txt")
bad_ids_filepath=os.path.join(script_dir,"bad_id.txt")

good_id=set()
bad_id=set()

if os.path.exists(good_ids_filepath):
    with open(good_ids_filepath,"r") as filp:
        good_id={int(line.strip()) for line in filp if line.strip().isdigit()}

if os.path.exists(bad_ids_filepath):
    with open(bad_ids_filepath,"r") as filp:
        bad_id={int(line.strip()) for line in filp if line.strip().isdigit()}


# START_RANGE=1
# END_RANGE=10000

# Initialize the parser
parser = argparse.ArgumentParser(description="Manga Scraper: Brutal Efficiency Edition")

# Define the arguments
parser.add_argument("--start", type=int, required=True, help="The ID to start scraping from (e.g., 100)")
parser.add_argument("--end", type=int, required=True, help="The ID to stop scraping at (e.g., 200)")

# Parse the arguments
args = parser.parse_args()

# Map them to your existing variables
START_RANGE = args.start
END_RANGE = args.end

# Logical sanity check (Don't let the user be stupid)
if START_RANGE > END_RANGE:
    print(f"CRITICAL ERROR: Start range ({START_RANGE}) cannot be higher than end range ({END_RANGE}). Fix your inputs.")
    exit(1)

print(f"[*] Configuration Locked: Scraping IDs {START_RANGE} to {END_RANGE}")

consecutive_faliure=0

# create_folder(DOWNLOAD_BASE)

for id in range(START_RANGE,END_RANGE+1):

    if id in good_id:
        continue

    if id in bad_id:
        continue


    nhentai_url=f"https://doujin-api.onrender.com/manga_id={id}"

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response=requests.get(url=nhentai_url,headers=HEADERS, impersonate="chrome")
    
    if response.status_code==404:
        print(f"{id} doesn't Exist. Skipping...")
        saveid(bad_ids_filepath,id)
        bad_id.add(id)
        consecutive_faliure+=1
        continue
    
    if response.status_code==429:
        print("Too many requests...Sleeping for 10 seconds")
        time.sleep(10)
        continue

    if response.status_code==200:

        data_payload = {}
        consecutive_faliure=0

        data=response.json()
        recommendations=data.get("recommendations",[])

        data_payload={
            "id" : data["id"],
            "title" : data["title"],
            "date" : data["date"],
            "parodies" : data["parodies"] if data["parodies"] else [],
            "charecters" : data["characters"] if data["characters"] else [],
            "groups" : data["groups"] if data["groups"] else [],
            "categories" : data["categories"] if data["categories"] else [],
            "language" : data["language"] if data["language"] else [],
            "favorites" : data["favorites"] if data["favorites"] else None,
            "tags" : data["tags"] if data["tags"] else [],
            "artists" : data["artists"] if data["artists"] else [],
            "num_pages" : data["num_pages"] if data["num_pages"] else None,
            "recommendations" : [{"id" : rec["id"], "title" : rec["title"]} for rec in recommendations],
            "cover_image" : data["cover_image"]
        }

        saveid(good_ids_filepath,id)
        good_id.add(id)
        # --- OUTPUT ---

        with open(filepath,"a",encoding="utf-8") as filp:
            json.dump(data_payload,filp,ensure_ascii=False)
            filp.write("\n")
        
        if consecutive_faliure >= 500:
            print("\n" + "="*40)
            print(f"!!! HIT 200 CONSECUTIVE FAILURES. STOPPING. !!!")
            print("="*40 + "\n")
            exit()
        
        # time.sleep(0.5)
        

