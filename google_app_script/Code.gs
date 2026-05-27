/**
 * Google Apps Script — Web App
 * Receives JSON from Make.com or process_reviews.py via HTTP POST
 * Batch-writes reviews to Sheets — zero Make.com credits
 *
 * SETUP:
 * 1. Open your Google Sheet → Extensions → Apps Script
 * 2. Paste this file, save
 * 3. Deploy → New deployment → Web App
 *    Execute as: Me  |  Access: Anyone
 * 4. Copy the Web App URL → paste into Make.com HTTP module
 *    and into APPS_SCRIPT_URL in process_reviews.py
 */

const RAW_SHEET     = "raw_reviews";
const RESULTS_SHEET = "processed";

const RAW_HEADERS = [
  "address","categories/0","categoryName","cid","city","countryCode",
  "isLocalGuide","language","likesCount","location/lat","location/lng",
  "name","originalLanguage","permanentlyClosed","placeId","postalCode",
  "price","publishedAtDate","rating","responseFromOwnerDate",
  "responseFromOwnerText",
  "reviewContext/Dietary restrictions","reviewContext/Group size",
  "reviewContext/Kid-friendliness","reviewContext/Meal type",
  "reviewContext/Noise level","reviewContext/Order type",
  "reviewContext/Parking","reviewContext/Parking options",
  "reviewContext/Parking space","reviewContext/Price per person",
  "reviewContext/Recommended dishes","reviewContext/Reservation",
  "reviewContext/Seating type","reviewContext/Special events",
  "reviewContext/Special offers","reviewContext/Vegetarian options",
  "reviewContext/Wait time","reviewContext/Wheelchair accessibility",
  "reviewDetailedRating/Atmosphere","reviewDetailedRating/Food",
  "reviewDetailedRating/Service",
  "reviewId","reviewOrigin","reviewUrl","reviewerId",
  "reviewerNumberOfReviews","reviewsCount","scrapedAt","searchString",
  "stars","state","street","temporarilyClosed",
  "text","textTranslated","title","totalScore",
  "translatedLanguage","url","visitedIn"
];

function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents);
    const action  = payload.action || "write_reviews";

    if (action === "write_reviews" && payload.reviews) {
      return jsonResponse({ status:"ok", written: writeReviews(payload.reviews) });
    }
    if (action === "write_results" && payload.results) {
      // chunk_index tells us if this is first chunk (clear sheet) or continuation
      const chunkIndex = payload.chunk_index !== undefined ? payload.chunk_index : 0;
      return jsonResponse({ status:"ok", written: writeResults(payload.results, chunkIndex) });
    }
    if (action === "clear_results") {
      // Called once before sending chunks — clears sheet and writes header
      clearResultsSheet(payload.headers || []);
      return jsonResponse({ status:"ok", action:"cleared" });
    }
    return jsonResponse({ status:"error", message:"Unknown action: " + action });
  } catch(err) {
    return jsonResponse({ status:"error", message: err.toString() });
  }
}

function doGet() {
  return jsonResponse({ status:"alive", message:"Apps Script is running" });
}

// ── Write raw reviews (deduplicates by reviewId) ──────────────────────────────
function writeReviews(reviews) {
  const ss   = SpreadsheetApp.getActiveSpreadsheet();
  let sheet  = ss.getSheetByName(RAW_SHEET);
  if (!sheet) {
    sheet = ss.insertSheet(RAW_SHEET);
    sheet.appendRow(RAW_HEADERS);
    SpreadsheetApp.flush();
  }

  // Dedup by reviewId (column index 43 = reviewId in RAW_HEADERS)
  const existing     = sheet.getDataRange().getValues();
  const existingKeys = new Set();
  const reviewIdIdx  = RAW_HEADERS.indexOf("reviewId");

  for (let i = 1; i < existing.length; i++) {
    const rid = existing[i][reviewIdIdx];
    if (rid) existingKeys.add(String(rid));
  }

  const newRows = reviews.filter(r => {
    const rid = r.reviewId || r["reviewId"] || "";
    return rid && !existingKeys.has(String(rid));
  }).map(r => RAW_HEADERS.map(h => {
    const val = r[h];
    return val !== undefined && val !== null ? val : "";
  }));

  if (newRows.length > 0) {
    sheet.getRange(sheet.getLastRow()+1, 1, newRows.length, RAW_HEADERS.length)
         .setValues(newRows);
  }
  return newRows.length;
}

// ── Clear processed sheet once before chunked writes ─────────────────────────
function clearResultsSheet(headers) {
  const ss    = SpreadsheetApp.getActiveSpreadsheet();
  let sheet   = ss.getSheetByName(RESULTS_SHEET);
  if (!sheet) {
    sheet = ss.insertSheet(RESULTS_SHEET);
  } else {
    sheet.clearContents();
  }
  if (headers && headers.length > 0) {
    sheet.appendRow(headers);
  }
  SpreadsheetApp.flush();
}

// ── Append chunk of results (NO clear — clear is separate) ───────────────────
function writeResults(results, chunkIndex) {
  if (!results || results.length === 0) return 0;

  const ss    = SpreadsheetApp.getActiveSpreadsheet();
  let sheet   = ss.getSheetByName(RESULTS_SHEET);

  const headers = Object.keys(results[0]);

  // Create sheet with header if it doesn't exist yet
  if (!sheet) {
    sheet = ss.insertSheet(RESULTS_SHEET);
    sheet.appendRow(headers);
    SpreadsheetApp.flush();
  } else if (chunkIndex === 0) {
    // First chunk — clear and write header
    sheet.clearContents();
    sheet.appendRow(headers);
    SpreadsheetApp.flush();
  }
  // Subsequent chunks — just append, do NOT clear

  const rows = results.map(r => headers.map(h => {
    const v = r[h];
    if (v === null || v === undefined) return "";
    if (typeof v === "number" && !isFinite(v)) return "";
    return v;
  }));

  sheet.getRange(sheet.getLastRow()+1, 1, rows.length, headers.length)
       .setValues(rows);

  return rows.length;
}

function jsonResponse(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}
