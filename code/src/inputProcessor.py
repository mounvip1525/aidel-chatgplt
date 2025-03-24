import os
import json
import re
import logging
from typing import Dict, List, Optional, Union
from processStructured import process_structured_transactions
from processUnstructured import process_unstructured_transactions, read_unstructured_file

# --- Configure Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def process_transactions(input_file_path: str) -> List[Dict]:
   """Determines file type and processes transactions accordingly."""
   try:
       if input_file_path.endswith('.csv'):
           return process_structured_transactions(input_file_path)
       elif input_file_path.endswith('.txt'):
           unstructured_data = read_unstructured_file(input_file_path)
           return process_unstructured_transactions(unstructured_data)
       else:
           logger.error("Unsupported file type. Please provide a .csv or .txt file.")
           return []
   except Exception as e:
       logger.error(f"Error processing file: {str(e)}")
       return []
   
if __name__ == "__main__":
   input_file_path = input("Enter the path to your input file (.csv or .txt): ")
   
   processed_data = process_transactions(input_file_path)

   output_file_path = f"data/processed_{os.path.basename(input_file_path).split('.')[0]}.json"
   
   if processed_data:
       try:
           with open(output_file_path, 'w', encoding='utf-8') as f:
               json.dump(processed_data, f, indent=2)
           print(f"Processed transactions saved to {output_file_path}")
       except IOError as e:
           logger.error(f"Failed to write output: {str(e)}")