#!/usr/bin/env python3
"""
Miller 3 Data Scraper - Enhanced Version with Fixes
Features:
- Semi-automated workflow (manual pagination)
- Fully automated workflow (automatic pagination)
- Uses default filename from website (no naming prompt)
- Processes pages in batches of 10
- CSV merge functionality
- Respects 1000 page download limit per search
- Handles various result volumes and search types
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
        
        # --- MODIFIED SECTION: START ---
        # Set up separate directories for downloads and screenshots
        self.download_dir = download_dir or os.path.join(script_dir, 'Downloads')
        self.screenshots_dir = os.path.join(script_dir, 'Screenshots')

        # Create directories if they don't exist
        for directory in [self.download_dir, self.screenshots_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")
        # --- MODIFIED SECTION: END ---

        self.driver = None
        self.wait = None
        self.download_count = 0
        self.batch_size = 10
        self.max_downloads = 1000
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

    def auto_select_pages(self, max_records=None):
        """Automatically select records on the current page."""
        if max_records is None:
            logger.info("Attempting to auto-select ALL records on the current page...")
        else:
            logger.info(f"Attempting to auto-select up to {max_records} records...")
        
        time.sleep(2)
        checkbox_selectors = [
            "//input[@type='checkbox' and @name='recordId']",
            "//table[@id='searchResultsTable']//tbody//input[@type='checkbox']"
        ]
        
        selected_count = 0
        for selector in checkbox_selectors:
            try:
                checkboxes = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, selector)))
                if not checkboxes: continue

                valid_checkboxes = [cb for cb in checkboxes if cb.is_displayed() and cb.is_enabled()]
                checkboxes_to_select = valid_checkboxes if max_records is None else valid_checkboxes[:max_records]
                
                for checkbox in checkboxes_to_select:
                    if not checkbox.is_selected():
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                        time.sleep(0.3)
                        self.driver.execute_script("arguments[0].click();", checkbox)
                        selected_count += 1
                
                if selected_count > 0:
                    logger.info(f"Successfully selected {selected_count} records.")
                    return selected_count
            except TimeoutException:
                continue
        logger.warning("No selectable records found on this page.")
        return 0

    def navigate_to_next_page(self):
        """Automatically navigate to the next page."""
        logger.info("Attempting to navigate to next page...")
        time.sleep(1)
        
        # --- MODIFIED SECTION: START (Expanded Selectors) ---
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
        # --- MODIFIED SECTION: END ---

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

    def click_download_button(self):
        """Find and click the Download Records button."""
        logger.info("Attempting to find and click Download Records button...")
        time.sleep(2)
        selectors = [
            "//a[contains(@class, 'action-download')]",
            "//input[@type='button' and contains(@value, 'DOWNLOAD RECORDS')]",
            "//button[contains(text(), 'DOWNLOAD RECORDS')]"
        ]
        for selector in selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                if element.is_displayed() and element.is_enabled():
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", element)
                    logger.info("Successfully clicked download button.")
                    return True
            except (NoSuchElementException, ElementNotInteractableException):
                continue
        
        # --- MODIFIED SECTION: START (Screenshot Path) ---
        screenshot_path = os.path.join(self.screenshots_dir, f"download_button_not_found_{int(time.time())}.png")
        # --- MODIFIED SECTION: END ---
        self.driver.save_screenshot(screenshot_path)
        logger.error(f"Download button not found. Screenshot saved to: {screenshot_path}")
        return False

    def wait_for_download_complete(self):
        """Wait for a new file to appear and finish downloading."""
        logger.info("Waiting for download to complete...")
        initial_files = set(os.listdir(self.download_dir))
        start_time = time.time()
        
        while time.time() - start_time < 120:
            current_files = set(os.listdir(self.download_dir))
            new_files = current_files - initial_files
            
            for file in new_files:
                if not file.endswith(('.crdownload', '.tmp')):
                    file_path = os.path.join(self.download_dir, file)
                    time.sleep(1) # Extra second to ensure write is finished
                    self.downloaded_files.append(file_path)
                    logger.info(f"Download completed: {file}")
                    return True
            time.sleep(1)
            
        logger.warning("Download timeout - no new files detected.")
        return False

    def navigate_to_download_page(self):
        """Navigate to the download page after selections are made."""
        logger.info("Looking for Download link...")
        selectors = [
            "//a[contains(text(), 'Download') and not(contains(text(), 'Download Records'))]",
            "//a[contains(@class, 'download')]"
        ]
        for selector in selectors:
            try:
                download_link = self.driver.find_element(By.XPATH, selector)
                if download_link.is_displayed() and download_link.is_enabled():
                    current_url = self.driver.current_url
                    self.driver.execute_script("arguments[0].click();", download_link)
                    time.sleep(3)
                    if self.driver.current_url != current_url:
                        logger.info("Successfully navigated to download page.")
                        return True
            except (NoSuchElementException, ElementNotInteractableException):
                continue
        logger.warning("Could not find or click the 'Download' link to get to the download page.")
        return False

    def run_workflow(self, url):
        """Main workflow runner."""
        try:
            self.setup_driver()
            self.driver.get(url)
            logger.info("\n" + "="*80)
            logger.info("INITIAL SETUP: Please login, perform your search, and navigate to the first page of results.")
            input("Press Enter when ready...")
            
            self.get_automation_mode()
            
            # Simplified logic for this test
            self.pages_per_batch = 10 
            
            batch_number = 1
            while self.pages_downloaded < self.max_downloads:
                logger.info(f"\n--- STARTING BATCH {batch_number} ---")
                total_selected_in_batch = 0
                
                for i in range(self.pages_per_batch):
                    page_in_batch = i + 1
                    logger.info(f"Processing Page {self.current_page} (Batch {batch_number}, Page {page_in_batch}/{self.pages_per_batch})")
                    
                    selected = self.auto_select_pages()
                    if selected == 0:
                        logger.info("No records selected. Assuming end of results.")
                        break 
                    
                    total_selected_in_batch += selected
                    
                    if i < self.pages_per_batch - 1:
                        if self.automation_mode == 'full':
                            if not self.navigate_to_next_page():
                                logger.info("Could not find next page. Ending batch.")
                                break
                        else: # semi-auto
                            input("Please navigate to the next page manually and press Enter...")
                        self.current_page += 1

                if total_selected_in_batch > 0:
                    logger.info(f"Batch complete. Total selected: {total_selected_in_batch}. Proceeding to download.")
                    
                    if self.automation_mode == 'full':
                        if not self.navigate_to_download_page():
                            input("Could not navigate to download page automatically. Please do so manually and press Enter.")
                    else: # semi-auto
                        input("Please navigate to the DOWNLOAD page manually and press Enter...")
                        
                    if self.click_download_button():
                        if self.wait_for_download_complete():
                            self.pages_downloaded += page_in_batch
                            logger.info(f"Batch {batch_number} download complete. Total pages downloaded so far: {self.pages_downloaded}")
                            if self.pages_downloaded >= self.max_downloads:
                                logger.info("Max download limit reached.")
                                break
                            
                            logger.info("Preparing for next batch. Please navigate back to search results.")
                            if self.automation_mode == 'full':
                                self.driver.back() # Go back to download page
                                time.sleep(2)
                                self.driver.back() # Go back to results
                                time.sleep(2)
                                self.current_page += 1
                            else: # semi-auto
                                input("Press Enter when you are back on the results page, ready for the next batch...")
                                self.current_page +=1
                        else:
                            logger.error("Download failed to complete. Stopping.")
                            break
                    else:
                        logger.error("Could not click download button. Stopping.")
                        break
                else:
                    logger.info("No records selected in this batch. Ending session.")
                    break
                
                batch_number += 1

            logger.info("\n" + "="*80)
            logger.info("DOWNLOAD SUMMARY")
            logger.info(f"Total pages downloaded: {self.pages_downloaded}")
            logger.info(f"Files saved to: {self.download_dir}")
            logger.info("="*80)

        except Exception as e:
            logger.error(f"An error occurred in the workflow: {e}")
            import traceback
            traceback.print_exc()
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
