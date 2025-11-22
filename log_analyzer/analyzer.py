from collections import defaultdict
from typing import Dict, Any

def analyze_logs(log_data: str, event_type_filter: str = None) -> Dict[str, Any]:
    """
    Parses a string of simulated infrastructure log data and calculates
    summary statistics: event counts and average latency per service.

    The expected log format is: TIMESTAMP | SERVICE_NAME | EVENT_TYPE | LATENCY_MS

    Args:
        log_data: A string containing newline-separated log entries.
        event_type_filter: If provided, only include events matching this type.

    Returns:
        A dictionary containing the calculated summary statistics, including
        'total_events', 'average_latency_ms', and 'error_rate' for each service.
    """
    lines = log_data.strip().split('\n')
    service_stats = defaultdict(lambda: {'total_count': 0, 'total_latency': 0.0, 'error_count': 0})

    for line in lines:
        # Ignore empty lines after strip() and lines that look like comments/headers
        if not line or line.startswith('#'):
            continue

        try:
            # Format: TIMESTAMP | SERVICE_NAME | EVENT_TYPE | LATENCY_MS
            parts = [p.strip() for p in line.split('|')]
            if len(parts) != 4:
                # Skip malformed lines for robustness
                continue

            # Extract data points
            _, service_name, event_type, latency_str = parts

            # Filter by event type if specified
            if event_type_filter and event_type.upper() != event_type_filter.upper():
                continue

            # Remove 'ms' suffix and convert to float
            latency = float(latency_str.lower().replace('ms', ''))

            # Update statistics for the service
            service_stats[service_name]['total_count'] += 1
            service_stats[service_name]['total_latency'] += latency

            if event_type.upper() == 'ERROR':
                service_stats[service_name]['error_count'] += 1

        except ValueError as e:
            # Handle cases where latency is not a number or other parsing failure
            print(f"Warning: Data type error encountered while parsing log line: '{line}' ({e}). Skipping.")
            continue

    # Final summary calculations
    summary = {}
    for service, stats in service_stats.items():
        total_count = stats['total_count']
        if total_count > 0:
            avg_latency = stats['total_latency'] / total_count
            error_rate_value = stats['error_count'] / total_count * 100
        else:
            avg_latency = 0
            error_rate_value = 0

        summary[service] = {
            'total_events': total_count,
            'average_latency_ms': round(avg_latency, 2),
            'error_rate': f"{error_rate_value:.2f}%"
        }

    return summary