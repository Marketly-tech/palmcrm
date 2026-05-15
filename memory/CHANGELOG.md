# CHANGELOG

## 2026-02 — Builder NOC Letterhead Restored
- **Bug fixed**: All 3 Builder NOC PDFs (HDFC Bank, Bank of Baroda, TATA Capital) were rendering without the RRL letterhead — just a small "Builder NOC" text in the top-right.
- **Fix**: Added a proper letterhead block with the RRL logo + company name ("RRL Builders and Developers Pvt. Ltd.") + tagline ("Beyond homes. A lifestyle") on the left, and the "Builder NOC" title on the right, separated by a gold divider. Shared via `_letterhead_styles()` / `_letterhead_html()` helpers in `noc_templates.py` so future tweaks happen in one place.
- Verified: HTML contains `<div class="letterhead">` + base64 logo + company name for all 3 NOCs; downloaded PDF is a valid 148KB file with embedded image stream.

## 2026-02 — Interest Amount Field
- **Feature**: Added editable **"Interest Amount"** field to Property & Pricing card on Customer Profile. Manual entry, added to Total Price **after GST** (non GST-taxable, per user request).
- **Backend**: New `customer.interest_amount` field on `Customer` model. `price_breakup` PDF now renders an "Interest Amount" row above the Grand Total whenever the value is > 0. `{interest_amount}` placeholder added for editable templates.
- **Frontend**: Input shown in edit mode under GST (5%); live preview breakdown shows the line when > 0; `calculateLivePrice` adds it to the final total. Save flow persists the field.
- Verified via curl: PUT /api/customers/{id} with `interest_amount=50000` → stored; price_breakup HTML contains "Interest Amount" row.

## 2026-02 — Payment Schedule Document Auto-Generation Fix
- **Bug fixed**: Generating a "Payment Schedule" document from Customer Profile → Documents tab failed with a generic "Failed to generate document" toast for any customer that had not yet auto-generated the schedule items.
- **Backend**: `documents/generators.py::_render_payment_schedule` now auto-creates the schedule from `DEFAULT_PAYMENT_SCHEDULE` (13 milestones) and persists it on the fly if missing. Same behavior also applied to `POST /api/documents/generate-payment-schedule-pdf/{customer_id}` (now routes through `render_document_content`).
- **Frontend**: `CustomerDetailPage.js` onGenerateDocument now surfaces backend `error.response.data.detail` in the toast instead of swallowing it, so future failures are diagnosable end-to-end.
- Verified via curl for both Ramya (existing schedule) and NANDAKUMAR (no schedule) — both return `Document generated` with full HTML content.
