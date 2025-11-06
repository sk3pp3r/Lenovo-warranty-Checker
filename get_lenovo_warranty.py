#!/usr/bin/env python3
"""
get_lenovo_warranty.py
Get Lenovo warranty information via web scrape using serial number
Usage:
  Single: python get_lenovo_warranty.py <serial_number>
  Bulk:   python get_lenovo_warranty.py -f devices.txt [-o output.csv]
  Bulk + summary by year:
          python get_lenovo_warranty.py -f devices.txt --summary-by-year [--summary-output summary.csv]

Haim Cohen 2025
LinkedIn: https://www.linkedin.com/in/haimc/
"""

import re
import sys
import argparse
import csv
import warnings
from typing import Dict, Optional, List
from datetime import datetime
from collections import defaultdict

# Suppress urllib3 OpenSSL warnings
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL 1.1.1+')

import requests

def get_lenovo_warranty(serial_number: str) -> Dict[str, str]:
    """
    Fetch and parse Lenovo warranty information for a given serial number.
    Returns the LATEST warranty end date.

    Args:
        serial_number: The device serial number

    Returns:
        Dictionary with serial number and latest warranty end date
    """
    url = f"https://csp.lenovo.com/ibapp/il/WarrantyStatus.jsp?serial={serial_number}"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        html_content = response.text

        # Extract all warranty end dates
        end_dates = re.findall(r'End Date:&nbsp;</b>([^<]+)', html_content, re.IGNORECASE)

        # Clean and parse dates
        valid_dates = []
        for date_str in end_dates:
            date_str = date_str.strip()
            if date_str and date_str != 'N/A':
                try:
                    parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                    valid_dates.append((parsed_date, date_str))
                except ValueError:
                    # Keep string for completeness, but won't be sortable by date
                    valid_dates.append((None, date_str))

        # Find the latest date
        if valid_dates:
            valid_dates.sort(key=lambda x: x[0] if x[0] else datetime.min)
            latest_date = valid_dates[-1][1]
        else:
            latest_date = 'N/A'

        return {
            'SerialNumber': serial_number,
            'WarrantyTill': latest_date
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching warranty for {serial_number}: {e}", file=sys.stderr)
        return {
            'SerialNumber': serial_number,
            'WarrantyTill': 'ERROR'
        }

def summarize_by_year(results: List[Dict[str, str]], summary_csv: Optional[str] = None):
    """
    Build a summary table by EndDate year: Total / Active / Expired.

    Args:
        results: list of dicts with keys ['SerialNumber', 'WarrantyTill']
        summary_csv: optional path to write CSV (Year,Total,Active,Expired)
    """
    today = datetime.now()
    year_counts = defaultdict(lambda: {"Total": 0, "Active": 0, "Expired": 0})

    for row in results:
        end_str = row.get('WarrantyTill', '')
        if not end_str or end_str in ('N/A', 'ERROR'):
            continue
        try:
            end_dt = datetime.strptime(end_str, '%Y-%m-%d')
        except ValueError:
            # Unparsable date — skip from year stats
            continue

        year = str(end_dt.year)
        year_counts[year]["Total"] += 1
        if end_dt >= today:
            year_counts[year]["Active"] += 1
        else:
            year_counts[year]["Expired"] += 1

    # Print table
    print("\nSummary by Year")
    print("-" * 48)
    print(f"{'Year':<6} {'Total':<8} {'Active':<8} {'Expired':<8}")
    for y in sorted(year_counts.keys()):
        data = year_counts[y]
        print(f"{y:<6} {data['Total']:<8} {data['Active']:<8} {data['Expired']:<8}")

    # Optional CSV export
    if summary_csv:
        with open(summary_csv, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Year", "Total", "Active", "Expired"])
            for y in sorted(year_counts.keys()):
                d = year_counts[y]
                writer.writerow([y, d["Total"], d["Active"], d["Expired"]])
        print(f"\nSaved summary CSV → {summary_csv}")

def process_bulk_lookup(input_file: str, output_file: Optional[str] = None,
                        do_summary_by_year: bool = False, summary_output: Optional[str] = None):
    """
    Process multiple serial numbers from a file.

    Args:
        input_file: Path to file containing serial numbers (one per line)
        output_file: Optional output CSV file path
        do_summary_by_year: If True, print summary by year
        summary_output: Optional CSV file for the summary
    """
    all_results = []
    active_count = 0
    expired_count = 0
    today = datetime.now()

    with open(input_file, 'r') as f:
        for line in f:
            serial = line.strip()

            # Skip empty lines and comments
            if not serial or serial.startswith('#'):
                continue

            warranty_info = get_lenovo_warranty(serial)
            all_results.append(warranty_info)

            # Count active vs expired (global)
            warranty_date = warranty_info['WarrantyTill']
            if warranty_date not in ('N/A', 'ERROR'):
                try:
                    warranty_end = datetime.strptime(warranty_date, '%Y-%m-%d')
                    if warranty_end >= today:
                        active_count += 1
                    else:
                        expired_count += 1
                except ValueError:
                    pass

    # Display as table
    print(f"\n{'SerialNumber':<15} {'WarrantyTill':<15}")
    print("-" * 32)
    for result in all_results:
        print(f"{result['SerialNumber']:<15} {result['WarrantyTill']:<15}")

    # Display summary (overall)
    print("\n" + "=" * 32)
    print(f"Warranty active: {active_count}")
    print(f"Warranty ended: {expired_count}")

    # Save main results if requested
    if output_file:
        with open(output_file, 'w', newline='') as f:
            fieldnames = ['SerialNumber', 'WarrantyTill']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"Saved detailed results CSV → {output_file}")

    # Yearly summary if requested
    if do_summary_by_year:
        summarize_by_year(all_results, summary_output)

def main():
    parser = argparse.ArgumentParser(
        description='Get Lenovo warranty information by serial number',
        add_help=False
    )
    parser.add_argument(
        'serial',
        nargs='?',
        help='Device serial number'
    )
    parser.add_argument(
        '-f', '--file',
        help='Input file containing serial numbers (one per line)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output CSV file (only used with -f option)'
    )
    parser.add_argument(
        '--summary-by-year',
        action='store_true',
        help='Print a summary table grouped by EndDate year (bulk mode only)'
    )
    parser.add_argument(
        '--summary-output',
        help='Optional CSV path to export the yearly summary table'
    )
    parser.add_argument(
        '-h', '--help',
        action='store_true',
        help='Show this help message and exit'
    )

    args = parser.parse_args()

    # Show custom help/credits when no parameters or -h/--help
    if args.help or (not args.file and not args.serial):
        print("=" * 70)
        print("  Lenovo Warranty Checker")
        print("  Haim Cohen 2025")
        print("  LinkedIn: https://www.linkedin.com/in/haimc/")
        print("=" * 70)
        print("\nGet Lenovo warranty information via web scrape using serial number")
        print("\nUsage:")
        print("  Single: python get_lenovo_warranty.py <serial_number>")
        print("  Bulk:   python get_lenovo_warranty.py -f devices.txt [-o output.csv]")
        print("  Bulk + summary by year:")
        print("          python get_lenovo_warranty.py -f devices.txt --summary-by-year")
        print("          [--summary-output summary.csv]")
        print("\nOptions:")
        print("  serial                Device serial number")
        print("  -f, --file FILE       Input file containing serial numbers (one per line)")
        print("  -o, --output OUTPUT   Output CSV file (only used with -f option)")
        print("  --summary-by-year     Print a summary table grouped by EndDate year")
        print("  --summary-output FILE Optional CSV path to export the yearly summary")
        print("  -h, --help            Show this help message and exit")
        sys.exit(0)

    # Show progress message when processing
    print("\nIn progress, please wait...\n")

    if args.file:
        # Bulk lookup (supports summary)
        process_bulk_lookup(
            args.file,
            args.output,
            do_summary_by_year=args.summary_by_year,
            summary_output=args.summary_output
        )
    elif args.serial:
        # Single lookup
        fieldnames = ['SerialNumber', 'WarrantyTill']
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        warranty_info = get_lenovo_warranty(args.serial)
        writer.writerow(warranty_info)

if __name__ == '__main__':
    main()