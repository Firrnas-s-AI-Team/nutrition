import os
import json
import requests
import time
from concurrent.futures import ThreadPoolExecutor
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'api_processing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

def process_single_file(file_path, api_url='http://localhost:8000/generate_meal_plan'):
    """Process a single JSON file through the API."""
    # Define filename early so it is available even if an error occurs
    filename = os.path.basename(file_path)
    try:
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Make the API request
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json'
        }
        response = requests.post(api_url, headers=headers, json=data)
        response.raise_for_status()
        
        # Create output directory structure
        output_base_dir = 'meal_plan_outputs'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(output_base_dir, timestamp)
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the response
        output_filename = f'meal_plan_{filename}'
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, indent=2)
        
        logging.info(f"Successfully processed and saved {filename} - Status: {response.status_code}")
        return True, filename
        
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed for {file_path}: {str(e)}")
        return False, filename
    except Exception as e:
        logging.error(f"Error processing {file_path}: {str(e)}")
        return False, filename

def process_all_files(directory_path, max_workers=5, delay=10):
    """Process all JSON files in the directory with threading and rate limiting."""
    # Get all JSON files in the directory
    json_files = [
        os.path.join(directory_path, f) 
        for f in os.listdir(directory_path) 
        if f.endswith('.json')
    ]
    
    total_files = len(json_files)
    successful = []
    failed = []
    
    logging.info(f"Starting to process {total_files} files...")
    
    # Create a timestamp for this batch
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, file_path in enumerate(json_files, 1):
            # Add delay for rate limiting
            if i > 1:
                time.sleep(10)
                
            success, filename = executor.submit(process_single_file, file_path).result()
            if success:
                successful.append(filename)
            else:
                failed.append(filename)
            
            logging.info(f"Progress: {i}/{total_files} files processed")
    
    # Create a summary JSON
    summary = {
        "timestamp": timestamp,
        "total_files": total_files,
        "successful_count": len(successful),
        "failed_count": len(failed),
        "successful_files": successful,
        "failed_files": failed
    }
    
    # Save summary
    summary_dir = 'meal_plan_outputs'
    os.makedirs(summary_dir, exist_ok=True)
    summary_path = os.path.join(summary_dir, f'summary_{timestamp}.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    logging.info(f"""
    Processing completed:
    - Total files: {total_files}
    - Successful: {len(successful)}
    - Failed: {len(failed)}
    Summary saved to: {summary_path}
    """)

def main():
    # Specify the directory path containing the JSON files
    directory_path = r'C:\Users\dell\Downloads\nutration\test\user_profiles'
    
    if not os.path.exists(directory_path):
        logging.error(f"Directory not found: {directory_path}")
        return
    
    # Process all files in the directory
    process_all_files(directory_path)

if __name__ == "__main__":
    main()
