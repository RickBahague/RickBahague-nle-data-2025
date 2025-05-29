#!/usr/bin/env python

import subprocess
import time
import psutil
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def is_scraper_running():
    """Check if scraper.py is currently running"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline']
                if cmdline and 'scraper.py' in cmdline:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def start_scraper():
    """Start the scraper.py script"""
    try:
        subprocess.Popen(['python', 'scraper.py'])
        logging.info("Started scraper.py")
    except Exception as e:
        logging.error(f"Failed to start scraper.py: {e}")

def main():
    logging.info("Starting scraper monitor")
    
    while True:
        if not is_scraper_running():
            logging.warning("Scraper is not running. Restarting in 5 minutes...")
            time.sleep(300)  # Wait for 5 minutes
            start_scraper()
        else:
            logging.info("Scraper is running")
        
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main() 