# CHANGELOG

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
