"""
Speed Test Data Collector for Databricks Volume

This script executes internet speed tests at regular intervals and uploads
the JSON results to a Databricks Unity Catalog Volume for real-time streaming
analytics and processing.

Requirements:
    - pip install databricks-sdk speedtest-cli python-dotenv
    - .env file or environment variables with credentials

Environment Variables:
    DATABRICKS_HOST: Databricks workspace URL (e.g., https://adb-123456.cloud.databricks.net)
    DATABRICKS_TOKEN: Personal Access Token for authentication
    VOLUME_PATH: Unity Catalog volume path (e.g., /Volumes/main/default/speed_test_data)
    RAW_PATH: Local directory for processed speed test results
    TEMP_PATH: Local directory for temporary speed test files

Usage:
    python script_name.py
    
    The script will run indefinitely, executing speed tests every 50 minutes.
    Press Ctrl+C to stop.
"""

from glob import glob
import os
import subprocess
import time
from datetime import datetime as dt
from io import BytesIO
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


class DB_SPEED_TEST:
    """
    Speed Test Manager with Databricks Volume Integration
    
    This class handles the execution of internet speed tests using speedtest-cli
    and automatically uploads the results to a Databricks Unity Catalog volume
    for real-time streaming ingestion and analytics.
    
    Attributes:
        client (WorkspaceClient): Authenticated Databricks SDK client
        volume_file_path (str): Path to the Unity Catalog volume for uploads
        RAW_PATH (str): Local directory path for finalized speed test results
        TEMP_PATH (str): Local directory path for temporary test files
        
    Example:
        >>> speed_test = DB_SPEED_TEST()
        >>> speed_test.upload_speed_test()
        ✓ Speed test completed: log_2024_01_15_10_30_45.json
        ✓ Uploaded: log_2024_01_15_10_30_45.json -> /Volumes/main/default/speed_test_data
    """

    def __init__(self):
        """
        Initialize the Speed Test Manager
        
        Loads configuration from environment variables, creates local directories
        if they don't exist, and establishes authenticated connection to the
        Databricks workspace.
        
        Environment variables required:
            - DATABRICKS_HOST: Workspace URL
            - DATABRICKS_TOKEN: Personal Access Token
            - RAW_PATH: Local raw data directory
            - TEMP_PATH: Local temp directory
            - VOLUME_PATH: Unity Catalog volume path
            
        Raises:
            Exception: If required environment variables are missing
        """
        # Load Databricks credentials from environment

        
        # Load local directory paths
        
        self.RAW_PATH = os.get('LOGS_PATH')
        self.TEMP_PATH = self.RAW_PATH.replace('raw','temp')
        
        # Create local directories if they don't exist
        os.makedirs(self.RAW_PATH, exist_ok=True)
        os.makedirs(self.TEMP_PATH, exist_ok=True)
        


    def upload_speed_test(self):
        """
        Execute a speed test and upload results to Databricks
        
        This method performs the following steps:
        1. Executes speedtest-cli to measure internet connection speed
        2. Saves the JSON output to a temporary file
        3. Validates the test completed successfully (non-zero file size)
        4. Moves the file from temp to raw directory
        5. Uploads the result to Databricks volume
        
        The filename format is: log_YYYY_MM_DD_HH_MM_SS.json
        
        Returns:
            None
            
        Note:
            If the speed test fails or produces an empty file, the temporary
            file is not moved to raw directory and no upload occurs.
            
            The method waits 5 seconds after moving the file to ensure
            filesystem consistency before uploading.
        """
        # Generate timestamp-based filename
        now = dt.now()
        file_name = f"log_{now.strftime('%Y_%m_%d_%H_%M_%S')}.json"
        temp_file = f"{self.TEMP_PATH}/{file_name}"
        raw_file = f"{self.RAW_PATH}/{file_name}"

        # Execute speedtest-cli command
        # --format=json outputs results in JSON format
        # Output is redirected to temporary file
        result = subprocess.run(
            f'speedtest --format=json > "{temp_file}"',
            shell=True,
            executable="/bin/bash",
            capture_output=True,
            text=True
        )
        
        # Validate speed test completed successfully
        # Check: return code is 0, file exists, and file is not empty
        if result.returncode == 0 and os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
            # Move file from temp to raw directory
            os.rename(temp_file, raw_file)
            print(f"✓ Speed test completed: {file_name}")
            
            # Wait briefly to ensure filesystem consistency
            time.sleep(5)
            


if __name__ == "__main__":
    """
    Main execution loop
    
    Initializes the speed test manager and runs tests continuously
    every 10 minutes. Press Ctrl+C to stop the service.
    """
    print('Starting Speed Test Collection Service...')
    
    # Initialize speed test manager
    speed_test = DB_SPEED_TEST()

    # Main loop: execute speed test every 50 minutes
    while True:
        speed_test.upload_speed_test()
        
        # Wait 10 minutes before next test
        time.sleep(60 * 10)
