#!/usr/bin/env python3
"""
Miller 3 Data Scraper - Enhanced Version with CSV Merge Options
NEW CSV MERGE ENHANCEMENTS:
- Standalone option to merge existing CSV files before scraping
- Enhanced merge option that includes ALL CSV files in downloads folder
- Option to merge existing files + new downloads together

[All previous enhancements remain unchanged]
"""

import time
import os
import glob
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Miller3DataScraper:
    def __init__(self, download_dir=None):
        """Initialize the scraper with Chrome options"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set up separate directories for downloads and screenshots
        self.download_dir = download_dir or os.path.join(script_dir, 'Downloads')
        self.screenshots_dir = os.path.join(script_dir, 'Screenshots')

        # Create directories if they don't exist
        for directory in [self.download_dir, self.screenshots_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")

        self.driver = None
        self.wait = None
        self.download_count = 0
        self.batch_size = 10
        self.max_downloads = 1000
        self.max_pages_to_download = 1000  # User-defined limit
        self.downloaded_files = []
        self.current_page = 1
        self.total_pages = None
        self.download_mode = None
        self.automation_mode = None
        self.no_results_count = 0
        self.max_no_results_attempts = 3
        self.use_select_all = False
        self.pages_per_batch = 10
        self.selected_pages_in_batch = 0
        self.start_page = 1
        self.end_page = None
        self.pages_downloaded = 0
        self._last_files = set()

    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safeBrowse.enabled": True,
            "safeBrowse.disable_download_protection": True,
            "profile.default_content_setting_values.automatic_downloads": 1
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        logger.info("Chrome driver initialized successfully")

    def get_initial_options(self):
        """NEW: Get initial user options before starting scraper"""
        logger.info("\n" + "="*80)
        logger.info("INITIAL OPTIONS")
        logger.info("="*80)
        logger.info("What would you like to do?")
        logger.info("1. Start scraping new data")
        logger.info("2. Merge existing CSV files in downloads folder")
        logger.info("3. Both - merge existing files first, then start scraping")
        logger.info("="*80)
        
        while True:
            choice = input("\nEnter your choice (1-3): ").strip()
            if choice == '1':
                return 'scrape'
            elif choice == '2':
                return 'merge_only'
            elif choice == '3':
                return 'merge_then_scrape'
            else:
                logger.warning("Invalid choice. Please enter 1, 2, or 3.")

    def get_all_csv_files_in_downloads(self):
        """NEW: Get all CSV files in the downloads folder"""
        try:
            all_files = os.listdir(self.download_dir)
            csv_files = [os.path.join(self.download_dir, f) for f in all_files if f.endswith('.csv')]
            return csv_files
        except Exception as e:
            logger.error(f"Error getting CSV files from downloads folder: {e}")
            return []

    def standalone_csv_merge(self):
        """NEW: Standalone CSV merge option for existing files"""
        logger.info("\n" + "="*80)
        logger.info("STANDALONE CSV MERGE")
        logger.info("="*80)
        
        csv_files = self.get_all_csv_files_in_downloads()
        
        if len(csv_files) == 0:
            logger.info("No CSV files found in the downloads folder.")
            logger.info(f"Downloads folder: {self.download_dir}")
            return False
        elif len(csv_files) == 1:
            logger.info(f"Only 1 CSV file found: {os.path.basename(csv_files[0])}")
            logger.info("Need at least 2 CSV files to merge.")
            return False
        else:
            logger.info(f"Found {len(csv_files)} CSV files in downloads folder:")
            for i, file_path in enumerate(csv_files, 1):
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                logger.info(f"  {i}. {os.path.basename(file_path)} ({file_size} bytes)")
            
            logger.info("="*80)
            merge_choice = input(f"\nWould you like to merge all {len(csv_files)} CSV files into one? (y/n): ").strip().lower()
            
            if merge_choice == 'y':
                # Set the files to merge and call existing merge function
                self.downloaded_files = csv_files  # Temporarily set for merge function
                self.merge_csv_files()
                self.downloaded_files = []  # Reset
                return True
            else:
                logger.info("CSV merge cancelled.")
                return False

    def get_automation_mode(self):
        """Get user's choice for automation mode"""
        logger.info("\n" + "="*80)
        logger.info("AUTOMATION MODE SELECTION")
        logger.info("="*80)
        logger.info("Choose automation level:")
        logger.info("1. Semi-Automated (you navigate between pages)")
        logger.info("2. Fully Automated (script navigates pages)")
        logger.info("="*80)
        while True:
            choice = input("\nEnter your choice (1-2): ").strip()
            if choice == '1':
                self.automation_mode = 'semi'
                return
            elif choice == '2':
                self.automation_mode = 'full'
                return
            else:
                logger.warning("Invalid choice. Please enter 1 or 2.")

    def get_page_limits(self):
        """Get user's choice for how many pages to download"""
        logger.info("\n" + "="*80)
        logger.info("PAGE DOWNLOAD LIMITS")
        logger.info("="*80)
        logger.info("Choose how many pages to download:")
        logger.info("1. Download ALL available pages (up to 1000 limit)")
        logger.info("2. Download a specific number of pages")
        logger.info("="*80)
        
        while True:
            choice = input("\nEnter your choice (1-2): ").strip()
            if choice == '1':
                self.max_pages_to_download = self.max_downloads  # Use existing limit
                logger.info(f"Will download all available pages (up to {self.max_downloads} pages)")
                return
            elif choice == '2':
                while True:
                    try:
                        pages = int(input("Enter number of pages to download (1-1000): ").strip())
                        if 1 <= pages <= 1000:
                            self.max_pages_to_download = pages
                            logger.info(f"Will download {pages} pages")
                            return
                        else:
                            logger.warning("Please enter a number between 1 and 1000.")
                    except ValueError:
                        logger.warning("Please enter a valid number.")
            else:
                logger.warning("Invalid choice. Please enter 1 or 2.")

    def try_select_all_records(self):
        """Try to find and use 'Select All' checkbox first"""
        logger.info("Attempting to find and use 'Select All' checkbox...")
        
        # Look for "Select All" checkboxes with various patterns
        select_all_selectors = [
            # Common "Select All" patterns
            "//input[@type='checkbox' and contains(@id, 'selectall')]",
            "//input[@type='checkbox' and contains(@id, 'select-all')]",
            "//input[@type='checkbox' and contains(@name, 'selectall')]",
            "//input[@type='checkbox' and contains(@name, 'select-all')]",
            "//input[@type='checkbox' and contains(@class, 'selectall')]",
            "//input[@type='checkbox' and contains(@class, 'select-all')]",
            
            # Look for checkboxes in header rows with "select all" text nearby
            "//th//input[@type='checkbox']",
            "//thead//input[@type='checkbox']",
            "//tr[1]//input[@type='checkbox']",
            
            # Look for checkboxes with "select all" in parent text
            "//input[@type='checkbox'][ancestor::*[contains(text(), 'Select All')]]",
            "//input[@type='checkbox'][ancestor::*[contains(text(), 'select all')]]",
            "//input[@type='checkbox'][ancestor::*[contains(text(), 'SELECT ALL')]]",
            
            # Check for the first checkbox in a table (often select all)
            "//table//input[@type='checkbox'][1]",
            "//form//input[@type='checkbox'][1]"
        ]
        
        for i, selector in enumerate(select_all_selectors):
            try:
                logger.info(f"Trying select all selector {i+1}: {selector}")
                select_all_checkbox = self.driver.find_element(By.XPATH, selector)
                
                if select_all_checkbox.is_displayed() and select_all_checkbox.is_enabled():
                    # Check if this looks like a select all checkbox
                    parent_text = ""
                    try:
                        # Get surrounding text to verify it's select all
                        parent_element = select_all_checkbox.find_element(By.XPATH, "./ancestor::tr[1] | ./ancestor::th[1] | ./ancestor::td[1]")
                        parent_text = parent_element.text.lower()
                    except:
                        pass
                    
                    # If it's in header or contains select all text, or is the first checkbox, try it
                    is_select_all = False
                    try:
                        # Check if it's in a header
                        select_all_checkbox.find_element(By.XPATH, "./ancestor::thead | ./ancestor::th")
                        is_select_all = True
                    except:
                        pass
                    
                    if (is_select_all or 
                        "select all" in parent_text or 
                        "company name" in parent_text):
                        
                        logger.info(f"Found potential Select All checkbox: {parent_text}")
                        
                        # Scroll into view and click
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", select_all_checkbox)
                        time.sleep(0.5)
                        
                        # Click the select all checkbox
                        self.driver.execute_script("arguments[0].click();", select_all_checkbox)
                        time.sleep(1)
                        
                        # Count how many checkboxes are now selected
                        all_checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
                        selected_count = sum(1 for cb in all_checkboxes if cb.is_selected())
                        
                        if selected_count > 1:  # More than just the select all checkbox
                            logger.info(f"Select All successful! {selected_count} total checkboxes selected.")
                            return selected_count - 1  # Subtract the select all checkbox itself
                        else:
                            logger.info("Select All checkbox clicked but no other checkboxes were selected.")
                            
            except (NoSuchElementException, ElementNotInteractableException):
                continue
            except Exception as e:
                logger.debug(f"Error with select all selector {i+1}: {e}")
                continue
        
        logger.info("No working Select All checkbox found.")
        return 0

    def debug_page_structure(self):
        """Debug method to analyze page structure and find checkboxes"""
        logger.info("Analyzing page structure for debugging...")
        
        try:
            # Look for all input elements
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            logger.info(f"Found {len(all_inputs)} total input elements")
            
            checkboxes = [inp for inp in all_inputs if inp.get_attribute("type") == "checkbox"]
            logger.info(f"Found {len(checkboxes)} checkbox elements")
            
            for i, cb in enumerate(checkboxes[:10]):  # Look at first 10
                try:
                    attrs = {
                        'id': cb.get_attribute('id'),
                        'name': cb.get_attribute('name'),
                        'class': cb.get_attribute('class'),
                        'value': cb.get_attribute('value'),
                        'displayed': cb.is_displayed(),
                        'enabled': cb.is_enabled(),
                        'selected': cb.is_selected()
                    }
                    logger.info(f"Checkbox {i+1}: {attrs}")
                except Exception as e:
                    logger.warning(f"Error analyzing checkbox {i+1}: {e}")
            
            # Look for table structure
            tables = self.driver.find_elements(By.TAG_NAME, "table")
            logger.info(f"Found {len(tables)} table elements")
            
            for i, table in enumerate(tables[:3]):  # Look at first 3 tables
                try:
                    table_id = table.get_attribute('id')
                    table_class = table.get_attribute('class')
                    logger.info(f"Table {i+1}: id='{table_id}', class='{table_class}'")
                except Exception as e:
                    logger.warning(f"Error analyzing table {i+1}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in debug analysis: {e}")

    def debug_download_workflow(self):
        """Debug method to analyze download workflow elements"""
        logger.info("Analyzing download workflow elements...")
        
        try:
            # Look for any buttons or links that might trigger download
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            all_inputs = self.driver.find_elements(By.XPATH, "//input[@type='button' or @type='submit']")
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            
            logger.info(f"Found {len(all_buttons)} buttons, {len(all_inputs)} input buttons, {len(all_links)} links")
            
            # Analyze buttons
            for i, btn in enumerate(all_buttons[:10]):
                try:
                    text = btn.text.strip()
                    class_attr = btn.get_attribute('class')
                    id_attr = btn.get_attribute('id')
                    if text or 'download' in (class_attr or '').lower() or 'download' in (id_attr or '').lower():
                        logger.info(f"Button {i+1}: text='{text}', class='{class_attr}', id='{id_attr}'")
                except Exception:
                    continue
            
            # Analyze input buttons
            for i, inp in enumerate(all_inputs[:10]):
                try:
                    value = inp.get_attribute('value')
                    class_attr = inp.get_attribute('class')
                    id_attr = inp.get_attribute('id')
                    if value and ('download' in value.lower() or 'export' in value.lower()):
                        logger.info(f"Input {i+1}: value='{value}', class='{class_attr}', id='{id_attr}'")
                except Exception:
                    continue
            
            # Analyze links
            download_links = []
            for link in all_links:
                try:
                    text = link.text.strip()
                    href = link.get_attribute('href')
                    if text and ('download' in text.lower() or 'export' in text.lower()):
                        download_links.append((text, href))
                except Exception:
                    continue
            
            if download_links:
                logger.info("Found potential download links:")
                for text, href in download_links[:5]:
                    logger.info(f"  Link: '{text}' -> '{href}'")
            
            # Look for forms
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            logger.info(f"Found {len(forms)} forms on the page")
            
            for i, form in enumerate(forms[:3]):
                try:
                    action = form.get_attribute('action')
                    method = form.get_attribute('method')
                    logger.info(f"Form {i+1}: action='{action}', method='{method}'")
                except Exception:
                    continue
                    
        except Exception as e:
            logger.error(f"Error in download workflow debug analysis: {e}")

    def manual_checkbox_selection(self):
        """Fallback method for manual checkbox selection"""
        logger.info("\n" + "="*60)
        logger.info("MANUAL SELECTION MODE")
        logger.info("="*60)
        logger.info("The automatic selection failed. Please:")
        logger.info("1. Manually select the records you want on this page")
        logger.info("2. Press Enter when done")
        logger.info("="*60)
        
        input("Press Enter after manually selecting records...")
        
        # Count selected checkboxes
        try:
            all_checkboxes = self.driver.find_elements(By.XPATH, "//input[@type='checkbox']")
            selected_count = sum(1 for cb in all_checkboxes if cb.is_selected())
            logger.info(f"Detected {selected_count} manually selected records")
            return selected_count
        except Exception as e:
            logger.warning(f"Could not count selected records: {e}")
            return 1  # Assume at least one was selected

    def manual_download_assistance(self):
        """Provide manual download assistance"""
        logger.info("\n" + "="*60)
        logger.info("MANUAL DOWNLOAD ASSISTANCE")
        logger.info("="*60)
        logger.info("The automatic download failed. Please:")
        logger.info("1. Look for a 'Download' or 'Export' button on the current page")
        logger.info("2. Click it manually")
        logger.info("3. Complete any download dialogs")
        logger.info("4. Wait for the file to download")
        logger.info("5. Press Enter when the download is complete")
        logger.info("="*60)
        
        input("Press Enter after manually completing the download...")
        
        # Check if any new files appeared
        current_files = set(os.listdir(self.download_dir))
        new_files = current_files - self._last_files
        if new_files:
            for file in new_files:
                if not file.endswith(('.crdownload', '.tmp', '.part')):
                    file_path = os.path.join(self.download_dir, file)
                    self.downloaded_files.append(file_path)
                    logger.info(f"Detected new download: {file}")
            self._last_files = current_files
            return True
        
        manual_confirm = input("Did you successfully download a file? (y/n): ").strip().lower()
        return manual_confirm == 'y'

    def auto_select_pages(self, max_records=None):
        """Automatically select records - Enhanced with Select All first."""
        if max_records is None:
            logger.info("Attempting to auto-select ALL records on the current page...")
        else:
            logger.info(f"Attempting to auto-select up to {max_records} records...")
        
        time.sleep(2)
        
        # Try Select All first
        if max_records is None:  # Only try select all if we want all records
            selected_count = self.try_select_all_records()
            if selected_count > 0:
                return selected_count
        
        # If Select All failed or we want limited records, proceed with individual selection
        logger.info("Proceeding with individual record selection...")
        
        # [Rest of the existing auto_select_pages method stays exactly the same]
        # Expanded list of checkbox selectors for better compatibility
        checkbox_selectors = [
            # Original selectors
            "//input[@type='checkbox' and @name='recordId']",
            "//table[@id='searchResultsTable']//tbody//input[@type='checkbox']",
            
            # More generic selectors for Reference USA
            "//input[@type='checkbox']",
            "//table//input[@type='checkbox']",
            "//tbody//input[@type='checkbox']",
            "//tr//input[@type='checkbox']",
            "//td//input[@type='checkbox']",
            
            # Specific patterns for data tables
            "//table[contains(@class, 'table')]//input[@type='checkbox']",
            "//div[contains(@class, 'table')]//input[@type='checkbox']",
            "//form//input[@type='checkbox']",
            
            # Look for checkboxes with common naming patterns
            "//input[@type='checkbox' and contains(@name, 'record')]",
            "//input[@type='checkbox' and contains(@name, 'select')]",
            "//input[@type='checkbox' and contains(@id, 'record')]",
            "//input[@type='checkbox' and contains(@id, 'select')]",
        ]
        
        selected_count = 0
        found_checkboxes = False
        
        for i, selector in enumerate(checkbox_selectors):
            try:
                logger.info(f"Trying selector {i+1}/{len(checkbox_selectors)}: {selector}")
                
                # First check if any checkboxes exist with this selector
                checkboxes = self.driver.find_elements(By.XPATH, selector)
                
                if checkboxes:
                    found_checkboxes = True
                    logger.info(f"Found {len(checkboxes)} checkboxes with this selector")
                    
                    # Filter for visible and enabled checkboxes
                    valid_checkboxes = []
                    for cb in checkboxes:
                        try:
                            if cb.is_displayed() and cb.is_enabled():
                                # Additional check: skip if this is a "select all" checkbox
                                try:
                                    parent_text = cb.find_element(By.XPATH, "./ancestor::tr[1]").text.lower()
                                    if "select all" not in parent_text and "company name" not in parent_text:
                                        valid_checkboxes.append(cb)
                                except:
                                    # If we can't get parent text, include it anyway
                                    valid_checkboxes.append(cb)
                        except Exception as e:
                            logger.debug(f"Checkbox validation error: {e}")
                            continue
                    
                    logger.info(f"Found {len(valid_checkboxes)} valid checkboxes")
                    
                    if valid_checkboxes:
                        # Determine how many to select
                        checkboxes_to_select = valid_checkboxes if max_records is None else valid_checkboxes[:max_records]
                        
                        # Try to select them
                        for j, checkbox in enumerate(checkboxes_to_select):
                            try:
                                if not checkbox.is_selected():
                                    # Scroll checkbox into view
                                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                                    time.sleep(0.2)
                                    
                                    # Try clicking with JavaScript first
                                    self.driver.execute_script("arguments[0].click();", checkbox)
                                    
                                    # Verify it was selected
                                    time.sleep(0.1)
                                    if checkbox.is_selected():
                                        selected_count += 1
                                        logger.info(f"Selected checkbox {j+1}/{len(checkboxes_to_select)}")
                                    else:
                                        # If JS click didn't work, try regular click
                                        try:
                                            checkbox.click()
                                            if checkbox.is_selected():
                                                selected_count += 1
                                        except Exception as click_error:
                                            logger.warning(f"Could not click checkbox {j+1}: {click_error}")
                                else:
                                    selected_count += 1  # Already selected
                                    
                            except (StaleElementReferenceException, ElementNotInteractableException) as e:
                                logger.warning(f"Error selecting checkbox {j+1}: {e}")
                                continue
                        
                        if selected_count > 0:
                            logger.info(f"Successfully selected {selected_count} records using selector: {selector}")
                            return selected_count
                    
            except TimeoutException:
                logger.debug(f"Timeout with selector: {selector}")
                continue
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        # If we found checkboxes but couldn't select any, provide debug info
        if found_checkboxes and selected_count == 0:
            logger.error("Found checkboxes but could not select any. Taking screenshot for debugging.")
            screenshot_path = os.path.join(self.screenshots_dir, f"checkbox_selection_failed_{int(time.time())}.png")
            self.driver.save_screenshot(screenshot_path)
            logger.error(f"Debug screenshot saved to: {screenshot_path}")
            
            # Try to get page source for debugging
            try:
                page_source_path = os.path.join(self.screenshots_dir, f"page_source_{int(time.time())}.html")
                with open(page_source_path, 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                logger.error(f"Page source saved to: {page_source_path}")
            except Exception as e:
                logger.warning(f"Could not save page source: {e}")
        
        if selected_count == 0:
            logger.warning("No selectable records found on this page with any selector.")
        
        return selected_count

    def navigate_to_next_page(self):
        """Automatically navigate to the next page."""
        logger.info("Attempting to navigate to next page...")
        time.sleep(1)
        
        # Expanded selectors for next page navigation
        next_page_selectors = [
            "//a[contains(text(), 'Next') and not(contains(@class, 'disabled'))]",
            "//a[contains(., 'Next') and not(contains(@class, 'disabled'))]",
            "//button[contains(text(), 'Next') and not(@disabled)]",
            "//button[contains(., 'Next') and not(@disabled)]",
            "//a[contains(@class, 'next') and not(contains(@class, 'disabled'))]",
            "//li[contains(@class, 'next') and not(contains(@class, 'disabled'))]/a",
            "//a[@title='Next Page' and not(contains(@class, 'disabled'))]",
            "//a[@aria-label='Next page' and not(contains(@class, 'disabled'))]",
            "//a[.//span[contains(text(),'Next')]]",
            "//div[contains(@class, 'pagination')]//a[contains(text(), 'Next')]",
            "//a[contains(text(), '›')]",
            "//a[contains(text(), '»')]"
        ]

        for selector in next_page_selectors:
            try:
                next_button = self.driver.find_element(By.XPATH, selector)
                if next_button.is_displayed() and next_button.is_enabled():
                    current_url = self.driver.current_url
                    self.driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(3) # Wait for page to load
                    if self.driver.current_url != current_url:
                        logger.info(f"Successfully navigated to next page using selector: {selector}")
                        return True
            except (NoSuchElementException, ElementNotInteractableException):
                continue
        
        logger.warning("Could not find or click the 'Next' page button.")
        return False

    def navigate_to_download_page(self):
        """Navigate to the download page after selections are made - improved for Reference USA."""
        logger.info("Looking for Download link...")
        
        # Extended selectors for Reference USA download navigation
        download_selectors = [
            # Original selectors
            "//a[contains(text(), 'Download') and not(contains(text(), 'Download Records'))]",
            "//a[contains(@class, 'download')]",
            
            # Reference USA specific selectors
            "//a[contains(text(), 'Download')]",
            "//button[contains(text(), 'Download')]",
            "//input[@type='button' and contains(@value, 'Download')]",
            "//input[@type='submit' and contains(@value, 'Download')]",
            
            # Link with download in href or class
            "//a[contains(@href, 'download')]",
            "//a[contains(@class, 'btn') and contains(text(), 'Download')]",
            
            # Menu or navigation items
            "//li//a[contains(text(), 'Download')]",
            "//div[contains(@class, 'menu')]//a[contains(text(), 'Download')]",
            
            # Action buttons
            "//div[contains(@class, 'action')]//a[contains(text(), 'Download')]",
            "//div[contains(@class, 'button')]//a[contains(text(), 'Download')]",
        ]
        
        for i, selector in enumerate(download_selectors):
            try:
                logger.info(f"Trying download navigation selector {i+1}: {selector}")
                download_link = self.driver.find_element(By.XPATH, selector)
                
                if download_link.is_displayed() and download_link.is_enabled():
                    current_url = self.driver.current_url
                    logger.info(f"Found download link: {download_link.text}")
                    
                    # Scroll into view and click
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_link)
                    time.sleep(1)
                    self.driver.execute_script("arguments[0].click();", download_link)
                    time.sleep(3)
                    
                    # Check if URL changed or new content loaded
                    if self.driver.current_url != current_url or self.check_for_download_page_content():
                        logger.info("Successfully navigated to download page.")
                        return True
                        
            except (NoSuchElementException, ElementNotInteractableException) as e:
                logger.debug(f"Selector {i+1} failed: {e}")
                continue
            except Exception as e:
                logger.warning(f"Unexpected error with selector {i+1}: {e}")
                continue
        
        # If no download link found, check if we're already on download page
        if self.check_for_download_page_content():
            logger.info("Already on download page or download content is visible.")
            return True
        
        logger.warning("Could not find or click any 'Download' link to get to the download page.")
        return False

    def check_for_download_page_content(self):
        """Check if download page content is visible"""
        download_page_indicators = [
            "//input[@type='button' and contains(@value, 'DOWNLOAD')]",
            "//button[contains(text(), 'DOWNLOAD')]",
            "//a[contains(text(), 'DOWNLOAD RECORDS')]",
            "//form[contains(@action, 'download')]",
            "//div[contains(@class, 'download')]",
            "//h1[contains(text(), 'Download')]",
            "//h2[contains(text(), 'Download')]",
            "//span[contains(text(), 'Download Records')]"
        ]
        
        for selector in download_page_indicators:
            try:
                if self.driver.find_element(By.XPATH, selector):
                    return True
            except NoSuchElementException:
                continue
        return False

    def check_for_results_page(self):
        """Check if we're on a results page with selectable records"""
        results_indicators = [
            "//input[@type='checkbox']",
            "//table//tr[position()>1]",  # Table with data rows
            "//div[contains(@class, 'results')]",
            "//span[contains(text(), 'Results')]",
            "//div[contains(text(), 'Results')]",
            "//table[contains(@class, 'data') or contains(@class, 'results')]"
        ]
        
        for selector in results_indicators:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                if len(elements) > 0:
                    return True
            except:
                continue
        return False

    def click_download_button(self):
        """Find and click the Download Records button - improved for Reference USA."""
        logger.info("Attempting to find and click Download Records button...")
        time.sleep(2)
        
        # Extended selectors for download buttons
        download_button_selectors = [
            # Original selectors
            "//a[contains(@class, 'action-download')]",
            "//input[@type='button' and contains(@value, 'DOWNLOAD RECORDS')]",
            "//button[contains(text(), 'DOWNLOAD RECORDS')]",
            
            # More generic download button selectors
            "//input[@type='button' and contains(@value, 'DOWNLOAD')]",
            "//input[@type='submit' and contains(@value, 'DOWNLOAD')]",
            "//button[contains(text(), 'DOWNLOAD')]",
            "//a[contains(text(), 'DOWNLOAD')]",
            
            # Case variations
            "//input[@type='button' and contains(@value, 'Download')]",
            "//button[contains(text(), 'Download')]",
            "//a[contains(text(), 'Download')]",
            
            # With specific classes or IDs
            "//button[contains(@class, 'download')]",
            "//input[contains(@class, 'download')]",
            "//a[contains(@class, 'download-btn')]",
            "//button[contains(@id, 'download')]",
            
            # Form submit buttons
            "//form//input[@type='submit']",
            "//form//button[@type='submit']",
            
            # Action buttons
            "//div[contains(@class, 'action')]//button",
            "//div[contains(@class, 'action')]//input[@type='button']",
            
            # Export buttons (alternative terminology)
            "//button[contains(text(), 'Export')]",
            "//input[@type='button' and contains(@value, 'Export')]",
            "//a[contains(text(), 'Export')]",
        ]
        
        for i, selector in enumerate(download_button_selectors):
            try:
                logger.info(f"Trying download button selector {i+1}: {selector}")
                element = self.driver.find_element(By.XPATH, selector)
                
                if element.is_displayed() and element.is_enabled():
                    button_text = element.text or element.get_attribute('value') or 'Unknown'
                    logger.info(f"Found download button: '{button_text}'")
                    
                    # Scroll into view and click
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", element)
                    logger.info("Successfully clicked download button.")
                    return True
                    
            except (NoSuchElementException, ElementNotInteractableException) as e:
                logger.debug(f"Download button selector {i+1} failed: {e}")
                continue
            except Exception as e:
                logger.warning(f"Unexpected error with download button selector {i+1}: {e}")
                continue
        
        # Take screenshot for debugging
        screenshot_path = os.path.join(self.screenshots_dir, f"download_button_not_found_{int(time.time())}.png")
        self.driver.save_screenshot(screenshot_path)
        logger.error(f"Download button not found. Screenshot saved to: {screenshot_path}")
        
        # Save page source for debugging
        try:
            page_source_path = os.path.join(self.screenshots_dir, f"download_page_source_{int(time.time())}.html")
            with open(page_source_path, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            logger.error(f"Page source saved to: {page_source_path}")
        except Exception as e:
            logger.warning(f"Could not save page source: {e}")
        
        return False

    def wait_for_download_complete(self, timeout=120):
        """Wait for a new file to appear and finish downloading - improved monitoring."""
        logger.info("Waiting for download to complete...")
        initial_files = set(os.listdir(self.download_dir))
        start_time = time.time()
        last_log_time = start_time
        
        while time.time() - start_time < timeout:
            current_files = set(os.listdir(self.download_dir))
            new_files = current_files - initial_files
            
            # Check for completed downloads
            for file in new_files:
                if not file.endswith(('.crdownload', '.tmp', '.part')):
                    file_path = os.path.join(self.download_dir, file)
                    
                    # Wait a bit more to ensure file is completely written
                    time.sleep(2)
                    
                    # Verify file exists and has content
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                        self.downloaded_files.append(file_path)
                        logger.info(f"Download completed: {file} ({os.path.getsize(file_path)} bytes)")
                        return True
            
            # Check for in-progress downloads
            in_progress_files = [f for f in new_files if f.endswith(('.crdownload', '.tmp', '.part'))]
            if in_progress_files:
                logger.info(f"Download in progress: {in_progress_files}")
            
            # Log status every 10 seconds
            if time.time() - last_log_time > 10:
                elapsed = int(time.time() - start_time)
                logger.info(f"Still waiting for download... ({elapsed}s elapsed)")
                last_log_time = time.time()
            
            time.sleep(1)
            
        logger.warning(f"Download timeout after {timeout} seconds - no new files detected.")
        
        # Show what files are in the directory for debugging
        current_files = os.listdir(self.download_dir)
        logger.info(f"Files currently in download directory: {current_files}")
        
        return False

    def merge_csv_files(self):
        """ENHANCED: Merge CSV files - now works with all files in downloads folder"""
        try:
            # If no downloaded files from current session, get all CSV files from downloads folder
            if not self.downloaded_files:
                csv_files = self.get_all_csv_files_in_downloads()
            else:
                # For current session, still use downloaded files but also offer to include existing files
                current_session_csv = [f for f in self.downloaded_files if f.endswith('.csv')]
                all_csv_files = self.get_all_csv_files_in_downloads()
                
                # Find files that exist but weren't downloaded in this session
                existing_files = [f for f in all_csv_files if f not in current_session_csv]
                
                if existing_files:
                    logger.info(f"\nFound {len(existing_files)} existing CSV files in downloads folder:")
                    for file_path in existing_files:
                        logger.info(f"  - {os.path.basename(file_path)}")
                    
                    include_existing = input("\nInclude existing files in merge? (y/n): ").strip().lower()
                    if include_existing == 'y':
                        csv_files = current_session_csv + existing_files
                    else:
                        csv_files = current_session_csv
                else:
                    csv_files = current_session_csv
            
            if len(csv_files) < 2:
                logger.info("Less than 2 CSV files found, no merge needed.")
                return
            
            logger.info(f"Merging {len(csv_files)} CSV files...")
            
            merged_data = []
            total_rows = 0
            for csv_file in csv_files:
                try:
                    df = pd.read_csv(csv_file)
                    merged_data.append(df)
                    total_rows += len(df)
                    logger.info(f"Added {len(df)} rows from {os.path.basename(csv_file)}")
                except Exception as e:
                    logger.warning(f"Could not read {csv_file}: {e}")
            
            if merged_data:
                combined_df = pd.concat(merged_data, ignore_index=True)
                
                # Remove duplicates if any
                initial_count = len(combined_df)
                combined_df = combined_df.drop_duplicates()
                final_count = len(combined_df)
                
                if initial_count != final_count:
                    logger.info(f"Removed {initial_count - final_count} duplicate records")
                
                # Save merged file
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                merged_filename = f"merged_data_{timestamp}.csv"
                merged_path = os.path.join(self.download_dir, merged_filename)
                
                combined_df.to_csv(merged_path, index=False)
                logger.info(f"Merged file saved as: {merged_filename}")
                logger.info(f"Total records in merged file: {len(combined_df)}")
                logger.info(f"Merged file location: {merged_path}")
            
        except Exception as e:
            logger.error(f"Error merging CSV files: {e}")

    def run_workflow(self, url):
        """ENHANCED: Main workflow runner with CSV merge options."""
        try:
            # NEW: Get initial user options
            initial_choice = self.get_initial_options()
            
            if initial_choice == 'merge_only':
                # Just do CSV merge and exit
                self.standalone_csv_merge()
                return
            elif initial_choice == 'merge_then_scrape':
                # Do CSV merge first, then continue with scraping
                self.standalone_csv_merge()
                logger.info("\nNow continuing with data scraping...")
            # If initial_choice == 'scrape', just continue with normal scraping
            
            self.setup_driver()
            self.driver.get(url)
            logger.info("\n" + "="*80)
            logger.info("INITIAL SETUP: Please login, perform your search, and navigate to the first page of results.")
            input("Press Enter when ready...")
            
            self.get_automation_mode()
            self.get_page_limits()  # Get user-defined page limits
            
            # Add option for debugging
            debug_choice = input("\nWould you like to enable debug mode? (y/n): ").strip().lower()
            enable_debug = debug_choice == 'y'
            
            if enable_debug:
                self.debug_page_structure()
            
            # Initialize file tracking
            self._last_files = set(os.listdir(self.download_dir))
            
            self.pages_per_batch = 10 
            batch_number = 1
            consecutive_failures = 0
            max_consecutive_failures = 3
            
            # Use user-defined page limit instead of hardcoded max_downloads
            while self.pages_downloaded < self.max_pages_to_download:
                logger.info(f"\n--- STARTING BATCH {batch_number} ---")
                total_selected_in_batch = 0
                
                for i in range(self.pages_per_batch):
                    page_in_batch = i + 1
                    logger.info(f"Processing Page {self.current_page} (Batch {batch_number}, Page {page_in_batch}/{self.pages_per_batch})")
                    
                    # Try automatic selection first (now with Select All enhancement)
                    selected = self.auto_select_pages()
                    
                    # If automatic selection fails, offer manual selection
                    if selected == 0:
                        logger.warning("Automatic selection failed.")
                        
                        if enable_debug:
                            self.debug_page_structure()
                        
                        retry_choice = input("Would you like to:\n1. Try manual selection\n2. Skip this page\n3. Stop scraping\nEnter choice (1-3): ").strip()
                        
                        if retry_choice == '1':
                            selected = self.manual_checkbox_selection()
                        elif retry_choice == '2':
                            logger.info("Skipping this page.")
                            consecutive_failures += 1
                            if consecutive_failures >= max_consecutive_failures:
                                logger.warning(f"Too many consecutive failures ({consecutive_failures}). Stopping.")
                                break
                            continue
                        else:
                            logger.info("Stopping scraper as requested.")
                            break
                    
                    if selected == 0:
                        logger.info("No records selected. Assuming end of results or continuing to next page.")
                        consecutive_failures += 1
                        if consecutive_failures >= max_consecutive_failures:
                            logger.warning(f"Too many consecutive failures ({consecutive_failures}). Stopping batch.")
                            break
                    else:
                        consecutive_failures = 0  # Reset failure counter
                        total_selected_in_batch += selected
                    
                    # Navigate to next page if not the last page in batch
                    if i < self.pages_per_batch - 1:
                        if self.automation_mode == 'full':
                            if not self.navigate_to_next_page():
                                logger.info("Could not find next page. Ending batch.")
                                break
                        else:  # semi-auto
                            next_page_choice = input("Navigate to next page? (y/n/stop): ").strip().lower()
                            if next_page_choice == 'stop':
                                break
                            elif next_page_choice == 'n':
                                logger.info("Staying on current page, ending batch.")
                                break
                            else:
                                input("Please navigate to the next page manually and press Enter...")
                        self.current_page += 1

                # Process downloads if we have selections
                if total_selected_in_batch > 0:
                    logger.info(f"Batch complete. Total selected: {total_selected_in_batch}. Proceeding to download.")
                    
                    # ALWAYS try automatic navigation to download page first
                    logger.info("Attempting automatic navigation to download page...")
                    download_page_success = self.navigate_to_download_page()
                    
                    if download_page_success:
                        logger.info("Successfully navigated to download page automatically.")
                    else:
                        logger.warning("Automatic navigation to download page failed.")
                        if enable_debug:
                            self.debug_download_workflow()
                        
                        # Always ask user to do it manually if auto fails
                        logger.info("Please navigate to the download page manually.")
                        input("Navigate to the DOWNLOAD page manually and press Enter when ready...")
                        download_page_success = True  # Assume user did it correctly
                    
                    # Step 2: Click download button
                    download_button_success = self.click_download_button()
                    if not download_button_success:
                        logger.warning("Could not click download button automatically.")
                        if enable_debug:
                            self.debug_download_workflow()
                        
                        # Offer manual download assistance
                        manual_choice = input("Would you like to:\n1. Try manual download\n2. Skip this batch\nEnter choice (1-2): ").strip()
                        
                        if manual_choice == '1':
                            download_button_success = self.manual_download_assistance()
                        else:
                            logger.info("Skipping this batch.")
                            continue
                    
                    # Step 3: Wait for download to complete
                    if download_button_success:
                        download_complete = self.wait_for_download_complete()
                        
                        if not download_complete:
                            logger.warning("Download did not complete automatically.")
                            
                            # Check if user completed download manually
                            manual_complete = input("Did you complete the download manually? (y/n): ").strip().lower()
                            if manual_complete == 'y':
                                download_complete = True
                                # Try to detect the downloaded file
                                current_files = set(os.listdir(self.download_dir))
                                new_files = current_files - self._last_files
                                for file in new_files:
                                    if not file.endswith(('.crdownload', '.tmp', '.part')):
                                        file_path = os.path.join(self.download_dir, file)
                                        self.downloaded_files.append(file_path)
                                        logger.info(f"Manual download detected: {file}")
                                self._last_files = current_files
                        
                        if download_complete:
                            self.pages_downloaded += page_in_batch
                            logger.info(f"Batch {batch_number} download complete. Total pages downloaded so far: {self.pages_downloaded}")
                            
                            # Check against user-defined limit
                            if self.pages_downloaded >= self.max_pages_to_download:
                                logger.info(f"Reached user-defined page limit of {self.max_pages_to_download} pages.")
                                break
                            
                            # Prepare for next batch
                            logger.info("Preparing for next batch.")
                            
                            # Navigate back to results
                            back_success = False
                            if self.automation_mode == 'full':
                                try:
                                    # Try to go back to results page
                                    logger.info("Attempting to navigate back to results...")
                                    self.driver.back()  # Go back to download page
                                    time.sleep(2)
                                    self.driver.back()  # Go back to results
                                    time.sleep(3)
                                    
                                    # Verify we're back on results page
                                    if self.check_for_results_page():
                                        back_success = True
                                        logger.info("Successfully navigated back to results page.")
                                    else:
                                        logger.warning("Auto-navigation back may have failed.")
                                        
                                except Exception as e:
                                    logger.warning(f"Auto-navigation back failed: {e}")
                            
                            if not back_success:
                                input("Please navigate back to the search results page and press Enter...")
                            
                            self.current_page += 1
                        else:
                            logger.error("Download failed to complete. Stopping.")
                            break
                    else:
                        logger.error("Could not initiate download. Stopping.")
                        break
                else:
                    logger.info("No records selected in this batch. Ending session.")
                    break
                
                batch_number += 1

            # ENHANCED Final summary with improved CSV merge options
            logger.info("\n" + "="*80)
            logger.info("DOWNLOAD SUMMARY")
            logger.info(f"Total pages downloaded: {self.pages_downloaded}")
            logger.info(f"User-defined limit: {self.max_pages_to_download}")
            logger.info(f"Files saved to: {self.download_dir}")
            
            if self.downloaded_files:
                logger.info("Downloaded files this session:")
                for file_path in self.downloaded_files:
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    logger.info(f"  - {os.path.basename(file_path)} ({file_size} bytes)")
            else:
                logger.warning("No files were downloaded this session.")
            
            # ENHANCED: Offer to merge ALL CSV files in downloads folder, not just current session
            all_csv_files = self.get_all_csv_files_in_downloads()
            current_session_csv = [f for f in self.downloaded_files if f.endswith('.csv')]
            
            if len(all_csv_files) > 1:
                logger.info(f"\nTotal CSV files in downloads folder: {len(all_csv_files)}")
                if len(current_session_csv) > 0:
                    logger.info(f"Downloaded this session: {len(current_session_csv)}")
                    logger.info(f"Existing files: {len(all_csv_files) - len(current_session_csv)}")
                
                merge_choice = input(f"\nWould you like to merge all {len(all_csv_files)} CSV files into one? (y/n): ").strip().lower()
                if merge_choice == 'y':
                    # Temporarily set all CSV files for merging
                    original_downloaded = self.downloaded_files.copy()
                    self.downloaded_files = all_csv_files
                    self.merge_csv_files()
                    self.downloaded_files = original_downloaded
            elif len(current_session_csv) > 1:
                merge_choice = input(f"\nWould you like to merge {len(current_session_csv)} CSV files from this session? (y/n): ").strip().lower()
                if merge_choice == 'y':
                    self.merge_csv_files()
            
            logger.info("="*80)

        except Exception as e:
            logger.error(f"An error occurred in the workflow: {e}")
            import traceback
            traceback.print_exc()
            
            # Save debug info on error
            try:
                screenshot_path = os.path.join(self.screenshots_dir, f"error_screenshot_{int(time.time())}.png")
                self.driver.save_screenshot(screenshot_path)
                logger.info(f"Error screenshot saved to: {screenshot_path}")
            except:
                pass
                
        finally:
            if self.driver:
                input("\nPress Enter to close browser...")
                self.driver.quit()

def main():
    """Main entry point"""
    scraper = Miller3DataScraper()
    url = "https://referenceusa.com.us1.proxy.openathens.net/"
    scraper.run_workflow(url)

if __name__ == "__main__":
    main()