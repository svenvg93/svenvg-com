#!/usr/bin/env python3
"""
Google Search Console API Client
Fetch search performance data from Google Search Console
"""

import json
from datetime import datetime, timedelta
import os
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuration
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), '..', 'search-console-credentials.json')
SITE_URL = 'sc-domain:svenvg.com'  # Domain property format
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']


def get_service():
    """Create and return Google Search Console service."""
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    service = build('searchconsole', 'v1', credentials=credentials)
    return service


def list_sites():
    """List all sites available in Search Console."""
    service = get_service()
    try:
        sites = service.sites().list().execute()
        print("Sites available in Search Console:")
        for site in sites.get('siteEntry', []):
            print(f"  - {site['siteUrl']} (permission: {site['permissionLevel']})")
        return sites
    except HttpError as error:
        print(f"Error listing sites: {error}")
        return None


def get_search_analytics(site_url, start_date, end_date, dimensions=['query'], row_limit=100):
    """
    Get search analytics data from Search Console.

    Args:
        site_url: The site URL (e.g., 'https://svenvg.com/')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        dimensions: List of dimensions (query, page, country, device, searchAppearance)
        row_limit: Maximum number of rows to return
    """
    service = get_service()

    request = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': dimensions,
        'rowLimit': row_limit
    }

    try:
        response = service.searchanalytics().query(
            siteUrl=site_url, body=request
        ).execute()
        return response
    except HttpError as error:
        print(f"Error fetching analytics: {error}")
        return None


def format_results(response, dimensions):
    """Format and display search analytics results."""
    if not response or 'rows' not in response:
        print("No data available for the specified period.")
        return

    print(f"\nSearch Analytics Results ({len(response['rows'])} rows):")
    print("-" * 80)

    # Header
    headers = dimensions + ['clicks', 'impressions', 'ctr', 'position']
    print(f"{headers[0]:<40} {'Clicks':<10} {'Impr.':<10} {'CTR':<8} {'Pos':<6}")
    print("-" * 80)

    # Data rows
    for row in response['rows']:
        keys = row.get('keys', [])
        clicks = row.get('clicks', 0)
        impressions = row.get('impressions', 0)
        ctr = row.get('ctr', 0) * 100
        position = row.get('position', 0)

        # Truncate first dimension if too long
        first_key = keys[0][:37] + '...' if len(keys[0]) > 40 else keys[0]

        print(f"{first_key:<40} {clicks:<10} {impressions:<10} {ctr:<7.2f}% {position:<6.1f}")


def main():
    """Main function to demonstrate Search Console API usage."""
    print("Google Search Console API Client")
    print("=" * 80)

    # List available sites
    print("\n1. Listing available sites:")
    list_sites()

    # Get last 30 days of search analytics
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    print(f"\n2. Fetching search analytics for {SITE_URL}")
    print(f"   Period: {start_date} to {end_date}")

    # Get top queries
    print("\n--- Top Queries ---")
    response = get_search_analytics(
        SITE_URL,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        dimensions=['query'],
        row_limit=25
    )
    format_results(response, ['query'])

    # Get top pages
    print("\n--- Top Pages ---")
    response = get_search_analytics(
        SITE_URL,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        dimensions=['page'],
        row_limit=25
    )
    format_results(response, ['page'])

    # Get performance by country
    print("\n--- Performance by Country ---")
    response = get_search_analytics(
        SITE_URL,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        dimensions=['country'],
        row_limit=10
    )
    format_results(response, ['country'])

    # Get performance by device
    print("\n--- Performance by Device ---")
    response = get_search_analytics(
        SITE_URL,
        start_date.strftime('%Y-%m-%d'),
        end_date.strftime('%Y-%m-%d'),
        dimensions=['device'],
        row_limit=10
    )
    format_results(response, ['device'])


if __name__ == '__main__':
    main()
