#!/usr/bin/env python3
"""
Force Google to recrawl sitemap using Search Console API
"""

import os
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), '..', 'search-console-credentials.json')
SITE_URL = 'sc-domain:svenvg.com'
SITEMAP_URL = 'https://svenvg.com/sitemap.xml'
SCOPES = ['https://www.googleapis.com/auth/webmasters']


def resubmit_sitemap():
    """Submit/resubmit sitemap to Google Search Console."""
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    service = build('searchconsole', 'v1', credentials=credentials)

    print("=" * 80)
    print("RESUBMITTING SITEMAP TO GOOGLE SEARCH CONSOLE")
    print("=" * 80)

    try:
        # Try to delete first (in case it exists)
        print(f"\n1. Attempting to delete existing sitemap...")
        try:
            service.sitemaps().delete(
                siteUrl=SITE_URL,
                feedpath=SITEMAP_URL
            ).execute()
            print(f"   ✅ Deleted existing sitemap")
        except Exception as e:
            print(f"   ℹ️  No existing sitemap to delete (this is OK)")

        # Submit the sitemap
        print(f"\n2. Submitting sitemap: {SITEMAP_URL}")
        service.sitemaps().submit(
            siteUrl=SITE_URL,
            feedpath=SITEMAP_URL
        ).execute()
        print(f"   ✅ Sitemap submitted successfully!")

        print("\n" + "=" * 80)
        print("SUCCESS!")
        print("=" * 80)
        print(f"""
Google will now:
1. Fetch your sitemap within 24 hours
2. Discover the new/changed URLs
3. Start recrawling updated pages
4. Remove old URLs from index

Check progress:
https://search.google.com/search-console/sitemaps

Expected timeline:
- Sitemap fetched: Within 24 hours
- Pages recrawled: 1-7 days
- Index fully updated: 2-4 weeks
""")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nYou may need to submit manually via Search Console UI:")
        print("https://search.google.com/search-console/sitemaps")


if __name__ == '__main__':
    resubmit_sitemap()
