# Enhanced Scraper

A powerful web scraper designed for Reference USA and similar database websites with advanced pagination calibration, session resume, and automated data extraction capabilities.

## 🌟 Key Features

- **Pagination Calibration**: One-time setup to identify Next button for fully automated mode
- **Session Resume**: Continue from where you left off if interrupted
- **Quick Mode**: Download exactly 10 pages at a time (recommended for reliability)
- **Smart Page Detection**: Multiple verification methods ensure successful navigation
- **CSV Merge Tool**: Combine multiple CSV files with duplicate removal
- **Semi & Fully Automated Modes**: Choose your level of automation
- **Persistent Settings**: Saves calibrations and progress between sessions

## 📋 Prerequisites

### For Both Mac and Windows:
- Python 3.7 or higher
- Google Chrome browser (latest version)
- ChromeDriver (instructions below)
- Basic familiarity with command line/terminal

## 🔧 Installation Guide

### Windows 11 Users

#### Step 1: Install Python
1. Visit [python.org](https://www.python.org/downloads/)
2. Download the latest Python 3.x installer for Windows
3. Run the installer
4. **IMPORTANT**: Check "Add Python to PATH" during installation
5. Click "Install Now"

#### Step 2: Verify Python Installation
1. Press `Win + R`, type `cmd`, press Enter
2. Type `python --version` and press Enter
3. You should see something like `Python 3.11.0`

#### Step 3: Install Required Python Packages
In Command Prompt, run:
```bash
pip install selenium pandas
```

#### Step 4: Install ChromeDriver
1. Open Chrome and check version: Menu (⋮) → Help → About Google Chrome
2. Note your Chrome version (e.g., 120.0.6099.109)
3. Visit [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
4. Download the ChromeDriver that matches your Chrome version
5. Extract the `chromedriver.exe` file
6. Place it in `C:\Windows\` or any folder in your PATH

#### Step 5: Download the Scraper
1. Save the `miller3_scraper.py` file to a folder (e.g., `C:\Users\YourName\Documents\Scraper`)
2. Open Command Prompt
3. Navigate to the folder: `cd C:\Users\YourName\Documents\Scraper`

### Mac Users

#### Step 1: Install Python (if not already installed)
1. Open Terminal (Cmd + Space, type "Terminal")
2. Check if Python is installed: `python3 --version`
3. If not installed:
   - Visit [python.org](https://www.python.org/downloads/)
   - Download and install the latest Python 3.x for macOS
   - OR use Homebrew: `brew install python3`

#### Step 2: Install Required Python Packages
In Terminal, run:
```bash
pip3 install selenium pandas
```

#### Step 3: Install ChromeDriver

**Option A: Using Homebrew (Recommended)**
```bash
brew install --cask chromedriver
```

**Option B: Manual Installation**
1. Open Chrome and check version: Chrome → About Google Chrome
2. Note your Chrome version
3. Visit [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
4. Download the ChromeDriver for Mac (choose ARM64 for M1/M2 Macs, or x64 for Intel)
5. Extract the file
6. Move to usr/local/bin: `sudo mv chromedriver /usr/local/bin/`
7. Make it executable: `sudo chmod +x /usr/local/bin/chromedriver`
8. Allow in Security settings if prompted

#### Step 4: Download the Scraper
1. Save the `miller3_scraper.py` file to a folder (e.g., `~/Documents/Scraper`)
2. Open Terminal
3. Navigate to the folder: `cd ~/Documents/Scraper`

## 🚀 Usage Instructions

### Starting the Scraper

**Windows 11:**
```bash
python miller3_scraper.py
```

**Mac:**
```bash
python3 miller3_scraper.py
```

### Step-by-Step Usage Guide

#### 1. Initial Options Menu
When you start the scraper, you'll see:
```
INITIAL OPTIONS
================
What would you like to do?
1. Start scraping new data
2. Merge existing CSV files in downloads folder
3. Both - merge existing files first, then start scraping
```

- Choose `1` for normal scraping
- Choose `2` to only merge existing CSV files
- Choose `3` to merge files then continue scraping

#### 2. Resume Previous Session (if available)
If you have a previous incomplete session, you'll see:
```
Found previous session:
  Last page: 15
  Pages downloaded: 14

Resume from previous session? (y/n):
```

#### 3. Login and Setup
1. Chrome will open to Reference USA
2. **Login** with your credentials
3. **Perform your search** (enter search criteria)
4. **Navigate to the first results page**
5. Press Enter when ready

#### 4. Choose Automation Mode
```
AUTOMATION MODE SELECTION
========================
1. Semi-Automated (you navigate between pages)
2. Fully Automated (script navigates pages)
```

- **Semi-Automated**: You manually click "Next" between pages
- **Fully Automated**: Script automatically navigates (recommended)

#### 5. Choose Page Limits
```
PAGE DOWNLOAD LIMITS
===================
1. Quick Mode - Download exactly 10 pages then stop (RECOMMENDED)
2. Download ALL available pages (up to 1000 limit)
3. Download a specific number of pages
```

- **Quick Mode** is most reliable, especially for beginners
- You can run multiple Quick Mode sessions to get more data

#### 6. Pagination Calibration (Fully Automated Mode Only)

The scraper will help you identify the "Next" button:

1. Make sure a "Next" button is visible on screen
2. Press Enter when ready
3. You'll see a list of potential buttons with scores:
   ```
   Found 5 potential 'Next' buttons (sorted by likelihood):
   1. A: 'Next »' [score: 23, class='pagination-next']
   2. BUTTON: '>' [score: 13, class='nav-arrow']
   3. A: '2' [score: 5, class='page-number']
   ```
4. Enter the number of the correct "Next" button
5. The button will be highlighted in RED for confirmation
6. Type 'y' if correct

**Note**: This calibration is saved and reused in future sessions!

#### 7. The Scraping Process

The scraper will:
1. **Select records** on each page (tries "Select All" first)
2. **Navigate** through pages in batches of 10
3. **Download** the selected records as CSV files
4. **Save progress** automatically

You'll see updates like:
```
Processing Page 1 (Batch 1, Page 1/10)
Select All successful! 51 total checkboxes selected.
```

#### 8. Manual Intervention (if needed)

If automatic selection fails:
```
Would you like to:
1. Try manual selection
2. Skip this page
3. Stop scraping
Enter choice (1-3):
```

For manual selection:
1. Click checkboxes manually on the webpage
2. Press Enter when done

#### 9. Download Process

After selecting records, the scraper will:
1. Navigate to the download page
2. Click the download button
3. Wait for the CSV file to download

If automatic download fails, follow the on-screen instructions for manual download.

#### 10. Final CSV Merge

At the end, you'll be asked:
```
Total CSV files in downloads folder: 5
Downloaded this session: 3
Existing files: 2

Would you like to merge all 5 CSV files into one? (y/n):
```

## 📁 File Structure

After running, you'll have:
```
Scraper Folder/
├── miller3_scraper.py      # The main script
├── Downloads/              # All downloaded CSV files
│   ├── download_1.csv
│   ├── download_2.csv
│   └── merged_data_20240115_143022.csv
├── Screenshots/            # Debug screenshots (if any errors)
│   └── error_screenshot_1234567.png
└── Config/                 # Saved settings
    ├── calibrations.json   # Saved Next button calibrations
    └── .scraper_progress.json  # Session progress
```

## 🛠️ Troubleshooting

### Common Issues and Solutions

#### "Chrome driver not found" Error
- **Windows**: Make sure chromedriver.exe is in your PATH or in C:\Windows\
- **Mac**: Run `which chromedriver` to verify installation

#### "No module named selenium" Error
- **Windows**: Run `pip install selenium`
- **Mac**: Run `pip3 install selenium`

#### Chrome Opens but Nothing Happens
- Make sure you're using a compatible ChromeDriver version
- Update Chrome to the latest version
- Download matching ChromeDriver version

#### Can't Find Next Button During Calibration
1. Try option 's' to skip calibration
2. Use semi-automated mode instead
3. Check if the page has fully loaded

#### Downloads Not Working
1. Check your Chrome download settings
2. Make sure the Downloads folder exists
3. Try manual download option when prompted

#### Session Resume Not Working
- Check if `.scraper_progress.json` exists in Config folder
- Sessions expire after 24 hours
- Delete the file to start fresh

### Debug Mode

Enable debug mode when prompted to get detailed information about:
- Page structure analysis
- Checkbox detection
- Download workflow elements

## 💡 Best Practices

1. **Start with Quick Mode** (10 pages) to test your setup
2. **Save your search** in Reference USA for easy access
3. **Run multiple Quick Mode sessions** for large datasets
4. **Monitor the first batch** to ensure everything works
5. **Use CSV merge** to combine all downloaded files
6. **Keep Chrome visible** to monitor progress

## ⚠️ Important Notes

- The scraper respects a max limit of 1000 pages per session
- Downloaded files are saved with timestamps
- Calibrations are saved per website URL
- Progress is saved after each page
- Always have a stable internet connection

## 🤝 Support

If you encounter issues:
1. Enable debug mode for detailed logs
2. Check the Screenshots folder for error captures
3. Verify all prerequisites are installed correctly
4. Try semi-automated mode as a fallback

## 📄 License

This tool is for educational and research purposes. Always comply with website terms of service and robots.txt files.
