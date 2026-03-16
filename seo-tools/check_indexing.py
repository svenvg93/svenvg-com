#!/usr/bin/env python3
"""
Google Search Console - Index Coverage Checker
Check for indexing issues and provide recommendations
"""

import json
from datetime import datetime
import os
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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


def get_sitemaps():
    """Get all sitemaps submitted to Search Console."""
    service = get_service()
    try:
        sitemaps = service.sitemaps().list(siteUrl=SITE_URL).execute()
        return sitemaps.get('sitemap', [])
    except HttpError as error:
        print(f"Error fetching sitemaps: {error}")
        return []


def inspect_url(url):
    """
    Inspect a specific URL for indexing status.
    Note: This requires the URL Inspection API scope.
    """
    service = get_service()
    try:
        # Build the inspection request
        body = {
            'inspectionUrl': url,
            'siteUrl': SITE_URL
        }
        response = service.urlInspection().index().inspect(body=body).execute()
        return response
    except HttpError as error:
        # URL Inspection API may not be available with current scope
        return None


def analyze_sitemaps():
    """Analyze sitemap status and coverage."""
    print("\n" + "=" * 80)
    print("SITEMAP ANALYSIS")
    print("=" * 80)

    sitemaps = get_sitemaps()

    if not sitemaps:
        print("\n⚠️  WARNING: No sitemaps found!")
        print("\nRecommendation:")
        print("  1. Submit your sitemap to Google Search Console")
        print("  2. Your sitemap URL should be: https://svenvg.com/sitemap.xml")
        print("  3. Submit it at: https://search.google.com/search-console")
        return None

    print(f"\nFound {len(sitemaps)} sitemap(s):")

    total_submitted = 0
    total_indexed = 0
    issues = []

    for sitemap in sitemaps:
        path = sitemap.get('path', 'Unknown')
        is_pending = sitemap.get('isPending', False)
        is_sitemap_index = sitemap.get('isSitemapsIndex', False)
        last_submitted = sitemap.get('lastSubmitted', 'Never')
        last_downloaded = sitemap.get('lastDownloaded', 'Never')

        # Get content stats
        contents = sitemap.get('contents', [])

        print(f"\n📄 {path}")
        print(f"   Type: {'Sitemap Index' if is_sitemap_index else 'Sitemap'}")
        print(f"   Status: {'Pending' if is_pending else 'Processed'}")
        print(f"   Last Submitted: {last_submitted}")
        print(f"   Last Downloaded: {last_downloaded}")

        if contents:
            for content in contents:
                content_type = content.get('type', 'unknown')
                submitted = int(content.get('submitted', 0))
                indexed = int(content.get('indexed', 0))

                total_submitted += submitted
                total_indexed += indexed

                print(f"   {content_type}: {indexed}/{submitted} indexed")

                # Check for issues
                if submitted > 0 and indexed == 0:
                    issues.append(f"No pages indexed from {path}")
                elif indexed < submitted * 0.8:  # Less than 80% indexed
                    issues.append(f"Low index rate for {path}: {indexed}/{submitted} ({indexed/submitted*100:.1f}%)")

        # Check if sitemap was recently downloaded
        if last_downloaded != 'Never':
            try:
                downloaded_date = datetime.fromisoformat(last_downloaded.replace('Z', '+00:00'))
                days_ago = (datetime.now(downloaded_date.tzinfo) - downloaded_date).days
                if days_ago > 7:
                    issues.append(f"Sitemap not fetched recently: {path} (last: {days_ago} days ago)")
            except:
                pass

    print(f"\n{'─' * 80}")
    print(f"TOTAL: {total_indexed}/{total_submitted} pages indexed ({total_indexed/total_submitted*100:.1f}%)" if total_submitted > 0 else "TOTAL: No data available")

    if issues:
        print(f"\n⚠️  ISSUES FOUND ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print(f"\n✅ No major sitemap issues detected")

    return {
        'total_submitted': total_submitted,
        'total_indexed': total_indexed,
        'issues': issues,
        'sitemaps': sitemaps
    }


def check_robots_txt():
    """Check if robots.txt might be blocking crawlers."""
    print("\n" + "=" * 80)
    print("ROBOTS.TXT CHECK")
    print("=" * 80)

    import requests

    try:
        response = requests.get('https://svenvg.com/robots.txt', timeout=5)
        if response.status_code == 200:
            print("\n✅ robots.txt found")
            print("\nContent:")
            print("-" * 40)
            print(response.text[:500])  # Show first 500 chars

            # Check for common blocking patterns
            content = response.text.lower()
            issues = []

            if 'disallow: /' in content and 'allow:' not in content:
                issues.append("robots.txt may be blocking all crawlers")
            if 'noindex' in content:
                issues.append("noindex directive found in robots.txt")

            if issues:
                print("\n⚠️  Potential Issues:")
                for issue in issues:
                    print(f"   - {issue}")
            else:
                print("\n✅ No blocking issues detected")

        elif response.status_code == 404:
            print("\nℹ️  No robots.txt file found (this is okay)")
        else:
            print(f"\n⚠️  Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"\n⚠️  Could not fetch robots.txt: {e}")


def provide_recommendations(sitemap_data):
    """Provide actionable recommendations based on analysis."""
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)

    if not sitemap_data:
        print("\n1. Submit your sitemap to Google Search Console")
        print("   - Go to: https://search.google.com/search-console")
        print("   - Navigate to: Sitemaps → Add new sitemap")
        print("   - Submit: sitemap.xml")
        return

    total_submitted = sitemap_data.get('total_submitted', 0)
    total_indexed = sitemap_data.get('total_indexed', 0)
    issues = sitemap_data.get('issues', [])

    recommendations = []

    # Check index ratio
    if total_submitted > 0:
        index_ratio = total_indexed / total_submitted

        if index_ratio < 0.5:
            recommendations.append({
                'priority': 'HIGH',
                'issue': f'Low indexing rate: {index_ratio*100:.1f}%',
                'actions': [
                    'Check for duplicate content across pages',
                    'Ensure pages have unique, quality content',
                    'Review for thin content or doorway pages',
                    'Check for canonical tag issues',
                    'Verify internal linking structure'
                ]
            })
        elif index_ratio < 0.8:
            recommendations.append({
                'priority': 'MEDIUM',
                'issue': f'Moderate indexing rate: {index_ratio*100:.1f}%',
                'actions': [
                    'Review excluded pages in Search Console',
                    'Check for "noindex" tags on important pages',
                    'Improve internal linking to orphaned pages',
                    'Consider adding more quality content'
                ]
            })

    # General best practices
    recommendations.append({
        'priority': 'INFO',
        'issue': 'General SEO Best Practices',
        'actions': [
            'Ensure all important pages are in sitemap',
            'Use structured data (Schema.org) for rich snippets',
            'Optimize page titles and meta descriptions',
            'Improve page load speed (Core Web Vitals)',
            'Ensure mobile-friendliness',
            'Build quality backlinks to important content',
            'Regular content updates and additions'
        ]
    })

    # Display recommendations
    for rec in recommendations:
        priority = rec['priority']
        icon = '🔴' if priority == 'HIGH' else '🟡' if priority == 'MEDIUM' else 'ℹ️'

        print(f"\n{icon} {priority}: {rec['issue']}")
        print("\n   Actions to take:")
        for i, action in enumerate(rec['actions'], 1):
            print(f"   {i}. {action}")


def main():
    """Main function to check indexing issues."""
    print("Google Search Console - Index Coverage Checker")
    print(f"Site: {SITE_URL}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Analyze sitemaps
    sitemap_data = analyze_sitemaps()

    # Check robots.txt
    check_robots_txt()

    # Provide recommendations
    provide_recommendations(sitemap_data)

    print("\n" + "=" * 80)
    print("For detailed coverage reports, visit:")
    print("https://search.google.com/search-console → Pages")
    print("=" * 80)


if __name__ == '__main__':
    main()
