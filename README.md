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

1.  **Clone the Repository:**

    ```bash
    git clone [your-github-repo-link]
    cd infra-log-analyzer
    
2.  **Execute the Script:**

    ```bash
    python run.py
    
The script will load the data, print the analysis summary, and then execute the unit tests for validation.