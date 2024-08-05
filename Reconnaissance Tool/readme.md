# Flask Security Tools

This Flask application provides a suite of tools for security testing and analysis, including features for SQL and XSS injection testing, Nmap scanning, and subdomain discovery. It also includes functionalities for processing `robots.txt` files and analyzing form data.

## Features

- **SQL Injection Testing**: Detect potential SQL injection vulnerabilities in web forms.
- **XSS Injection Testing**: Identify potential XSS (Cross-Site Scripting) vulnerabilities in web forms.
- **Nmap Scanner**: Perform various types of Nmap scans to analyze network security.
- **Subdomain Finder**: Extract and analyze subdomains from a list.
- **Robots.txt Processor**: Fetch and process disallowed paths from `robots.txt` files.
- **File Operations**: Manage and analyze text files containing results from various scans and tests.

## Requirements

The project depends on several Python packages. You can install them using the following command:

```bash
sudo pip install -r requirements.txt
```
## Running the Tool
```bash
sudo python main.py
```
## Usage

### SQL Injection
- **Endpoint:** `/sql_injection`
- **Method:** POST
- **Parameters:**
  - `url`: URL of the page to test.
  - `sort_by`: Field to sort the results (`code`, `time`, or `length`).

### XSS Injection
- **Endpoint:** `/xss_injection`
- **Method:** POST
- **Parameters:**
  - `url`: URL of the page to test.
  - `sort_by`: Field to sort the results (`code`, `time`, or `length`).

### Nmap Scanner
- **Endpoint:** `/nmap_scanner`
- **Method:** POST
- **Parameters:**
  - `ip`: IP address to scan.
  - `scan_type`: Type of scan to perform (e.g., Ping Scan, Regular Scan, Intense Scan).

### Subdomain Finder
- **Endpoint:** `/subdomains_finder`
- **Method:** POST
- **Parameters:**
  - `ip`: IP address for which subdomains need to be found.

### Robots.txt Processor
- **Endpoint:** `/robots`
- **Method:** POST
- **Parameters:**
  - `ip`: IP address to fetch `robots.txt` from.

## File Outputs

- **SQL Injection Results:** `sql_injection_output.txt`
- **XSS Injection Results:** `xss_injection_output.txt`
- **Nmap Results:** `nmap_output.txt`

These files are generated during the testing process and can be accessed through the respective endpoints.

## Contributing

Feel free to open issues or submit pull requests if you have improvements or suggestions for the project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
