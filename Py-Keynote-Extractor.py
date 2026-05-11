import requests
import json
import os

# --- PASTE YOUR COOKIE HERE ---
# Find this line in the script I gave you and paste the value
SESSION_COOKIE = "MoodleSession=77fad158dd62bca4184d286ad4dd13c3"

# Create a directory for raw data
os.makedirs("slides_data", exist_ok=True)

# Load URLs
with open("urls.txt", "r") as f:
    # We only want the .json files, and we skip the 'header.json' for the loop
    urls = [line.strip() for line in f.readlines() if line.strip().endswith(".json") and "header.json" not in line]

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
        response = requests.get(url, headers=headers, timeout=10)
        
        # If the response isn't JSON, it means we likely got redirected to a login page
        if "application/json" not in response.headers.get("Content-Type", ""):
            print(f"❌ Slide {i}: Auth failed. Cookie might be expired or copied incorrectly.")
            continue
            
        data = response.json()
        slide_content = extract_strings(data)
        
        if slide_content:
            # Remove duplicates while keeping order
            unique_content = list(dict.fromkeys(slide_content))
            all_text += f"Slide {i}\n" + "-"*10 + "\n" + "\n".join(unique_content) + "\n\n"
            print(f"✅ Processed Slide {i}")
        else:
            print(f"⚠️ Slide {i}: No text found.")
            
    except Exception as e:
        print(f"❌ Error on Slide {i}: {e}")

with open("Scraped_Lesson_Content.txt", "w", encoding="utf-8") as f:
    f.write(all_text)

print("\n🎉 Check 'Scraped_Lesson_Content.txt' for your results!")