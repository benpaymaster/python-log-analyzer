from collections import defaultdict
from typing import Dict, Any
import re
import multiprocessing

def _parse_log_line(args):
    line, regex, delimiter, start_dt, end_dt, service_names, event_type_filter = args
    from datetime import datetime
    def parse_time(ts):
        try:
            return datetime.fromisoformat(ts)
        except Exception:
            try:
                return datetime.fromtimestamp(float(ts))
            except Exception:
                return None
    if not line or line.startswith('#'):
        return None
    try:
        if regex:
            match = regex.match(line)
            if not match:
                return None
            gd = match.groupdict()
            timestamp_str = gd.get('timestamp')
            service_name = gd.get('service')
            event_type = gd.get('event_type')
            latency_str = gd.get('latency')
        else:
            parts = [p.strip() for p in line.split(delimiter)]
            if len(parts) != 4:
                return None
            timestamp_str, service_name, event_type, latency_str = parts
        # Time window filtering
        if start_dt or end_dt:
            ts_dt = parse_time(timestamp_str)
            if ts_dt is None:
                return None
            if start_dt and ts_dt < start_dt:
                return None
            if end_dt and ts_dt > end_dt:
                return None
        # Service name filtering
        if service_names and service_name not in service_names:
            return None
        # Filter by event type if specified
        if event_type_filter and event_type.upper() != event_type_filter.upper():
            return None
        latency = float(latency_str.lower().replace('ms', ''))
        return {
            'service_name': service_name,
            'timestamp': timestamp_str,
            'event_type': event_type,
            'latency': latency
        }
    except Exception:
        return None

def analyze_logs(log_data: str, event_type_filter: str = None, delimiter: str = '|', log_regex: str = None, start_time: str = None, end_time: str = None, service_names: list = None, top_slowest: int = None, latency_histogram: list = None, detect_anomalies: bool = False, parallel: bool = False) -> Dict[str, Any]:
    """
    Parses a string of simulated infrastructure log data and calculates
    summary statistics: event counts and average latency per service.
    Supports parallel processing for large log files.

    The expected log format is: TIMESTAMP | SERVICE_NAME | EVENT_TYPE | LATENCY_MS
    Or a user-supplied regex with named groups: timestamp, service, event_type, latency

    Args:
        log_data: A string containing newline-separated log entries.
        event_type_filter: If provided, only include events matching this type.
        log_regex: Optional regex pattern for parsing log entries.

    Returns:
        A dictionary containing the calculated summary statistics, including
        'total_events', 'average_latency_ms', and 'error_rate' for each service.
    """
    lines = log_data.strip().split('\n')
    service_stats = defaultdict(lambda: {'total_count': 0, 'total_latency': 0.0, 'error_count': 0, 'latencies': []})

    from datetime import datetime
    def parse_time(ts):
        # Try ISO format, then epoch
        try:
            return datetime.fromisoformat(ts)
        except Exception:
            try:
                return datetime.fromtimestamp(float(ts))
            except Exception:
                return None

    start_dt = parse_time(start_time) if start_time else None
    end_dt = parse_time(end_time) if end_time else None

    regex = re.compile(log_regex) if log_regex else None

    parsed = []
    if parallel:
        with multiprocessing.Pool() as pool:
            args = [(line, regex, delimiter, start_dt, end_dt, service_names, event_type_filter) for line in lines]
            parsed = pool.map(_parse_log_line, args)
        parsed = [p for p in parsed if p]
    else:
        for line in lines:
            result = _parse_log_line((line, regex, delimiter, start_dt, end_dt, service_names, event_type_filter))
            if result:
                parsed.append(result)

    for entry in parsed:
        service_name = entry['service_name']
        latency = entry['latency']
        event_type = entry['event_type']
        timestamp_str = entry['timestamp']
        # Update statistics for the service
        service_stats[service_name]['total_count'] += 1
        service_stats[service_name]['total_latency'] += latency
        service_stats[service_name]['latencies'].append({'timestamp': timestamp_str, 'latency': latency, 'event_type': event_type})

        if event_type.upper() == 'ERROR':
            service_stats[service_name]['error_count'] += 1

    # Final summary calculations
    summary = {}
    import statistics
    for service, stats in service_stats.items():
        total_count = stats['total_count']
        if total_count > 0:
            avg_latency = stats['total_latency'] / total_count
            error_rate_value = stats['error_count'] / total_count * 100
        else:
            avg_latency = 0
            error_rate_value = 0

        # Top-N slowest events
        top_slowest_events = None
        if top_slowest and stats['latencies']:
            sorted_latencies = sorted(stats['latencies'], key=lambda x: x['latency'], reverse=True)
            top_slowest_events = sorted_latencies[:top_slowest]

        # Anomaly detection (z-score > 2)
        anomalies = []
        if detect_anomalies and stats['latencies'] and len(stats['latencies']) > 2:
            latencies = [entry['latency'] for entry in stats['latencies']]
            mean = statistics.mean(latencies)
            stdev = statistics.stdev(latencies)
            for entry in stats['latencies']:
                if stdev > 0 and abs((entry['latency'] - mean) / stdev) > 2:
                    anomalies.append(entry)

        # Latency histogram
        latency_hist = None
        if latency_histogram and stats['latencies']:
            buckets = latency_histogram + [float('inf')]
            bucket_labels = [f"<= {b}" for b in latency_histogram] + ["> {latency_histogram[-1]}"]
            counts = [0] * len(buckets)
            for entry in stats['latencies']:
                latency = entry['latency']
                for i, edge in enumerate(buckets):
                    if latency <= edge:
                        counts[i] += 1
                        break
            latency_hist = dict(zip(bucket_labels, counts))

        summary[service] = {
            'total_events': total_count,
            'average_latency_ms': round(avg_latency, 2),
            'error_rate': f"{error_rate_value:.2f}%"
        }
        if top_slowest_events is not None:
            summary[service]['top_slowest_events'] = top_slowest_events
        if latency_hist is not None:
            summary[service]['latency_histogram'] = latency_hist
        if anomalies:
            summary[service]['anomalies'] = anomalies

    return summary