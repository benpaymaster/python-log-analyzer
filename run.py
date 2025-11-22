# Alert thresholds (can be adjusted)
ERROR_RATE_THRESHOLD = 20.0  # percent
LATENCY_THRESHOLD = 100.0    # ms
import json
import unittest
import sys
import argparse
from log_analyzer.analyzer import analyze_logs
from log_analyzer.tests import TestLogAnalyzer # Imports tests for display

# Define the file path for the mock log data
LOG_FILE_PATH = 'logs/mock_data.txt'

def run_analysis(log_data_source, is_stream=False, output_path=None, event_type_filter=None, delimiter='|'):
    """
    Main function to load logs, run the analysis, and print the results.
    log_data_source: file path or stdin
    is_stream: if True, read from stdin; else, read from file
    """
    try:
        if is_stream:
            print("--- 1. Loading log data from stdin (stream mode) ---")
            log_data = sys.stdin.read()
        else:
            print(f"--- 1. Loading log data from: {log_data_source} ---")
            with open(log_data_source, 'r') as f:
                log_data = f.read()

        # Run the analysis using the core function
        analysis_results = analyze_logs(log_data, event_type_filter=event_type_filter, delimiter=delimiter)

        print("\n--- 2. Infrastructure Summary Report ---")
        if event_type_filter:
            print(f"(Filtered by event type: {event_type_filter})")

        print(json.dumps(analysis_results, indent=4))
        if output_path:
            with open(output_path, 'w') as out_f:
                json.dump(analysis_results, out_f, indent=4)
            print(f"\nSummary report saved to {output_path}")

        # --- Overall summary statistics ---
        print("\n--- 2b. Overall Summary Statistics ---")
        total_events = 0
        total_latency = 0.0
        total_errors = 0
        for stats in analysis_results.values():
            total_events += stats['total_events']
            total_latency += stats['average_latency_ms'] * stats['total_events']
            total_errors += float(stats['error_rate'].replace('%','')) * stats['total_events'] / 100.0
        if total_events > 0:
            overall_avg_latency = total_latency / total_events
            overall_error_rate = (total_errors / total_events) * 100
        else:
            overall_avg_latency = 0.0
            overall_error_rate = 0.0
        print(f"Total events: {total_events}")
        print(f"Overall average latency: {overall_avg_latency:.2f} ms")
        print(f"Overall error rate: {overall_error_rate:.2f}%")

        # --- Alerting for high error rate or latency ---
        print("\n--- 2a. Alerts ---")
        for service, stats in analysis_results.items():
            error_rate = float(stats['error_rate'].replace('%',''))
            avg_latency = stats['average_latency_ms']
            if error_rate > ERROR_RATE_THRESHOLD:
                print(f"ALERT: {service} error rate is high: {error_rate:.2f}% (threshold: {ERROR_RATE_THRESHOLD}%)")
            if avg_latency > LATENCY_THRESHOLD:
                print(f"ALERT: {service} average latency is high: {avg_latency:.2f} ms (threshold: {LATENCY_THRESHOLD} ms)")

        print("\n--- 3. Running Unit Tests to Verify Quality ---")
        # Run tests to demonstrate commitment to testable code
        suite = unittest.TestLoader().loadTestsFromTestCase(TestLogAnalyzer)
        runner = unittest.TextTestRunner(verbosity=2)
        runner.run(suite)

        print("\n--- Analysis & Validation Complete ---")

    except FileNotFoundError:
        print(f"ERROR: Log file not found at {log_data_source}. Please ensure the directory structure is correct.")
    except Exception as e:
        print(f"An unexpected error occurred during execution: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Infrastructure Log Analyzer")
    parser.add_argument('--stream', action='store_true', help='Read log data from stdin instead of a file')
    parser.add_argument('--file', type=str, default=LOG_FILE_PATH, help='Path to the log file (default: logs/mock_data.txt)')
    parser.add_argument('--output', type=str, help='Path to save the summary report as a JSON file')
    parser.add_argument('--event-type', type=str, help='Filter analysis by event type (e.g., ERROR, SUCCESS, INFO)')
    parser.add_argument('--delimiter', type=str, default='|', help='Log entry delimiter (default: |)')
    args = parser.parse_args()

    event_type_filter = args.event_type
    delimiter = args.delimiter

    if args.stream:
        run_analysis(None, is_stream=True, output_path=args.output, event_type_filter=event_type_filter, delimiter=delimiter)
    else:
        run_analysis(args.file, output_path=args.output, event_type_filter=event_type_filter, delimiter=delimiter)