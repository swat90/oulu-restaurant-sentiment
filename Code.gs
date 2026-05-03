/**
 * Google Apps Script — Web App
 * Receives JSON from Make.com via HTTP POST
 * Batch-writes all reviews to Sheets in one call
 * Costs 0 Make.com credits
 *
 * SETUP:
 * 1. Open your Google Sheet → Extensions → Apps Script
 * 2. Paste this file, save
 * 3. Deploy → New deployment → Web App
 *    Execute as: Me  |  Access: Anyone
 * 4. Copy the Web App URL → paste into Make.com HTTP module
 */

const SHEET_NAME    = "raw_reviews";
const RESULTS_SHEET = "sentiment_results";
const RAW_HEADERS = [
  "restaurant","place_url","place_avg_rating","place_total_reviews",
  "reviewer","review_rating","review_text","review_date",
  "review_language","fetched_at"
];

function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents);
    const action  = payload.action || "write_reviews";

    if (action === "write_reviews" && payload.reviews) {
      return jsonResponse({ status:"ok", written: writeReviews(payload.reviews) });
    }
    if (action === "write_results" && payload.results) {
      return jsonResponse({ status:"ok", written: writeResults(payload.results) });
    }
    return jsonResponse({ status:"error", message:"Unknown action" });
  } catch(err) {
    return jsonResponse({ status:"error", message: err.toString() });
  }
}

function doGet() {
  return jsonResponse({ status:"alive" });
}

function writeReviews(reviews) {
  const ss   = SpreadsheetApp.getActiveSpreadsheet();
  let sheet  = ss.getSheetByName(SHEET_NAME);
  if (!sheet) { sheet = ss.insertSheet(SHEET_NAME); sheet.appendRow(RAW_HEADERS); }

  // Build dedup key set from existing data
  const existing    = sheet.getDataRange().getValues();
  const existingKeys = new Set();
  for (let i = 1; i < existing.length; i++) {
    existingKeys.add(`${existing[i][0]}|${existing[i][4]}|${existing[i][7]}`);
  }

  // Filter to new rows only then batch-write
  const newRows = reviews
    .filter(r => !existingKeys.has(`${r.restaurant}|${r.reviewer}|${r.review_date}`))
    .map(r => RAW_HEADERS.map(h => r[h] ?? ""));

  if (newRows.length > 0) {
    sheet.getRange(sheet.getLastRow()+1, 1, newRows.length, RAW_HEADERS.length)
         .setValues(newRows);
  }
  return newRows.length;
}

function writeResults(results) {
  if (!results || results.length === 0) return 0;
  const ss      = SpreadsheetApp.getActiveSpreadsheet();
  let sheet     = ss.getSheetByName(RESULTS_SHEET);
  const headers = Object.keys(results[0]);
  if (!sheet) { sheet = ss.insertSheet(RESULTS_SHEET); }
  sheet.clearContents();
  sheet.appendRow(headers);
  const rows = results.map(r => headers.map(h => r[h] ?? ""));
  sheet.getRange(2, 1, rows.length, headers.length).setValues(rows);
  sheet.autoResizeColumns(1, headers.length);
  return rows.length;
}

function jsonResponse(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}
