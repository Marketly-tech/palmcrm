# CHANGELOG

## 2026-02-28 (bug fix) — Manual Labour Cess override respected end-to-end (P0)
- **Symptom** — When admin toggled Manual on Labour Cess and entered 0, the value was persisted in the DB but the standalone `/api/calculator/price` endpoint (used by the New Booking form + external tests) still auto-computed `subtotal × 0.7%`, ignoring the manual flag. On legacy customer records the save path also didn't proactively mirror liveCalc's labour_cess/labour_cess_manual onto the payload — relying on editData spread.
- **Fix**:
  - `backend/payments/models.py` — `PriceCalculation` gained `labour_cess_manual: bool = False` and `labour_cess_override: Optional[float] = None`.
  - `backend/payments/routes.py::calculate_price` — when `labour_cess_manual=true` AND `labour_cess_override` is provided, honour it verbatim (0 respected); else fall back to standard `subtotal × labour_cess_percentage / 100`.
  - `frontend/src/hooks/useCustomerPage.js::handleSaveCustomer` — legacy branch now explicitly writes `labour_cess` and `labour_cess_manual` from `liveCalc` onto the payload (in addition to preserving the historical `total_price`).
- **Verified** — 8/8 pytest cases pass (`/app/backend/tests/test_labour_cess_manual_iter56.py`): calculator/price returns 0 on manual override 0, returns 12345 on manual override 12345, auto path returns 36400 on the standard 5.2 M subtotal, PUT + GET on Ramya test lead persists `labour_cess=0` + `labour_cess_manual=true`, `price_breakup` HTML renders `₹0.00` on the Labour Cess row, and `generate-schedule` still returns 13 items summing to Ramya's preserved `211655.79`.
- Files touched: `backend/payments/models.py`, `backend/payments/routes.py`, `frontend/src/hooks/useCustomerPage.js`.


## 2026-02-28 (feature) — Labour Cess manual-override on Customer Profile
- **What** — Labour Cess field on the Property & Pricing card is now editable. A "Manual" checkbox toggles between the default 0.7%-of-subtotal auto-calc and an admin-entered value. Manual mode is respected on save (0 is honoured); a helper caption always shows what the auto value *would* be for reference.
- **Files**:
  - `frontend/src/hooks/useCustomerPage.js` — `calculateLivePrice` now honours `data.labour_cess_manual`: when true, uses `numOr(data.labour_cess, 0)`; when false, computes `subtotal * 0.007`. Return object gained `labourCessManual` + `autoLabourCess` for the UI. `handleSaveCustomer` includes both in the PUT payload.
  - `frontend/src/components/customer/details/PropertyPricingCard.jsx` — replaced the readonly Labour Cess `<p>` with an `<Input>` + `Manual` checkbox. Auto mode disables the input and shows the live-computed value; Manual mode enables it and seeds with the current auto value. View mode adds "(manual override)" tag when applicable. Test IDs: `labour-cess-input`, `labour-cess-manual-toggle`, `labour-cess-value`.
  - `backend/customers/models.py` — added `labour_cess_manual: bool = False` to `CustomerBase` alongside the existing `labour_cess` float.
- **Verified** — Playwright: Auto→Manual toggle switches disabled state, input accepts a custom value (₹99,999 test). Curl PUT `{labour_cess: 12345, labour_cess_manual: true}` → GET confirms both persist; setting `labour_cess_manual: false` cleanly reverts to auto.
- Files touched: `frontend/src/hooks/useCustomerPage.js`, `frontend/src/components/customer/details/PropertyPricingCard.jsx`, `backend/customers/models.py`.



## 2026-02-28 (bug fix) — Disbursement Summary: Loans / Pending / Sanctioned columns were empty
- **Symptom (production)** — On `rrlcrm.com/dashboard`, every row of the Bank Disbursement Summary showed `Loans = 0`, `Sanctioned = —`, `Pending = ₹0` (even though `Disbursed` had real amounts). Users saw "across 10 banks" but no per-bank counts.
- **Root cause** — Yesterday's rewrite indexed only customers with `loan_amount > 0`. In production, the accounts team routinely captures `finance_bank` on customer records but leaves `loan_amount` blank/0 (they log disbursements as transactions instead). So every prod customer was excluded from the per-bank rollup — Loans count fell to 0, Sanctioned stayed at 0 (`—` in UI), and Pending never got a `flat_value_total` to subtract from.
- **Fix (`backend/dashboard/routes.py`)**:
  - Customer index now selects `{finance_bank: {$nin: [None, ""]}}` — any customer with a bank assigned, regardless of `loan_amount` / `finance_type` / paperwork state.
  - Bank buckets are built from customer records FIRST (so a bank shows up in the widget the moment a customer is assigned to it, even before any disbursements or before `loan_amount` is captured).
  - Transaction rollup layers `total_disbursed` on top of the customer-built buckets, preferring the customer's `finance_bank` over the transaction's own `bank_name` so mistyped txn banks don't split a row.
- **Verified** — Synthetic reproduction of the production pattern: 5 customers (3 BOB variants + 2 HDFC) with `loan_amount=null/0`, 4 disbursement transactions. Endpoint returns Loans=3/2, Sanctioned=0 (correctly — nothing was captured), Pending computed from `SUM(total_price) − SUM(disbursed)`. Bank variants merged into single canonical rows.
- Files touched: `backend/dashboard/routes.py`.



## 2026-02-28 (bug fix) — Zero values now accepted on Customer Profile edit
- **Symptom** — Admins couldn't reliably set Club House / Car Parking / Additional Charges to ₹0 on the Customer Profile. When a legacy customer had those fields as `null` in DB, the UI silently showed the pre-Jun-2026 defaults (₹3L / ₹2L) in both view and edit modes, and the very next save persisted those phantom defaults into the DB — corrupting the record. The Price Breakup PDF then diverged from the customer card (PDF read real DB values → ₹0; card read defaulted UI values → ₹2L/₹3L).
- **Fixes** (all in preview):
  1. `frontend/src/components/customer/details/PropertyPricingCard.jsx` — replaced the `?? 200000` / `?? 300000` fallbacks on Car Parking + Club House with `?? 0` in both view and edit modes. Both inputs now placeholder-hint *"Enter 0 if not applicable"*. Added test IDs `car-parking-charges-value` / `club-house-value` / `club-house-input`, plus `labour-cess-value`, `gst-value`, `base-price-value`, `floor-rise-total-value`.
  2. Same file — Base Price, Floor Rise Total, Labour Cess, and GST view-mode readouts now `?? 0` any null field (previously would render as `₹NaN` or the misleading live-preview even for legacy records) and *skip* the live-preview branch entirely when `legacyPricing === true`.
  3. `frontend/src/hooks/useCustomerPage.js` — `calculateLivePrice` fallback for `club_house_charges` / `additional_parking_charges` changed from 300000/200000 → 0. Combined with the earlier "0 is respected" `numOr` helper, this means: a null field now saves as `0` on the next edit (rather than silently persisting the default), and an explicit admin-typed `0` is always honored.
- **Legacy-record safety** — customers with `created_at < 2026-06-02` still bypass the recalc branch entirely, so their stored `total_price` remains unchanged. The pricing calculator is only used to preview subtotals during edit.
- **Verified** —
  - Playwright: JAYANTHI S (legacy) — view shows Car Parking `₹0` (not `₹2,00,000` anymore); edit mode accepts explicit `0` in both fields; Historical price badge still displayed.
  - Curl PUT on a non-legacy customer with `{club_house_charges: 0, additional_parking_charges: 0, additional_charges: 0}` → GET confirms all three persist as `0`; labour_cess and gst_amount computed fresh (no phantom defaults).
- Files touched: `frontend/src/components/customer/details/PropertyPricingCard.jsx`, `frontend/src/hooks/useCustomerPage.js`.



## 2026-02-28 (admin ops) — Legacy zero-charges backfill endpoint
- **Purpose** — For customers created 2026-03-20 → 2026-03-22 (RRL-00025..RRL-00035 in production) whose `club_house_charges` / `additional_parking_charges` were stored as `null` (predating the "0 is respected" pricing fix), give admins a safe one-shot way to explicitly set both fields to `0` so their UI cards and Price Breakup PDFs render identical numbers.
- **Endpoint** — `POST /api/dashboard/backfill/legacy-zero-charges` (admin-only). Query params: `start_date` (default 2026-03-20, inclusive), `end_date_exclusive` (default 2026-03-23), `apply` (default `false` = dry-run). Response includes the full candidate list, per-field would-update counts, applied counts (only when `apply=true`), and a post-run verify block. Idempotent — only touches rows whose target field is `null` / `""` / missing; a non-null value (even `0`) is left untouched.
- **Verified on preview** — 4-case synthetic test: (a) both-null customer → both set to 0; (b) only-club-null with parking=50000 → club set to 0, parking preserved at 50000; (c) only-parking-null with club=0 → parking set to 0; (d) customer outside the window (Mar 25) → untouched. Re-run with `apply=true` after applying returned 0 modifications (idempotence).
- **Runbook for production** (after redeploy):
  1. Get admin token via `POST /api/auth/login`.
  2. Dry-run: `POST /api/dashboard/backfill/legacy-zero-charges` — review the returned `candidates` list.
  3. Apply: same URL + `?apply=true`.
  4. Verify: response's `verify.still_null` should be `0`.
- Files touched: `backend/dashboard/routes.py`.



## 2026-02-28 (bug fix) — Disbursement Summary logic rewrite
- **Symptom** — Dashboard Bank Disbursement widget had five defects:
  1. `BOB BANK LOAN`, `BOB LOAN`, `BOB` showed as separate rows (same for HDFC / Canara variants).
  2. **Sanctioned** column was empty (`—`) because query filtered `finance_type IN {loan, mixed}` — records saved as `self` or blank were excluded even when they carried a real `loan_amount`.
  3. **Loans** column used a per-customer counter — a duplicate index entry could inflate the count.
  4. **Pending** was `loan_amount − disbursed`, which under-represents the collectible from each lender's book.
  5. "across N banks" summary showed the raw pre-normalization count.
- **Fix (`backend/dashboard/routes.py`)** — rewrote `_normalize_bank()` + `get_disbursement_summary()`:
  1. **Normalization** — expanded `_BANK_SUFFIXES_TO_STRIP` to also strip `LOAN`, `HOME LOAN`, `HOUSING LOAN`, `HOUSING FINANCE`, `HOME FINANCE`, `FINANCE`. Added a declarative `_BANK_CANONICAL_MAP` covering common variants (BOB → *Bank of Baroda*, HDFC/HDC → *HDFC Bank*, CANARA → *Canara Bank*, SBI, ICICI, AXIS, KOTAK, IDBI, IDFC, PNB, Union, Bank of India, Bank of Maharashtra, plus common NBFCs — LIC Housing, Tata Capital, Bajaj Housing, Piramal, PNB Housing). Unknown banks fall through as Title Case (nothing silently gets dropped).
  2. **Sanctioned** — removed the `finance_type` filter. Now `SUM(loan_amount)` for every customer with `loan_amount > 0` regardless of finance_type.
  3. **Loans** — now `len({customer_ids})` per bank (unique-by-id set), immune to duplicates.
  4. **Pending** — recomputed as `max(SUM(total_price) − SUM(disbursed), 0)` per bank. Response now also includes `flat_value_total` per bank and `grand_total_flat_value` at the top for transparency.
  5. **Summary bar** — the frontend already used `banks.length`; because that array is now the normalized set, "across N banks" reflects the post-merge count automatically.
- **Verified** — 30-case unit test for `_normalize_bank` (BOB × 6 variants, HDFC × 6, Canara × 4, SBI × 3, ICICI, Axis, Kotak, edge cases — all pass). Synthetic end-to-end test seeded 6 customers across BOB/HDFC/Canara variants (mixed finance_type=self/blank/loan) + 4 disbursement transactions → endpoint returned 3 normalized bank rows with correct sanctioned totals (BOB 60L, HDFC 40L, Canara 18L), correct loans counts (3/2/1), correct pending (BOB=19.8M, Canara=6.5M).
- Files touched: `backend/dashboard/routes.py`.



## 2026-02-28 (enhancement) — "Historical price (locked)" badge for legacy customers
- **What** — Added an amber `🔒 Historical price (locked)` badge in the header of the Property & Pricing card whenever the customer's `created_at < 2026-06-02` (matches the legacy pricing cutoff enforced in `useCustomerPage.js`). Tooltip explains: *"This customer was created before 02 Jun 2026, when the pricing formula changed (BESCOM added to subtotal). Their original agreed total price is preserved and will NOT be recalculated on save."*
- **Total Price row** — During edit mode on a legacy record, the row now shows *"(legacy — recalc skipped on save)"* in amber instead of the green "(live preview)" hint, so admins understand why the stored total won't move even if they tweak fields.
- **Files touched** — `frontend/src/components/customer/details/PropertyPricingCard.jsx`.
- **Verified** — Playwright: JAYANTHI S (created Mar 2026) shows the badge; BESCOM Test User (created Jun 6, 2026 — post-cutoff) shows no badge.



## 2026-02-28 (bug fix) — Pricing formula: honour explicit zeros + legacy-record protection
- **Symptom** — In the Property & Pricing edit form, entering `0` for Club House, Car Parking, BESCOM, or Additional Charges silently reverted to the default (₹3L / ₹2L / etc.) because of the classic `parseFloat(x) || default` short-circuit. Legacy customers (pre-BESCOM formula) had their historical `total_price` silently overwritten every time an admin saved unrelated fields.
- **Fix (`frontend/src/hooks/useCustomerPage.js`)**:
  1. Added a `numOr(raw, fallback)` helper that only falls back when the field is missing (`null` / `undefined` / `""`) — an explicit `0` (numeric or string) is respected.
  2. Rewrote `calculateLivePrice` to use `numOr` for every input: `saleable_area`, `rate_per_sqft`, `floor_rise_cost`, `club_house_charges`, `additional_parking_charges`, `additional_charges`, `bescom_rate`, `interest_amount`.
  3. **Interest gate** — `interest_amount` is now only added to the total when > 0. Null / 0 / NaN contribute nothing (previously would still `+ 0`, but the explicit guard makes intent clear and prevents any NaN slip-up poisoning the total).
  4. **Legacy pricing policy** — customers with `created_at < 2026-06-02T00:00:00Z` predate the BESCOM-inclusive subtotal formula. `handleSaveCustomer` now detects them via `isLegacyPricingCustomer` and **skips the auto-recalc branch entirely**, deleting any stale `total_price` from the PUT payload so their historical price survives edits. Toast reads "Customer updated (historical price preserved — pre-Jun 2026 record)".
- **List View confirmed clean** — `CustomerTable.jsx` doesn't display `total_price` at all; `CustomerQuickInfo.jsx`, `PaymentSummaryCard.jsx`, `DisbursementCalculatorCard.jsx`, `LeadsPage.js` all read `customer.total_price` directly from the API response. No on-the-fly recomputation anywhere on read paths.
- **Verified** — 
  - Unit-level: 8 semantic cases (undefined / null / "" / 0 / "0" / positive num / positive str / NaN str) all behave as expected with `numOr`.
  - Curl round-trip: PUT `club_house_charges: 0` → GET confirms `0` persists (previously would flip to 300000 on next save with liveCalc).
- Files touched: `frontend/src/hooks/useCustomerPage.js`.



## 2026-02-28 (bug fix) — Demand Letter preview eye-icon returned "Not authenticated"
- **Symptom** — Clicking the Preview (eye) icon on `/demand-letters` opened a new tab showing `{"detail":"Not authenticated"}`.
- **Root cause** — The button did `window.open('/api/documents/preview/{id}')`, which fires an unauthenticated GET (no `Authorization` header). Additionally, `/documents/preview/{id}` searches `customer_documents` (uploaded files) and doesn't serve generated docs at all.
- **Fix** — `frontend/src/pages/DemandLettersPage.js`: new helper `openDemandLetterPreview(docId)` that (1) opens a blank tab immediately (to avoid popup-blocker heuristics), (2) fetches the HTML via authenticated axios call to `/api/documents/html/{id}` (the app's global axios instance carries the Bearer token from `AuthContext`), (3) wraps the HTML in a Blob and points the pre-opened tab at the Blob URL. The blob URL is released after 60s. Falls back to same-tab navigation if popup is blocked.
- **Verified** — Playwright: clicked the eye button on the Demand Letters page → new tab opened → body renders `RRL Builders and Developers`, `DEMAND LETTER`, applicant + `Co-Applicant: Marketly` block, full payment table + TDS section. No auth error.
- Files touched: `frontend/src/pages/DemandLettersPage.js`.



## 2026-02-28 (bug fix, HIGH severity) — Save-as-Master corrupted dynamic documents
- **Symptom** — User saved a Demand Letter (for Ramya test lead) as a master template. All subsequent Demand Letters — even for the same customer — lost the Co-Applicant details and rendered with a broken layout (`{saleable_area}th Floor` instead of `11th Floor`, stale stage text, frozen payment-table values, etc.).
- **Root cause** — `render_document_content` blindly preferred any active master template from `db.document_templates` over the built-in per-doc-type generator, even for **dynamic** doc types (Demand Letter, NOCs, Payment Receipt, Price/Cost Breakup, Payment Schedule). These generators compute runtime values that CANNOT be represented as static placeholders:
  - Payment table rows (`Demand Raised`, `Current Due`, `Amount Paid`, TDS Payable, `Net Amount Payable`, `Total Outstanding`, current-stage cumulative percentage, amount-in-words).
  - Conditional Co-Applicant block — `format_applicant_block()` returns only the fields that exist on the source customer (Ramya's co-applicant "Marketly" had only a name, so the saved master baked in JUST `<strong>{co_applicant_name}</strong>` with no Aadhaar/PAN/Phone/Address/DOB rows). Every future customer with a fuller co-applicant lost those rows.
  - Numeric-value collisions in the placeholder scrubber — Ramya's `floor=11` and `saleable_area=11` share the same numeric value; the scrubber matched `saleable_area` first and rewrote "11th Floor" → "{saleable_area}th Floor".
- **Fix (backend)** — `documents/routes.py` + `documents/generators.py`:
  - Introduced `TEMPLATE_SAFE_DOC_TYPES` / `_MASTER_OVERRIDE_ALLOWED` sets containing only doc types built from placeholder-based `.py` templates: `sales_agreement`, `allotment_letter`, `welcome_letter`.
  - `POST /api/templates/save-from-document/{doc_id}` now rejects any doc type outside this set with a clear 400 explaining the reason.
  - `render_document_content` now consults `document_templates` overrides **only** for safe doc types. Dynamic doc types always take the built-in generator path so runtime computations, TDS calc, stage info, and conditional co-applicant rendering are never frozen.
  - One-time DB cleanup: the corrupted demand_letter master saved during user's test session was deactivated (marked `is_active=False`) with an audit reason.
- **Fix (frontend)** — `components/customer/documents/EditableDocumentDialog.jsx`: added a mirror `MASTER_SAFE_DOC_TYPES` allow-list; the "Save as Master" button is hidden for dynamic doc types. Per-customer Edit + Save + Download PDF continue to work as before.
- **Verified** —
  - Regenerated Ramya's Demand Letter after fix: Co-Applicant label + "Marketly" name present, full Payment Table + TDS Payable + TDS Disclaimer restored, "11th Floor" ordinal restored, no `{saleable_area}` leak, reference reads `Flat no. 0701, Tower-1, 11th Floor` (single Tower prefix from prior fix).
  - `POST /api/templates/save-from-document/{doc_id}` for a demand letter now returns HTTP 400 with an actionable message.
- **Files touched** — `backend/documents/routes.py`, `backend/documents/generators.py`, `frontend/src/components/customer/documents/EditableDocumentDialog.jsx`.



## 2026-02-28 (feature) — TDS Disclaimer on Demand Letter + Tower Display Normalization
- **Demand Letter**: added a highlighted disclaimer block after the bank-details section reading: *"TDS to be paid within 30 days, in case failed to, interest shall be levied by Income Tax authorities. Builder will not be held responsible for any interest or penalty."* Styled with a soft amber background and left border to draw attention without disrupting the letter's black/gold theme (`.tds-disclaimer` class).
- **Tower duplication fix** (customer complaint: PDFs were rendering `"Tower- Tower 1"` because DB stores towers inconsistently as `"Tower 1"` / `"Tower-1"` / `"1"`):
  - New shared helper `format_tower(raw)` in `documents/templates/common.py` → strips any leading `Tower` / `Tower-` / `Tower ` prefix (case-insensitive) and re-prefixes with a single canonical `Tower-`. Examples: `Tower 1` → `Tower-1`, `Tower-1` → `Tower-1`, `1` → `Tower-1`, `TOWER-A` → `Tower-A`.
  - New sibling helper `tower_id(raw)` returns just the identifier (`"1"`, `"A"`) — used in info-table cells where the row label is already `Tower` to avoid a `Tower: Tower-1` visual duplicate.
  - **Applied across templates**: `demand_letter.py`, `cost_breakup.py`, `noc_templates.py` (HDFC/BOB/TATA/Bajaj — 4 render functions), `payment_receipt.py`, `payment_schedule.py`, `transactions_export.py`, `booking_form.py`, `price_breakup.py`, `allotment_letter.py` (`{tower}` placeholder), `sales_agreement_html.py` (`{tower}` placeholder).
- **Verified** — 
  - Unit-level: `format_tower` + `tower_id` tests covering all stored variants (`Tower 1`, `Tower-1`, `1`, `A`, `TOWER-B`, empty, None).
  - Per-template renders across all 4 NOC variants + cost/price/booking/payment schedule/transactions export — asserted no `Tower- Tower` / `Tower Tower ` substrings and canonical `Tower-1` present.
  - End-to-end: live demand letter generated via `POST /api/documents/generate` for Ramya test lead now renders `Flat no. 0701, Tower-1, ...` (single occurrence) + TDS disclaimer.
- Files touched: `backend/documents/templates/common.py`, `demand_letter.py`, `cost_breakup.py`, `noc_templates.py`, `payment_receipt.py`, `payment_schedule.py`, `transactions_export.py`, `booking_form.py`, `price_breakup.py`, `allotment_letter.py`, `sales_agreement_html.py`.



## 2026-02-28 (feature) — Additional Charges Description (P0, recurring resolved)
- **Frontend** — `components/customer/details/PropertyPricingCard.jsx`: added a description text input just below the "Additional Charges" amount (edit mode only), plus a helper hint "Optional label — defaults to 'Additional Charges' when blank". View mode now shows the custom description as a small subtitle under the amount when both a non-zero amount and a description exist. Persisted via the existing `editData` spread in `useCustomerPage.js` → PUT /api/customers/{id}. Test IDs: `additional-charges-input`, `additional-charges-description-input`, `additional-charges-value`, `additional-charges-description-value`.
- **Backend** — no schema change (field `additional_charges_description: str = ""` already lived in `customers/models.py` from prior sessions).
- **PDF Template** — `documents/templates/price_breakup.py` already used the field (line 57) as the row label with a fallback to "Additional Charges". Confirmed behaviour with unit-level render tests:
  - Custom label rendered when both amount>0 and description set.
  - Generic "Additional Charges" fallback when description is blank.
  - Row completely hidden when amount is zero.
- **Verified** — curl PUT + GET round-trip on Ramya test lead (`6d902613-5106-4294-bc3e-b907f85127f7`); Playwright screenshot on preview URL confirms the new input appears in edit mode and accepts text.
- Files touched: `frontend/src/components/customer/details/PropertyPricingCard.jsx`.



## 2026-07-28 (feature) — Bulk Demand-Letter Workflow
- **Backend** — extends `GeneratedDocument` model in `documents/models.py` with optional `stage_key`, `stage_name`, `batch_id`, `emailed_at`, `email_status`, `emailed_by` fields (all default None → single-doc flows unaffected).
- Three new endpoints in `documents/routes.py`:
  - `POST /api/documents/generate-bulk-demand-letters` — admin/manager/accounts. Loads current stage from `db.settings`, iterates every non-pending_approval customer, and generates a demand letter for anyone missing one for that `stage_key`. Idempotent: repeat calls only skip. Reuses `_render_demand_letter` so the layout is identical to single-generation. Returns `{ batch_id, stage_key, stage_name, generated/skipped/error counts, generated_ids[] }`.
  - `GET /api/documents/demand-letters` — same roles. Lists all demand letters with customer name/unit/email hydrated in one aggregated query, supports `?stage_key=`, `?batch_id=`, `?emailed=true|false`. Declared BEFORE `/documents/{customer_id}` to prevent route-shadowing.
  - `POST /api/documents/bulk-email-demand-letters` — accepts `{ids: [...]}` or `{batch_id: '...'}`. Renders each doc's stored HTML → PDF via WeasyPrint, sends through the existing `_resend_send` helper with the PDF attached, and stamps `emailed_at` / `email_status` / `emailed_by` per row. Failures are persisted (so retries can be scoped) and communication_logs entries are inserted per send.
  - Both helpers `_resolve_recipient_email` (applicant → co-applicant fallback) and `_build_demand_letter_email` (personalised subject + HTML body) live in `documents/routes.py`.
- **Frontend** — new `pages/DemandLettersPage.js` (route `/demand-letters`, sidebar entry with MailWarning icon, roles admin/manager/accounts):
  - Total / Emailed / Pending stat tiles.
  - Filters (search, milestone dropdown, emailed y/n) with `?batch_id=` URL param support so the confirmation flow from PaymentStageCard can deep-link to the freshly-generated batch.
  - Table with row checkboxes and per-row preview button (`GET /documents/preview/{id}`).
  - Sticky bulk-select toolbar (`data-testid="bulk-toolbar"`) + `Email Selected (N)` button with a browser confirm().
  - Client-side role guard prevents the 403 fetch for sales/support roles.
- **PaymentStageCard** — new AlertDialog (`data-testid="bulk-demand-confirm-dialog"`) shown after a successful stage update; offers to bulk-generate for the new milestone (`bulk-demand-trigger`) or skip (`bulk-demand-skip`); on success navigates the user to `/demand-letters?batch_id=…` so they can review + email in the same flow.
- **Verified** — iteration_54: **15/15 backend pytest cases pass** + full Playwright frontend flow (sidebar visibility per-role, generation, listing, selection, bulk-email including a customer-missing failure isolation case), all data-testids present. Regression test file `backend/tests/test_bulk_demand_letters_iter54.py`.
- Files: `backend/documents/models.py`, `backend/documents/routes.py`, `frontend/src/pages/DemandLettersPage.js`, `frontend/src/App.js`, `frontend/src/components/layout/DashboardLayout.js`, `frontend/src/components/dashboard/PaymentStageCard.jsx`.


## 2026-07-28 (feature) — Bank Disbursement Summary card on Dashboard
- **Backend** — new admin-only `GET /api/dashboard/disbursement-summary` (in `backend/dashboard/routes.py`) that:
  - Sums `payment_transactions.amount` where `transaction_stage == 'scheduled_disbursement'` → `total_disbursed`.
  - For customers with `finance_type in {loan, mixed}` and `loan_amount > 0`, computes `pending = max(loan_amount - disbursed_to_date, 0)` (never negative).
  - Normalizes bank names via `_normalize_bank` (uppercase + iterative strip of ` BANK`, ` LTD`, ` LIMITED`, ` BANK LTD.`, ` BANK LIMITED`, etc.), so `HDFC BANK` == `HDFC` == `HDFC Bank Ltd`. Empty → `UNSPECIFIED`.
  - Bucket-key preference: `customer.finance_bank > txn.bank_name` for financed customers; txn fallback for non-financed. Rolls up per bank into `banks[]` with `total_disbursed / pending_disbursement / loan_amount / customer_count`, sorted by pending desc.
  - Orphan handling: disbursements whose `customer_id` is not in the customers collection are excluded from `banks[]` / grand totals and surfaced separately in `unmatched[]` (capped at 50 rows) with `unmatched_total` and `unmatched_count`. Cleanup uses the existing `POST /api/dashboard/reconciliation/delete-orphan/{id}` endpoint (admin-only, refuses if customer still exists, writes an activity audit log).
- **Frontend** — new `DisbursementSummaryCard.jsx` in `components/dashboard/`:
  - Headlines `Grand Total Pending Disbursement` in 4xl–5xl indigo text; supporting `Total Disbursed To Date` tile beside it.
  - Per-bank breakdown table (Bank / Loans / Sanctioned / Disbursed / Pending) with a small "% disbursed" hint under each bank name.
  - Unmatched-disbursements section (only when count > 0) with per-row delete button (`data-testid="delete-unmatched-<txn_id>"`) that calls the delete-orphan endpoint and refreshes.
  - Refresh button `data-testid="refresh-disbursement-btn"`; all rows have stable testids (`disbursement-row-<BANK>`, `unmatched-row-<txn_id>`).
  - Mounted on `pages/DashboardPage.js` after `<RevenueCards>` and before `<PaymentStageCard>`, admin-gated via `hasRole('admin')`.
- **Verified** — iteration_53 report: **10/10 backend pytest cases pass** + full Playwright frontend flow; regression-safe test file `backend/tests/test_disbursement_summary_iteration53.py` self-seeds and cleans up TEST_ITER53_DISB_-prefixed data.
- Files: `backend/dashboard/routes.py`, `frontend/src/components/dashboard/DisbursementSummaryCard.jsx`, `frontend/src/components/dashboard/index.js`, `frontend/src/pages/DashboardPage.js`.


## 2026-07-03 (bug fix) — Co-Applicant Missing From Restored Sales Agreement
- **Bug**: After "Restore to Default" or Save-As-Master + regenerate, the Sales Agreement signature block showed `{customer_name} AND {co_applicant_name}` as literal placeholder text instead of the customer's real co-applicant name.
- **Root cause**: `_scrub_customer_values_to_placeholders` was correctly scrubbing co-applicant scalars (`co_applicant_name`, `_father_name`, `_pan`, `_aadhar`, `_email`, `_phone`, `_address`) into `{co_applicant_*}` tokens, but `_build_placeholders` (used by the override-template render path) did not resolve those tokens back to customer data at render time. Same issue for `{customer_names}`, `{age}`, `{salutation}`, `{aadhaar_number}`, `{floor_ordinal}`, `{additional_parking}`, `{additional_parking_text}`, `{possession_date}`, `{base_price_formatted}`, `{club_house_formatted}`, `{parking_charges_formatted}`, `{labour_cess_formatted}`, `{gst_formatted}`, `{logo_img}`, `{company_name}` — all present in `sales_agreement_html.py` but missing from the fallback builder.
- **Fix**: extended `_build_placeholders` in `documents/generators.py` to resolve every placeholder emitted by `sales_agreement_html.py`, so any Sales Agreement master template saved via `save_master_from_document` now re-renders correctly for any target customer (with or without a co-applicant).
- **Verified**: iteration_52 91/91 pytest cases green. Manual check: signature block correctly renders `Ramya test lead AND Marketly` and PURCHASER block correctly renders the `Co-Applicant:` paragraph. Zero unresolved `{...}` tokens in the final doc.
- Files: `backend/documents/generators.py`.


## 2026-07-03 (feature) — Bulk-Delete Across All 8 Delete Surfaces
- **Backend**: 8 new admin-only `POST /api/.../bulk-delete` endpoints, all accept `{ids: [...]}`:
  - `POST /api/users/bulk-delete` — silently strips current user's id (self-lockout guard)
  - `POST /api/customers/bulk-delete` — cascades to payment_schedules, document_checklists, generated_documents, communication_logs, payment_transactions
  - `POST /api/templates/bulk-delete` — reverts overrides to defaults
  - `POST /api/documents/bulk-delete` — generated documents
  - `POST /api/customers/{customer_id}/documents/bulk-delete` — uploaded docs + strips pointers from customer.uploaded_documents
  - `POST /api/transactions/{customer_id}/bulk-delete` — recomputes customer totals/percentages
  - `POST /api/customers/{customer_id}/notes/bulk-delete` — MongoDB $pull with $in
  - `POST /api/customers/{customer_id}/follow-ups/bulk-delete` — recomputes latest_call_status
- **Parity fix**: single-delete `DELETE /api/customers/{id}` now also cascades to payment_transactions (previously orphaned; flagged by iteration_52 testing agent).
- **Frontend reusable pieces**: `hooks/useBulkSelect.js` (Set-based O(1) toggle, isAllSelected/isPartiallySelected/clear helpers) + `components/common/BulkDeleteBar.jsx` (sticky red toolbar + AlertDialog listing up to 20 preview names).
- **Wired into 8 surfaces**: Customers list, Users, Document Templates (chip-style multi-select), Generated Documents (regular + NOC), Uploaded Docs, Transactions, Notes, Follow-ups.
- **Safety rails**: admin-only via `check_role([UserRole.ADMIN])` on every endpoint; UI toolbar only renders for `isAdmin=true`; empty/missing/non-array ids → 400; non-existent ids → 200 with `deleted_count:0` (no 500).
- **Tested**: iteration_52 — 48/48 pytest cases green (`backend/tests/test_bulk_delete_iteration52.py`), 3/3 Playwright flows verified.
- Files: `auth/routes.py`, `customers/routes.py`, `documents/routes.py`, `payments/routes.py`, `settings/__init__.py`, `hooks/useBulkSelect.js`, `components/common/BulkDeleteBar.jsx`, `pages/CustomersPage.js`, `pages/SettingsPage.js`, `pages/CustomerDetailPage.js`, `hooks/useCustomerPage.js`, `components/customers/CustomerTable.jsx`, `components/settings/UserManagementCard.jsx`, `components/settings/DocumentTemplatesTab.jsx`, `components/customer/{NotesTab,DocumentsTab,UploadsTab,FollowUpTracker,PaymentTrackingTab}.jsx`, `components/customer/payment/TransactionsTable.jsx`.

## 2026-07-03 (feature) — Master Template Placeholder Coverage
- Extended `_scrub_customer_values_to_placeholders` (now async) to also scrub word-form amounts (`{total_price_words}`, `{booking_amount_words}`, `{total_received_words}`), Indian-formatted amounts (both decimal variants) into `{*_formatted}`, applicant/co-applicant block into `{applicant_details_block}`, payment-schedule rows into `{payment_schedule_rows}`, booking/agreement transaction rows into `{transaction_rows}`, and the sales-agreement date string into `{agreement_date_text}`.
- Extended `_build_placeholders` (now async, takes `db`) to resolve those same placeholders at render time.
- Extracted 4 shared helpers into `documents/templates/common.py` (`build_agreement_date_text`, `build_applicant_details_block`, `build_payment_schedule_rows_html`, `build_transaction_rows_html`); refactored `sales_agreement_html.py` to use them for scrub↔render parity.
- Files: `backend/documents/routes.py`, `backend/documents/generators.py`, `backend/documents/templates/common.py`, `backend/documents/templates/sales_agreement_html.py`.


## 2026-06-28 (feature) — Notification Bell: current_stage Filter
- Both `/api/follow-ups/pending` and `/api/follow-ups/upcoming` now filter out follow-ups whose `stage_key` is past the admin-set `current_stage`. Reason: stages beyond current are not yet being collected — surfacing them in the bell is noise.
- New helper `_valid_stage_keys(current_stage_key)` in `backend/settings/__init__.py` mirrors the walking logic in `_compute_overdue_stages()`. Fall-open semantics: unknown / missing / null current_stage → empty set → filter skipped (no accidental bell blackout).
- Composes with the existing filters (Completed skip + paid-stage drop + dedup per customer × stage) — a follow-up must clear all four gates to appear.
- Test updates in `backend/tests/test_notification_bell.py`:
  - New module-scope fixture `stage_at_handover` bumps current_stage to `handover` for the whole module so the pre-existing tests can freely seed follow-ups on any stage_key; restores the original value at teardown.
  - `test_keep_follow_up_on_unpaid_far_stage` inverted per user request — now asserts a `handover` follow-up is FILTERED OUT when current_stage='podium'.
  - `test_keep_follow_up_on_next_unpaid_stage` mirrored to check `2nd_floor` filtering (same rationale).
- Tested: 18/18 pytest in `test_notification_bell.py` + 4/4 in `test_stage_filter_iter50.py` (helper unit + endpoint variations). Iteration_50 — 100% pass, DB `current_stage` correctly preserved + restored.
- Files: `backend/settings/__init__.py`, `backend/tests/test_notification_bell.py`, `backend/tests/test_stage_filter_iter50.py` (new).

## 2026-06-28 (bugfix) — Notification Bell: De-dupe & Stage-Aware Filtering
- **Bug 1** (user-reported, visible in screenshot): same customer × same stage appeared multiple times in the bell because every historical follow-up log entry was emitted (e.g. *Deepankar Dutta · 1-1303* listed once as `Connected` and again as `Follow-up`, both for the same '6th Floor Roof Slab' stage).
- **Bug 2** (user-reported): old-stage follow-ups never dropped off even after the customer paid past that slab — the bell kept nagging on resolved stages.
- **Bug 3** (caught by testing agent in same iteration): `/api/follow-ups/upcoming` did NOT filter `status='Completed'` — already-resolved entries still fired in-app reminder toasts.
- **Fix** in `backend/settings/__init__.py::get_pending_follow_ups()`:
  - Collapse to ONE entry per (customer × stage_key) — keep the latest by `created_at`, skip Completed.
  - Drop the entry if `total_received + 1 INR ≥ total_price × stage.cumulative% / 100` (same +1 INR tolerance as `_compute_overdue_stages`) — so paid-up stages auto-clear.
- **Fix** in `backend/settings/__init__.py::get_upcoming_follow_ups()`: also skip Completed entries.
- Tested: 18/18 pytest in `test_notification_bell.py` (11 existing + 7 new) — iteration_49, 100% pass.
- Files: `backend/settings/__init__.py`. Tests: `backend/tests/test_notification_bell.py`.

## 2026-06-28 (feature) — Revenue Reconciliation Debug Card
- New admin-only **Revenue Reconciliation** card on the main dashboard. Surfaces the gap between "Total Revenue Collected" (aggregate sum) and "Total Collected (Cumulative)" (per-customer loop) — current preview DB had 142 orphan transactions worth ₹9.22 Cr causing exactly this drift (customer_ids deleted while payment receipts stayed behind).
- Backend endpoints (`backend/dashboard/routes.py`):
  - `GET /api/dashboard/reconciliation` (admin-only) — returns both totals, difference, orphan list (cap 25, sorted by amount desc), verdict (`ok` / `orphans` / `unknown`) and a human-readable message.
  - `POST /api/dashboard/reconciliation/delete-orphan/{transaction_id}` (admin-only) — hard-deletes an orphan txn; refuses if the customer_id still exists in customers (safety lock). Writes to `activity_logs` for audit compliance.
- Frontend `ReconciliationCard.jsx`:
  - 3-card grid (Total Revenue / Total Collected / Difference) with rose-red diff highlight when drift > ₹0.5.
  - Inline orphan table with Trash button per row (shows 5 by default, "Show all" expands to 25). Optimistic removal after delete.
  - Verdict-based theming (emerald=ok, amber=orphans, rose=unknown).
  - Card returns null for non-admin roles (hidden silently — no error UI).
- **Tested**: 8/8 backend pytest (`test_reconciliation.py`) + Playwright admin/sales role gating + delete-flow API. Iteration_48 — 100% pass, no defects.
- Files: `backend/dashboard/routes.py`, `frontend/src/components/dashboard/ReconciliationCard.jsx` (new), `frontend/src/components/dashboard/index.js`, `frontend/src/pages/DashboardPage.js`. Tests: `backend/tests/test_reconciliation.py`.

## 2026-06-28 (feature) — Call-Status Filter on Customers List
- New "All Call Statuses" Select dropdown on `/customers`, placed immediately next to the Disbursement Overdue button. Options: All / — Not Called Yet — / Dialed / Connected / Unanswered / Follow-up / Completed. Active selection gets amber styling + a "<n> match(es)" badge.
- **Filter is combinable** — e.g. `Overdue + Unanswered` issues `?agreement_filter=overdue&call_status=Unanswered` to surface the highest-priority calls.
- **Backend**: new `call_status` query param on `GET /api/customers`. `no_status` matches customers whose `latest_call_status` field is missing or null. Special-cased in a future-safe `$and` merge so it doesn't clobber any pre-existing `$or` clause.
- **Denormalisation**: new `_recompute_latest_call_status()` helper in `settings/__init__.py` writes a top-level `latest_call_status` field on the customer document whenever a follow-up is added/updated/deleted/quick-set. Backfilled current DB.
- The in-memory derivation in `GET /api/customers` is kept as a fallback so legacy rows still render their status in the Call Status column.
- Tested: 11/11 backend pytest (`test_call_status_filter.py`) + Playwright e2e — iter_47, 100% pass.
- Files: `backend/customers/routes.py`, `backend/settings/__init__.py`, `frontend/src/components/customers/CustomerFilters.jsx`, `frontend/src/pages/CustomersPage.js`.

## 2026-06-28 (UX) — Interior Email: Mobile-Friendly + Prominent WhatsApp/Phone Block
- **Bug**: 3-column CTA row squeezed on narrow viewports — button text wrapped vertically ("Book a Design / Consultation"). Phone number relegated to small print at the bottom.
- **Fix** in `generate_interior_email_html`:
  - Single-column nested-table layout — every CTA anchor is `display: block` full-width with `text-align: center`; buttons now stack one per row on every device.
  - New dashed-green phone block on top of the CTAs containing: a label ("CALL OR WHATSAPP US DIRECTLY"), the number rendered as a 26px `tel:+919619995516` link, and a bright green "Chat on WhatsApp →" anchor (wa.me link with prefilled message).
  - Padding bumped (14–16px button vertical) → tap-friendly targets on mobile.
  - Phone number + tel: URL added to `INTERIOR_CTA_LINKS` for single-source-of-truth.
- **Fix** in `generate_document_email_html` base template:
  - Added `<meta name="viewport" content="width=device-width, initial-scale=1.0">`.
  - Added a `@media (max-width: 600px)` block that tightens `.rrl-body` / `.rrl-shell` / `.rrl-card` padding on phones.
  - Welcome / Sales Agreement / Allotment Letter / Interior emails all benefit.
- Tested: 8/8 pytest + Playwright headless render at 420×900 (mobile) and 1280×1200 (desktop). Iteration_46 — 100% pass, no defects.
- Files: `backend/email_service/routes.py`, `backend/documents/templates/email_templates.py`. Tests: `backend/tests/test_interior_email.py`.

## 2026-06-28 (bugfix) — Welcome Email: 4-PDF Attachment Pack & Preview Tab
- **Bug A** (auto-welcome via public booking): only `PriceBreakup.pdf` + static `Total_Registration_Charges.pdf` were attached. Missing `BookingFormPreview.pdf` and `TermsAndConditions.pdf`. Fix in `backend/booking/__init__.py::_send_booking_welcome_email` — now renders form preview HTML + T&C HTML + Price Breakup HTML, attaches all 3 + the static asset (= 4 total). Comm-log content now lists each filename.
- **Bug B** (composer preview): Total Registration Charges PDF was not previewable. Fix in `backend/email_service/routes.py::preview_welcome_email` — returns new `attachment_filename_4` + `attachment_pdf_base64_4` (base64 of the static PDF). `attachments[]` array updated to 4. Default body now lists item 4.
- **Frontend** (`EmailComposerDialog.jsx`): 5th tab `Registration Charges` renders the static PDF in an `<iframe data-testid="attachment-pdf-preview-4">`. 4th badge added to the Attachments box. Tabs grid bumped to `grid-cols-5 max-w-3xl` for welcome.
- **Parity fix**: `send-document-email` with `email_type=welcome` also now appends the static asset (was 3 attachments, now 4) — matches `_send_booking_welcome_email` + `send-welcome-email`.
- **Interior email "not going" in prod**: verified send works in preview/dev. Production-only failure — user needs to redeploy to push these fixes (and earlier interior email refactor) to https://rrlcrm.com.
- **Tested**: 5/5 backend pytest (`backend/tests/test_welcome_4_attachments.py`) + Playwright frontend (iteration_45 — 100% pass).
- Files: `backend/booking/__init__.py`, `backend/email_service/routes.py`, `frontend/src/components/customer/EmailComposerDialog.jsx`.

## 2026-06-27 (hardening) — XSS Sanitisation + Lint Cleanup
- New shared utility `frontend/src/utils/sanitize.js` exporting `sanitizeEmailHtml()` and `sanitizeText()`. Forbids `<script>/<iframe>/<object>/<embed>/<link>/<base>/<form>/<input>/<button>/<textarea>/<select>/<option>`, all `on*` event handlers, `formaction`, `srcdoc`. Auto-stamps `rel="noopener noreferrer"` on every `<a target=_blank>` via a `DOMPurify.addHook` registered once at module-load.
- `frontend/src/utils/safePreview.js`: hardened. `openSafePreviewWindow` uses the strict config; new `openSafePdfPreview` validates the `data:application/pdf;` scheme prefix and escapes quotes before stamping into the iframe `src`. Both open the new window with `noopener,noreferrer`. Hook registration delegated to `sanitize.js` (no double-register).
- `EmailComposerDialog.jsx`: dropped direct `DOMPurify` import; all four `dangerouslySetInnerHTML` sites now route through `sanitizeEmailHtml`.
- `useCustomerPage.js`: removed 3 stale `eslint-disable-next-line react-hooks/exhaustive-deps` comments (deps were already satisfied). `handlePreviewUploadedDoc` now delegates to `openSafePdfPreview` instead of inline blob-URL construction.
- `DashboardPage.js`: unescaped apostrophes (`'`) replaced with `&apos;` to satisfy `react/no-unescaped-entities`.
- Verified by testing_agent_v3_fork (iteration_44): 27/27 XSS unit tests pass (`/app/frontend/tests/sanitize.test.cjs`), 0 lint warnings, all 4 email preview dialogs still render with inline styles + CTA buttons intact. No regressions.
- Files: `frontend/src/utils/sanitize.js` (new), `frontend/src/utils/safePreview.js`, `frontend/src/components/customer/EmailComposerDialog.jsx`, `frontend/src/hooks/useCustomerPage.js`, `frontend/src/pages/DashboardPage.js`. Tests: `frontend/tests/sanitize.test.cjs`.

## 2026-06-27 (feature) — Interior Email: Inline CTA Buttons, No PDF Attachment
- Replaced the PDF attachment (`RRL_Interior_Inhouse_Team.pdf`) with **three CTA buttons embedded directly in the email HTML**: Book a Design Consultation (WhatsApp deep link), View Design Catalog (designhive.in), Follow on Instagram. Single source of truth: `INTERIOR_CTA_LINKS` dict.
- New helper `generate_interior_email_html(customer, subject, body)` wraps the existing dark/gold email template and injects a gold-bordered CTA block before the signature.
- `preview_interior_email` no longer returns `attachment_filename`/`attachment_static`. `send_document_email` interior branch is now a no-op for attachments and uses the new wrapper.
- Frontend `EmailComposerDialog`:
  - New title "Send Interior Design Email"
  - Hides the "Attachments (Auto-generated)" badge box when there's no attachment
  - Shows an amber info banner explaining CTA buttons are embedded inline
  - Tabs grid is `grid-cols-1` (only Email Preview) for interior emails
- Body copy refreshed — removed "The complete brochure is attached" line.
- **Tested**: 100% pass backend + Playwright frontend (iteration_43, no defects).
- Files: `backend/email_service/routes.py`, `frontend/src/components/customer/EmailComposerDialog.jsx`. Tests: `backend/tests/test_interior_email.py`.

## 2026-06-27 (bugfix) — Bajaj NOC: Details of Purchaser table overlap/break
- **Bug**: When downloading the Bajaj Housing Finance NOC, the "Details of Purchaser" table broke at page boundaries — the long Project Location/Address row would wrap and split mid-row, drawing two partial borders that overlapped the next row's border in the rendered PDF.
- **Fix** in `backend/documents/templates/noc_templates.py::generate_noc_bajaj_html`:
  - `.details-table { table-layout: fixed; }` — predictable column widths
  - `.details-table tr { page-break-inside: avoid; break-inside: avoid; }` — rows that don't fit move wholesale to the next page
  - `.details-table th, .details-table td { vertical-align: top; word-wrap: break-word; overflow-wrap: anywhere; }` — long content wraps inside cells, never distorts layout
- Scope: noc_bajaj only (HDFC/BOB/TATA NOC regression verified — no impact).
- **Tested**: 7/7 pytest (iteration_42, 100% pass). Page 1 contains rows 1–9 ending with 'Lender's Name' complete; page 2 starts cleanly with 'Own Contribution'. Long Bengaluru address wraps to 2 lines inside its cell.
- Files: `backend/documents/templates/noc_templates.py`. Tests: `backend/tests/test_noc_bajaj_pdf.py`.

## 2026-06-27 (bugfix) — Customer List Pagination (skip/limit)
- **Bug**: Only the first 50 customers were visible on `/customers` because frontend `fetchCustomers` omitted `skip`/`limit` and the backend defaulted to `limit=50`, silently truncating without any UI affordance.
- **Fix**: `CustomersPage.js` now drives a 0-based `page` + `pageSize` state (default 50, options 25/50/100/200/500), sends `skip=page*pageSize&limit=pageSize` on every fetch, and resets `page=0` on any filter change.
- **UI**: New "Showing N–M of TOTAL" label, page-size Select dropdown, and a Prev / `Page X of Y` / Next footer (only shown when `total > pageSize`). Buttons disabled at boundaries.
- **Tested**: 6/6 backend pytest + Playwright UI exercise with 55 seeded TEST_pagination_* customers (iteration_41, 100% pass). All seeded rows cleaned up.
- Files: `frontend/src/pages/CustomersPage.js`. Tests: `backend/tests/test_customers_pagination.py`.

## 2026-06-27 (later still) — Notification Bell in Header
- New **bell icon** in the header (left of the user dropdown) — surfaces every follow-up whose status is not yet `Completed`. Badge shows total count (red when past-due+today > 0, slate otherwise; "99+" cap).
- Popover lists entries grouped into buckets: **Past Due → Today → Upcoming → Unscheduled**. Each row: customer + tower-unit, status badge (colour-coded), stage, scheduled date+time, truncated notes.
- Row click deep-links to `/customers/{id}?tab=notes&focus={fid}` — CustomerDetailPage now reads `?tab=` via `useSearchParams` and opens the Notes tab (= Calling & Follow-up Tracker / call log) by default.
- Each row has a **Done** button (emerald outline) that PATCHes the follow-up to status=`Completed` (stamps `completed_at`, `completed_by`, `completed_by_name`), removes it optimistically from the popover, and decrements the badge.
- New backend endpoints in `followups_router`: `GET /api/follow-ups/pending` and `PATCH /api/customers/{id}/follow-ups/{fid}`. Pending list sorts by urgency bucket then date+time. PATCH validates against FOLLOW_UP_STATUSES.
- Accessibility: row wrapper is `<div role="button" tabIndex={0}>` with Enter/Space keyboard handler (avoids nested `<button>` HTML violation that initially caused a React `insertBefore` crash — caught + fixed in iter_40).
- Polling: bell refreshes every 60s in addition to on-mount and after PATCH.
- **Tested**: 11/11 backend pytest + Playwright e2e across admin/sales/accounts — 100% pass, no defects (iteration_40).
- Files: `backend/settings/__init__.py`, `frontend/src/components/layout/NotificationBell.jsx` (new), `frontend/src/components/layout/DashboardLayout.js`, `frontend/src/pages/CustomerDetailPage.js`. Tests: `backend/tests/test_notification_bell.py`.

## 2026-06-27 (later) — Call Status Column on Customers List
- Added a new **Call Status** column on `/customers` table, between *Agreement* and *Actions*, with quick-edit Select dropdown.
- Backend: `POST /api/customers/{id}/follow-ups/quick-status` (no role guard — all roles intentional) logs a follow-up against the admin-set `current_stage` (fallback to `PAYMENT_STAGES[0].key`). GET `/api/customers` now enriches each row with `latest_call_status`, `latest_call_status_at`, `latest_call_status_stage` from the most recent follow_ups entry.
- Frontend: `CustomerTable.jsx` shows colour-coded badge trigger (Dialed=blue, Connected=emerald, Unanswered=rose, Follow-up=amber, Completed=violet); dropdown stops row-click propagation so it does not navigate to the profile. Handler in `CustomersPage.js::handleCallStatusChange` calls the new endpoint and updates the row in place.
- Quick-status entries land in the same `follow_ups` array — they show up in the Calling & Follow-up Tracker history on the customer profile too.
- Tested: 8/8 pytest + Playwright e2e for admin, sales, accounts (iteration_38, 100%).
- Files: `backend/customers/routes.py`, `backend/settings/__init__.py`, `frontend/src/components/customers/CustomerTable.jsx`, `frontend/src/pages/CustomersPage.js`. Tests: `backend/tests/test_call_status_column.py`.

## 2026-06-27 — Multi-Level Calling / Follow-up Tracker
- **New feature**: Sales/Accounts/Admin can log multi-level follow-up calls tied to disbursement stages directly from the customer profile (Notes tab). Differentiated amber-themed card sits above the existing Notes card.
- **Schema**: `follow_ups` array embedded on each customer doc — `{id, stage_key, stage_name, status, notes, next_follow_up_date, next_follow_up_time, created_at, created_by, created_by_name}`. Valid statuses: `Dialed`, `Connected`, `Unanswered`, `Follow-up`, `Completed`.
- **Backend endpoints** (`/app/backend/settings/__init__.py`, exposed via `followups_router`):
  - `GET /api/customers/{id}/follow-ups` → returns `{follow_ups, overdue_stages, current_stage, all_stages, statuses}`. Overdue stages computed from PAYMENT_STAGES cumulative% × total_price vs total_received, capped at admin's current stage.
  - `POST /api/customers/{id}/follow-ups` → validates stage_key + status; pushes entry; logs activity.
  - `DELETE /api/customers/{id}/follow-ups/{follow_up_id}`.
  - `GET /api/follow-ups/upcoming` → today + past-due entries with `is_today`/`is_past_due` flags for the reminder hook.
- **Frontend**:
  - `components/customer/FollowUpTracker.jsx` (amber gradient card, stage+status+date+time+notes form, history grouped by stage, delete per entry).
  - `hooks/useFollowUpReminders.js` mounted in `DashboardLayout` — polls `/follow-ups/upcoming` every 60s; when due, plays Web-Audio chime + browser notification + toast (one fire per entry per session).
  - `utils/followUpSound.js` — Web Audio API 2-tone chime (C5→E5), no shipped assets.
  - `NotesTab.jsx` now wraps both tracker + notes; `CustomerDetailPage.js` passes `customerId` prop.
- **Permissions**: All roles (admin, manager, sales, accounts, support) can create + delete entries per product spec.
- **Tested**: 10/10 pytest (`/app/backend/tests/test_follow_ups.py`) + frontend Sales+Accounts UI flow (iteration_37).
- Files: `backend/settings/__init__.py`, `backend/server.py`, `frontend/src/components/customer/FollowUpTracker.jsx` (new), `frontend/src/components/customer/NotesTab.jsx`, `frontend/src/pages/CustomerDetailPage.js`, `frontend/src/hooks/useFollowUpReminders.js` (new), `frontend/src/utils/followUpSound.js` (new), `frontend/src/components/layout/DashboardLayout.js`.

## 2026-06-17 (final) — Interior Email Button + Static Brochure Attachment
- **New "Interior" button** in the customer profile header, sitting right next to "Allotment Letter" (purple accent, sofa icon, `data-testid="send-interior-btn"`).
- **Personalized email body** auto-fills customer name + flat number (e.g. *"Congratulations on your new home at Flat No. 0701, RRL Palm Altezze!"*). Content is faithfully adapted from `RRL PA WHY IN HOUSE TEAM.pdf` — covers why-in-house benefits, external-vendor protocols (₹2L deposit, no early access, debris management), and Sunrise DesignHive contact links (Instagram, website, WhatsApp).
- **Attachment**: static PDF stored at `/app/backend/assets/email_templates/interior/RRL_Interior_Inhouse_Team.pdf` (74 KB). Same file goes out to every customer — no per-customer regeneration.
- **New backend endpoints**: `GET /api/communication/preview-interior-email/{customer_id}` + extended `POST /api/communication/send-document-email/{customer_id}` with `email_type: "interior"` branch (loads PDF as `static_bytes`, skips the per-customer doc-persistence step).
- **Frontend**: `useCustomerPage.js::handlePreviewInteriorEmail` opens the existing EmailComposerDialog with the preview body editable before send. Uses the same axios + auth flow as other email buttons.
- **Verified via Resend API**: Interior email sent to test recipient, id `6eb192a0-f2b5-442c-887b-766e0f2a7497`, attachments delivered to Resend = 1 (`RRL_Interior_Inhouse_Team.pdf`). Personalized subject: *"Design Your New Home – RRL Palm Altezze - Flat No. 0701"*.
- Files: `backend/assets/email_templates/interior/RRL_Interior_Inhouse_Team.pdf` (new), `backend/email_service/routes.py`, `frontend/src/components/customer/CustomerHeader.jsx`, `frontend/src/hooks/useCustomerPage.js`, `frontend/src/pages/CustomerDetailPage.js`. Lint clean.

## 2026-06-17 (later) — Total Registration Charges PDF Added to Welcome Email
- New static PDF `Total_Registration_Charges.pdf` (131 KB) saved to `/app/backend/assets/welcome_email/`. Sent to customers as `RRL_Total_Registration_Charges.pdf`.
- New helper `documents/templates/common.py::get_welcome_email_static_attachments()` reads + base64-encodes any file listed in `WELCOME_EMAIL_STATIC_ATTACHMENTS`. Missing files are logged + skipped, never raise.
- Wired into both welcome paths: `booking/__init__.py::_send_booking_welcome_email` (auto on submit) and `email_service/routes.py::send_welcome_email` (manual). Existing 3 attachments preserved.
- **Verified via Resend API**: latest manual welcome to Ramya (id `42482b20-cbfb-4f11-b88d-d667f70a5470`) shows 4 attachments — BookingFormPreview, T&C, PriceBreakup, **Total Registration Charges** ✅
- To add another static add-on later: drop the PDF in `/app/backend/assets/welcome_email/` and append `(sent_name, disk_name)` to `WELCOME_EMAIL_STATIC_ATTACHMENTS`.
- Files: `backend/assets/welcome_email/Total_Registration_Charges.pdf` (new), `backend/documents/templates/common.py`, `backend/booking/__init__.py`, `backend/email_service/routes.py`. Memory: `DEPLOYMENT_INVARIANTS.md` § 5.

## 2026-06-17 — Demand Letter: TDS excluded from Installment Paid + Net Amount uses Total TDS Payable
- **Installment Amount Paid Till Date (C)** now excludes any payment_transaction with `transaction_stage == 'tds'`. TDS challans are reported only on the "TDS Paid" row — keeping them out of "Installment Paid" prevents double-counting.
- **Net Amount Payable** formula reverted to `max(0, Total Outstanding − Total TDS Payable)` (lifetime). The earlier per-slab formula (`− Current TDS due for Slab X%`) is removed. Sub-label updated.
- "Current TDS due for Slab X%" row is still shown for reference but is no longer used in the Net Amount calculation.
- **Verified end-to-end on Ramya**: With no TDS txns → Paid=85,560, Net=0. After injecting ₹5,000 TDS-stage txn → Paid still 85,560 (no double count), TDS Paid=5,000, TDS To be Paid=0. Then cleaned up the test txn.
- Files: `backend/documents/templates/demand_letter.py`; memory: `DEPLOYMENT_INVARIANTS.md` § 3, `TDS_CALCULATION_LOGIC.md` next-update.

## 2026-06-16 (later still) — Auto-Persist PDF at Booking Submit + View/Download UI
- **Every new booking submission now stores the actual PDF binary** on the customer record (`original_booking_form_pdf_b64`, `recovered_from = "booking_submit"`) — generated via WeasyPrint immediately before `insert_one`. Wrapped in try/except so the booking itself is never blocked by a render failure. Going forward, no dependency on Resend retention.
- **Customer profile → Documents tab** has a new amber-bordered locked card at the top with **View** + **Download** buttons (uses axios with global Authorization header — fixes earlier 403 caused by reading from wrong storage).
- Files: `backend/booking/__init__.py` (PDF persistence in `submit_booking_form`), `frontend/src/components/customer/DocumentsTab.jsx` (View/Download buttons via axios + Blob), `frontend/src/pages/CustomerDetailPage.js` (passes `customer` to DocumentsTab).
- **Verified end-to-end on a freshly-submitted booking**: PDF binary 206 KB base64 → endpoint returns 154 KB valid PDF with `%PDF-` magic. View opens in new tab, Download saves as `RRL_OriginalBookingForm_<Name>.pdf`. BCC `docs.rrlprojects@gmail.com` confirmed in every outbound send path.

## 2026-06-16 (final) — Resend Recovery for Truly-Original PDFs ✅
- **Recovery script** `backend/scripts/recover_booking_form_pdfs.py` — uses Resend's `GET /emails` + `GET /emails/{id}/attachments` to pull the actual PDF binary that was emailed to each customer, stores as base64 on `customers.original_booking_form_pdf_b64`. Idempotent.
- **Download endpoint** `GET /api/customers/{id}/original-booking-form.pdf` — serves the recovered PDF if present, falls back to rendering the frozen HTML snapshot via WeasyPrint. Single source of truth for "show me what the customer received".
- **Immutability**: PUT now strips all 4 snapshot fields (html, snapshot_at, pdf_b64, pdf_recovered_from).
- **Tested on preview**: 2 customers recovered (Ramya 156 KB PDF + 1 test). 3 other recoverable bookings exist on production only — will recover automatically when the same script runs against production Mongo.
- **Production run**: After redeploying, on production execute:
  `RESEND_RECOVERY_API_KEY="re_X2pW1Ak6_..." python -m scripts.recover_booking_form_pdfs`
- Files: `backend/customers/models.py`, `backend/customers/routes.py`, `backend/scripts/recover_booking_form_pdfs.py`.

## 2026-06-16 (later) — Email Archive BCC + resend_message_id Persistence
- **New env var `RESEND_BCC_ARCHIVE`** (set to `docs.rrlprojects@gmail.com`). Every outbound email from the CRM now silently BCCs this address — auto-welcome on booking submit, manual welcome-send, doc sends, and the generic `/communication/email` endpoint. Customers don't see the BCC; team gets a permanent off-platform archive.
- **`resend_message_id` now persisted** in `communications` and `communication_logs` collections (previously thrown away). Makes future Resend-API attachment recovery trivial.
- **Discovered**: the existing `RESEND_API_KEY` in `backend/.env` is a SEND-ONLY key — cannot list/retrieve sent emails or attachments. Recovery requires a Full Access key from the Resend team that owns `crm@rrlbuildersanddevelopers.com` (the user gave a key from a different team — Nature Crust — which we cannot use for Builders recovery).
- Files: `backend/.env`, `backend/config.py`, `backend/email_service/routes.py`, `backend/booking/__init__.py`. Memory: `DEPLOYMENT_INVARIANTS.md` § 5.
- **Verified**: sent a test welcome to Ramya, Resend ID `61276165-665a-434e-997c-238ee1b940bd` persisted on the log, BCC param accepted by Resend API.

## 2026-06-16 — Booking Form Snapshot (Immutable) + Backfill
- **Problem**: The "Booking Form Preview" attached to the welcome email was re-generated live from the customer record every time it was previewed/sent. Any admin edit to the customer profile silently changed the preview, so the customer's *original* submission was effectively un-recoverable.
- **Fix — going forward**: At public booking-form submission (`/api/public/booking-form`), the booking form preview HTML is generated and saved to `customers.original_booking_form_html` (+ `original_booking_form_snapshot_at`) before `insert_one`. The three welcome-email endpoints (`preview-welcome-email`, `send-welcome-email`, generic `/communication/email` with `email_type=welcome`) now serve this snapshot, falling back to live render only if missing.
- **Immutability**: `PUT /api/customers/{id}` strips these two fields from the update dict. No other code path writes them except booking submit + the backfill endpoint below.
- **Backfill**: New admin endpoint `POST /api/customers/admin/backfill-booking-form-snapshots` (idempotent). One-off run for the 37 existing customers — locked their current state in as the snapshot. Caveat: not truly "original" for pre-2026-06-16 bookings, but freezes them from this moment.
- **Verified**: 37/37 customers backfilled, 0 failures. Hash test: PUT with `original_booking_form_html: "HACKED"` → SHA256 unchanged. Editing `bhk_type` afterwards does not affect snapshot length.
- Files: `backend/customers/models.py`, `backend/customers/routes.py`, `backend/booking/__init__.py`, `backend/email_service/routes.py`; memory: `DEPLOYMENT_INVARIANTS.md` § 3.5.

## 2026-06-06 (later) — Demand Letter TDS Split into Per-Slab + Lifetime
- **Renamed** "TDS Payable" → **"Total TDS Payable"** (lifetime cumulative, = `demand_raised ÷ 101`).
- **Added** new row above Total TDS Payable: **"Current TDS due for Slab {X%}"** where `X = int(cumulative_percentage)`. Formula: `current_due ÷ 101` (TDS owed on the current installment only).
- **Changed Net Amount Payable formula** from `Total Outstanding − Total TDS Payable` (over-credits prior-slab TDS) to `max(0, Total Outstanding − Current TDS due for Slab X%)`. Sub-label updated to match.
- **Verified end-to-end** on Ramya test lead at 40% slab: Current Due ₹84,662 ÷ 101 = ₹838 → Current TDS due for Slab 40% = ₹838, Total TDS Payable = ₹838, Net Amount Payable = ₹0 ✓.
- Files: `backend/documents/templates/demand_letter.py`; memory: `TDS_CALCULATION_LOGIC.md`, `DEPLOYMENT_INVARIANTS.md`.

## 2026-06-06 — Bajaj NOC Added + BESCOM in Booking Form + Doc-Delete Rollback
- **Bajaj Housing Finance NOC** added as 11th document type (`noc_bajaj` enum). NOC-cum-Release **request letter from RRL to Bajaj** (Bajaj is RRL's construction-finance lender) — distinct from the HDFC/BOB/TATA NOCs which are issued by RRL to the buyer's bank. Fields mapped: purchaser names, mobile, flat/tower/area, agreement value, loan amount, lender's name (buyer's bank, defaults HDFC), own contribution (auto = total − loan), booking date, agreement date. Sanction date pullable from `custom_fields.bajaj_sanction_date`. Reuses the dark-band letterhead + gold footer.
- **BESCOM in Booking Form**: `bescom_rate` was missing from the public booking-form path entirely (frontend `calculatePrice` + backend `_calculate_pricing` ignored it). Added input + live-preview row in `PropertyDetailsStep.jsx` and `ReviewStep.jsx`; wired into `BookingFormPage` payload and `booking/__init__.py` `_calculate_pricing` so the saved customer's subtotal, labour cess and GST all include BESCOM from the very first save.
- **Document Delete Rollback**: Briefly hid delete buttons globally for all roles; rolled back per user request — original behaviour restored (`!isAccountsRole` gate). Admin/manager/sales/support can delete; accounts cannot.
- **New deployment doc**: `/app/memory/DEPLOYMENT_INVARIANTS.md` — single-page index of every locked-in rule (pricing math, BESCOM, TDS, doc formats, roles, endpoints, pre-deploy checklist). Read this before any future deploy.
- Files: `backend/utils/enums.py`, `backend/documents/templates/noc_templates.py`, `backend/documents/templates/__init__.py`, `backend/documents/generators.py`, `backend/booking/__init__.py`, `frontend/src/components/booking/{constants.js, PropertyDetailsStep.jsx, ReviewStep.jsx}`, `frontend/src/pages/BookingFormPage.js`, `frontend/src/components/customer/DocumentsTab.jsx`, `frontend/src/components/settings/DocumentTemplatesTab.jsx`.
- **Verified**: Bajaj NOC PDF generated (155 KB, all fields mapped). BESCOM end-to-end test: 1678 sq.ft × ₹50 = ₹83,900 → subtotal ₹1,16,58,700 → labour cess ₹81,610.90 + GST ₹5,82,935 → total ₹1,23,23,245.90 ✓.

## 2026-02-15 — Price Breakup Phantom ₹2L Fixed (Additional Charges Now Visible)
- **Bug**: Customer reported a ₹2,00,000 "phantom" being added to the Grand Total with no visible row in the Price Breakup PDF. Math didn't reconcile.
- **Root cause**: `useCustomerPage.js::calculateLivePrice` includes `customer.additional_charges` in the subtotal that drives labour cess (0.7%) and GST (5%) — but `documents/templates/price_breakup.py` never rendered a row for it. So any non-zero value (admin-entered or legacy from old booking flow) was silently baked into the totals.
- **Fix** (`price_breakup.py`): Added a conditional "Additional Charges" row between Car Parking and BESCOM. Renders when amount > 0, hidden otherwise.
- **Math now reconciles**: For the customer in the screenshot — base 1,09,21,000 + club 3L + parking 2L + **additional 2L** (now visible) + bescom 1,630 = subtotal ₹1,16,22,630 → cess ₹81,358 + GST ₹5,81,132 → Grand Total **₹1,22,85,120** ✓
- 13/13 regression tests pass.
- Files: `/app/backend/documents/templates/price_breakup.py`.

## 2026-02-15 — Email Migration: SendGrid → Resend (Hard Swap)
- **Why**: Better deliverability + cleaner API.
- **Backend code** (`email_service/routes.py` + `booking/__init__.py` + `config.py`):
  - Removed `sendgrid` SDK + all `Mail/Attachment/FileContent/FileName/FileType/Disposition` imports
  - Installed `resend==2.30.1` (pip freeze → requirements.txt)
  - New helper `_resend_send(to, subject, html, attachments)` runs the sync Resend SDK in a thread via `asyncio.to_thread` so the FastAPI loop stays free
  - All 4 send sites migrated: customer-facing welcome email, booking auto-email, `/communication/email` admin sender, document-attached emails
  - Attachments now sent as `[{filename, content(base64)}]` — same payload shape that worked across all 4 sites
- **Config** (`backend/.env`):
  - Removed `SENDGRID_API_KEY`, `SENDGRID_FROM_EMAIL`, `SENDGRID_FROM_NAME`
  - Added `RESEND_API_KEY`, `RESEND_FROM_EMAIL=crm@rrlbuildersanddevelopers.com`, `RESEND_FROM_NAME=RRL Group`
- **API contract preserved**: response field `email_status` ("sent"/"failed"/"mocked") unchanged. The `sendgrid_response` field name kept (legacy frontend reads it) but value now contains `{provider: "resend", id, error, attachments}`.
- **Verified end-to-end**: live POST `/api/communication/email` → HTTP 200, Resend message id `2b752b54-...` returned. Backend boot clean. 13/13 regression tests pass.
- Files: `backend/email_service/routes.py`, `backend/booking/__init__.py`, `backend/config.py`, `backend/.env`, `backend/requirements.txt`.

## 2026-02-15 — Cost Breakup: Car Parking & Amenities ₹0 Bug Fixed
- **Bug**: For legacy customers whose `additional_parking_charges` / `club_house_charges` were stored as `0` (or `None`) in MongoDB, the Cost Breakup PDF rendered both as ₹0 even though defaults of ₹2L / ₹3L should kick in.
- **Root cause**: `dict.get(key, default)` returns the default **only when the key is missing**. Legacy records had the key with a falsy value, so `.get()` returned 0 instead of the default.
- **Fix** (`documents/templates/cost_breakup.py`): switched to `float(customer.get(key) or default)` for `additional_parking_charges` (200000), `club_house_charges` (300000), `saleable_area`, `bescom_rate`, `total_price`. Now `0`, `None`, missing key, and empty string all fall back to the right default; explicit non-zero values are honoured.
- **Verified end-to-end**:
  - Legacy customer (zero stored) → Car Parking **₹2,00,000**, Amenities **₹3,00,000**, BESCOM correctly computed from rate × area ✓
  - New customer (explicit ₹2.5L / ₹3.5L) → values render as stored ✓
  - Reverse-calc balances: Basic Cost + BESCOM + Parking + Amenities + TDS = total_price exactly ✓
- 13/13 regression tests pass. Backend restart clean.
- File: `/app/backend/documents/templates/cost_breakup.py`.

## 2026-02-15 — Demand Letter: customer.interest_amount Now Mapped to Outstanding
- **Feature**: `customer.interest_amount` is now included in the Demand Letter's "Total Outstanding" calculation. Previously the "Interest (D)" row was hardcoded to `0`.
- **Formula** (updated in `documents/templates/demand_letter.py`):
  ```
  Total Outstanding = (Demand Raised − Amount Paid) + Interest Amount
                    =  (A)            − (C)          + (D)
  ```
- "Interest (D)" row now renders `customer.interest_amount`. Row label updated to `(A)-(C)+(D)`.
- `Net Amount Payable = Total Outstanding − TDS Payable` (unchanged — TDS still computed on demand_raised ÷ 101, not on outstanding).
- **Verified**: total_price ₹1Cr, 50% cumulative, paid ₹30L, interest ₹25K → Outstanding renders **₹20,25,000** ✓.
- Memory file `TDS_CALCULATION_LOGIC.md` updated with the new interest-handling section.
- 13/13 regression tests still pass.

## 2026-02-15 — Code Quality Pass: Critical Items
**Real fixes applied:**
- **Hardcoded test credentials → env vars**: `test_slab_overdue_stats.py`, `test_iteration35_booking_reject.py`, `test_bank_filter.py` now read `TEST_ADMIN_EMAIL` / `TEST_ADMIN_PASSWORD` / `TEST_CUSTOMER_ID` from env, falling back to documented defaults so CI doesn't break.
- **Defensive variable init / linter clarity**:
  - `database.py::connect_to_mongo` — `db` is always rebound; removed redundant `try/except` that obscured the `global` assignment.
  - `documents/routes.py::download_pdf` — explicit `pdf_bytes: bytes` annotation + `raise … from e` for proper exception chain.
  - `email_service/routes.py` — renamed loop variable `att` → `attachment` to avoid F821-style false positives at L260.

**Items in the report that were already fixed in prior sessions:**
- `safePreview.js` already uses `DOMPurify.sanitize` + Blob URLs (no `document.write`).
- `EmailComposerDialog.jsx` already wraps every `dangerouslySetInnerHTML` with `DOMPurify.sanitize()` (lines 143/147/152/158).

**Items deferred to a dedicated refactor session** (large scope, real regression risk close to deploy):
- React hook deps in `useCustomerPage.js` (28+ deps), `AuthContext.js`, `DashboardPage.js` — would risk infinite loops / stale closures if done hastily.
- Complexity refactors for `format_applicant_block`, `generate_cost_breakup_html`, `generate_booking_form_preview_html`, `submit_booking_form`, `SendMessageDialog`, `BankDetailsCard`, `DocumentsTab`, `PaymentScheduleTab`.
- `is True/False` → `==` replacements (~18 occurrences, mostly tests).
- Type-hint coverage for `common.py`, `sales_agreement_template.py`, `server.py`.

13/13 regression tests pass. Lint clean. Backend restart clean.

## 2026-02-15 — Cost Breakup BESCOM Now Dynamic (Was Hardcoded ₹2L)
- **Bug**: Cost Breakup PDF had `bescom = 200000` hardcoded — ignored the user-entered `bescom_rate`. Also used `customer.additional_charges` for car parking (wrong field) and `club_house_charges` defaulted to 150000 (wrong default).
- **Fix** (`cost_breakup.py`):
  - `bescom = bescom_rate × saleable_area` (derived, matches Price Breakup)
  - `car_parking = customer.additional_parking_charges` default 200000 (correct field)
  - `amenities = customer.club_house_charges` default 300000 (correct default)
  - Reverse-calc `basic_cost = total_price − bescom − car_parking − amenities − tds` automatically picks up the dynamic values
  - BESCOM row label now shows `BESCOM (₹50/sq.ft × 1500)` derivation when amount > 0
- **Verified**: rate=0 → BESCOM = ₹0 (no longer ₹2L); rate=50 × 11 sqft → ₹550 with derivation label "(₹50/sq.ft × 11)".
- File: `/app/backend/documents/templates/cost_breakup.py`.

## 2026-02-15 — BESCOM Charges (Per-Sqft Rate Input)
- **Feature**: New BESCOM Charges line in Customer Profile → Property & Pricing. Admin enters a rate (e.g. ₹50/sq.ft); system auto-calculates `amount = rate × saleable_area`, includes it in subtotal (so labour cess + GST apply on top), and shows it in the Price Breakup PDF.
- **Storage**: `Customer.bescom_rate: float = 0` (sqft rate). The amount is derived, not stored — keeps it consistent if saleable_area is later edited.
- **Live calc updated** (`useCustomerPage.js`): subtotal now includes BESCOM; live preview shows `BESCOM (₹50/sq.ft): ₹75,000` row when > 0.
- **PDF updated** (`price_breakup.py`): conditional BESCOM row rendered between Additional Parking and Grand Total. Hidden when 0.
- **Memory locked**: New file `/app/memory/BESCOM_LOGIC.md` captures formula, tax treatment (pre-GST), storage rule, common mistakes, reference implementations, and verified test case. PRD.md now mandates reading it.
- **Verified end-to-end**: rate ₹50/sqft × 11 sqft → ₹550 rendered correctly in price_breakup HTML.
- Files: `backend/customers/models.py`, `backend/documents/templates/price_breakup.py`, `frontend/src/hooks/useCustomerPage.js`, `frontend/src/components/customer/details/PropertyPricingCard.jsx`, `/app/memory/BESCOM_LOGIC.md`, `/app/memory/PRD.md`.

## 2026-02-15 — Fixed Charges on Booking: Car Parking ₹2L + Club House ₹3L
- **Feature**: For all **new** bookings, two charges are now fixed: **Club House ₹3,00,000** (was ₹2L) and **Car Parking ₹2,00,000** (replaces the old "additional_parking × ₹3L" formula). The "Additional Parking count" input is removed from both the booking form and the customer profile. Existing customers' values are preserved as stored.
- **Customer profile editability**: Admin can still edit both **Club House** and **Car Parking Charges** per customer from the Property & Pricing card — preserved by user request.
- **Backend**:
  - `customers/models.py::Customer`: `club_house_charges` default 200000 → **300000**; `additional_parking_charges` default 0 → **200000**
  - `booking/__init__.py::BookingFormData`: same default changes
  - `_calculate_pricing()`: `parking_charges = 200000` (fixed), no longer `data.additional_parking × 300000`. `data.additional_parking` kept on the model for backward compat but ignored in pricing.
- **Frontend**:
  - `components/booking/constants.js`: `initialFormData.club_house_charges = "300000"` + new `car_parking_charges = "200000"`. `calculatePrice` now adds both.
  - `components/booking/PropertyDetailsStep.jsx`: Removed editable Club House input; replaced with two **read-only "fixed" tiles** (Club House ₹3,00,000 + Car Parking ₹2,00,000) + a one-line note that admin can edit per-customer later. Price preview shows both as separate rows.
  - `components/customer/details/PropertyPricingCard.jsx`: Removed "Additional Parking" count input; added editable "Car Parking Charges" amount field (₹ default 200000). Club House default in editor → 300000. Live-preview row relabeled "Additional Parking" → "Car Parking".
  - `hooks/useCustomerPage.js::calculateLivePrice`: removed `additionalParking × 300000`. Now uses `data.additional_parking_charges || 200000`; `clubHouse` reads from edited data with fallback 300000.
- **Verified**: Backend pricing test → club ₹3L + car ₹2L applied; `additional_parking=5` is correctly ignored. 13/13 regression tests pass. Backend restart clean. Lint clean.
- Files: `backend/booking/__init__.py`, `backend/customers/models.py`, `frontend/src/components/booking/constants.js`, `frontend/src/components/booking/PropertyDetailsStep.jsx`, `frontend/src/components/customer/details/PropertyPricingCard.jsx`, `frontend/src/hooks/useCustomerPage.js`.

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
