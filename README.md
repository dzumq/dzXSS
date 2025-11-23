# dzXSS
dzXSS is a lightweight, fast, and effective automated XSS vulnerability scanner built for bug bounty hunters and enthusiests. It crawls a target, discovers forms, URL parameters, and loose inputs (like search boxes), then intelligently fuzzes them with your payloads. It detects XSS via JavaScript alert() popups.

## Features
Real browser automation with Selenium (detects reflected, stored & DOM-based XSS)
Automatic ChromeDriver management (no version issues ever)
Smart parameter fuzzing with built-in evasion techniques
Real-time output with full vulnerable URLs (copy-paste ready)
Loose input detection (works on sites without proper <form> tags)
Lightweight crawling (focuses on high-risk pages)
Scan summary: vulnerabilities found + time taken
Supports single domain or bulk scanning from a file

## Installation
```bash
git clone https://github.com/yourusername/dzXSS.git
cd dzXSS
pip install -r requirements.txt
```

## Usage
Simply run the script
```bash
python dzXSS.py
```

## Output Example
```bash
VULNERABLE --> https://example.com/search.php?q=%3Cscript%3Ealert(1)%3C/script%3E
NOT VULNERABLE --> https://example.com/search.php?q=%22%3E%3Cscript%3Ealert(1)%3C/script%3E
VULNERABLE --> https://example.com/profile (stored with payload: <img src=x onerror=alert(1)>)

============================================================
     TARGET IS VULNERABLE TO XSS!
Scan completed in 8.42 seconds. Vulnerabilities found: 3
============================================================
```

## Disclaimer
This tool is for authorized security testing only. Do not scan systems you do not own or have explicit permission to test.

