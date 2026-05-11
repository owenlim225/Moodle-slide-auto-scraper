Here is the comprehensive and formatted Markdown content for your **README.md**. It now includes the detailed **Virtual Environment activation** steps, the **URL Collector** script, and instructions for both automation types.

---

# Moodle Slide Automation & Extraction Suite

This suite contains two specialized automation tools designed to extract, clean, and format text content from Moodle LMS presentation resources.

## 🛠️ Tool Selection Guide

Before choosing a tool, open your browser's **Network Tab** (`F12` -> `Network`) while the lesson is open to identify the resource structure.

| Resource Type | Data Format | Detection | Recommended Tool |
| --- | --- | --- | --- |
| **Legacy HTML Slide** | `.js` files containing HTML strings | Network shows `slide1.js`, `slide2.js`, etc. | **JS-DOM-Scraper** |
| **Keynote/Modern Export** | Nested `.json` and `.pdf` chunks | Network shows GUIDs like `04A2F3DA...json` | **Py-Keynote-Extractor** |

---

## 1. JS-DOM-Scraper (Browser Console)

**File Name:** `dom_scraper.js`

Use this for lessons where data is stored in a `data/` folder as JavaScript files containing HTML (e.g., *Life and Works of Rizal*).

### 🚀 Usage Instructions

1. Open the Moodle Lesson in your browser.
2. Open **DevTools** (`F12`) and go to the **Console** tab.
3. Edit the following variables at the top of the script:
* `totalSlides`: Total number of slides.
* `baseUrl`: The URL directory where the `.js` files are located.
* `titleHeading`: The name of the subject.


4. Paste the script and hit `Enter`. A `.txt` file will download automatically.

---

## 2. Py-Keynote-Extractor (Python)

**File Name:** `keynote_extractor.py`

Use this for modern Moodle lessons exported from Apple Keynote. This requires a two-step process: collecting URLs and running the Python extraction.

### 📍 Step 1: URL Collection (Console)

Because Keynote exports use randomized filenames, you must first generate a list of assets.

1. Click through **every slide** in the lesson to ensure the browser loads all data chunks.
2. Open the **Console** (`F12`) and run the following **URL Collector** script:
```javascript
(async () => {
    console.log("🔍 Searching for slide data...");
    const performanceEntries = performance.getEntriesByType("resource");
    const dataFiles = performanceEntries
        .map(e => e.name)
        .filter(url => (url.includes('.pdf') || url.includes('.json')) && url.includes('/assets/'));
    const uniqueFiles = [...new Set(dataFiles)];

    if (uniqueFiles.length === 0) {
        console.log("❌ No data files found. Click through all slides and try again.");
    } else {
        console.log(`✅ Found ${uniqueFiles.length} data chunks!`);
        console.log(uniqueFiles.join('\n'));
    }
})();

```


3. Copy the list of URLs from the console and save them into a file named **`urls.txt`** in your project folder.

### 📍 Step 2: Python Extraction

#### A. Environment Setup

1. Open your project folder (e.g., on your **S: Drive**) in VS Code.
2. Create a virtual environment:
```powershell
python -m venv .venv
```


3. **Activate the Environment**: You must tell your terminal to use the S: Drive Python instead of the system default. Run:
```powershell
.\.venv\Scripts\Activate.ps1
```


*Note: You should see `(.venv)` appear in green at the start of your command line.*
4. Install dependencies:
```powershell
pip install requests
```



#### B. Authentication

1. In the browser **Network** tab, click any `.json` file request.
2. Under **Request Headers**, find and copy the `Cookie` value (e.g., `MoodleSession=77fad...`).
3. Paste this value into the `SESSION_COOKIE` variable inside `keynote_extractor.py`.

#### C. Execution

1. Ensure `urls.txt` is in the same directory as the script.
2. Run the script:
```powershell
python keynote_extractor.py

```


3. Your extracted text will be saved in **`Scraped_Lesson_Content.txt`**.

---

## 🛠️ Troubleshooting

* **"Expecting value: line 1 column 1"**: This indicates a Moodle Auth block. Your `MoodleSession` cookie has likely expired. Refresh the page and grab a new cookie.
* **"ModuleNotFoundError"**: Ensure your terminal shows `(.venv)`. If not, re-run the `Activate.ps1` command.
* **Scripts Disabled Error**: If PowerShell blocks the activation script, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` before activating.

---

## 📜 Dependencies

* **Python 3.x**
* **Requests Library** (`pip install requests`)
* **Modern Browser** (Chrome/Edge/Brave)