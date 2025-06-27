#!/usr/bin/env python3
"""
Launcher for Miller 3 Data Scraper - Enhanced Version
Double-click this file to run the scraper
"""

import os
import sys
import subprocess

def main():
    print("=" * 80)
    print("MILLER 3 DATA SCRAPER - ENHANCED VERSION")
    print("=" * 80)
    print("\nFeatures:")
    print("✓ Semi-automated OR Fully automated modes")
    print("✓ No file naming prompts (uses website defaults)")
    print("✓ Batch processing (10 pages at a time)")
    print("✓ CSV merge option after downloads")
    print("✓ Respects 1000 download limit")
    print("\nAutomation Options:")
    print("• Semi-Automated: You navigate pages, script selects records")
    print("• Fully Automated: Script handles everything (with fallbacks)")
    print("\n" + "=" * 80)
    
    # Get the directory where this launcher is located
    launcher_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the main scraper
    scraper_path = os.path.join(launcher_dir, "scraper_enhanced.py")
    
    if os.path.exists(scraper_path):
        print("\nStarting Miller 3 Data Scraper...")
        print("A Chrome browser window will open.\n")
        
        try:
            subprocess.run([sys.executable, scraper_path])
        except KeyboardInterrupt:
            print("\n\nScraper interrupted by user.")
        except Exception as e:
            print(f"\nError: {e}")
    else:
        print(f"Error: Could not find {scraper_path}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
