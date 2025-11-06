# Lenovo Warranty Checker

A Python tool to check Lenovo warranty information via web scraping using device serial numbers. Supports both single device lookups and bulk processing with detailed reporting.

<img width="710" height="830" alt="image" src="https://github.com/user-attachments/assets/23c3fa71-1d39-4a0c-95fc-8de8fff2ddfd" />


## Features

- ✅ Single device warranty lookup
- ✅ Bulk processing from file
- ✅ CSV export of results
- ✅ Yearly warranty summary with active/expired counts
- ✅ Clean, formatted console output
- ✅ Error handling for failed lookups

## Requirements

- Python 3.6 or higher
- `requests` library

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/lenovo-warranty-checker.git
cd lenovo-warranty-checker
```

2. Install dependencies:
```bash
pip3 install requests
```

## Usage

### Single Device Lookup

Check warranty for a single device by serial number:

```bash
python3 get_lenovo_warranty.py <serial_number>
```

Example:
```bash
python3 get_lenovo_warranty.py ABC123XYZ
```

Output:
```
SerialNumber,WarrantyTill
ABC123XYZ,2026-12-31
```

### Bulk Lookup

Process multiple devices from a text file (one serial number per line):

```bash
python3 get_lenovo_warranty.py -f devices.txt
```

Example `devices.txt`:
```
ABC123XYZ
DEF456UVW
GHI789RST
```

### Bulk Lookup with CSV Export

Save results to a CSV file:

```bash
python3 get_lenovo_warranty.py -f devices.txt -o output.csv
```

### Yearly Summary Report

Generate a summary grouped by warranty end date year:

```bash
python3 get_lenovo_warranty.py -f devices.txt --summary-by-year
```

Output example:
```
Summary by Year
------------------------------------------------
Year   Total    Active   Expired
2024   15       0        15
2025   23       23       0
2026   42       42       0
2027   18       18       0
```

### Export Yearly Summary to CSV

Save the yearly summary to a separate CSV file:

```bash
python3 get_lenovo_warranty.py -f devices.txt --summary-by-year --summary-output summary.csv
```

## Command Line Options

| Option | Description |
|--------|-------------|
| `serial` | Device serial number (positional argument) |
| `-f, --file FILE` | Input file containing serial numbers (one per line) |
| `-o, --output OUTPUT` | Output CSV file for detailed results (bulk mode only) |
| `--summary-by-year` | Print summary table grouped by warranty end date year |
| `--summary-output FILE` | Export yearly summary to CSV file |
| `-h, --help` | Show help message and exit |

## Input File Format

The input file should contain one serial number per line. Empty lines and lines starting with `#` are ignored.

Example:
```
# Production laptops
ABC123XYZ
DEF456UVW

# Development machines
GHI789RST
JKL012MNO
```

## Output Formats

### Console Output (Bulk Mode)
```
SerialNumber    WarrantyTill
--------------------------------
ABC123XYZ       2026-12-31
DEF456UVW       2025-06-15
GHI789RST       N/A

================================
Warranty active: 2
Warranty ended: 0
```

### CSV Output (Detailed Results)
```csv
SerialNumber,WarrantyTill
ABC123XYZ,2026-12-31
DEF456UVW,2025-06-15
GHI789RST,N/A
```

### CSV Output (Yearly Summary)
```csv
Year,Total,Active,Expired
2025,23,23,0
2026,42,42,0
2027,18,18,0
```

## Building Standalone Executable

You can compile the script into a standalone executable using PyInstaller:

1. Install PyInstaller:
```bash
pip3 install pyinstaller
```

2. Build the executable:
```bash
pyinstaller --onefile --name lenovo-warranty --clean get_lenovo_warranty.py
```

3. The executable will be created in the `dist/` folder:
```bash
./dist/lenovo-warranty -f devices.txt --summary-by-year
```

## Error Handling

- **Network errors**: If the Lenovo server is unreachable, the warranty will be marked as `ERROR`
- **Invalid serial numbers**: If no warranty information is found, the warranty will be marked as `N/A`
- **Unparseable dates**: Any dates that cannot be parsed are excluded from year-based statistics

## Notes

- The script fetches warranty information from Lenovo's official warranty status page
- It extracts the **latest** warranty end date if multiple warranties exist
- Processing time depends on network speed and number of devices
- Rate limiting may apply for very large bulk operations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Credits

**Haim Cohen** - 2025  
LinkedIn: [https://www.linkedin.com/in/haimc/](https://www.linkedin.com/in/haimc/)

## Disclaimer

This tool is for informational purposes only. Warranty information is scraped from Lenovo's public warranty status page. Always verify warranty details directly with Lenovo for official confirmation.
