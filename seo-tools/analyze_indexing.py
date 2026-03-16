#!/usr/bin/env python3
"""
Comprehensive indexing analysis
Compare sitemap URLs with actually indexed pages getting traffic
"""

import requests
from datetime import datetime, timedelta
import os
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
import xml.etree.ElementTree as ET

# Configuration
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), '..', 'search-console-credentials.json')
SITE_URL = 'sc-domain:svenvg.com'
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']


def get_service():
    """Create and return Google Search Console service."""
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    service = build('searchconsole', 'v1', credentials=credentials)
    return service


def get_sitemap_urls():
    """Fetch and parse all URLs from the sitemap."""
    response = requests.get('https://svenvg.com/sitemap.xml')
    root = ET.fromstring(response.content)

    # XML namespace for sitemap
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    urls = []
    for url_elem in root.findall('ns:url', ns):
        loc = url_elem.find('ns:loc', ns)
        if loc is not None:
            urls.append(loc.text)

    return urls


def get_pages_with_traffic():
    """Get all pages that have received impressions or clicks."""
    service = get_service()

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)  # Last 90 days

    request = {
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': end_date.strftime('%Y-%m-%d'),
        'dimensions': ['page'],
        'rowLimit': 25000  # Get all pages
    }

    try:
        response = service.searchanalytics().query(
            siteUrl=SITE_URL, body=request
        ).execute()

        pages = {}
        for row in response.get('rows', []):
            url = row['keys'][0]
            pages[url] = {
                'clicks': row.get('clicks', 0),
                'impressions': row.get('impressions', 0),
                'ctr': row.get('ctr', 0),
                'position': row.get('position', 0)
            }

        return pages
    except Exception as e:
        print(f"Error fetching pages: {e}")
        return {}


def main():
    """Main analysis function."""
    print("=" * 80)
    print("COMPREHENSIVE INDEXING ANALYSIS")
    print("=" * 80)

    # Get sitemap URLs
    print("\n1. Fetching sitemap URLs...")
    sitemap_urls = get_sitemap_urls()
    print(f"   Found {len(sitemap_urls)} URLs in sitemap")

    # Get pages with traffic
    print("\n2. Fetching pages with search traffic (last 90 days)...")
    pages_with_traffic = get_pages_with_traffic()
    print(f"   Found {len(pages_with_traffic)} pages with impressions/clicks")

    # Analysis
    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)

    # Find pages in sitemap that are getting traffic (indexed and performing)
    indexed_from_sitemap = []
    for url in sitemap_urls:
        if url in pages_with_traffic:
            indexed_from_sitemap.append(url)

    # Find pages getting traffic but NOT in sitemap
    not_in_sitemap = []
    for url in pages_with_traffic:
        if url not in sitemap_urls:
            not_in_sitemap.append(url)

    # Find pages in sitemap but NOT getting traffic
    not_getting_traffic = []
    for url in sitemap_urls:
        if url not in pages_with_traffic:
            not_getting_traffic.append(url)

    print(f"\n📊 Summary:")
    print(f"   • Sitemap URLs: {len(sitemap_urls)}")
    print(f"   • Indexed & Getting Traffic: {len(indexed_from_sitemap)}")
    print(f"   • In Sitemap but No Traffic: {len(not_getting_traffic)}")
    print(f"   • Getting Traffic but Not in Sitemap: {len(not_in_sitemap)}")

    # Show indexed pages performing well
    print(f"\n✅ TOP PERFORMING PAGES ({min(10, len(indexed_from_sitemap))}):")
    sorted_pages = sorted(
        [(url, pages_with_traffic[url]) for url in indexed_from_sitemap],
        key=lambda x: x[1]['impressions'],
        reverse=True
    )[:10]

    for url, stats in sorted_pages:
        # Shorten URL for display
        display_url = url.replace('https://svenvg.com', '')[: 60]
        print(f"   {display_url}")
        print(f"      Clicks: {stats['clicks']}, Impressions: {stats['impressions']}, Pos: {stats['position']:.1f}")

    # Show pages in sitemap but not getting traffic
    if not_getting_traffic:
        print(f"\n⚠️  PAGES IN SITEMAP BUT NO TRAFFIC ({len(not_getting_traffic)}):")
        print(f"   These pages may not be indexed or need optimization:")

        for url in not_getting_traffic[:15]:  # Show first 15
            display_url = url.replace('https://svenvg.com', '')[:70]
            print(f"   • {display_url}")

        if len(not_getting_traffic) > 15:
            print(f"   ... and {len(not_getting_traffic) - 15} more")

    # Show pages getting traffic but not in sitemap
    if not_in_sitemap:
        print(f"\n💡 PAGES WITH TRAFFIC BUT NOT IN SITEMAP ({len(not_in_sitemap)}):")
        for url in not_in_sitemap[:10]:
            stats = pages_with_traffic[url]
            display_url = url.replace('https://svenvg.com', '')[:60]
            print(f"   {display_url}")
            print(f"      Clicks: {stats['clicks']}, Impressions: {stats['impressions']}")

    # Recommendations
    print("\n" + "=" * 80)
    print("ACTIONABLE RECOMMENDATIONS")
    print("=" * 80)

    index_rate = len(indexed_from_sitemap) / len(sitemap_urls) * 100 if sitemap_urls else 0

    print(f"\nCurrent Index Rate: {index_rate:.1f}% of sitemap URLs getting traffic")

    if index_rate < 50:
        print("\n🔴 CRITICAL: Low indexing rate detected!")
        print("\nImmediate actions:")
        print("   1. Check Google Search Console → Pages → 'Why pages aren't indexed'")
        print("   2. Look for 'Crawled - currently not indexed' or 'Discovered - not indexed'")
        print("   3. Verify pages are accessible (not behind authentication)")
        print("   4. Check for duplicate content or thin content issues")
        print("   5. Ensure proper canonical tags are set")

    elif index_rate < 80:
        print("\n🟡 MODERATE: Some pages not performing")
        print("\nRecommended actions:")
        print("   1. Review pages without traffic for quality and relevance")
        print("   2. Improve internal linking to boost crawlability")
        print("   3. Update content on underperforming pages")
        print("   4. Consider adding more unique, valuable content")

    else:
        print("\n✅ GOOD: Strong indexing rate")
        print("\nContinue optimizing:")
        print("   1. Focus on improving rankings for existing indexed pages")
        print("   2. Add fresh content regularly")
        print("   3. Build quality backlinks")

    if not_getting_traffic:
        print("\n📋 Priority Pages to Check:")
        print("   The following page types in your sitemap have no traffic:")

        # Categorize by type
        categories = set()
        tags = set()
        posts = set()
        other = set()

        for url in not_getting_traffic:
            if '/categories/' in url:
                categories.add(url)
            elif '/tags/' in url:
                tags.add(url)
            elif '/posts/' in url:
                posts.add(url)
            else:
                other.add(url)

        if categories:
            print(f"   • Category pages: {len(categories)} (consider noindex for these)")
        if tags:
            print(f"   • Tag pages: {len(tags)} (consider noindex for these)")
        if posts:
            print(f"   • Blog posts: {len(posts)} (need content optimization!)")
        if other:
            print(f"   • Other pages: {len(other)}")

    print("\n" + "=" * 80)
    print("Next Steps:")
    print("   1. Visit Google Search Console → Pages for detailed coverage report")
    print("   2. Focus on optimizing blog posts without traffic")
    print("   3. Consider removing or noindexing non-essential pages (tags, categories)")
    print("   4. Monitor indexing improvements over the next 2-4 weeks")
    print("=" * 80)


if __name__ == '__main__':
    main()
