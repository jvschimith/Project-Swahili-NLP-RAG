# 🐛 Fixing 500 Internal Server Error

## 📍 You're Here Because:
```
INFO: 127.0.0.1:49600 - "POST /news/save HTTP/1.1" 500 Internal Server Error
```

This means there's a **bug in the API code**, not BBC's fault.

---

## 🔍 Step 1: Find the Error

### **Look at your API terminal** (where uvicorn is running)

You should see a Python traceback that looks like:

```python
Traceback (most recent call last):
  File "...", line X, in save_news_article
    ...
SomeError: the actual error message
```

**This tells you EXACTLY what's wrong.**

---

## 🎯 Common 500 Errors & Fixes:

### **Error 1: Import Error**
```python
ImportError: cannot import name 'NewsArticle'
```

**Fix:**
```bash
# Check the import exists
grep "from src.domain.entities import NewsArticle" src/web/api.py

# If missing, add to src/web/api.py (line ~437):
from src.domain.entities import NewsArticle
from src.domain.value_objects import SentimentScore
```

---

### **Error 2: Database Not Initialized**
```python
sqlalchemy.exc.OperationalError: no such table: news
```

**Fix:**
```bash
# Initialize database
python -c "from src.infrastructure.database import init_db; init_db()"

# Restart API
uvicorn src.web.api:app --reload
```

---

### **Error 3: Missing Repository Method**
```python
AttributeError: 'NewsRepository' object has no attribute 'save'
```

**Fix:**
Check that `src/infrastructure/repositories/news_repository.py` has a `save()` method.

---

### **Error 4: Validation Error**
```python
pydantic.error_wrappers.ValidationError: ...
```

**Fix:**
The request data doesn't match the model. Check:
- `content` is a string
- `category` is a string
- `sentiment_polarity` is a number between -1 and 1
- `sentiment_confidence` is a number between 0 and 1

---

### **Error 5: Session/Transaction Error**
```python
sqlalchemy.exc.InvalidRequestError: This Session's transaction has been rolled back
```

**Fix:**
```bash
# Restart the API
# Press Ctrl+C
uvicorn src.web.api:app --reload
```

---

## 🧪 Step 2: Test with Diagnostic Script

```bash
python test_save_detailed.py
```

This will:
- Send a test request
- Show the full error
- Suggest fixes

---

## 🔧 Step 3: Apply the Fix

### **Quick Fix (Works for most errors):**

```bash
# 1. Stop API (Ctrl+C)

# 2. Extract updated files
unzip -o COMPLETE_FIX.zip

# 3. Initialize database (if needed)
python -c "from src.infrastructure.database import init_db; init_db()"

# 4. Restart API
uvicorn src.web.api:app --reload

# 5. Test again
python test_save_detailed.py
```

---

## 📋 Checklist:

- [ ] Looked at API terminal for error traceback
- [ ] Identified the specific error type
- [ ] Applied the relevant fix above
- [ ] Restarted the API
- [ ] Tested with `python test_save_detailed.py`
- [ ] Got 200 OK ✅

---

## 🆘 If Still Not Working:

### **Copy the FULL error from API terminal and share it**

Example of what to copy:
```
Traceback (most recent call last):
  File "/path/to/api.py", line 456, in save_news_article
    article_id = repo.save(article)
  File "/path/to/news_repository.py", line 78, in save
    self.session.add(db_article)
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: news
```

**Copy ALL of this** and I can give you the exact fix.

---

## 💡 Most Likely Issues:

### **90% of the time it's one of these:**

1. **Database not initialized** → Run `init_db()`
2. **Old code running** → Restart API
3. **Missing import** → Update api.py file
4. **Session not committing** → Restart API

---

## ✅ Success Looks Like:

```bash
$ python test_save_detailed.py

============================================================
Testing POST /news/save with detailed error output
============================================================

Status Code: 200
============================================================
✅ SUCCESS!
{
  "success": true,
  "message": "Article saved successfully",
  "article_id": 1,
  "category": "Politics",
  "sentiment": "positive"
}
```

---

## 🚀 Next Steps After Fix:

1. ✅ Test in dashboard (should work now)
2. ✅ Save a real article
3. ✅ Check Database Analytics tab
4. ✅ See the count increase!

---

**Run `python test_save_detailed.py` and share the output if it still fails!**
