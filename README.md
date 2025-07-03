# Miller 3 Data Scraper - Enhanced Version with CSV Merge Options

## Overview
An advanced web scraper for Miller 3 Data (Reference USA) with both semi-automated and fully automated modes, batch processing, and comprehensive CSV merge capabilities. The scraper now includes standalone CSV merge functionality and enhanced end-of-session merge options.

## 🆕 NEW CSV MERGE FEATURES

### ✨ **Initial Options Menu**
When you start the scraper, you'll see:
```
================================================================================
INITIAL OPTIONS
================================================================================
What would you like to do?
1. Start scraping new data
2. Merge existing CSV files in downloads folder
3. Both - merge existing files first, then start scraping
================================================================================
```

### ✨ **Standalone CSV Merge (Option 2)**
- Merge existing CSV files **without any scraping**
- Perfect for combining files from previous sessions
- Works with ALL CSV files in your Downloads folder
- Automatic duplicate detection and removal

### ✨ **End-of-Session Merge**
- After completing scraping, option to merge all CSV files
- Smart detection of current session vs existing files
- Choose to merge all files or just current session

## Key Features
* **🆕 CSV Merge Options**: Standalone merge and end-of-session merge with duplicate removal
* **Automation Modes**: Choose between Semi-Automated (you navigate pages) and Fully Automated (script handles everything)
* **Enhanced Select All**: Automatically finds and uses "Select All" checkboxes when available
* **Smart Record Selection**: Falls back to individual selection if Select All fails
* **Batch Processing**: Configurable batch sizes (default: 10 pages per batch)
* **User-Defined Limits**: Set specific page limits (1-1000 pages) or download all available
* **Automated Navigation**: Automatically clicks next/arrow buttons in full automation mode
* **No File Naming Prompts**: Uses default filenames from website, saves to Downloads folder
* **Robust Error Handling**: Screenshots and page source capture for debugging
* **Manual Fallbacks**: Manual assistance options when automation fails
* **Download Limit Management**: Respects 1000-page limit per search and stops automatically

---

## IMPORTANT: ChromeDriver Security Warning
When you run the scraper for the first time, your operating system may block ChromeDriver because it is an application downloaded from the internet.

* **On macOS**: You may see a warning that says **"ChromeDriver cannot be opened because the developer cannot be verified."**
    * **Solution**: Open `System Settings` > `Privacy & Security`. Scroll down and you will see a message about "ChromeDriver" being blocked. Click the **"Allow Anyway"** button. You may need to run the launcher script one more time after allowing it.

* **On Windows**: Windows Defender SmartScreen might show a blue screen that says **"Windows protected your PC"**.
    * **Solution**: Click on **"More info"** and then click the **"Run anyway"** button.

---

## Installation & Setup

### Step 1: Requirements
Ensure you have **Python 3.7+** and **Google Chrome** installed on your system.

### Step 2: Install Dependencies
Open a terminal or command prompt and run:
```bash
pip install selenium pandas
```

### Step 3: Download Files
Ensure you have these files in the same folder:
- `scraper_enhanced.py` (main scraper)
- `launcher.py` (easy launcher)
- `README.md` (this file)

---

## How to Use

### Method 1: Easy Launcher (Recommended)
**Double-click `launcher.py`** to start the scraper with a user-friendly interface.

### Method 2: Direct Command Line
```bash
python scraper_enhanced.py
```

## Usage Workflows

### 🔄 **Workflow 1: Standalone CSV Merge**
Perfect for combining files from previous sessions:
1. Run the scraper (`launcher.py` or command line)
2. **Choose Option 2**: "Merge existing CSV files in downloads folder"
3. Review the list of CSV files found
4. Confirm merge to create a single combined file
5. Done! No browser opens, no scraping occurs

**Example Output:**
```
Found 5 CSV files in downloads folder:
  1. data_20250101_120000.csv (15,432 bytes)
  2. data_20250102_130000.csv (23,891 bytes)
  3. data_20250103_140000.csv (18,765 bytes)

Would you like to merge all 5 CSV files into one? (y/n): y
Merged file saved as: merged_data_20250103_145030.csv
Total records in merged file: 2,847
```

### 🕷️ **Workflow 2: Fresh Scraping Session**
For new data collection:
1. Run the scraper
2. **Choose Option 1**: "Start scraping new data"
3. Browser opens to Reference USA website
4. Login and perform your search manually
5. Navigate to first page of results
6. Choose automation mode (Semi or Fully Automated)
7. Set page limits (All pages or specific number)
8. Scraper processes data in batches
9. At the end, option to merge all CSV files

### 🔄🕷️ **Workflow 3: Merge Then Scrape**
Combine existing files, then collect more data:
1. Run the scraper
2. **Choose Option 3**: "Both - merge existing files first, then start scraping"
3. Existing files are merged first
4. Then continues with fresh scraping session
5. Final merge option includes all files (old + new)

## 🎛️ Configuration Options

### **Automation Modes**
```
Choose automation level:
1. Semi-Automated (you navigate between pages)
2. Fully Automated (script navigates pages)
```

- **Semi-Automated**: You manually navigate pages, script selects records and downloads
- **Fully Automated**: Script handles everything with intelligent fallbacks to manual mode

### **Page Download Limits**
```
Choose how many pages to download:
1. Download ALL available pages (up to 1000 limit)
2. Download a specific number of pages
```

### **Debug Mode**
Enable debug mode for troubleshooting:
- Page structure analysis
- Element detection debugging
- Enhanced logging and screenshots

## 📁 Directory Structure

The scraper automatically creates this structure:
```
├── scraper_enhanced.py        # Main scraper script
├── launcher.py               # Easy launcher (double-click to run)
├── README.md                # This documentation
├── Downloads/               # All CSV files saved here
│   ├── data_20250103_143022.csv
│   ├── data_20250103_144513.csv
│   └── merged_data_20250103_145030.csv
└── Screenshots/             # Debug screenshots and page sources
    ├── error_screenshot_*.png
    └── page_source_*.html
```

## 📊 CSV Merge Process

### **What Gets Merged**
- All `.csv` files in the Downloads folder
- Combines using pandas for robust data handling
- Removes duplicate records automatically
- Creates timestamped output: `merged_data_YYYYMMDD_HHMMSS.csv`

### **Merge Examples**

**End-of-Session Merge:**
```
================================================================================
DOWNLOAD SUMMARY
Total pages downloaded: 25
Files saved to: /path/to/Downloads

Downloaded files this session:
  - data_20250103_143022.csv (15,432 bytes)
  - data_20250103_144513.csv (23,891 bytes)

Total CSV files in downloads folder: 7
Downloaded this session: 2
Existing files: 5

Would you like to merge all 7 CSV files into one? (y/n): y

Merging 7 CSV files...
Added 445 rows from data_20250101_120000.csv
Added 892 rows from data_20250102_130000.csv
Added 657 rows from data_20250103_140000.csv
Added 523 rows from data_20250103_141500.csv
Added 389 rows from data_20250103_143000.csv
Added 534 rows from data_20250103_143022.csv
Added 612 rows from data_20250103_144513.csv
Removed 15 duplicate records
Merged file saved as: merged_data_20250103_145030.csv
Total records in merged file: 4,037
```

## 🔧 Advanced Features

### **Enhanced Select All**
- Automatically detects and uses "Select All" checkboxes
- Multiple detection patterns for different website layouts
- Falls back to individual selection if Select All unavailable

### **Intelligent Page Navigation**
- Multiple selector patterns for "Next" buttons
- Automatic URL change detection
- Fallback to manual navigation when needed

### **Smart Download Detection**
- Monitors download folder in real-time
- Handles various download states (.crdownload, .tmp, .part)
- Manual download assistance when automation fails

### **Robust Error Handling**
- Automatic screenshot capture on failures
- Page source saving for debugging
- Multiple retry strategies with user choices

## 🛠️ Troubleshooting

### **No Records Selected**
1. Enable debug mode: Answer "y" when prompted
2. Review debug output and screenshots
3. Try manual selection mode when offered
4. Check `Screenshots/` folder for debug information

### **Download Fails**
1. Script provides manual download assistance
2. Complete download manually when prompted
3. Script automatically detects manually downloaded files
4. Confirm completion when asked

### **CSV Merge Issues**
1. Ensure CSV files have consistent column structure
2. Check file permissions in Downloads folder
3. Review console output for specific error details
4. Verify pandas is properly installed: `pip install pandas`

### **Page Navigation Problems**
1. Switch to semi-automated mode for manual control
2. Navigate pages manually when prompted
3. Enable debug mode to identify page elements
4. Check Screenshots folder for page structure analysis

## ⚙️ Customization

### **Batch Size**
Modify in the script's `__init__` method:
```python
self.pages_per_batch = 10  # Change to desired batch size
```

### **Timeout Settings**
```python
self.wait = WebDriverWait(self.driver, 20)  # Page load timeout
timeout=120  # Download completion timeout (in wait_for_download_complete)
```

### **Download Directory**
```python
# Custom download directory
scraper = Miller3DataScraper(download_dir="/path/to/custom/downloads")
```

## 🎯 Supported Websites

Primarily optimized for **Reference USA** but adaptable to other data platforms with:
- Tabular data with selectable checkboxes
- Pagination controls (Next buttons, page numbers)
- Download/export functionality
- Batch download capabilities

## 📈 Performance Tips

1. **Use Fully Automated Mode** for fastest processing
2. **Enable Select All** detection (automatic when available)
3. **Set realistic page limits** to avoid session timeouts
4. **Monitor download folder size** for disk space management
5. **Use standalone merge** regularly to consolidate files
6. **Close other browser windows** to reduce resource conflicts

## 🔒 Best Practices

### **Before Scraping**
- Ensure stable internet connection
- Close unnecessary browser windows
- Verify adequate disk space
- Test with small page limits first

### **During Scraping**
- Monitor console output for errors
- Don't interact with the automated browser window
- Keep the terminal/command prompt window visible
- Have backup manual navigation ready

### **After Scraping**
- Review downloaded files for completeness
- Use merge functionality to consolidate data
- Check Screenshots folder if issues occurred
- Backup important data files

## 🐛 Debug Information

When reporting issues, include:
- Console log output (copy and paste)
- Screenshots from `Screenshots/` folder
- Page source HTML files (if generated)
- Website URL and specific page details
- Operating system and Python version

## 🔗 Target Website

**Primary URL**: `https://referenceusa.com.us1.proxy.openathens.net/`

The scraper is optimized for Reference USA's interface but can be adapted for similar data platforms.

## 📄 License & Disclaimer

This tool is for educational and research purposes. Users must:
- Comply with website terms of service
- Respect data usage policies
- Use responsibly and ethically
- Ensure proper attribution of data sources

---

**Version**: Enhanced with CSV Merge Options  
**Last Updated**: January 2025  
**Author**: Miller 3 Data Scraper Team

**Quick Start**: Double-click `launcher.py` to begin!