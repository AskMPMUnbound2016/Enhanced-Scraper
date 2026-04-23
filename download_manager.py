import time
import random
import datetime
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from logging_manager import get_logger

class DownloadManager:
    def __init__(self, browser_manager, state_manager, search_parameters):
        self.browser = browser_manager
        self.state = state_manager
        self.search_parameters = search_parameters
        self.pages_per_batch = search_parameters.get('pages_per_batch', 10)
        self.logger = get_logger()
    
    def navigate_to_page(self, page_num):
        """Navigate to a specific page of results"""
        try:
            # Take a screenshot before navigation
            try:
                self.logger.save_screenshot(f"before_page_nav_{page_num}", self.browser.driver, f"Navigating to page {page_num}")
            except Exception as e:
                print(f"Failed to save screenshot: {str(e)}")
                
            # Make sure we're on the results page
            if self.state.state["results_url"] and ("Result" in self.state.state["results_url"] or "result" in self.state.state["results_url"]):
                current_url = self.browser.driver.current_url
                if "Result" not in current_url and "result" not in current_url:
                    print("Navigating back to results page...")
                    self.browser.navigate(self.state.state["results_url"])
                    time.sleep(random.uniform(3, 5))
            
            # Find the page input field
            page_inputs = self.browser.find_elements(By.XPATH, 
                "//input[@type='text' and (contains(@class, 'page') or parent::*[contains(@class, 'pagination')])]")
            
            if page_inputs:
                # Clear the field and enter the page number
                page_inputs[0].clear()
                page_inputs[0].send_keys(str(page_num))
                page_inputs[0].send_keys(Keys.ENTER)  # Enter key
                self.logger.log_page_navigation(page_num, True)
                time.sleep(random.uniform(3, 5))
            else:
                # Try alternative pagination approaches
                print("Standard page input field not found. Trying alternatives...")
                
                # Try clicking directly on page number links
                page_links = self.browser.find_elements(By.XPATH, 
                    f"//a[contains(text(), '{page_num}') and ancestor::*[contains(@class, 'pagination')]]")
                
                if page_links:
                    page_links[0].click()
                    print(f"Clicked on page number {page_num}")
                    time.sleep(random.uniform(3, 5))
                else:
                    # Try next/previous buttons
                    current_page_elements = self.browser.find_elements(By.XPATH,
                        "//span[contains(@class, 'current') and parent::*[contains(@class, 'pagination')]]")
                    
                    if current_page_elements:
                        current_page = int(current_page_elements[0].text.strip())
                        print(f"Current page identified as {current_page}")
                        
                        if page_num > current_page:
                            # Need to go forward
                            steps = page_num - current_page
                            print(f"Clicking Next button {steps} times...")
                            
                            next_buttons = self.browser.find_elements(By.XPATH,
                                "//a[contains(text(), 'Next') or contains(@class, 'next')] | //button[contains(text(), 'Next')]")
                            
                            if next_buttons:
                                for i in range(steps):
                                    next_buttons[0].click()
                                    print(f"Clicked Next button ({i+1}/{steps})")
                                    time.sleep(random.uniform(2, 4))
                            else:
                                print("Next button not found")
                                print(f"Please navigate to page {page_num} manually")
                                input(f"Press Enter after navigating to page {page_num}...")
                        elif page_num < current_page:
                            # Need to go backward
                            steps = current_page - page_num
                            print(f"Clicking Previous button {steps} times...")
                            
                            prev_buttons = self.browser.find_elements(By.XPATH,
                                "//a[contains(text(), 'Prev') or contains(@class, 'prev')] | //button[contains(text(), 'Prev')]")
                            
                            if prev_buttons:
                                for i in range(steps):
                                    prev_buttons[0].click()
                                    print(f"Clicked Previous button ({i+1}/{steps})")
                                    time.sleep(random.uniform(2, 4))
                            else:
                                print("Previous button not found")
                                print(f"Please navigate to page {page_num} manually")
                                input(f"Press Enter after navigating to page {page_num}...")
                    else:
                        print("Current page indicator not found")
                        print(f"Please navigate to page {page_num} manually")
                        input(f"Press Enter after navigating to page {page_num}...")
            
            return True
        
        except Exception as e:
            print(f"Navigation error: {str(e)}")
            print(f"Please navigate to page {page_num} manually")
            input(f"Press Enter after navigating to page {page_num}...")
            return True
    
    def handle_manual_download_intervention(self, batch_num, intervention_type="general"):
        """Comprehensive manual intervention handler for download issues"""
        print(f"\n🔧 Manual Intervention Required - {intervention_type}")
        print("=" * 60)
        
        # Log the intervention
        self.logger.log_manual_intervention(f"{intervention_type} - user intervention required")
        
        # Prompt for download path change
        new_download_path = self.prompt_manual_download_path(batch_num)
        
        if new_download_path:
            # Generate expected filename
            state_name = self.search_parameters.get('state', 'State')
            timestamp = datetime.datetime.now().strftime('%d%m%y_%H%M')
            start_page = (batch_num - 1) * self.pages_per_batch + 1
            end_page = start_page + self.pages_per_batch - 1
            expected_filename = f"{state_name}_{start_page}to{end_page}_{timestamp}.csv"
            expected_full_path = os.path.join(new_download_path, expected_filename)
            
            print(f"\n📁 Save Location Instructions:")
            print(f"   Directory: {new_download_path}")
            print(f"   Filename: {expected_filename}")
            print(f"   Full Path: {expected_full_path}")
            print("\n📆 Important: Please save the file to this exact location!")
            
            return new_download_path
        else:
            print("\n📁 Using current download directory")
            return None
    
    def prompt_manual_download_path(self, current_batch):
        """Prompt user to change download path during manual intervention"""
        print("\n📁 Download Path Options During Manual Process")
        print("=" * 50)
        
        current_download_dir = getattr(self.browser, 'download_dir', 'Unknown')
        print(f"Current download directory: {current_download_dir}")
        
        print("\nWould you like to:")
        print("1. Continue with current download directory")
        print("2. Change download directory for remaining batches")
        print("3. Use browser's default Downloads folder")
        print("4. Specify one-time download location for this batch")
        
        while True:
            choice = input("\nChoose option (1-4): ").strip()
            
            if choice == "1":
                print(f"✅ Continuing with: {current_download_dir}")
                return None
                
            elif choice == "2":
                new_path = input("Enter new download directory path: ").strip()
                if new_path:
                    new_path = os.path.expanduser(new_path)
                    if os.path.isdir(new_path) or self.create_directory_if_needed(new_path):
                        print(f"✅ Changed download directory to: {new_path}")
                        # Update browser manager's download directory
                        if hasattr(self.browser, 'download_dir'):
                            self.browser.download_dir = new_path
                        self.logger.session_logger.info(f"📁 Download directory changed to: {new_path}")
                        return new_path
                    else:
                        print("❌ Invalid directory, using current location")
                        return None
                else:
                    print("❌ No path entered, using current location")
                    return None
                    
            elif choice == "3":
                default_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
                print(f"✅ Using browser default: {default_downloads}")
                self.logger.session_logger.info(f"📁 Switched to browser default downloads: {default_downloads}")
                return default_downloads
                
            elif choice == "4":
                temp_path = input("Enter temporary download path for this batch: ").strip()
                if temp_path:
                    temp_path = os.path.expanduser(temp_path)
                    if os.path.isdir(temp_path) or self.create_directory_if_needed(temp_path):
                        print(f"✅ Using temporary location: {temp_path}")
                        print("⚠️ Note: This is only for the current batch")
                        self.logger.session_logger.info(f"📁 Temporary download location for batch {current_batch}: {temp_path}")
                        return temp_path
                    else:
                        print("❌ Invalid directory, using current location")
                        return None
                else:
                    print("❌ No path entered, using current location")
                    return None
            else:
                print("❌ Invalid choice. Please enter 1-4")
                continue
    
    def create_directory_if_needed(self, path):
        """Create directory if it doesn't exist"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            print(f"❌ Cannot create directory {path}: {e}")
            return False
    
    def clear_all_selections(self):
        """Clear all currently selected records before making new selections"""
        try:
            self.logger.debug_logger.info("🧹 Clearing all previous selections...")
            cleared_count = 0
            
            # Strategy 1: Find and uncheck the "select all" checkbox if it's checked
            select_all_checkboxes = self.browser.find_elements(By.XPATH,
                "//th//input[@type='checkbox'] | //th[contains(@class, 'checkbox')]//input")
            
            if select_all_checkboxes:
                for checkbox in select_all_checkboxes:
                    if checkbox.is_selected():
                        checkbox.click()
                        cleared_count += 1
                        time.sleep(0.5)
                        self.logger.log_selection_clearing(cleared_count)
                        return True
            
            # Strategy 2: Find and uncheck individual selected records
            selected_checkboxes = self.browser.find_elements(By.XPATH,
                "//tr//input[@type='checkbox' and @checked] | //tr//input[@type='checkbox'][contains(@class, 'selected')]")
            
            if not selected_checkboxes:
                # Try alternative selector for checked boxes
                all_checkboxes = self.browser.find_elements(By.XPATH,
                    "//tr//input[@type='checkbox']")
                selected_checkboxes = [cb for cb in all_checkboxes if cb.is_selected()]
            
            if selected_checkboxes:
                for checkbox in selected_checkboxes:
                    try:
                        if checkbox.is_selected():
                            checkbox.click()
                            cleared_count += 1
                            time.sleep(0.1)
                    except:
                        continue  # Skip any checkboxes that can't be unchecked
                
                self.logger.log_selection_clearing(cleared_count)
                return True
            
            self.logger.log_selection_clearing(0)
            return True
            
        except Exception as e:
            print(f"⚠️ Error clearing selections: {str(e)}")
            print("🔧 Please manually uncheck any selected records")
            return True  # Continue anyway
    
    def select_pages(self, start_page, end_page):
        """Select all records in the specified page range"""
        try:
            # First, clear any existing selections
            self.clear_all_selections()
            
            # Take a screenshot before selection
            try:
                screenshot_path = "before_selection.png"
                self.browser.driver.save_screenshot(screenshot_path)
                print(f"Saved screenshot to {screenshot_path}")
            except Exception as e:
                print(f"Failed to save screenshot: {str(e)}")
                
            # First, make sure we're selecting all records on the current page
            select_all_checkboxes = self.browser.find_elements(By.XPATH,
                "//th//input[@type='checkbox'] | //th[contains(@class, 'checkbox')]//input")
            
            if not select_all_checkboxes:
                # Try alternative selectors for the "select all" checkbox
                select_all_checkboxes = self.browser.find_elements(By.XPATH,
                    "//input[@type='checkbox' and @id and contains(@id, 'selectAll')] | " +
                    "//input[@type='checkbox' and @class and contains(@class, 'selectAll')] | " +
                    "//span[contains(@class, 'checkbox') and ancestor::th]")
            
            if select_all_checkboxes:
                if not select_all_checkboxes[0].is_selected():
                    select_all_checkboxes[0].click()
                    time.sleep(random.uniform(1, 2))
                print("Selected all records on current page")
            else:
                print("Select all checkbox not found. Trying individual checkboxes...")
                
                # Try selecting individual record checkboxes
                record_checkboxes = self.browser.find_elements(By.XPATH,
                    "//tr//input[@type='checkbox'] | //tr//span[contains(@class, 'checkbox')]/input")
                
                if record_checkboxes:
                    selected_count = 0
                    for checkbox in record_checkboxes:
                        if not checkbox.is_selected():
                            try:
                                checkbox.click()
                                selected_count += 1
                                time.sleep(random.uniform(0.2, 0.5))
                            except:
                                print("Error clicking individual checkbox, continuing...")
                    
                    print(f"Selected {selected_count} individual records")
                else:
                    print("No checkboxes found at all")
                    print("Please select all records manually")
                    input("Press Enter after selecting records...")
            
            # If we need to select multiple pages
            if end_page > start_page:
                # Navigate through each additional page
                for page in range(start_page + 1, end_page + 1):
                    print(f"Moving to page {page} for selection...")
                    self.navigate_to_page(page)
                    
                    # Select all records on this page
                    select_all_checkboxes = self.browser.find_elements(By.XPATH,
                        "//th//input[@type='checkbox'] | //th[contains(@class, 'checkbox')]//input")
                    
                    if not select_all_checkboxes:
                        # Try alternative selectors
                        select_all_checkboxes = self.browser.find_elements(By.XPATH,
                            "//input[@type='checkbox' and @id and contains(@id, 'selectAll')] | " +
                            "//input[@type='checkbox' and @class and contains(@class, 'selectAll')] | " +
                            "//span[contains(@class, 'checkbox') and ancestor::th]")
                    
                    if select_all_checkboxes:
                        if not select_all_checkboxes[0].is_selected():
                            select_all_checkboxes[0].click()
                            time.sleep(random.uniform(1, 2))
                        print(f"Selected all records on page {page}")
                    else:
                        # Try selecting individual record checkboxes
                        record_checkboxes = self.browser.find_elements(By.XPATH,
                            "//tr//input[@type='checkbox'] | //tr//span[contains(@class, 'checkbox')]/input")
                        
                        if record_checkboxes:
                            selected_count = 0
                            for checkbox in record_checkboxes:
                                if not checkbox.is_selected():
                                    try:
                                        checkbox.click()
                                        selected_count += 1
                                        time.sleep(random.uniform(0.2, 0.5))
                                    except:
                                        print("Error clicking individual checkbox, continuing...")
                            
                            print(f"Selected {selected_count} individual records on page {page}")
                        else:
                            print(f"No checkboxes found on page {page}")
                            print(f"Please select all records on page {page} manually")
                            input("Press Enter after selecting records...")
            
            return True
        
        except Exception as e:
            print(f"Selection error: {str(e)}")
            print("Please select required pages manually")
            input("Press Enter after selecting pages...")
            return True
    
    def find_download_records_button(self):
        """Enhanced button detection with multiple strategies"""
        self.logger.debug_logger.info("🔍 Searching for Download Records button...")
        
        # Strategy 1: Direct text matching with multiple variations
        button_selectors = [
            "//button[contains(text(), 'DOWNLOAD RECORDS')]",
            "//button[contains(text(), 'Download Records')]", 
            "//button[text()='Download']",  # Exact match for Download button
            "//button[contains(text(), 'Download')]",
            "//a[contains(text(), 'DOWNLOAD RECORDS')]",
            "//a[contains(text(), 'Download Records')]",
            "//a[text()='Download']",  # Exact match for Download link
            "//a[contains(text(), 'Download')]",
            "//input[@type='submit' and contains(@value, 'DOWNLOAD RECORDS')]",
            "//input[@type='submit' and contains(@value, 'Download Records')]",
            "//input[@type='button' and contains(@value, 'DOWNLOAD RECORDS')]",
            "//input[@type='button' and contains(@value, 'Download Records')]"
        ]
        
        for attempt_num, selector in enumerate(button_selectors, 1):
            buttons = self.browser.find_elements(By.XPATH, selector)
            if buttons:
                self.logger.log_button_detection(f"1.{attempt_num}", True, f"Selector: {selector}")
                return buttons[0]
            else:
                self.logger.log_button_detection(f"1.{attempt_num}", False)
        
        # Strategy 2: Look for buttons containing "download" (case insensitive)
        download_buttons = self.browser.find_elements(By.XPATH, 
            "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'download')] | " +
            "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'download')] | " +
            "//input[contains(translate(@value, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'download')]")
        
        if download_buttons:
            self.logger.log_button_detection(2, True, "Case-insensitive text search")
            print(f"✅ Found {len(download_buttons)} download button(s) with case-insensitive search")
            # Filter for ones that likely say "records"
            for button in download_buttons:
                button_text = button.text.lower() if hasattr(button, 'text') else button.get_attribute('value').lower()
                if 'record' in button_text:
                    print(f"✅ Found button with 'record' in text: {button_text}")
                    return button
            # If no "records" found, return the first download button
            print(f"✅ Using first download button found: {download_buttons[0].text}")
            return download_buttons[0]
        self.logger.log_button_detection(2, False)
        
        # Strategy 3: Look by class names or IDs that might contain "download"
        class_based_buttons = self.browser.find_elements(By.XPATH,
            "//button[contains(@class, 'download')] | " +
            "//a[contains(@class, 'download')] | " +
            "//input[contains(@class, 'download')] | " +
            "//button[contains(@id, 'download')] | " +
            "//a[contains(@id, 'download')] | " +
            "//input[contains(@id, 'download')]")
        
        if class_based_buttons:
            self.logger.log_button_detection(3, True, "Class/ID contains 'download'")
            print(f"✅ Found {len(class_based_buttons)} button(s) with download in class/id")
            return class_based_buttons[0]
        self.logger.log_button_detection(3, False)
        
        # Strategy 4: Look for common download button containers
        container_buttons = self.browser.find_elements(By.XPATH,
            "//div[contains(@class, 'download')]//button | " +
            "//div[contains(@class, 'download')]//a | " +
            "//form[contains(@class, 'download')]//button | " +
            "//form[contains(@class, 'download')]//input[@type='submit']")
        
        if container_buttons:
            self.logger.log_button_detection(4, True, "Download container search")
            print(f"✅ Found {len(container_buttons)} button(s) in download containers")
            return container_buttons[0]
        self.logger.log_button_detection(4, False)
        
        # Strategy 5: Look for any blue colored buttons (common for primary actions)
        blue_buttons = self.browser.find_elements(By.XPATH,
            "//button[contains(@class, 'blue') or contains(@class, 'primary') or contains(@class, 'btn-primary')] | " +
            "//a[contains(@class, 'blue') or contains(@class, 'primary') or contains(@class, 'btn-primary')]")
        
        if blue_buttons:
            self.logger.log_button_detection(5, True, "Primary/blue button search")
            print(f"✅ Found {len(blue_buttons)} blue/primary button(s), checking text...")
            for button in blue_buttons:
                button_text = button.text.lower() if hasattr(button, 'text') else ''
                if 'download' in button_text or 'record' in button_text:
                    print(f"✅ Found blue button with relevant text: {button.text}")
                    return button
        self.logger.log_button_detection(5, False)
        
        # Strategy 6: Look in the top toolbar area where Download button is typically located
        toolbar_buttons = self.browser.find_elements(By.XPATH,
            "//div[contains(@class, 'toolbar') or contains(@class, 'nav') or contains(@class, 'menu')]//button[contains(text(), 'Download')] | " +
            "//div[contains(@class, 'toolbar') or contains(@class, 'nav') or contains(@class, 'menu')]//a[contains(text(), 'Download')] | " +
            "//table/preceding-sibling::*//button[contains(text(), 'Download')] | " +
            "//table/preceding-sibling::*//a[contains(text(), 'Download')]")
        
        if toolbar_buttons:
            self.logger.log_button_detection(6, True, "Toolbar/nav search")
            print(f"✅ Found {len(toolbar_buttons)} button(s) in toolbar area")
            return toolbar_buttons[0]
        self.logger.log_button_detection(6, False)
        
        # Strategy 7: Look in the bottom area of the page where the button appears to be
        bottom_buttons = self.browser.find_elements(By.XPATH,
            "//div[position()>last()-3]//button | " +
            "//div[position()>last()-3]//a | " +
            "//form[position()>last()-3]//button | " +
            "//form[position()>last()-3]//input[@type='submit']")
        
        if bottom_buttons:
            self.logger.log_button_detection(7, True, "Bottom area search")
            print(f"✅ Found {len(bottom_buttons)} button(s) in bottom area, checking text...")
            for button in bottom_buttons:
                button_text = button.text.lower() if hasattr(button, 'text') else button.get_attribute('value', '').lower()
                if 'download' in button_text:
                    print(f"✅ Found bottom button with download text: {button.text}")
                    return button
        self.logger.log_button_detection(7, False)
        
        # Strategy 8: Look for any visible Download button on the page
        all_download_elements = self.browser.find_elements(By.XPATH,
            "//*[contains(text(), 'Download') and (@href or @onclick or name()='button' or name()='input')]")
        
        if all_download_elements:
            self.logger.log_button_detection(8, True, "Generic interactive Download search")
            print(f"✅ Found {len(all_download_elements)} download element(s) on page")
            # Filter for interactive elements that are likely buttons
            for element in all_download_elements:
                tag_name = element.tag_name.lower()
                if tag_name in ['button', 'a', 'input']:
                    element_text = element.text or element.get_attribute('value') or ''
                    print(f"✅ Found interactive download element: {tag_name} - '{element_text}'")
                    return element
        self.logger.log_button_detection(8, False)
        
        print("❌ Could not find Download Records button automatically")
        return None
    
    def download_selected_records(self, batch_num):
        """Download the selected records to a CSV file"""
        try:
            # Take a screenshot before download
            self.logger.save_screenshot("before_automated_download", self.browser.driver, f"Before downloading batch {batch_num}")
                
            # Check if any records are selected
            print("Checking if records are selected...")
            
            # Look for selected count indicators
            selected_count_elements = self.browser.find_elements(By.XPATH,
                "//div[contains(text(), 'selected')] | //span[contains(text(), 'selected')]")
            
            if selected_count_elements:
                selected_text = selected_count_elements[0].text
                print(f"Selected records indicator found: {selected_text}")
                
                # Check if zero records are selected
                if "0 " in selected_text or " 0 " in selected_text:
                    print("Warning: It appears no records are selected!")
                    choice = input("Continue anyway? (y/n): ").lower()
                    if choice != 'y' and choice != 'yes':
                        print("Aborting download due to no records selected")
                        return False
            
            # Find and click the download button in the top toolbar - use enhanced detection
            print("🔍 AUTO-CLICKING: Searching for Download button...")
            toolbar_download_button = None
            
            # Strategy 1: Direct toolbar download button search
            download_buttons = self.browser.find_elements(By.XPATH,
                "//a[contains(text(), 'Download')] | //button[contains(text(), 'Download')]")
            
            if download_buttons:
                toolbar_download_button = download_buttons[0]
                print("✅ Found Download button with direct search")
            else:
                # Strategy 2: Try alternative download buttons with enhanced detection
                alt_download_buttons = self.browser.find_elements(By.XPATH,
                    "//a[contains(@class, 'download')] | //button[contains(@class, 'download')] | " +
                    "//i[contains(@class, 'download')] | //span[contains(@class, 'download')]")
                
                if alt_download_buttons:
                    toolbar_download_button = alt_download_buttons[0]
                    print("✅ Found Download button with class-based search")
                else:
                    # Strategy 3: Use the enhanced button detection method
                    print("🔍 Trying enhanced button detection for toolbar download...")
                    
                    # Look specifically for toolbar/menu download buttons
                    toolbar_specific_buttons = self.browser.find_elements(By.XPATH,
                        "//div[contains(@class, 'toolbar') or contains(@class, 'nav') or contains(@class, 'menu')]//button[contains(text(), 'Download')] | " +
                        "//div[contains(@class, 'toolbar') or contains(@class, 'nav') or contains(@class, 'menu')]//a[contains(text(), 'Download')] | " +
                        "//table/preceding-sibling::*//button[contains(text(), 'Download')] | " +
                        "//table/preceding-sibling::*//a[contains(text(), 'Download')]")
                    
                    if toolbar_specific_buttons:
                        toolbar_download_button = toolbar_specific_buttons[0]
                        print("✅ Found Download button in toolbar area")
                    else:
                        # Strategy 4: Look for any visible download element
                        all_download_elements = self.browser.find_elements(By.XPATH,
                            "//*[contains(text(), 'Download') and (@href or @onclick or name()='button' or name()='input')]")
                        
                        if all_download_elements:
                            for element in all_download_elements:
                                tag_name = element.tag_name.lower()
                                if tag_name in ['button', 'a', 'input']:
                                    toolbar_download_button = element
                                    print(f"✅ Found Download element: {tag_name} - '{element.text}'")
                                    break
            
            # Try to click the found button
            if toolbar_download_button:
                try:
                    print(f"🎯 AUTO-CLICKING: Clicking Download button: {toolbar_download_button.text}")
                    
                    # Scroll into view first
                    self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", toolbar_download_button)
                    time.sleep(1)
                    
                    # Try regular click first
                    toolbar_download_button.click()
                    print("✅ Successfully clicked Download button")
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as click_error:
                    print(f"⚠️ Regular click failed: {str(click_error)}")
                    print("🔄 Trying JavaScript click...")
                    try:
                        self.browser.driver.execute_script("arguments[0].click();", toolbar_download_button)
                        print("✅ Successfully clicked Download button with JavaScript")
                        time.sleep(random.uniform(2, 4))
                    except Exception as js_error:
                        print(f"❌ JavaScript click also failed: {str(js_error)}")
                        # Fall back to manual intervention
                        self.handle_manual_download_intervention(batch_num, "Download button not found in toolbar")
                        print("Please click the download button manually")
                        input("Press Enter after clicking download...")
            else:
                # No download button found at all
                self.handle_manual_download_intervention(batch_num, "Download button not found in toolbar")
                print("Please click the download button manually")
                input("Press Enter after clicking download...")
            
            # Take a screenshot of download options page
            self.logger.save_screenshot("download_dialog_auto", self.browser.driver, f"Download options page for batch {batch_num}")
            
            # On the download page, select CSV format (Step 1)
            csv_radio_buttons = self.browser.find_elements(By.XPATH,
                "//input[@type='radio' and (@id or @name) and following::*[contains(text(), 'Comma') or contains(text(), 'CSV')]]")
            
            if csv_radio_buttons:
                if not csv_radio_buttons[0].is_selected():
                    csv_radio_buttons[0].click()
                    time.sleep(random.uniform(1, 2))
                print("✅ Selected CSV format")
            else:
                # Try alternative CSV selection methods
                csv_options = self.browser.find_elements(By.XPATH,
                    "//label[contains(text(), 'Comma') or contains(text(), 'CSV')] | " +
                    "//div[contains(text(), 'Comma') or contains(text(), 'CSV')] | " +
                    "//span[contains(text(), 'Comma') or contains(text(), 'CSV')]")
                
                if csv_options:
                    csv_options[0].click()
                    time.sleep(random.uniform(1, 2))
                    print("✅ Clicked CSV option text")
                else:
                    print("⚠️ CSV format option not found - it may already be selected")
                    print("Please ensure CSV format is selected manually if needed")
                    # Don't require input here, continue
            
            # Select Detailed data level (Step 2)
            detailed_radio_buttons = self.browser.find_elements(By.XPATH,
                "//input[@type='radio' and (@id or @name) and following::*[contains(text(), 'Detailed')]]")
            
            if detailed_radio_buttons:
                if not detailed_radio_buttons[0].is_selected():
                    detailed_radio_buttons[0].click()
                    time.sleep(random.uniform(1, 2))
                print("✅ Selected Detailed data level")
            else:
                # Try alternative detailed selection methods
                detailed_options = self.browser.find_elements(By.XPATH,
                    "//label[contains(text(), 'Detailed')] | //div[contains(text(), 'Detailed')] | " +
                    "//span[contains(text(), 'Detailed')]")
                
                if detailed_options:
                    detailed_options[0].click()
                    time.sleep(random.uniform(1, 2))
                    print("✅ Clicked Detailed option text")
                else:
                    print("⚠️ Detailed data level not found, trying alternatives...")
                    # Try to find any data level options
                    data_level_options = self.browser.find_elements(By.XPATH,
                        "//input[@type='radio'] | //input[@type='checkbox']")
                    
                    if data_level_options:
                        # Print available options for debugging
                        print("Available form options:")
                        for i, option in enumerate(data_level_options):
                            try:
                                option_text = option.get_attribute('value') or f"Option {i+1}"
                                following_text = self.browser.driver.execute_script(
                                    "return arguments[0].parentNode.textContent;", option)
                                print(f"  {i+1}: {option_text} - {following_text}")
                            except:
                                print(f"  {i+1}: Option {i+1}")
                    
                    print("⚠️ Could not auto-select detailed format")
                    print("Please select 'Detailed' (not Summary) manually if needed")
                    # Continue without requiring input
            
            # Handle any additional options or fields
            custom_options = self.search_parameters.get('download_options', {})
            if custom_options:
                print("Applying custom download options...")
                # Implementation for custom options would go here
            
            # Wait a moment for any dynamic updates
            time.sleep(2)
            
            # Now use enhanced button detection for Download Records
            print("🔍 AUTO-DOWNLOADING: Starting download process...")
            download_button = self.find_download_records_button()
            
            if download_button:
                print(f"🎯 AUTO-DOWNLOAD: Clicking Download Records button")
                try:
                    # Scroll button into view
                    self.browser.driver.execute_script("arguments[0].scrollIntoView(true);", download_button)
                    time.sleep(1)
                    
                    # Try clicking the button
                    download_button.click()
                    print("✅ AUTO-DOWNLOAD: Successfully clicked Download Records button")
                    
                    # Wait for download to initiate
                    download_wait = random.uniform(15, 25)
                    print(f"⏳ AUTO-DOWNLOAD: Waiting {download_wait:.1f} seconds for download to complete...")
                    time.sleep(download_wait)
                    
                except Exception as click_error:
                    print(f"❌ Error clicking button: {str(click_error)}")
                    print("🔄 Trying JavaScript click...")
                    try:
                        self.browser.driver.execute_script("arguments[0].click();", download_button)
                        print("✅ Successfully clicked with JavaScript")
                        
                        download_wait = random.uniform(15, 25)
                        print(f"⏳ Waiting {download_wait:.1f} seconds for download...")
                        time.sleep(download_wait)
                    except Exception as js_error:
                        print(f"❌ JavaScript click also failed: {str(js_error)}")
                        raise click_error
            else:
                # Use comprehensive manual intervention handler
                self.handle_manual_download_intervention(batch_num, "Download Records button not found")
                print("🔧 Please click 'Download Records' manually and save the file to the specified location")
                input("Press Enter when you've saved the file...")
            
            # Generate file name for tracking
            state_name = self.search_parameters.get('state', 'State')
            timestamp = datetime.datetime.now().strftime('%d%m%y_%H%M')
            start_page = (batch_num - 1) * self.pages_per_batch + 1
            end_page = start_page + self.pages_per_batch - 1
            
            expected_filename = f"{state_name}_{start_page}to{end_page}_{timestamp}.csv"
            print(f"📁 Expected saved filename: {expected_filename}")
            
            # Add to downloaded files list
            self.state.add_downloaded_file(
                batch_num=batch_num,
                filename=expected_filename,
                pages=f"{start_page}-{end_page}"
            )
            
            # Only ask for confirmation if we couldn't auto-download
            if download_button is None:
                print("\nDid the file download complete successfully? (y/n)")
                confirm = input().lower().strip()
                if confirm != 'y' and confirm != 'yes' and confirm != '':
                    print("Download reported as unsuccessful")
                    # Remove from downloaded files
                    self.state.remove_batch_data(batch_num)
                    return False
            else:
                print("✅ AUTO-DOWNLOAD: Download should be complete")
            
            # Go back to results page
            print("🔙 Navigating back to results page...")
            back_buttons = self.browser.find_elements(By.XPATH, 
                "//a[contains(text(), 'Back')] | //button[contains(text(), 'Back')]")
            
            if back_buttons:
                back_buttons[0].click()
                time.sleep(random.uniform(3, 5))
                print("✅ Clicked Back button")
            else:
                # Try the browser back button
                self.browser.driver.back()
                time.sleep(random.uniform(3, 5))
                
                current_url = self.browser.driver.current_url.lower()
                if "download" in current_url:
                    print("⚠️ Browser back button didn't work")
                    print("🔧 Please navigate back to the results page manually")
                    input("Press Enter after navigating back...")
                else:
                    print("✅ Successfully navigated back")
            
            return True
            
        except Exception as e:
            print(f"❌ Download error: {str(e)}")
            print("🔧 Please complete the download process manually")
            input("Press Enter after downloading...")
            return False
    
    def download_batch(self, batch_num):
        """Download a batch of records (10 pages at a time by default)"""
        try:
            start_page = (batch_num - 1) * self.pages_per_batch + 1
            end_page = start_page + self.pages_per_batch - 1
            
            self.logger.log_batch_start(batch_num, start_page, end_page)
            
            # Go to starting page
            print(f"Navigating to page {start_page}...")
            self.navigate_to_page(start_page)
            
            # Select all records on current page range
            print(f"Selecting pages {start_page} to {end_page}...")
            self.select_pages(start_page, end_page)
            
            # Download the selected records
            self.logger.log_download_start(batch_num)
            if self.download_selected_records(batch_num):
                # Update state
                self.state.update_last_batch(batch_num)
                self.state.add_completed_batch(batch_num)
                
                # Generate expected filename for logging
                state_name = self.search_parameters.get('state', 'State')
                timestamp = datetime.datetime.now().strftime('%d%m%y_%H%M')
                expected_filename = f"{state_name}_{start_page}to{end_page}_{timestamp}.csv"
                
                self.logger.log_batch_end(batch_num, True, expected_filename)
                return True
            else:
                self.logger.log_batch_end(batch_num, False)
                return False
            
        except Exception as e:
            print(f"Error processing batch {batch_num}: {str(e)}")
            print("Please try manually.")
            input("Press Enter after manual batch processing...")
            return False
