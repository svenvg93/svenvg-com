#!/usr/bin/env python3
"""
Helper script for requesting URL removals in Google Search Console

Note: Google doesn't provide a public API for the Removals tool,
so this script helps you process removals more efficiently through the UI.
"""

import webbrowser
import time


def read_urls_to_remove():
    """Read URLs from URLS_TO_REMOVE.txt"""
    try:
        with open('seo-tools/URLS_TO_REMOVE.txt', 'r') as f:
            urls = []
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    urls.append(line)
            return urls
    except FileNotFoundError:
        print("❌ URLS_TO_REMOVE.txt not found!")
        print("   Make sure you're running from the repo root:")
        print("   cd /Users/sven/Documents/svenvg-com")
        print("   python3 seo-tools/request_removals.py")
        return []


def main():
    print("=" * 80)
    print("GOOGLE SEARCH CONSOLE - URL REMOVAL HELPER")
    print("=" * 80)

    urls = read_urls_to_remove()

    if not urls:
        print("\n❌ No URLs found to remove")
        return

    print(f"\n📋 Found {len(urls)} URLs to remove\n")

    # Categorize by priority
    high_priority = urls[:5]
    medium_priority = urls[5:10]
    low_priority = urls[10:]

    print("🔴 HIGH PRIORITY (Process first):")
    for i, url in enumerate(high_priority, 1):
        print(f"   {i}. {url}")

    if medium_priority:
        print("\n🟡 MEDIUM PRIORITY:")
        for i, url in enumerate(medium_priority, 1):
            print(f"   {i}. {url}")

    if low_priority:
        print(f"\n🟢 LOW PRIORITY ({len(low_priority)} URLs)")

    print("\n" + "=" * 80)
    print("REMOVAL OPTIONS")
    print("=" * 80)

    print("""
Google Search Console Removals Tool doesn't have a public API,
so you have two options:

OPTION 1: Manual Removal (Recommended for <20 URLs)
  ✅ Fastest for small batches
  ✅ Immediate effect (24-48 hours)
  ⚠️  Manual process (one at a time)

OPTION 2: Let Google Naturally Deindex
  ✅ No manual work
  ✅ Permanent solution
  ⚠️  Slower (3-6 months)

OPTION 3: Use This Script's Interactive Mode
  ✅ Opens removal form automatically
  ✅ Copies URLs to clipboard (if available)
  ⚠️  Still requires clicking "Submit" manually
""")

    choice = input("\nChoose option (1/2/3) or 'q' to quit: ").strip()

    if choice == '1':
        manual_removal_guide(urls)
    elif choice == '2':
        natural_deindex_info()
    elif choice == '3':
        interactive_removal(urls)
    elif choice.lower() == 'q':
        print("\nExiting...")
    else:
        print("\n❌ Invalid choice")


def manual_removal_guide(urls):
    """Provide step-by-step manual removal guide"""
    print("\n" + "=" * 80)
    print("MANUAL REMOVAL GUIDE")
    print("=" * 80)

    print("""
📝 STEP-BY-STEP PROCESS:

1. Open Google Search Console Removals Tool:
   https://search.google.com/search-console/removals

2. For EACH URL below:
   a) Click "New Request"
   b) Paste the URL
   c) Select "Temporarily remove URL from Google"
   d) Click "Next" → "Submit"

⚠️  IMPORTANT:
   • Process 5-10 URLs per day (to avoid rate limits)
   • Start with HIGH PRIORITY URLs first
   • Removals last 6 months, then URL reappears if still crawlable

""")

    # Show URLs with checkboxes
    print("📋 URLS TO PROCESS (copy one at a time):\n")
    for i, url in enumerate(urls, 1):
        priority = "🔴 HIGH" if i <= 5 else "🟡 MED" if i <= 10 else "🟢 LOW"
        print(f"[ ] {priority} - {url}")

    print("\n" + "=" * 80)

    open_tool = input("\nOpen Removals Tool in browser now? (y/n): ").strip().lower()
    if open_tool == 'y':
        webbrowser.open('https://search.google.com/search-console/removals')
        print("\n✅ Opened Removals Tool in your browser")
        print("   Process URLs one at a time from the list above")


def natural_deindex_info():
    """Explain natural deindexing"""
    print("\n" + "=" * 80)
    print("NATURAL DEINDEXING (DO NOTHING OPTION)")
    print("=" * 80)

    print("""
If you choose not to manually remove URLs, here's what happens:

TIMELINE:
  Week 1-2:   Google continues showing old URLs
  Week 3-4:   Some URLs start dropping from index
  Month 2-3:  Most 404 URLs removed from index
  Month 4-6:  All 404 URLs fully deindexed

PROS:
  ✅ Zero manual work required
  ✅ Permanent solution (URLs won't reappear)
  ✅ Natural, organic cleanup

CONS:
  ⚠️  Slow process (3-6 months)
  ⚠️  Poor user experience (404 errors in search)
  ⚠️  Potential SEO impact during cleanup

RECOMMENDATION:
  • Use manual removal for HIGH PRIORITY URLs (top 5)
  • Let natural deindexing handle LOW PRIORITY URLs

This balances time investment with user experience.
""")


def interactive_removal(urls):
    """Interactive mode - opens browser for each URL"""
    print("\n" + "=" * 80)
    print("INTERACTIVE REMOVAL MODE")
    print("=" * 80)

    print("""
This mode will:
1. Open the Removals Tool in your browser
2. Show you each URL to remove
3. You manually submit each one

""")

    start = input("Process HIGH PRIORITY URLs now? (y/n): ").strip().lower()
    if start != 'y':
        print("\nCancelled.")
        return

    # Open removals tool
    print("\n✅ Opening Google Search Console Removals Tool...")
    webbrowser.open('https://search.google.com/search-console/removals')
    time.sleep(2)

    # Process high priority URLs
    high_priority = urls[:5]

    print("\n" + "=" * 80)
    print(f"PROCESSING {len(high_priority)} HIGH PRIORITY URLS")
    print("=" * 80)

    for i, url in enumerate(high_priority, 1):
        print(f"\n🔴 URL {i}/{len(high_priority)}:")
        print(f"   {url}")
        print("\n   Steps:")
        print("   1. Click 'New Request' in browser")
        print(f"   2. Paste: {url}")
        print("   3. Select 'Temporarily remove URL from Google'")
        print("   4. Click 'Next' → 'Submit'")

        # Try to copy to clipboard (requires pyperclip)
        try:
            import pyperclip
            pyperclip.copy(url)
            print(f"\n   ✅ URL copied to clipboard!")
        except ImportError:
            print(f"\n   ℹ️  (Install pyperclip for auto-copy: pip3 install pyperclip)")

        if i < len(high_priority):
            next_url = input(f"\n   Press Enter when done to continue to next URL... ")
        else:
            print(f"\n   ✅ All HIGH PRIORITY URLs processed!")

    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)

    print(f"""
Completed: {len(high_priority)} high priority URLs removed

TOMORROW: Process medium priority URLs
  • Run: python3 seo-tools/request_removals.py
  • Process URLs 6-10 from the list

WEEKLY: Monitor progress
  • Run: python3 seo-tools/monitor_cleanup.py
  • Check removal status in Search Console

URLS remaining: {len(urls) - len(high_priority)}
""")


if __name__ == '__main__':
    main()
