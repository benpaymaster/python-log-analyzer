import sys
import os
import glob
import json
import unittest
import argparse
from log_analyzer.analyzer import analyze_logs
from log_analyzer.tests import TestLogAnalyzer

LOG_FILE_PATH = 'logs/mock_data.txt'
ERROR_RATE_THRESHOLD = 20.0  # percent
LATENCY_THRESHOLD = 100.0    # ms

def run_analysis(log_data_source, is_stream=False, output_path=None, event_type_filter=None, delimiter='|', start_time=None, end_time=None, service_names=None, top_slowest=None, latency_histogram=None, csv_output=None, error_threshold=None, latency_threshold=None, detect_anomalies=False, log_dir=None):
    try:
        if is_stream:
            print("--- 1. Loading log data from stdin (stream mode) ---")
            log_data = sys.stdin.read()
        elif log_dir:
            print(f"--- 1. Loading log data from directory: {log_dir} ---")
            log_data = ''
            for file in glob.glob(os.path.join(log_dir, '*.txt')):
                print(f"  - Including {file}")
                with open(file, 'r') as f:
                    log_data += f.read() + '\n'
        else:
            print(f"--- 1. Loading log data from: {log_data_source} ---")
            with open(log_data_source, 'r') as f:
                log_data = f.read()

        # Auto-detect delimiter if not specified
        auto_delimiter = delimiter
        if delimiter is None or delimiter == 'auto':
            for line in log_data.splitlines():
                line = line.strip()
                if not line or line.startswith('#') or 'Format:' in line:
                    continue
                for delim in ['|', ',', '\t', ';', ':']:
                    parts = [p.strip() for p in line.split(delim)]
                    if len(parts) == 4:
                        auto_delimiter = delim
                        print(f"Auto-detected delimiter: '{delim}'")
                        break
                if auto_delimiter != delimiter:
                    break

        analysis_results = analyze_logs(
            log_data,
            event_type_filter=event_type_filter,
            delimiter=auto_delimiter,
            start_time=start_time,
            end_time=end_time,
            service_names=service_names,
            top_slowest=top_slowest,
            latency_histogram=latency_histogram,
            detect_anomalies=detect_anomalies
        )

        if csv_output:
            import csv
            with open(csv_output, 'w', newline='') as csvfile:
                fieldnames = ['service', 'total_events', 'average_latency_ms', 'error_rate']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for service, stats in analysis_results.items():
                    row = {
                        'service': service,
                        'total_events': stats.get('total_events', 0),
                        'average_latency_ms': stats.get('average_latency_ms', 0),
                        'error_rate': stats.get('error_rate', '0.00%')
                    }
                    writer.writerow(row)
            print(f"\nCSV summary report saved to {csv_output}")

        print("\n--- 2. Infrastructure Summary Report ---")
        if event_type_filter:
            print(f"(Filtered by event type: {event_type_filter})")

        print(json.dumps(analysis_results, indent=4))
        for service, stats in analysis_results.items():
            if 'anomalies' in stats and stats['anomalies']:
                print(f"\n--- Anomalies detected for {service} ---")
                for anomaly in stats['anomalies']:
                    print(f"Timestamp: {anomaly['timestamp']}, Latency: {anomaly['latency']}ms, Event Type: {anomaly['event_type']}")

        if output_path:
            with open(output_path, 'w') as out_f:
                json.dump(analysis_results, out_f, indent=4)
            print(f"\nSummary report saved to {output_path}")

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

        print("\n--- 2a. Alerts ---")
        err_thresh = error_threshold if error_threshold is not None else ERROR_RATE_THRESHOLD
        lat_thresh = latency_threshold if latency_threshold is not None else LATENCY_THRESHOLD
        for service, stats in analysis_results.items():
            error_rate = float(stats['error_rate'].replace('%',''))
            avg_latency = stats['average_latency_ms']
            if error_rate > err_thresh:
                print(f"ALERT: {service} error rate is high: {error_rate:.2f}% (threshold: {err_thresh}%)")
            if avg_latency > lat_thresh:
                print(f"ALERT: {service} average latency is high: {avg_latency:.2f} ms (threshold: {lat_thresh} ms)")

        print("\n--- 3. Running Unit Tests to Verify Quality ---")
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
    parser.add_argument('--config', type=str, help='Path to YAML or JSON config file for all options')
    parser.add_argument('--stream', action='store_true', help='Read log data from stdin instead of a file')
    parser.add_argument('--file', type=str, default=LOG_FILE_PATH, help='Path to the log file (default: logs/mock_data.txt)')
    parser.add_argument('--output', type=str, help='Path to save the summary report as a JSON file')
    parser.add_argument('--event-type', type=str, help='Filter analysis by event type (e.g., ERROR, SUCCESS, INFO)')
    parser.add_argument('--delimiter', type=str, default=None, help='Log entry delimiter (default: auto-detect)')
    parser.add_argument('--start-time', type=str, help='Start time for log filtering (ISO format or epoch)')
    parser.add_argument('--end-time', type=str, help='End time for log filtering (ISO format or epoch)')
    parser.add_argument('--service', type=str, help='Comma-separated list of service names to include')
    parser.add_argument('--top-slowest', type=int, help='Report the N slowest events per service')
    parser.add_argument('--latency-histogram', type=str, help='Comma-separated latency bucket edges (e.g., \"0,50,100,200,500\")')
    parser.add_argument('--csv-output', type=str, help='Path to save the summary report as a CSV file')
    parser.add_argument('--error-threshold', type=float, help='Custom error rate threshold for alerts (percent)')
    parser.add_argument('--latency-threshold', type=float, help='Custom latency threshold for alerts (ms)')
    parser.add_argument('--detect-anomalies', action='store_true', help='Flag latency/error rate anomalies using statistical methods')
    parser.add_argument('--log-dir', type=str, help='Directory containing log files to analyze (all *.txt files will be processed)')
    args = parser.parse_args()

    # Load config file if specified
    config = {}
    if getattr(args, 'config', None):
        ext = os.path.splitext(args.config)[1].lower()
        if ext == '.yaml' or ext == '.yml':
            import yaml
            with open(args.config, 'r') as f:
                config = yaml.safe_load(f)
        elif ext == '.json':
            with open(args.config, 'r') as f:
                config = json.load(f)
        else:
            print(f"Unsupported config file format: {ext}")

    # Helper to get value from CLI or config
    def get_opt(opt, default=None):
        return getattr(args, opt) if getattr(args, opt) is not None else config.get(opt, default)
    event_type_filter = get_opt('event_type')
    delimiter = get_opt('delimiter')
    start_time = get_opt('start_time')
    end_time = get_opt('end_time')
    service_names = [s.strip() for s in get_opt('service', '').split(',')] if get_opt('service') else None
    top_slowest = get_opt('top_slowest')
    latency_histogram = [float(x) for x in get_opt('latency_histogram', '').split(',')] if get_opt('latency_histogram') else None
    csv_output = get_opt('csv_output')
    error_threshold = get_opt('error_threshold')
    latency_threshold = get_opt('latency_threshold')
    detect_anomalies = get_opt('detect_anomalies', False)
    is_stream = get_opt('stream', False)
    file_path = get_opt('file', LOG_FILE_PATH)
    output_path = get_opt('output')
    log_dir = get_opt('log_dir')

    if is_stream:
        run_analysis(None, is_stream=True, output_path=output_path, event_type_filter=event_type_filter, delimiter=delimiter, start_time=start_time, end_time=end_time, service_names=service_names, top_slowest=top_slowest, latency_histogram=latency_histogram, csv_output=csv_output, error_threshold=error_threshold, latency_threshold=latency_threshold, detect_anomalies=detect_anomalies)
    elif log_dir:
        run_analysis(None, is_stream=False, output_path=output_path, event_type_filter=event_type_filter, delimiter=delimiter, start_time=start_time, end_time=end_time, service_names=service_names, top_slowest=top_slowest, latency_histogram=latency_histogram, csv_output=csv_output, error_threshold=error_threshold, latency_threshold=latency_threshold, detect_anomalies=detect_anomalies, log_dir=log_dir)
    else:
        run_analysis(file_path, output_path=output_path, event_type_filter=event_type_filter, delimiter=delimiter, start_time=start_time, end_time=end_time, service_names=service_names, top_slowest=top_slowest, latency_histogram=latency_histogram, csv_output=csv_output, error_threshold=error_threshold, latency_threshold=latency_threshold, detect_anomalies=detect_anomalies)