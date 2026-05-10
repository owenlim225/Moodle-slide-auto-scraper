# Moodle Slide Auto Scraper

A JavaScript utility for automatically extracting and cleaning text content from Moodle slide presentations.

## Overview

This script extracts text from HTML-based slide presentations, formats it for readability, and exports it as a clean text file. It's designed to work with the "Life and Works of Rizal: A Century Hence" presentation but can be adapted for other slide sets.

## Features

- **Automatic Extraction**: Fetches and processes multiple slide files (HTML content)
- **Smart Text Formatting**: 
  - Preserves acronyms and special formatting
  - Converts bullets and list items to readable format
  - Handles sentence breaks and line breaks intelligently
- **Duplicate Removal**: Eliminates duplicate lines within each slide
- **Title Cleanup**: Removes repeated title text while preserving slide subtitles
- **Auto-Download**: Generates and downloads a formatted text file automatically

## How It Works

1. Loads a configurable number of slides from a `data/` directory
2. Extracts HTML content from each slide file
3. Parses the HTML and cleans the text with:
   - Non-breaking space normalization
   - Smart capitalization detection
   - Bullet point and list item formatting
   - Sentence and line break insertion
4. Deduplicates content per slide
5. Exports all content to a downloadable `.txt` file

## Configuration

Edit these variables in the script:

```javascript
const totalSlides = 11;                    // Number of slides to process
const baseUrl = window.location.href...    // Base directory for slide files
const titleHeading = "...";                // Main heading for the document
```

## Usage

1. Ensure all slide files are stored in a `data/` directory (e.g., `slide1.js`, `slide2.js`, etc.)
2. Open the web page containing the slides in your browser
3. Open the browser console (F12 → Console tab)
4. Paste and run this script
5. A text file will automatically download with the extracted and formatted content

## Output

- **File**: `Rizal_Coursework_Final_Text.txt`
- **Format**: Plain text with clear slide separators and formatted content

## Dependencies

- Modern browser with ES6+ support
- DOMParser API
- Fetch API
- Blob and URL APIs

## Notes

- The script preserves the main title while removing redundant repeats
- Standalone slide subtitles are preserved
- PNG references and pixel measurements are filtered out
- Multiple consecutive blank lines are reduced to double line breaks
#
