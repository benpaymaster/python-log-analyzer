import json
import unittest
from log_analyzer.analyzer import analyze_logs
from log_analyzer.tests import TestLogAnalyzer # Imports tests for display

# Define the file path for the mock log data
LOG_FILE_PATH = 'logs/mock_data.txt'

def run_analysis():
    """
    Main function to load logs, run the analysis, and print the results.
    """
    try:
        print(f"--- 1. Loading log data from: {LOG_FILE_PATH} ---")
        with open(LOG_FILE_PATH, 'r') as f:
            log_data = f.read()

        # Run the analysis using the core function
        analysis_results = analyze_logs(log_data)

        print("\n--- 2. Infrastructure Summary Report ---")
        print(json.dumps(analysis_results, indent=4))
        
        print("\n--- 3. Running Unit Tests to Verify Quality ---")
        # Run tests to demonstrate commitment to testable code
        # Uses a TextTestRunner for clean output
        suite = unittest.TestLoader().loadTestsFromTestCase(TestLogAnalyzer)
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)

        print("\n--- Analysis & Validation Complete ---")

    except FileNotFoundError:
        print(f"ERROR: Log file not found at {LOG_FILE_PATH}. Please ensure the directory structure is correct.")
    except Exception as e:
        print(f"An unexpected error occurred during execution: {e}")

if __name__ == '__main__':
    run_analysis()