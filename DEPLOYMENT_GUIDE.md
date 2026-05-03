# Deployment Guide — Oulu Restaurant Sentiment
## Zero credentials. Make.com handles scraping. 3 credits per week.

---

## HOW IT ALL CONNECTS

```
Make.com (runs weekly, 3 credits total)
  [Apify: Run Actor]         1 credit — scrapes Google Maps
       ↓
  [Apify: Get Dataset Items] 1 credit — collects all reviews
       ↓
  [HTTP POST to Apps Script] 1 credit — sends ALL rows in one call
       ↓
Google Apps Script (free, no credits)
  Deduplicates + batch-writes → Google Sheets "raw_reviews" tab
       ↓
process_reviews.py  (runs on your laptop or GitHub Actions)
  Reads sheet via public CSV URL — NO credentials needed
  Processes: Google ratings > context fields > NLP text
  Writes results via Apps Script → "processed" tab
       ↓
Streamlit dashboard
  Reads "processed" tab via public CSV — NO credentials needed
  Public URL via Streamlit Cloud — FREE
```

---

## PART 1 — Google Sheets setup (5 minutes)

1. Create a new Google Sheet
2. Name it anything — e.g. "Oulu Restaurant Sentiment"
3. **Share it publicly:**
   - Click Share (top right)
   - Change "Restricted" → **"Anyone with the link"**
   - Set permission to **"Viewer"**
   - Copy the link
4. **Get your Sheet ID** from the URL:
   ```
   https://docs.google.com/spreadsheets/d/THIS_IS_YOUR_SHEET_ID/edit
   ```
5. Paste `SHEET_ID` at the top of both:
   - `src/process_reviews.py`
   - `src/dashboard.py`

---

## PART 2 — Google Apps Script setup (10 minutes)

This handles ALL writing to Sheets — no credentials, no API keys.

1. In your Google Sheet: **Extensions → Apps Script**
2. Delete the default code
3. Paste everything from `google_apps_script/Code.gs`
4. Click Save
5. Click **Deploy → New Deployment**
   - Type: **Web App**
   - Execute as: **Me**
   - Who has access: **Anyone**
6. Click Deploy → Copy the **Web App URL**
7. Paste `APPS_SCRIPT_URL` at the top of `src/process_reviews.py`
8. Also paste it into Make.com (see Part 3)

**Test it:**
Open the Web App URL in your browser — you should see:
```json
{"status":"alive"}
```

---

## PART 3 — Make.com scenario (3 credits per run)

Create a new scenario with exactly 3 modules:

### Module 1: Schedule
- Interval: **Every week** on Monday at 06:00

### Module 2: Apify → Run Actor
- Connection: your Apify account (free at apify.com)
- Actor: `compass/google-maps-reviews-scraper`
- Run input:
```json
{
  "searchStringsArray": [
    "indian restaurant Oulu Finland",
    "intiaalainen ravintola Oulu",
    "curry restaurant Oulu",
    "spice restaurant Oulu"
  ],
  "maxReviews": 100,
  "reviewsSort": "newest",
  "includeHistogram": false,
  "includeImageUrls": false,
  "language": "en"
}
```
- Wait for finish: **Yes**

### Module 3: Apify → Get Dataset Items
- Dataset ID: map `{{2.defaultDatasetId}}`
- This returns everything in one response

### Module 4: HTTP → Make a Request
- URL: paste your Apps Script Web App URL
- Method: **POST**
- Body type: **Raw**
- Content type: **application/json**
- Body:
```json
{
  "action": "write_reviews",
  "reviews": {{3.items}}
}
```

That's it. Save and run once manually to test.
**Cost: 4 operations total per run** (schedule trigger is free).

---

## PART 4 — Run the processing script

After Make.com has populated "raw_reviews":

```bash
# Install dependencies (once)
pip install -r requirements.txt

# Run processing — reads from Sheets, writes back
python src/process_reviews.py
```

No environment variables needed. Just make sure `SHEET_ID` and
`APPS_SCRIPT_URL` are filled in at the top of the file.

---

## PART 5 — GitHub + Streamlit Cloud deployment

### 5.1 Push to GitHub

```bash
cd your-project-folder
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/oulu-restaurant-sentiment.git
git branch -M main
git push -u origin main
```

### 5.2 GitHub Secrets (only for automated weekly processing)

Settings → Secrets → Actions → New repository secret:

| Secret | Value |
|--------|-------|
| `SHEET_ID` | Your Google Sheet ID |
| `APPS_SCRIPT_URL` | Your Apps Script Web App URL |

These replace the hardcoded values when running in GitHub Actions.
Update `process_reviews.py` to read them:
```python
import os
SHEET_ID       = os.environ.get("SHEET_ID", "YOUR_SHEET_ID_HERE")
APPS_SCRIPT_URL= os.environ.get("APPS_SCRIPT_URL", "YOUR_URL_HERE")
```

### 5.3 Streamlit Cloud

1. Go to **share.streamlit.io**
2. New app → select your repo
3. Main file: `src/dashboard.py`
4. No secrets needed — just make sure `SHEET_ID` is set in the file
5. Deploy → get public URL

### 5.4 Everyday Git workflow

```bash
git add .
git commit -m "Describe what changed"
git push
```

### 5.5 Revert if something breaks

```bash
git log --oneline          # see history
git revert HEAD            # undo last commit
git push
```

---

## Cost summary

| Service | Cost |
|---------|------|
| Make.com | ~4 credits/week = ~16/month (free: 1000/month) |
| Google Apps Script | Free |
| Google Sheets | Free |
| GitHub | Free |
| GitHub Actions | ~10 min/month (free: 2000 min/month) |
| Streamlit Cloud | Free |
| Apify | Free tier ($5 compute/month) |
| **Total** | **Free** |
