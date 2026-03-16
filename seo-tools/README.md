# SEO Tools & Scripts

Google Search Console analysis and optimization tools for svenvg.com

## 📁 Contents

### 🔧 Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `search_console.py` | View search performance data | `python3 search_console.py` |
| `analyze_indexing.py` | Compare sitemap vs actual traffic | `python3 analyze_indexing.py` |
| `check_indexing.py` | Check sitemap and indexing health | `python3 check_indexing.py` |
| `find_missing_redirects.py` | Find posts needing URL aliases | `python3 find_missing_redirects.py` |
| `check_noindex.py` | Check for noindex tags on pages | `python3 check_noindex.py` |
| `resubmit_sitemap.py` | Force Google to refetch sitemap | `python3 resubmit_sitemap.py` |
| `monitor_cleanup.py` | Monitor index cleanup progress | `python3 monitor_cleanup.py` |
| `request_removals.py` | **NEW!** Helper for removing old URLs | `python3 request_removals.py` |

### 📚 Documentation

| File | Description |
|------|-------------|
| `SEO_ACTION_PLAN.md` | Comprehensive SEO strategy and recommendations |
| `DELETED_POSTS_ACTION_PLAN.md` | Guide for handling deleted/missing posts |
| `FINAL_ACTION_SUMMARY.md` | Summary of all fixes and next steps |
| `URLS_TO_REMOVE.txt` | List of old URLs to remove from Google index |

## 🚀 Quick Start

### Prerequisites

```bash
# Install required Python packages (already done)
pip3 install --user google-auth google-api-python-client requests
```

### Running Scripts

All scripts should be run from the **repository root**, not from inside the `seo-tools/` folder:

```bash
# Correct (from repo root)
cd /Users/sven/Documents/svenvg-com
python3 seo-tools/search_console.py

# Wrong (don't do this)
cd /Users/sven/Documents/svenvg-com/seo-tools
python3 search_console.py  # This will fail - can't find credentials
```

## 📊 Common Workflows

### Daily Check (5 minutes)

```bash
# View recent performance
python3 seo-tools/search_console.py
```

### Weekly Analysis (15 minutes)

```bash
# Check indexing status
python3 seo-tools/analyze_indexing.py

# Monitor cleanup progress
python3 seo-tools/monitor_cleanup.py
```

### After Content Changes (10 minutes)

```bash
# Find posts needing redirects
python3 seo-tools/find_missing_redirects.py

# Resubmit sitemap
python3 seo-tools/resubmit_sitemap.py
```

### Troubleshooting Issues

```bash
# Check for noindex tags
python3 seo-tools/check_noindex.py

# Check sitemap health
python3 seo-tools/check_indexing.py
```

## 🔑 Authentication

Scripts use `search-console-credentials.json` in the repo root (already configured).

**Security:**
- Credentials file is in `.gitignore` (won't be committed)
- Read-only access to Search Console data
- Service account: `search-console-access@svenvg-search-console.iam.gserviceaccount.com`

## 📈 Script Details

### search_console.py

**What it does:**
- Fetches last 30 days of search performance
- Shows top queries, pages, countries, devices
- Great for daily monitoring

**Output:**
- Top 25 search queries with clicks/impressions
- Top 25 pages by impressions
- Performance by country
- Desktop vs mobile breakdown

**Example:**
```
Top Queries
query                                    Clicks     Impr.      CTR      Pos
wireshark remote capture                 12         156        7.69   % 3.5
```

---

### analyze_indexing.py

**What it does:**
- Compares sitemap URLs with pages getting traffic
- Identifies missing redirects
- Shows indexing rate

**Use when:**
- Checking overall SEO health
- After URL restructuring
- Monthly audits

**Output:**
- Sitemap URLs vs indexed pages
- Pages in sitemap but no traffic
- Pages with traffic but not in sitemap
- Actionable recommendations

---

### check_indexing.py

**What it does:**
- Analyzes sitemap submission status
- Checks robots.txt
- Provides indexing recommendations

**Use when:**
- Sitemap issues suspected
- Index coverage dropping
- New to Search Console

---

### find_missing_redirects.py

**What it does:**
- Finds old URLs still getting traffic
- Matches them to current posts
- Suggests aliases to add

**Use when:**
- After renaming posts
- After URL restructuring
- Finding broken redirects

**Output:**
```
📄 /posts/old-url-slug/
   Traffic: 46 clicks, 4762 impressions
   Possible match: 2025-01-05-new-post
   ➜ Add alias to: content/posts/2025-01-05-new-post/index.md
```

---

### check_noindex.py

**What it does:**
- Checks live pages for noindex tags
- Scans meta tags and HTTP headers
- Identifies indexing blocks

**Use when:**
- Google shows "Excluded by noindex"
- Important pages not indexing
- Troubleshooting index coverage

---

### resubmit_sitemap.py

**What it does:**
- Forces Google to refetch sitemap
- Deletes and resubmits via API

**Use when:**
- After deploying sitemap changes
- Sitemap not being fetched
- Accelerating index updates

**Note:** Can also be done manually in Search Console

---

### monitor_cleanup.py

**What it does:**
- Tracks sitemap fetch status
- Shows recent crawl activity
- Provides cleanup checklist

**Use when:**
- Monitoring index cleanup progress
- Tracking weekly improvements
- Verifying sitemap updates

---

## 🎯 Common Tasks

### "Google shows noindex errors"

```bash
# 1. Check which pages have noindex
python3 seo-tools/check_noindex.py

# 2. If URLs are old/renamed, find redirects
python3 seo-tools/find_missing_redirects.py

# 3. After fixing, resubmit sitemap
python3 seo-tools/resubmit_sitemap.py
```

### "My posts aren't indexed"

```bash
# 1. Check overall indexing status
python3 seo-tools/analyze_indexing.py

# 2. Check sitemap health
python3 seo-tools/check_indexing.py

# 3. Look for noindex issues
python3 seo-tools/check_noindex.py
```

### "I renamed some posts"

```bash
# 1. Find which URLs need aliases
python3 seo-tools/find_missing_redirects.py

# 2. Add aliases to frontmatter (manual step)

# 3. Deploy and resubmit
python3 seo-tools/resubmit_sitemap.py
```

### "Monitoring monthly progress"

```bash
# Run these weekly
python3 seo-tools/analyze_indexing.py
python3 seo-tools/monitor_cleanup.py
python3 seo-tools/search_console.py
```

## 📖 Documentation Files

### SEO_ACTION_PLAN.md
Complete SEO strategy including:
- Current statistics
- Technical improvements needed
- Content optimization priorities
- Monitoring schedule
- Expected outcomes

### DELETED_POSTS_ACTION_PLAN.md
Guide for handling 16 deleted posts still getting traffic:
- List of deleted posts with traffic data
- Restore vs remove decision matrix
- Git commands to restore posts
- Timeline and expectations

### FINAL_ACTION_SUMMARY.md
Executive summary:
- All fixes completed
- Changes made
- Deployment instructions
- Expected results

### URLS_TO_REMOVE.txt
List of old URLs to remove from Google index using the Removals Tool:
- Prioritized by traffic
- Ready to copy/paste into Search Console
- Organized by priority (high/medium/low)

## ⚙️ Configuration

All scripts use these settings (from the scripts):

```python
CREDENTIALS_FILE = '../search-console-credentials.json'
SITE_URL = 'sc-domain:svenvg.com'
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']
```

**If you move the credentials file, update this path in all scripts.**

## 🔒 Security Notes

- Credentials file is **read-only** (can't modify Search Console settings)
- Service account has **Owner** permission (required for API access)
- Never commit `search-console-credentials.json` to git
- Scripts only read data, never modify your site

## 🐛 Troubleshooting

### "No such file: search-console-credentials.json"

**Cause:** Running script from wrong directory

**Fix:** Always run from repo root:
```bash
cd /Users/sven/Documents/svenvg-com
python3 seo-tools/script-name.py
```

### "403 Forbidden" or "Permission Denied"

**Cause:** Service account not added to Search Console

**Fix:** Verify service account is added at:
https://search.google.com/search-console → Settings → Users

### "Module not found: google.auth"

**Cause:** Python packages not installed

**Fix:**
```bash
pip3 install --user google-auth google-api-python-client requests
```

### Scripts show old data

**Cause:** Google Search Console data has 2-3 day delay

**Fix:** This is normal - data is always 2-3 days behind

## 📅 Recommended Schedule

| Frequency | Task | Script |
|-----------|------|--------|
| **Daily** | Check performance | `search_console.py` |
| **Weekly** | Full analysis | `analyze_indexing.py`<br>`monitor_cleanup.py` |
| **After changes** | Resubmit sitemap | `resubmit_sitemap.py` |
| **Monthly** | Complete audit | All scripts + documentation |
| **When issues** | Troubleshoot | `check_noindex.py`<br>`find_missing_redirects.py` |

## 🎓 Learning Resources

- [Google Search Console Documentation](https://support.google.com/webmasters)
- [Search Console API Reference](https://developers.google.com/webmaster-tools/v1/api_reference_index)
- [SEO Best Practices](https://developers.google.com/search/docs)

## 📞 Support

For issues with:
- **Scripts:** Check troubleshooting section above
- **Search Console:** Visit https://support.google.com/webmasters
- **Hugo/Site:** Check Hugo documentation

---

**Last Updated:** 2026-03-16
**Site:** svenvg.com
**Service Account:** search-console-access@svenvg-search-console.iam.gserviceaccount.com
