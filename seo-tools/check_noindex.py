#!/usr/bin/env python3
"""
Check for noindex issues in Google Search Console
and detect which pages are affected
"""

import requests
from datetime import datetime, timedelta
import os
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
import xml.etree.ElementTree as ET

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), '..', 'search-console-credentials.json')
SITE_URL = 'sc-domain:svenvg.com'
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']


def get_service():
    """Create and return Google Search Console service."""
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    service = build('webmasters', 'v3', credentials=credentials)
    return service


def check_url_for_noindex(url):
    """Fetch a URL and check if it has noindex in meta tags or headers."""
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)

        issues = []

        # Check for noindex in meta tags
        if 'noindex' in response.text.lower():
            # Look for meta robots tag
            if '<meta name="robots"' in response.text.lower() and 'noindex' in response.text.lower():
                issues.append("Meta robots tag contains 'noindex'")
            if '<meta name="googlebot"' in response.text.lower() and 'noindex' in response.text.lower():
                issues.append("Meta googlebot tag contains 'noindex'")

        # Check for noindex in HTTP headers
        if 'X-Robots-Tag' in response.headers:
            if 'noindex' in response.headers['X-Robots-Tag'].lower():
                issues.append(f"X-Robots-Tag header contains 'noindex': {response.headers['X-Robots-Tag']}")

        return {
            'url': url,
            'status_code': response.status_code,
            'issues': issues,
            'has_noindex': len(issues) > 0
        }
    except Exception as e:
        return {
            'url': url,
            'status_code': None,
            'issues': [f"Error fetching: {str(e)}"],
            'has_noindex': None
        }


def get_sitemap_urls():
    """Get all URLs from sitemap."""
    response = requests.get('https://svenvg.com/sitemap.xml')
    root = ET.fromstring(response.content)
    ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    urls = []
    for url_elem in root.findall('ns:url', ns):
        loc = url_elem.find('ns:loc', ns)
        if loc is not None:
            urls.append(loc.text)

    return urls


def main():
    print("=" * 80)
    print("CHECKING FOR NOINDEX ISSUES")
    print("=" * 80)

    print("\n1. Fetching sitemap URLs...")
    sitemap_urls = get_sitemap_urls()
    print(f"   Found {len(sitemap_urls)} URLs in sitemap")

    print("\n2. Checking sample URLs for noindex tags...")
    print("   (Checking first 10 URLs + homepage)\n")

    # Check homepage
    test_urls = ['https://svenvg.com/']

    # Add first 10 sitemap URLs
    test_urls.extend(sitemap_urls[:10])

    noindex_found = []
    clean_urls = []

    for url in test_urls:
        print(f"   Checking: {url}")
        result = check_url_for_noindex(url)

        if result['has_noindex']:
            noindex_found.append(result)
            print(f"      ❌ NOINDEX FOUND!")
            for issue in result['issues']:
                print(f"         - {issue}")
        else:
            clean_urls.append(url)
            print(f"      ✅ Clean (no noindex)")

    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    if noindex_found:
        print(f"\n❌ FOUND {len(noindex_found)} URLs WITH NOINDEX:")
        for result in noindex_found:
            print(f"\n   URL: {result['url']}")
            print(f"   Status: {result['status_code']}")
            for issue in result['issues']:
                print(f"   Issue: {issue}")
    else:
        print(f"\n✅ NO NOINDEX ISSUES FOUND")
        print(f"   All {len(test_urls)} tested URLs are indexable")

    print("\n" + "=" * 80)
    print("GOOGLE SEARCH CONSOLE CHECK")
    print("=" * 80)

    print("\nTo see which pages Google says have 'noindex':")
    print("1. Go to: https://search.google.com/search-console")
    print("2. Select your property: svenvg.com")
    print("3. Click: Pages (left sidebar)")
    print("4. Scroll down to: 'Why pages aren't indexed'")
    print("5. Look for: 'Excluded by 'noindex' tag'")
    print("6. Click on it to see the list of affected URLs")

    print("\n" + "=" * 80)
    print("COMMON CAUSES OF NOINDEX")
    print("=" * 80)

    print("""
1. **Theme Default Behavior**
   - Some Hugo themes add noindex to tag/category pages by default
   - Check theme templates for robots meta tags

2. **Frontmatter Override**
   - Individual posts with 'robots: noindex' in frontmatter
   - Check: grep -r "robots:" content/posts/

3. **Hugo Configuration**
   - Check config for taxonomy/section-specific noindex settings
   - Check: config/_default/hugo.yaml and params.yaml

4. **Cloudflare Workers**
   - If you're using CF Workers, check for X-Robots-Tag headers
   - File: wrangler.jsonc or worker script

5. **Draft Posts**
   - Posts with draft: true are typically excluded
   - Check: grep -r "draft: true" content/posts/
""")

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)

    if noindex_found:
        print("""
1. Check Google Search Console for full list of noindex pages
2. Decide which pages SHOULD be indexed
3. Remove noindex tags from those pages
4. For Hugo theme issues, check theme documentation
5. Rebuild and redeploy your site
6. Request reindexing in Google Search Console
""")
    else:
        print("""
Your sample URLs look good! But you still need to:

1. Check Google Search Console → Pages → 'Excluded by noindex tag'
2. Get the full list of affected URLs
3. Determine if those pages should be indexed
4. Common noindex pages (that's OK):
   - Tag archive pages
   - Category archive pages
   - Paginated pages (page/2/, page/3/, etc.)

5. Important pages that should NOT have noindex:
   - Blog posts
   - Homepage
   - About page
   - Project pages
""")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
