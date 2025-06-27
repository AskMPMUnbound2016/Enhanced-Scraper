# Miller 3 Data Scraper - Enhanced Version

## Overview
An advanced web scraper for Miller 3 Data with both semi-automated and fully automated modes, batch processing, and CSV merge capabilities.

## Key Features
* **Automation Modes**: Choose between Semi-Automated (you navigate pages) and Fully Automated (script handles everything).
* **Download Mode Options**: Download all pages, continue from where you left off, process a specific page range, or just download the current page.
* **Smart Record Selection**: Automatically selects records in batches, respecting the website's limits.
* **Automated Navigation (Full Mode)**: Automatically clicks next/arrow buttons or uses the page number input to navigate. It falls back to manual prompts if needed.
* **No File Naming Prompts**: Downloads use default filenames from the website and are saved to a local `Downloads` folder.
* **CSV Merge Option**: An option to merge all downloaded CSV files into a single, timestamped file at the end of a session.
* **Download Limit Management**: Respects the 1000-page limit per search and stops automatically.

---

## IMPORTANT: ChromeDriver Security Warning
When you run the scraper for the first time, your operating system may block ChromeDriver because it is an application downloaded from the internet.

* **On macOS**: You may see a warning that says **"ChromeDriver cannot be opened because the developer cannot be verified."**
    * **Solution**: Open `System Settings` > `Privacy & Security`. Scroll down and you will see a message about "ChromeDriver" being blocked. Click the **"Allow Anyway"** button. You may need to run the launcher script one more time after allowing it.

* **On Windows**: Windows Defender SmartScreen might show a blue screen that says **"Windows protected your PC"**.
    * **Solution**: Click on **"More info"** and then click the **"Run anyway"** button.

---

## How to Use

### Step 1: Initial Setup
Ensure you have Python 3 and Google Chrome installed on your system. Then, install the required Python libraries by opening a terminal or command prompt and running:
```bash
pip install selenium pandas
