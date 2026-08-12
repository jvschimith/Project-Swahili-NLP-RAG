# 💾 Data Storage & Management Guide

## Where Your Articles Are Saved

### Current Setup: SQLite Database ✅

**Location:** `data/swahili_knowledge.db`

Your analyzed articles are already being saved here when you check "💾 Save to database" in the dashboard!

---

## 📊 Storage Options Comparison

| Option | Best For | Capacity | Ease | Cost |
|--------|----------|----------|------|------|
| **SQLite** ⭐⭐⭐ | Small-Medium (< 100K articles) | 140 TB max | ✅ Easy | Free |
| **PostgreSQL** ⭐⭐⭐ | Production, research | Unlimited | ⚠️ Moderate | Free |
| **CSV/Parquet Files** ⭐⭐ | Archival, sharing | Unlimited | ✅ Easy | Free |
| **MongoDB** ⭐ | Unstructured data | Unlimited | ⚠️ Moderate | Free |
| **Google Sheets** ⭐ | Quick access | 5M cells | ✅ Easy | Free |
| **Airtable** ⭐⭐ | Non-technical users | 50K records | ✅ Easy | $$ |

---

## 🎯 Recommended Workflow

### **Strategy: SQLite + Monthly Exports**

```
┌─────────────────┐
│  Daily Usage    │  SQLite database
│  (SQLite)       │  - Fast queries
│                 │  - Real-time updates
└────────┬────────┘
         │
         │ Monthly backup
         ▼
┌─────────────────┐
│ Monthly Archive │  Parquet files
│ (Parquet)       │  - Compressed
│                 │  - Long-term storage
└────────┬────────┘
         │
         │ Annual archive
         ▼
┌─────────────────┐
│ Long-term       │  Cloud storage
│ (S3/Drive)      │  - Backup
│                 │  - Disaster recovery
└─────────────────┘
```

---

## 🔧 How to Use

### 1. **Save Articles via Dashboard**

```
1. Go to http://localhost:8501
2. Navigate to "🔗 URL Analysis"
3. Paste Swahili news URL
4. ✅ Check "💾 Save to database"
5. Select category
6. Click "Analyze"
```

**Articles are now in SQLite!**

---

### 2. **Backup Your Database (Weekly/Monthly)**

```bash
# Simple backup
cp data/swahili_knowledge.db data/backups/swahili_$(date +%Y%m%d).db

# Automated backup script
python scripts/backup_articles.py
```

**Creates:**
- `data/backups/articles_20240312_1430.csv` (human-readable)
- `data/backups/articles_20240312_1430.parquet` (compressed)
- `data/backups/database_20240312_1430.db` (full database copy)
- `data/backups/metadata_20240312_1430.json` (statistics)

---

### 3. **Generate Monthly Reports**

```bash
# Current month
python scripts/monthly_report.py

# Specific month
python scripts/monthly_report.py --month 2024-03
```

**Output:**
```
============================================================
MONTHLY REPORT: 2024-03
============================================================

📊 Summary:
  Total Articles: 127
  Total Words: 18,450
  Avg Words/Article: 145

📚 By Category:
  Politics              45 (35.4%)
  Economy               32 (25.2%)
  Sports                28 (22.0%)

😊 By Sentiment:
  Positive              52 (40.9%)
  Neutral               48 (37.8%)
  Negative              27 (21.3%)

🎯 Most Positive Category:
  Economy: 0.35
============================================================
```

**Saves to:** `data/reports/monthly_report_2024-03.json`

---

### 4. **Export for External Analysis**

**Python:**
```python
import pandas as pd
import requests

# Get all articles
response = requests.get("http://localhost:8000/news/articles?limit=10000")
articles = response.json()

# Convert to DataFrame
df = pd.DataFrame(articles)

# Export to various formats
df.to_csv("my_analysis.csv")
df.to_excel("my_analysis.xlsx")
df.to_parquet("my_analysis.parquet")  # Recommended!
df.to_json("my_analysis.json")
```

**R:**
```r
library(arrow)
library(dplyr)

# Read Parquet (efficient)
df <- read_parquet("data/backups/articles_20240312.parquet")

# Analyze
df %>%
  group_by(category, sentiment_label) %>%
  summarize(count = n(), avg_polarity = mean(sentiment_polarity))
```

---

## 📦 Backup Strategies

### **Strategy 1: Local Backups (Daily)**

```bash
# Add to crontab
0 2 * * * cd /path/to/project && python scripts/backup_articles.py
```

**Keep:**
- Last 7 daily backups
- Last 4 weekly backups
- All monthly backups

---

### **Strategy 2: Cloud Backups (Monthly)**

```bash
# Upload to Google Drive
rclone copy data/backups/ gdrive:swahili-news-backups/

# Or AWS S3
aws s3 sync data/backups/ s3://my-bucket/swahili-news/

# Or Dropbox
rclone copy data/backups/ dropbox:swahili-news/
```

---

### **Strategy 3: Git LFS (For Small Datasets)**

```bash
# Install Git LFS
git lfs install

# Track Parquet files
git lfs track "*.parquet"

# Commit
git add data/backups/*.parquet
git commit -m "Monthly backup"
git push
```

---

## 🔍 Querying Your Data

### **SQLite (SQL)**

```bash
# Open database
sqlite3 data/swahili_knowledge.db

# Count articles
SELECT COUNT(*) FROM news;

# Articles by category
SELECT category, COUNT(*) as count
FROM news
GROUP BY category
ORDER BY count DESC;

# Sentiment by category
SELECT 
  category,
  sentiment_label,
  COUNT(*) as count,
  AVG(sentiment_polarity) as avg_polarity
FROM news
GROUP BY category, sentiment_label;
```

---

### **Python (Pandas)**

```python
import pandas as pd
import sqlite3

# Connect to database
conn = sqlite3.connect('data/swahili_knowledge.db')

# Query
df = pd.read_sql_query("SELECT * FROM news", conn)

# Analyze
sentiment_by_cat = df.groupby(['category', 'sentiment_label']).size()
print(sentiment_by_cat)

# Time series
df['date'] = pd.to_datetime(df['created_at'])
df.set_index('date').resample('W')['sentiment_polarity'].mean().plot()
```

---

## 📈 Advanced: PostgreSQL Migration

When you outgrow SQLite (>100K articles):

```bash
# 1. Install PostgreSQL
sudo apt-get install postgresql

# 2. Create database
sudo -u postgres createdb swahili_news

# 3. Update .env
DATABASE_URL=postgresql://user:pass@localhost/swahili_news

# 4. Migrate data
python scripts/migrate_to_postgres.py

# 5. Restart API
uvicorn src.web.api:app --reload
```

**Benefits:**
- ✅ Millions of articles
- ✅ Concurrent access
- ✅ Full-text search
- ✅ Complex analytics

---

## 💡 Storage Estimates

| Articles | SQLite | Parquet | CSV |
|----------|--------|---------|-----|
| 1,000 | 5 MB | 1 MB | 3 MB |
| 10,000 | 50 MB | 10 MB | 30 MB |
| 100,000 | 500 MB | 100 MB | 300 MB |
| 1,000,000 | 5 GB | 1 GB | 3 GB |

**Parquet is 3-5x smaller than CSV!**

---

## 🛡️ Data Security

### **Backup Checklist:**

- [ ] Daily: Copy SQLite database
- [ ] Weekly: Export to Parquet
- [ ] Monthly: Upload to cloud
- [ ] Quarterly: Verify backups work
- [ ] Yearly: Archive old data

### **Encryption (Optional):**

```bash
# Encrypt backup
gpg -c data/backups/articles_20240312.parquet

# Decrypt
gpg data/backups/articles_20240312.parquet.gpg
```

---

## 📊 Monitoring Storage

```bash
# Check database size
du -h data/swahili_knowledge.db

# Check all backups
du -sh data/backups/*

# Find large files
find data/ -type f -size +10M -ls
```

---

## 🎓 Best Practices

1. **✅ DO:**
   - Backup before major changes
   - Export monthly summaries
   - Keep 3 backup copies (3-2-1 rule)
   - Use Parquet for archives
   - Document your data schema

2. **❌ DON'T:**
   - Delete original database
   - Store passwords in backups
   - Forget to test restores
   - Use only CSV (too large)
   - Ignore backup automation

---

## 🆘 Recovery

**Lost database?**

```bash
# Restore from latest backup
cp data/backups/database_20240312.db data/swahili_knowledge.db

# Or rebuild from Parquet
python scripts/restore_from_parquet.py data/backups/articles_20240312.parquet
```

---

## 📞 Support

**Database issues?**
- Check logs: `data/logs/`
- Verify integrity: `sqlite3 data/swahili_knowledge.db "PRAGMA integrity_check;"`
- Rebuild: `python -c "from src.infrastructure.database import init_db; init_db()"`

**Need more space?**
- Migrate to PostgreSQL
- Archive old data to Parquet
- Use cloud storage

---

## Summary

**Your articles are saved in:** `data/swahili_knowledge.db`

**Recommended workflow:**
1. Use SQLite for daily work ✅ (Already set up!)
2. Run `python scripts/backup_articles.py` monthly
3. Upload backups to cloud quarterly
4. Generate reports with `python scripts/monthly_report.py`

**That's it! Your data is safe and analyzable!** 🎉
