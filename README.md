# Moodle Slide Automation & Extraction Suite

This suite contains two specialized automation tools designed to extract, clean, and format text from Moodle LMS presentation resources. Since Moodle content is packaged differently depending on the source software, this guide helps you choose and use the correct tool for your specific course.

---

## 🛠️ Tool Selection Guide

Before starting, check your browser's **Network Tab** (`F12` -> `Network`) while the lesson is open to see which data structure your LMS is using.

| Resource Type | Data Format | Detection | Recommended Tool |
| :--- | :--- | :--- | :--- |
| **Standard HTML Slide** | `.js` files containing HTML strings | Network shows `slide1.js`, `slide2.js`, etc. | **JS-DOM-Scraper** |
| **Keynote Export** | Nested `.json` and `.pdf` chunks | Network shows GUIDs like `04A2F3DA...json` | **Py-Keynote-Extractor** |

---

## 1. JS-DOM-Scraper (Browser Console)
**File Name:** `dom_scraper.js`

Best for lessons where data is stored in a `data/` folder as JavaScript files containing HTML strings (e.g., *Life and Works of Rizal*).

### ✨ Features
- **Smart Formatting**: Handles sentence breaks, bullet points, and capitalization.
- **Title Sanitization**: Automatically removes repetitive course headers while keeping unique subtitles.
- **Zero Installation**: Runs directly in the browser console without needing Python.

### 🚀 Usage Instructions
1. Open the Moodle Lesson in your browser.
2. Open **DevTools** (`F12`) and go to the **Console** tab.
3. Edit the following variables at the top of the script:
   - `totalSlides`: The number of slides in the lesson.
   - `baseUrl`: The URL directory where the `.js` files are located.
   - `titleHeading`: The name of the subject.
4. Paste the script and hit `Enter`.
5. A cleaned `.txt` file will download automatically.

---

## 2. Py-Keynote-Extractor (Python)
**File Name:** `keynote_extractor.py`

Best for modern Moodle lessons exported from Apple Keynote. This version uses your session cookie to bypass LMS login security.

### ✨ Features
- **Deep JSON Parsing**: Recursively searches nested Keynote objects for text strings.
- **Auth Persistence**: Uses `MoodleSession` cookies to access private resource files.
- **Environment Isolation**: Designed to run from a virtual environment (`.venv`) to keep your system clean.

### 🚀 Usage Instructions

#### A. Setup (First Time Only)
1. Create a project folder on your **S: Drive**.
2. Open the folder in VS Code and create a virtual environment:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install requests