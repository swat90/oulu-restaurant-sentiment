# Make.com Scenario Setup — Exact Steps

## Understanding the output structure

Apify "Get Dataset Items" outputs BUNDLES — one bundle per review.
Make.com processes each bundle separately through the flow.
We need to COLLECT all bundles into one array before sending to Apps Script.
This requires an Array Aggregator module between Apify and HTTP.

## Exact module sequence (4 modules, still 3 credits):

```
[1] Schedule trigger          — free
[2] Apify: Run Actor          — 1 credit
[3] Apify: Get Dataset Items  — 1 credit
[4] Array Aggregator          — free (0 credits)
[5] HTTP: Make a request      — 1 credit
────────────────────────────────────────
TOTAL: 3 credits per run
```

---

## Module 1 — Schedule

- Type: Schedule
- Run every: 1 Week
- Day: Monday
- Time: 06:00

---

## Module 2 — Apify: Run Actor

- App: Apify
- Action: Run Actor
- Actor ID: `compass/google-maps-reviews-scraper`
- Run input (paste as JSON):

```json
{
  "startUrls": [],
  "searchStringsArray": [
    "indian restaurant Oulu Finland",
    "pakistani restaurant Oulu Finland",
    "intiaalainen ravintola Oulu",
    "curry restaurant Oulu Finland"
  ],
  "maxReviews": 100,
  "reviewsSort": "newest",
  "language": "en",
  "includeHistogram": false,
  "includeImageUrls": false
}
```

- Wait for finish: **YES** (important — otherwise module 3 runs before scraping ends)
- Timeout (seconds): 300

---

## Module 3 — Apify: Get Dataset Items

- App: Apify
- Action: Get Dataset Items
- Dataset ID: map from module 2 → `{{2.defaultDatasetId}}`

This outputs one BUNDLE per review. Each bundle has all the fields
you saw: title, reviewDetailedRating, text, language, etc.

---

## Module 4 — Array Aggregator

This is the key module that collects all bundles into one array.

- App: Flow Control (built into Make.com, no connection needed)
- Action: **Array Aggregator**
- Source Module: Module 3 (Apify: Get Dataset Items)
- Aggregated fields — map each field you want to keep:

Click "Add item" for each field below and map from Module 3:

| Field name to create    | Map from Module 3              |
|-------------------------|-------------------------------|
| `title`                 | `{{3.title}}`                 |
| `text`                  | `{{3.text}}`                  |
| `textTranslated`        | `{{3.textTranslated}}`        |
| `stars`                 | `{{3.stars}}`                 |
| `rating`                | `{{3.rating}}`                |
| `totalScore`            | `{{3.totalScore}}`            |
| `reviewId`              | `{{3.reviewId}}`              |
| `publishedAtDate`       | `{{3.publishedAtDate}}`       |
| `visitedIn`             | `{{3.visitedIn}}`             |
| `language`              | `{{3.language}}`              |
| `originalLanguage`      | `{{3.originalLanguage}}`      |
| `translatedLanguage`    | `{{3.translatedLanguage}}`    |
| `reviewerId`            | `{{3.reviewerId}}`            |
| `reviewerNumberOfReviews` | `{{3.reviewerNumberOfReviews}}` |
| `isLocalGuide`          | `{{3.isLocalGuide}}`          |
| `likesCount`            | `{{3.likesCount}}`            |
| `responseFromOwnerText` | `{{3.responseFromOwnerText}}` |
| `responseFromOwnerDate` | `{{3.responseFromOwnerDate}}` |
| `reviewOrigin`          | `{{3.reviewOrigin}}`          |
| `address`               | `{{3.address}}`               |
| `city`                  | `{{3.city}}`                  |
| `neighborhood`          | `{{3.neighborhood}}`          |
| `street`                | `{{3.street}}`                |
| `postalCode`            | `{{3.postalCode}}`            |
| `countryCode`           | `{{3.countryCode}}`           |
| `categoryName`          | `{{3.categoryName}}`          |
| `price`                 | `{{3.price}}`                 |
| `url`                   | `{{3.url}}`                   |
| `placeId`               | `{{3.placeId}}`               |
| `totalScore`            | `{{3.totalScore}}`            |
| `reviewsCount`          | `{{3.reviewsCount}}`          |
| `location_lat`          | `{{3.location.lat}}`          |
| `location_lng`          | `{{3.location.lng}}`          |
| `reviewDetailedRating_Food`       | `{{3.reviewDetailedRating.Food}}`       |
| `reviewDetailedRating_Service`    | `{{3.reviewDetailedRating.Service}}`    |
| `reviewDetailedRating_Atmosphere` | `{{3.reviewDetailedRating.Atmosphere}}` |
| `reviewContext_Meal_type`         | `{{3.reviewContext.Meal type}}`         |
| `reviewContext_Order_type`        | `{{3.reviewContext.Order type}}`        |
| `reviewContext_Noise_level`       | `{{3.reviewContext.Noise level}}`       |
| `reviewContext_Wait_time`         | `{{3.reviewContext.Wait time}}`         |
| `reviewContext_Kid_friendliness`  | `{{3.reviewContext.Kid-friendliness}}`  |
| `reviewContext_Parking`           | `{{3.reviewContext.Parking}}`           |
| `reviewContext_Parking_options`   | `{{3.reviewContext.Parking options}}`   |
| `reviewContext_Wheelchair`        | `{{3.reviewContext.Wheelchair accessibility}}` |
| `reviewContext_Vegetarian`        | `{{3.reviewContext.Vegetarian options}}`|
| `reviewContext_Group_size`        | `{{3.reviewContext.Group size}}`        |
| `reviewContext_Seating_type`      | `{{3.reviewContext.Seating type}}`      |
| `reviewContext_Dietary`           | `{{3.reviewContext.Dietary restrictions}}` |
| `reviewContext_Price_per_person`  | `{{3.reviewContext.Price per person}}`  |
| `reviewContext_Recommended`       | `{{3.reviewContext.Recommended dishes}}`|
| `reviewContext_Reservation`       | `{{3.reviewContext.Reservation}}`       |
| `reviewContext_Special_events`    | `{{3.reviewContext.Special events}}`    |

IMPORTANT: The Array Aggregator flattens nested objects.
Note we use `reviewDetailedRating_Food` (with underscore) instead of
`reviewDetailedRating/Food` (with slash) because slashes cause issues
in some JSON parsers. The process_reviews.py handles both formats.

---

## Module 5 — HTTP: Make a request

- App: HTTP
- Action: Make a request
- URL: paste your Google Apps Script Web App URL
- Method: POST
- Headers: Content-Type → application/json
- Body type: Raw
- Content type: application/json
- Body:

```json
{
  "action": "write_reviews",
  "reviews": {{4.array}}
}
```

`{{4.array}}` is the output of the Array Aggregator — a proper JSON array.

---

## ALTERNATIVE if Array Aggregator is confusing

If you want a simpler setup with fewer fields to map,
use this approach — just send the whole bundle as-is:

Module 4 body (skip Array Aggregator, use HTTP directly after module 3):

```json
{
  "action": "write_single_review",
  "review": {
    "title": "{{3.title}}",
    "text": "{{3.text}}",
    "textTranslated": "{{3.textTranslated}}",
    "stars": "{{3.stars}}",
    "totalScore": "{{3.totalScore}}",
    "reviewId": "{{3.reviewId}}",
    "publishedAtDate": "{{3.publishedAtDate}}",
    "language": "{{3.language}}",
    "originalLanguage": "{{3.originalLanguage}}",
    "reviewerNumberOfReviews": "{{3.reviewerNumberOfReviews}}",
    "isLocalGuide": "{{3.isLocalGuide}}",
    "likesCount": "{{3.likesCount}}",
    "responseFromOwnerText": "{{3.responseFromOwnerText}}",
    "address": "{{3.address}}",
    "city": "{{3.city}}",
    "categoryName": "{{3.categoryName}}",
    "price": "{{3.price}}",
    "url": "{{3.url}}",
    "reviewsCount": "{{3.reviewsCount}}",
    "location_lat": "{{3.location.lat}}",
    "location_lng": "{{3.location.lng}}",
    "reviewDetailedRating_Food": "{{3.reviewDetailedRating.Food}}",
    "reviewDetailedRating_Service": "{{3.reviewDetailedRating.Service}}",
    "reviewDetailedRating_Atmosphere": "{{3.reviewDetailedRating.Atmosphere}}",
    "reviewContext_Noise_level": "{{3.reviewContext.Noise level}}",
    "reviewContext_Wait_time": "{{3.reviewContext.Wait time}}",
    "reviewContext_Kid_friendliness": "{{3.reviewContext.Kid-friendliness}}",
    "reviewContext_Parking": "{{3.reviewContext.Parking}}",
    "reviewContext_Wheelchair": "{{3.reviewContext.Wheelchair accessibility}}",
    "reviewContext_Vegetarian": "{{3.reviewContext.Vegetarian options}}",
    "reviewContext_Meal_type": "{{3.reviewContext.Meal type}}",
    "reviewContext_Order_type": "{{3.reviewContext.Order type}}",
    "reviewContext_Group_size": "{{3.reviewContext.Group size}}",
    "reviewContext_Recommended": "{{3.reviewContext.Recommended dishes}}"
  }
}
```

This sends ONE HTTP call per review (1 credit per review = expensive).
Use Array Aggregator approach instead to keep it at 3 credits total.

---

## Update Apps Script for single-review action

Add this to Code.gs doPost() if using the single-review approach:

```javascript
if (action === "write_single_review" && payload.review) {
  const count = writeReviews([payload.review]);
  return jsonResponse({ status:"ok", written: count });
}
```

---

## Update process_reviews.py column names

Since we renamed nested fields with underscores, update _v() calls:

The current code uses `reviewDetailedRating/Food` — change to handle
both formats by updating the helper:

```python
# In process_reviews.py, the _f() calls for Google ratings become:
g_food       = _f(row, "reviewDetailedRating_Food",
                       "reviewDetailedRating/Food")
g_service    = _f(row, "reviewDetailedRating_Service",
                       "reviewDetailedRating/Service")
g_atmosphere = _f(row, "reviewDetailedRating_Atmosphere",
                       "reviewDetailedRating/Atmosphere")
```

And for context fields:
```python
# Replace reviewContext/Noise level → reviewContext_Noise_level
# The _v() function tries multiple key names, so just add both:
out["ctx_noise_raw"] = _v(row,
    "reviewContext_Noise_level",
    "reviewContext/Noise level")
```
