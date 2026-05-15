# CHANGELOG

## 2026-02-15 — NOC Format Restored to Original (Dark Band + Footer Band)
- **User feedback**: The Feb 15 morning "letterhead fix" replaced the original (yesterday's) NOC format with a different style. User wants the **original** back: dark charcoal full-width header band, gold RRL GROUP logo + white company name + gold tagline, centered "BUILDER NOC — <BANK>" title, and a bottom footer band with company address/website/email/RERA/ref-no.
- **Fix**: Rewrote `_letterhead_styles()` / `_letterhead_html()` in `noc_templates.py` to match the original PDF exactly (analyzed via `analyze_file_tool` on `RRL_Noc_Hdfc_SOVARAJ_PRUSTY (4).pdf`). Added `_doc_title_html()` and `_footer_band_html()` helpers. Updated all 3 NOC bodies (HDFC / BOB / TATA) to use them. Changed page margins to `0 20mm 30mm 20mm` so header band touches the page edge and footer band has reserved space.
- **Memory-loss fix**: Created `/app/memory/DOCUMENT_FORMAT_REFERENCE.md` — single source of truth for every approved doc layout, locked-in colors, footer text, and constants. PRD.md now mandates reading this before touching any PDF template.
- Verified: All 3 NOC PDFs render at ~152KB with dark band, gold logo, white company name, footer band with RERA + ref no. Visual screenshot confirms match.

## 2026-02 — Cost Breakup Letterhead Restored (Letterhead Regression Sweep)
- **Bug fixed** (caught by `testing_agent_v3_fork` iteration 36): Cost Breakup PDF was missing the RRL logo — it had only the "RRL PALM ALTEZZE / Cost Break Up" text on the right with no logo on the left. Imported `get_logo_img_tag` was a dead import.
- **Fix**: Added a proper two-column header to `cost_breakup.py` — RRL logo + company name + tagline on the left, project title + "Cost Break Up" on the right, separated by a gold border. HTML went from ~6.7KB → 147KB, PDF from ~17KB → 148KB.
- **Verified**: All 13 letterhead tests now pass (10 doc types + 3 regression tests). Test file at `/app/backend/tests/test_letterhead_iteration36.py`.

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
