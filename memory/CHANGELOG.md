# CHANGELOG

## 2026-02-15 — Removed Disbursement Letter Document Type
- **Feature**: Disbursement Letter removed entirely from the system at user request (option b — full removal, not just hiding).
- **Backend**: Removed `DISBURSEMENT_LETTER` from `utils/enums.py::DocumentType`. Removed default template body from `documents/templates/default_template.py`. Backend now returns HTTP 422 for any `doc_type: "disbursement_letter"` request — enum validation rejects it.
- **Frontend**: Removed from 4 places:
  - `components/customer/DocumentsTab.jsx` — Generate Document dropdown
  - `pages/DocumentsPage.js` — getDocTypeBadge() styles, Generate dropdown, Create Template dropdown
  - `pages/DocumentsPage.js` — Default Templates info banner ("Available for Sales Agreement and Allotment Letter")
  - `pages/DocumentsPage.js` — Default Templates grid (only renders 2 cards now)
- **Verified**: Backend rejects disbursement_letter with 422; allotment_letter still works (200); 13/13 regression tests pass; backend restart clean. Lint clean.
- Files: `backend/utils/enums.py`, `backend/documents/templates/default_template.py`, `frontend/src/components/customer/DocumentsTab.jsx`, `frontend/src/pages/DocumentsPage.js`.

## 2026-02-15 — TDS Calculation Fixed in Demand Letter (matches UI now)
- **Bug**: Demand Letter PDF computed `tds_paid = amount_paid / 101` — i.e., 1% of **all** payments (booking + agreement + disbursements + everything). That's wrong: TDS Paid must be the sum of **actual TDS challans only** (transactions where `transaction_stage == "tds"`).
- **Fix** (`documents/templates/demand_letter.py`): `tds_paid` is now `sum(t.amount for t in transactions if t.transaction_stage == 'tds')`. `tds_payable` and `tds_to_be_paid` formulas unchanged.
- **Verified**: On total ₹1Cr / 50% cumulative + booking 5L + agreement 10L + TDS 5K + TDS 7.5K + disbursement 20L:
  - TDS Payable = ₹49,505 (50L ÷ 101) ✓
  - TDS Paid    = ₹12,500 (only TDS-stage txns) ✓
  - TDS To Be Paid = ₹37,005 ✓
- **Memory locked**: New file `/app/memory/TDS_CALCULATION_LOGIC.md` captures the formulas, common mistakes, and reference test case. PRD.md now mandates reading it before any TDS code change.
- All 13 regression tests still pass.
- File: `/app/backend/documents/templates/demand_letter.py`.

## 2026-02-15 — Master Template Save: Auto-Scrub Customer Values
- **Fix**: When admin clicked "Save as Master", the entire HTML (including the **source** customer's name, unit, address, prices, dates) was being persisted. Future customers' docs ended up showing Ramya's name instead of their own.
- **Fix**: Backend `_scrub_customer_values_to_placeholders()` now scans the saved HTML and replaces each literal value (e.g., "Ramya test lead", "0701", "Tower 1", `211655.79`, `2,11,655`) with its corresponding `{placeholder}` token before persisting. Only the document **format** (layout, styling, legal text) is preserved.
- Replaces both raw numerics (`211655.79`, `211656`) **and** Indian-formatted variants (`2,11,656`, `₹2,11,656`, `Rs.2,11,656`). Skips strings shorter than 3 chars to avoid corrupting layout. Longest values are replaced first to prevent partial-match corruption.
- Frontend confirmation dialog updated to clearly state: *"All future documents will use this format. Customer-specific fields are automatically refilled from each customer's profile."*
- **Verified end-to-end**:
  - Saved Ramya's allotment letter as master → master template now contains `{customer_name}`, `{unit_number}`, `{tower}`, `{customer_id}` placeholders instead of literal values
  - Generated allotment letter for NANDAKUMAR → contains "NANDAKUMAR T V AND PRIYADHARSHINI NANDAKUMAR" (not Ramya), correctly using the master format with NANDAKUMAR's data
- Files: `/app/backend/documents/routes.py`, `/app/frontend/src/components/customer/documents/EditableDocumentDialog.jsx`. Lint clean.

## 2026-02-15 — Digital-signature Note Added to T&C PDF
- **Update**: Added a paraphrased digital-signature notice to the Terms & Conditions PDF (the one sent with the Welcome email), right below the signature block.
- **Text rendered**: *"This document is digitally generated and signed by RRL Builders and Developers Pvt. Ltd. No physical signature is required. Once issued, it stands officially recorded."*
- **Styling**: Cream background, gold left-border accent, italic centered text — matches the existing dark/gold theme.
- File: `/app/backend/documents/templates/terms_conditions.py`. Lint clean. Verified via direct render.

## 2026-02-15 — Terms & Conditions Bank/Tax Details Corrected
- **Update**: Replaced developer's bank-account and tax particulars across the T&C and Allotment-letter PDFs (the one bundled with the Welcome email).
- **Old (incorrect)** → **New**:
  - Bank: `Axis Bank` (Kudlu Gate, 922020009963054, UTIB0001504) → **HDFC BANK · SOMPURA · 57500001802063 · IFSC HDFC0009590**
  - Account Holder's Name: `RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED`
  - PAN: `AADCR1969A` → **AAKCR4125J**
  - GST: `29AADCR1969A1ZW` → **29AAKCR4125J1Z2**
- Labels aligned to user's exact wording: *Account Holder's Name*, *Bank Name*, *Branch Name*, *Account No.*, *IFSC*.
- Verified end-to-end on the rendered Allotment Letter HTML AND directly on `generate_terms_and_conditions_html()`: 9/9 assertions pass (new values present, all old values absent).
- All 13 letterhead/document regression tests pass.
- Files: `/app/backend/documents/templates/terms_conditions.py`, `/app/backend/documents/templates/default_template.py`. Lint clean.

## 2026-02-15 — Sales Role Can Approve/Reject Leads
- **Feature**: The `sales` role can now approve & reject leads (previously only `admin`/`manager` could). Reject requires a non-empty reason — enforced on both client and server.
- **Backend** (`booking/__init__.py`): Added `UserRole.SALES` to `check_role(...)` on both `PUT /api/leads/{id}/approve` and `PUT /api/leads/{id}/reject`. Backend now returns HTTP 400 "Rejection reason is required" if reason is blank.
- **Frontend** (`pages/LeadsPage.js`): Reject dialog: reason marked required with red asterisk + helper text; Confirm Reject button is disabled until a reason is entered. Approve handler now surfaces backend detail in toast.
- **Verified**: Accounts → 403 (still excluded); Sales + no reason → 400 with clear message; Sales + reason → 200, lead deleted, unit released; Sales approve → 200, stage→`qualified`.
- **Credentials**: `sales@rrlrprojects.com / sales123` added to `test_credentials.md`.
- Files: `/app/backend/booking/__init__.py`, `/app/frontend/src/pages/LeadsPage.js`. Lint clean.

## 2026-02-15 — Save Document Edits as Master Template (Admin)
- **Feature**: Customer Profile → Documents → open any generated doc → click **"Save as Master"** (admin/manager only). The edited content becomes the active master template for that doc_type — all future generations across all customers will start from it. Existing generated docs are not affected.
- **Backend**: New endpoint `POST /api/templates/save-from-document/{doc_id}` (admin/manager only). Upserts the doc_type's row in `document_templates` with `is_active=true`. Returns the template id. Activity logged.
- **Frontend**: `EditableDocumentDialog` gains a "Save as Master" button (visible only when `user.role` is `admin` / `manager`) + confirmation AlertDialog warning about the global effect. If the user is in edit mode, per-customer changes are persisted first, then promoted to master. Surfaces backend errors in toast.
- **Revert**: Settings → Document Templates → delete the template row → system reverts to the built-in default.
- Verified: master save replaces existing template; subsequent generations use master content; accounts-role user receives HTTP 403.
- Files: `/app/backend/documents/routes.py`, `/app/frontend/src/components/customer/documents/EditableDocumentDialog.jsx`. Lint clean.

## 2026-02-15 — Payment Tracking TDS Calculation Fix
- **Bug**: Customer Profile → Payments tab → "Stage-wise TDS" card showed `TDS Payable = expected × 1%` (e.g. ₹10,000 on ₹10L), but the Demand Letter PDF correctly uses `TDS Payable = expected ÷ 101` (₹9,901). The two screens disagreed.
- **Fix**: Aligned `PaymentSummaryCard.jsx` to use the same `÷ 101` formula as `documents/templates/demand_letter.py` (Section 194-IA: the demand amount is gross-inclusive of the 1% TDS). Helper text below the figure updated from "1% of demand raised" → "Demand ÷ 101".
- File: `/app/frontend/src/components/customer/payment/PaymentSummaryCard.jsx`. Lint clean. (No backend change — demand letter already correct.)

## 2026-02-15 — Communication Tab Email Send Fix
- **Bug**: From customer profile → Communication tab → compose & send email failed with "Failed to send email". Root cause: backend `/api/communication/email` was declared with **query parameters** (`customer_id: str`) but the frontend sends `multipart/form-data`. FastAPI returned 422 every time. Same form also tried to upload a local file which was being silently dropped.
- **Fix (backend)**: Changed signature to `Form(...)` + `UploadFile = File(None)`. Added parsing of `attachment_ids` as JSON list (frontend sends `JSON.stringify(array)`), preserved CSV fallback. Now actually attaches each selected generated/uploaded doc PLUS any local file to the SendGrid `Mail`. Returns SendGrid status code + attachment count.
- **Fix (frontend)**: Toast now surfaces backend `error.response.data.detail` so future failures are diagnosable.
- Verified end-to-end via curl: SendGrid returns 202 for plain-text email and 202 for email with 1 PDF attachment.
- Files: `/app/backend/email_service/routes.py`, `/app/frontend/src/components/customer/communication/SendMessageDialog.jsx`. Lint clean.

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
