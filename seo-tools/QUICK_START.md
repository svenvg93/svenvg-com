# SEO Tools - Quick Start Guide

## 🚀 Installation Complete!

All SEO analysis tools have been organized in the `seo-tools/` folder.

## 📂 Folder Structure

```
svenvg-com/
├── search-console-credentials.json  (in root, not committed to git)
└── seo-tools/
    ├── README.md                     ⭐ Full documentation
    ├── QUICK_START.md                📖 This file
    ├── SEO_ACTION_PLAN.md            📋 Complete SEO strategy
    ├── DELETED_POSTS_ACTION_PLAN.md  📋 Deleted posts guide
    ├── FINAL_ACTION_SUMMARY.md       📋 Summary of fixes
    ├── URLS_TO_REMOVE.txt            📝 List of URLs to remove
    │
    ├── search_console.py             📊 View performance data
    ├── analyze_indexing.py           📊 Comprehensive analysis
    ├── check_indexing.py             📊 Sitemap health check
    ├── find_missing_redirects.py     🔍 Find posts needing aliases
    ├── check_noindex.py              🔍 Check for noindex tags
    ├── resubmit_sitemap.py           🔄 Resubmit sitemap to Google
    ├── monitor_cleanup.py            📈 Monitor cleanup progress
    └── request_removals.py           🗑️  Helper for URL removals
```

## ⚡ Quick Commands

**Always run from repo root:**

```bash
cd /Users/sven/Documents/svenvg-com

# Daily check
python3 seo-tools/search_console.py

# Weekly analysis
python3 seo-tools/analyze_indexing.py
python3 seo-tools/monitor_cleanup.py

# When you have issues
python3 seo-tools/check_noindex.py
python3 seo-tools/find_missing_redirects.py

# After making changes
python3 seo-tools/resubmit_sitemap.py

# Request URL removals
python3 seo-tools/request_removals.py
```

## 🎯 Next Steps

### 1. Deploy Your Changes (Required!)

```bash
cd /Users/sven/Documents/svenvg-com

# Commit the SEO improvements
git add .
git commit -m "feat: add URL aliases and SEO tools"

# Build and deploy
hugo --gc --minify
git push
```

### 2. After Deployment

```bash
# Resubmit sitemap
python3 seo-tools/resubmit_sitemap.py

# Request removals for old URLs
python3 seo-tools/request_removals.py
```

### 3. Monitor Progress (Weekly)

```bash
# Check indexing improvements
python3 seo-tools/monitor_cleanup.py

# Analyze traffic vs sitemap
python3 seo-tools/analyze_indexing.py
```

## 📚 Documentation

- **README.md** - Complete tool documentation
- **SEO_ACTION_PLAN.md** - Full SEO strategy and timeline
- **DELETED_POSTS_ACTION_PLAN.md** - Guide for deleted posts
- **FINAL_ACTION_SUMMARY.md** - Summary of all changes

## 🔑 Authentication

Scripts use the service account credentials in the repo root:
- File: `search-console-credentials.json`
- Account: `search-console-access@svenvg-search-console.iam.gserviceaccount.com`
- Already configured and working!

## ❓ Troubleshooting

**"No such file: search-console-credentials.json"**
- Make sure you're running from repo root
- Run: `cd /Users/sven/Documents/svenvg-com`

**"Permission denied" or "403 error"**
- Service account needs to be added in Search Console
- Check: https://search.google.com/search-console → Settings → Users

**Scripts show old data**
- Google Search Console data has 2-3 day delay
- This is normal

## 🎉 You're All Set!

1. ✅ Scripts organized in `seo-tools/` folder
2. ✅ All paths configured correctly
3. ✅ Documentation ready
4. ✅ Ready to deploy!

**Start here:** Deploy your changes, then run `python3 seo-tools/resubmit_sitemap.py`
