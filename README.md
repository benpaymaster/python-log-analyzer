# 📊 Simple Infrastructure Log Analyzer

A lightweight Python tool demonstrating strong coding fundamentals, commitment to testable code, and experience relevant to Production Engineering and Infrastructure Monitoring.

This utility parses standardized log entries to calculate critical operational metrics like **average latency** and **error rates** per service, which is essential for maintaining and optimizing complex systems.

## 🎯 Key Features

  * **Log Parsing:** Extracts structured data (Service Name, Event Type, Latency) from semi-structured log entries.
  * **Metric Calculation:** Computes:
      * Total Event Count
      * Average Latency (in milliseconds)
      * Error Rate (%)
  * **Quality Assurance:** Includes dedicated unit tests to ensure the core logic is reliable and reproducible.

## 💻 Technical Stack

  * **Language:** Python 3.x
  * **Libraries:** Standard Library (`collections`, `json`, `unittest`)

This project demonstrates proficiency in Python and is structured as a proper Python package, reflecting best practices in software development.

## 🏗️ Project Structure

infra-log-analyzer/
├── log_analyzer/
│   ├── __init__.py       # Makes it a Python package
│   ├── analyzer.py       # Core log parsing and calculation logic
│   └── tests.py          # Unit tests for the analyzer logic
├── logs/
│   └── mock_data.txt     # Simulated input data for demonstration
└── run.py                # Main script to execute the tool and run tests


## ▶️ How to Run

1. **Clone the Repository:**
  ```bash
  git clone [your-github-repo-link]
  cd infra-log-analyzer
  ```

2. **Run the Analyzer (default log file):**
  ```bash
  python3 run.py
  ```

3. **Specify a Custom Log File:**
  ```bash
  python3 run.py --file path/to/your/logfile.txt
  ```

4. **Custom Log Format/Delimiter (auto-detect by default):**
  ```bash
  python3 run.py --delimiter ','
  python3 run.py --delimiter $'\t'  # For tab-delimited logs
  python3 run.py                    # Auto-detects delimiter from log file
  ```

5. **Stream Logs from Another Process:**
  ```bash
  tail -f logs/mock_data.txt | python3 run.py --stream
  ```

6. **Save the Summary Report to a JSON File:**
  ```bash
  python3 run.py --output summary.json
  ```

7. **Export the Summary Report to CSV:**
  ```bash
  python3 run.py --csv-output summary.csv
  ```

8. **Filter Analysis by Event Type (e.g., ERROR, SUCCESS, INFO):**
  ```bash
  python3 run.py --event-type ERROR
  python3 run.py --event-type SUCCESS
  ```

9. **Filter by Service Name(s):**
  ```bash
  python3 run.py --service DataIngest,RiskEngine
  ```

10. **Filter by Time Window:**
  ```bash
  python3 run.py --start-time '2025-01-01T00:00:00' --end-time '2025-12-31T23:59:59'
  ```

11. **Show Top-N Slowest Events per Service:**
  ```bash
  python3 run.py --top-slowest 3
  ```

12. **Show Latency Histogram per Service:**
  ```bash
  python3 run.py --latency-histogram '0,50,100,200,500'
  ```

13. **Set Custom Alert Thresholds:**
  ```bash
  python3 run.py --error-threshold 10 --latency-threshold 50
  ```
  ```

---

## 🚦 Features

- **Log Parsing:** Reads logs from a file or real-time stream (stdin).
- **Configurable Input:** Use `--file` to specify any log file.
- **Real-Time Streaming:** Use `--stream` to process logs piped from another process.
- **Alerting:** Prints alerts if error rate or latency exceeds thresholds.
- **Overall Summary:** Prints total events, overall average latency, and error rate.
- **Export:** Use `--output` to save the summary as a JSON file.
- **Log Level Filtering:** Use `--event-type` to filter analysis by event type (e.g., ERROR, SUCCESS, INFO).
- **Service Name Filtering:** Use `--service` to analyze only specific services.
- **Time Window Filtering:** Use `--start-time` and `--end-time` to restrict analysis to a time range.
- **Top-N Slowest Events:** Use `--top-slowest` to report slowest events per service.
- **Latency Histogram:** Use `--latency-histogram` to print bucketed latency summary per service.
- **Export to CSV:** Use `--csv-output` to save summary as CSV.
- **Configurable Alert Thresholds:** Use `--error-threshold` and `--latency-threshold` to set custom alert levels.
- **Log Format Auto-Detection:** If `--delimiter` is not specified, the tool auto-detects the log format.
- **Unit Tests:** Ensures reliability with `python3 -m unittest log_analyzer/tests.py`.