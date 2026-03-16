#!/usr/bin/env python3
"""
Find which posts need URL aliases/redirects
by comparing traffic URLs with current sitemap
"""

import requests
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
import xml.etree.ElementTree as ET
import os

CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), '..', 'search-console-credentials.json')
SITE_URL = 'sc-domain:svenvg.com'
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']


def get_traffic_urls():
    """Get URLs getting traffic in last 30 days."""
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES
    )
    service = build('searchconsole', 'v1', credentials=credentials)

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    request = {
        'startDate': start_date.strftime('%Y-%m-%d'),
        'endDate': end_date.strftime('%Y-%m-%d'),
        'dimensions': ['page'],
        'rowLimit': 1000
    }

    response = service.searchanalytics().query(siteUrl=SITE_URL, body=request).execute()

    urls_with_stats = {}
    for row in response.get('rows', []):
        url = row['keys'][0]
        # Remove fragments (anchors)
        if '#' in url:
            url = url.split('#')[0]

        if url not in urls_with_stats:
            urls_with_stats[url] = {
                'clicks': 0,
                'impressions': 0
            }

        urls_with_stats[url]['clicks'] += row.get('clicks', 0)
        urls_with_stats[url]['impressions'] += row.get('impressions', 0)

    return urls_with_stats


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


def get_post_directories():
    """Get all post directories and their slugs."""
    posts = {}
    posts_dir = 'content/posts'

    for dirname in os.listdir(posts_dir):
        post_path = os.path.join(posts_dir, dirname)
        if os.path.isdir(post_path):
            index_file = os.path.join(post_path, 'index.md')
            if os.path.exists(index_file):
                # Extract slug from frontmatter if exists, otherwise use directory name
                with open(index_file, 'r') as f:
                    content = f.read()
                    slug = None
                    for line in content.split('\n'):
                        if line.startswith('slug:'):
                            slug = line.split(':', 1)[1].strip().strip('"').strip("'")
                            break

                    if not slug:
                        # Hugo generates slug from directory name (remove date prefix)
                        slug = '-'.join(dirname.split('-')[3:]) if '-' in dirname else dirname

                    posts[dirname] = {
                        'slug': slug,
                        'path': post_path,
                        'url': f'https://svenvg.com/posts/{slug}/'
                    }

    return posts


def main():
    print("=" * 80)
    print("FINDING MISSING URL REDIRECTS/ALIASES")
    print("=" * 80)

    print("\n1. Fetching URLs with traffic (last 30 days)...")
    traffic_urls = get_traffic_urls()
    print(f"   Found {len(traffic_urls)} unique URLs with traffic")

    print("\n2. Fetching sitemap URLs...")
    sitemap_urls = set(get_sitemap_urls())
    print(f"   Found {len(sitemap_urls)} URLs in sitemap")

    print("\n3. Analyzing post directories...")
    posts = get_post_directories()
    print(f"   Found {len(posts)} post directories")

    # Find URLs with traffic but not in sitemap
    missing_in_sitemap = {
        url: stats for url, stats in traffic_urls.items()
        if url not in sitemap_urls and '/posts/' in url and url != 'https://svenvg.com/posts/'
    }

    print("\n" + "=" * 80)
    print("URLS WITH TRAFFIC BUT NOT IN CURRENT SITEMAP")
    print("=" * 80)

    if not missing_in_sitemap:
        print("\n✅ All URLs with traffic are in the sitemap!")
        return

    print(f"\nFound {len(missing_in_sitemap)} URLs that need aliases/redirects:\n")

    # Sort by impressions
    sorted_urls = sorted(
        missing_in_sitemap.items(),
        key=lambda x: x[1]['impressions'],
        reverse=True
    )

    recommendations = []

    for url, stats in sorted_urls:
        path = url.replace('https://svenvg.com', '')
        clicks = stats['clicks']
        impressions = stats['impressions']

        print(f"📄 {path}")
        print(f"   Traffic: {clicks} clicks, {impressions} impressions")

        # Try to find matching post
        old_slug = path.replace('/posts/', '').strip('/')

        # Check if we have a similar post in current structure
        possible_matches = []
        for dirname, post_info in posts.items():
            current_slug = post_info['slug']

            # Check for partial matches
            old_parts = set(old_slug.split('-'))
            current_parts = set(current_slug.split('-'))
            common = old_parts & current_parts

            if len(common) >= 3:  # At least 3 words in common
                similarity = len(common) / max(len(old_parts), len(current_parts))
                possible_matches.append((dirname, current_slug, similarity))

        if possible_matches:
            # Sort by similarity
            possible_matches.sort(key=lambda x: x[2], reverse=True)
            best_match = possible_matches[0]

            print(f"   Possible match: {best_match[0]} (slug: {best_match[1]})")
            print(f"   ➜ Add alias to: content/posts/{best_match[0]}/index.md")
            print(f"   ➜ Alias: {path}")

            recommendations.append({
                'old_url': path,
                'directory': best_match[0],
                'new_slug': best_match[1],
                'impressions': impressions,
                'clicks': clicks
            })
        else:
            print(f"   ⚠️  No matching post found - may be deleted or significantly renamed")
            recommendations.append({
                'old_url': path,
                'directory': 'UNKNOWN',
                'new_slug': 'UNKNOWN',
                'impressions': impressions,
                'clicks': clicks
            })

        print()

    # Summary
    print("=" * 80)
    print("ACTIONABLE RECOMMENDATIONS")
    print("=" * 80)

    print("\nAdd these aliases to your post frontmatter:\n")

    current_dir = None
    for rec in recommendations:
        if rec['directory'] == 'UNKNOWN':
            continue

        if rec['directory'] != current_dir:
            print(f"\n📁 content/posts/{rec['directory']}/index.md")
            print(f"   Add to frontmatter:")
            print(f"   aliases:")
            current_dir = rec['directory']

        print(f"     - {rec['old_url']}")

    print("\n" + "=" * 80)
    print("UNKNOWN/MISSING POSTS")
    print("=" * 80)

    unknown = [rec for rec in recommendations if rec['directory'] == 'UNKNOWN']
    if unknown:
        print("\nThese URLs have traffic but no matching post was found:")
        for rec in unknown:
            print(f"  {rec['old_url']} ({rec['clicks']} clicks, {rec['impressions']} impr)")
    else:
        print("\n✅ All URLs matched to existing posts")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
