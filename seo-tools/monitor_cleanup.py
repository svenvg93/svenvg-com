#!/usr/bin/env python3
"""
Monitor index cleanup progress in Google Search Console
"""

import os
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), '..', 'search-console-credentials.json')
SITE_URL = 'sc-domain:svenvg.com'
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']


def monitor_cleanup():
    """Monitor indexing status and cleanup progress."""
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    service = build('searchconsole', 'v1', credentials=credentials)

    print("=" * 80)
    print("INDEX CLEANUP PROGRESS MONITOR")
    print("=" * 80)

    # Check sitemap status
    print("\n📄 SITEMAP STATUS")
    print("-" * 80)
    try:
        sitemaps = service.sitemaps().list(siteUrl=SITE_URL).execute()
        for sitemap in sitemaps.get('sitemap', []):
            path = sitemap.get('path', 'Unknown')
            last_downloaded = sitemap.get('lastDownloaded', 'Never')

            if last_downloaded != 'Never':
                download_date = datetime.fromisoformat(last_downloaded.replace('Z', '+00:00'))
                days_ago = (datetime.now(download_date.tzinfo) - download_date).days
                status = "🟢 Recent" if days_ago < 7 else "🟡 Stale"
            else:
                status = "🔴 Never fetched"
                days_ago = None

            print(f"\n{path}")
            print(f"  Status: {status}")
            print(f"  Last Downloaded: {last_downloaded}")
            if days_ago is not None:
                print(f"  Days Since Fetch: {days_ago}")

            contents = sitemap.get('contents', [])
            for content in contents:
                content_type = content.get('type', 'unknown')
                submitted = int(content.get('submitted', 0))
                indexed = int(content.get('indexed', 0))

                if submitted > 0:
                    index_rate = (indexed / submitted) * 100
                    print(f"  {content_type}: {indexed}/{submitted} indexed ({index_rate:.1f}%)")

    except Exception as e:
        print(f"Error fetching sitemap status: {e}")

    # Check recent crawl activity
    print("\n\n🤖 RECENT CRAWL ACTIVITY (Last 7 Days)")
    print("-" * 80)

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)

    request = {
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': end_date.strftime('%Y-%m-%d'),
        'dimensions': ['page'],
        'rowLimit': 10
    }

    try:
        response = service.searchanalytics().query(
            siteUrl=SITE_URL, body=request
        ).execute()

        if response.get('rows'):
            print("\nPages with search impressions (showing top 10):")
            for row in response['rows'][:10]:
                url = row['keys'][0]
                impressions = row.get('impressions', 0)
                clicks = row.get('clicks', 0)

                # Shorten URL
                display_url = url.replace('https://svenvg.com', '')[:60]
                print(f"  {display_url}")
                print(f"    Impressions: {impressions}, Clicks: {clicks}")
        else:
            print("  No recent search activity found")

    except Exception as e:
        print(f"Error fetching crawl activity: {e}")

    # Recommendations
    print("\n\n📋 CLEANUP PROGRESS CHECKLIST")
    print("-" * 80)
    print("""
Week 1 (Current):
  [ ] Deploy site with aliases
  [ ] Resubmit sitemap
  [ ] Request reindexing for key URLs
  [ ] Remove old URLs using Removals tool

Week 2:
  [ ] Check sitemap was fetched (last downloaded < 7 days)
  [ ] Verify old URLs are redirecting (not 404)
  [ ] Check index coverage improving

Week 3-4:
  [ ] Monitor index rate improvement
  [ ] Check noindex errors decreasing
  [ ] Verify traffic recovering

To accelerate further:
  • Use URL Inspection daily (10 URLs/day limit)
  • Submit important URLs first
  • Remove unwanted URLs via Removals tool
  • Update content on important pages (triggers recrawl)
""")

    print("\n" + "=" * 80)
    print("View detailed reports:")
    print("  Indexing: https://search.google.com/search-console/index")
    print("  Sitemaps: https://search.google.com/search-console/sitemaps")
    print("  Removals: https://search.google.com/search-console/removals")
    print("=" * 80)


if __name__ == '__main__':
    monitor_cleanup()
