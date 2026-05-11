import requests
import json
import os

# --- CONFIGURATION ---
SESSION_COOKIE = "MoodleSession=77fad158dd62bca4184d286ad4dd13c3"
OUTPUT_FOLDER = "scraped_outputs"
BASE_FILENAME = "Scraped_Lesson_Content"
# ---------------------

# Create the output directory if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load URLs
try:
    with open("urls.txt", "r") as f:
        urls = [line.strip() for line in f.readlines() if line.strip().endswith(".json") and "header.json" not in line]
except FileNotFoundError:
    print("❌ Error: 'urls.txt' not found. Please create it first.")
    exit()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Cookie": SESSION_COOKIE,
    "Accept": "application/json"
}

all_text = "SAM_Lesson2 Scraped Content\n" + "="*30 + "\n\n"

def extract_strings(obj):
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ['text', 'string', 'textString'] and isinstance(v, str):
                if len(v.strip()) > 1: found.append(v.strip())
            else: found.extend(extract_strings(v))
    elif isinstance(obj, list):
        for item in obj: found.extend(extract_strings(item))
    return found

print(f"🚀 Starting extraction for {len(urls)} slides...")

for i, url in enumerate(urls, 1):
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if "application/json" not in response.headers.get("Content-Type", ""):
            print(f"❌ Slide {i}: Auth failed. Cookie might be expired.")
            continue
            
        data = response.json()
        slide_content = extract_strings(data)
        
        if slide_content:
            unique_content = list(dict.fromkeys(slide_content))
            all_text += f"Slide {i}\n" + "-"*10 + "\n" + "\n".join(unique_content) + "\n\n"
            print(f"✅ Processed Slide {i}")
        else:
            print(f"⚠️ Slide {i}: No text found.")
            
    except Exception as e:
        print(f"❌ Error on Slide {i}: {e}")

# --- LOGIC TO PREVENT OVERWRITING ---
filename = f"{BASE_FILENAME}.txt"
filepath = os.path.join(OUTPUT_FOLDER, filename)
counter = 1

# If file exists, add a number until we find a name that isn't taken
while os.path.exists(filepath):
    filename = f"{BASE_FILENAME}_{counter}.txt"
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    counter += 1

# Save the final output
with open(filepath, "w", encoding="utf-8") as f:
    f.write(all_text)

print(f"\n🎉 Done! Results saved to: {filepath}")