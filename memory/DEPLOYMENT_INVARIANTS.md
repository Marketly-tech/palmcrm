# RRL CRM — Deployment Invariants & Logic Index

> 🚨 **MANDATORY FOR ANY AGENT BEFORE A DEPLOY OR REFACTOR.**
> This is the single source of truth for *what must never break* across the RRL post-sales CRM. Every rule here is **user-locked-in** through real-world testing on the deployed `https://rrlcrm.com` site. Modify only with explicit user confirmation.
>
> Last revised: 2026-06-06 — after Bajaj NOC + BESCOM-in-booking-form fixes.

---

## 0 · Architecture (recap)

```
Frontend  : React + Tailwind + Shadcn UI            → process.env.REACT_APP_BACKEND_URL
Backend   : FastAPI (uvicorn via supervisor:8001)   → all routes under /api
DB        : MongoDB (Motor async, MONGO_URL + DB_NAME from .env)
PDF       : WeasyPrint (HTML → PDF)
Email     : Resend (formerly SendGrid — DO NOT revert)
```

* All URLs/ports/keys live in `frontend/.env` and `backend/.env`. **Never hardcode** and never delete the protected keys (`REACT_APP_BACKEND_URL`, `MONGO_URL`, `DB_NAME`).
* Backend routes are **always prefixed `/api`** (Kubernetes ingress relies on this).
* Hot reload handles code changes. Restart supervisor only after `.env` edits or new packages.

---

## 1 · Pricing Math (THE most-broken thing — read carefully)

### The canonical subtotal/total formula

```
subtotal     = base_price                          # rate_per_sqft × saleable_area
             + floor_rise_total                    # floor_rise_cost × saleable_area
             + club_house_charges                  # default ₹3,00,000 — editable
             + additional_parking_charges          # default ₹2,00,000 — editable (was "Car Parking")
             + additional_charges                  # manual entry — defaults 0
             + bescom_amount                       # bescom_rate × saleable_area

labour_cess  = subtotal × 0.007                    # 0.70 % — applies on full subtotal incl. BESCOM
gst_amount   = subtotal × 0.05                     # 5 %   — applies on full subtotal incl. BESCOM
total_price  = subtotal + labour_cess + gst_amount + interest_amount
                                                   # interest_amount is post-GST flat (NOT taxed)
```

### Hard rules

| Rule | Value | Why |
|---|---|---|
| Club House default | ₹3,00,000 | Booking form auto-prefills; editable later |
| Additional Parking ("Car Parking") default | ₹2,00,000 | Booking form auto-prefills; editable later |
| BESCOM | `bescom_rate × saleable_area`, **inside** subtotal | Full GST + Labour Cess on top — see `BESCOM_LOGIC.md` |
| Interest Amount | Flat add-on AFTER GST | Non-taxable; see Property & Pricing card |
| Labour Cess | 0.70 % of subtotal | Government cess |
| GST | 5 % of subtotal | India real estate GST |
| Total | Subtotal + Cess + GST + Interest | Stored as `customers.total_price` |

### Where the formula must stay in sync (do NOT diverge)

1. `backend/booking/__init__.py::_calculate_pricing` — public booking form intake
2. `backend/documents/templates/price_breakup.py` — Price Breakup PDF
3. `backend/documents/templates/cost_breakup.py` — Cost Breakup PDF (uses reverse-calc — see below)
4. `frontend/src/components/booking/constants.js::calculatePrice` — booking form live preview
5. `frontend/src/hooks/useCustomerPage.js::calculateLivePrice` — customer profile live preview

> Any drift across these five files = silent ₹phantom bug. Always cross-check before merging changes.

### Cost Breakup PDF special note
`documents/templates/cost_breakup.py` reverse-calculates `basic_cost = total_price − bescom − car_parking − amenities − tds`. It uses `float(customer.get(key) or default)` to handle legacy records where the key exists but is `0`/`None` (see 2026-02-15 fix in CHANGELOG).

### Verified test (2026-02-15) — Ramya test lead
- 1678 sq.ft × ₹6600 + ₹3L club + ₹2L parking + 0 additional + ₹50/sq.ft × 1678 BESCOM
- → subtotal ₹1,16,58,700 → cess ₹81,610.90 + GST ₹5,82,935 → total **₹1,23,23,245.90** ✓ to the paisa.

---

## 2 · BESCOM Charges — see `BESCOM_LOGIC.md`

* Stored on `customers.bescom_rate` (₹/sqft). **`bescom_amount` is always derived** (not stored as primary).
* Visible everywhere conditional `> 0`: customer-profile live preview row, booking-form live preview row, Price Breakup PDF, Cost Breakup PDF.
* Inside subtotal — full GST + Cess apply.

---

## 3 · TDS Calculation — see `TDS_CALCULATION_LOGIC.md`

* **TDS Payable**  = 1 % of total_price (statutory)
* **TDS Paid**     = sum of `payment_transactions` where `transaction_stage == 'tds'`
* **TDS To Be Paid** = Payable − Paid
* Used in: Demand Letter PDF (`demand_letter.py`), Payment Tracking UI, Transactions Export.
* **Never** use a blanket 1 % on the demand letter — always sum actual TDS-stage transactions.

---

## 4 · Document Templates — see `DOCUMENT_FORMAT_REFERENCE.md`

### Visual format (locked-in 2026-04, restored from production)
Every PDF uses:
- **Dark charcoal header band** (`#1A1A1A`) full-bleed (`margin: 0 -20mm`)
- **Gold RRL Group logo** (70 px) on the left
- Company name + tagline ("Beyond Homes. A Lifestyle") right-aligned on dark band
- **Footer band** (light grey, gold top border) with address / website / email / RERA / Doc-generated date / Ref

Reference helpers in `documents/templates/noc_templates.py` (re-used by Bajaj, HDFC, BOB, TATA):
- `_letterhead_styles()` — shared CSS
- `_letterhead_html()` — gold logo + company name on dark band
- `_doc_title_html(label)` — centered title with gold underline
- `_footer_band_html(customer)` — full footer

### Document types
`backend/utils/enums.py::DocumentType` (current 11 values):
`sales_agreement`, `allotment_letter`, `price_breakup`, `cost_breakup`, `welcome_letter`, `demand_letter`, `payment_schedule`, `noc_hdfc`, `noc_bob`, `noc_tata`, `noc_bajaj`, `payment_receipt`.

> 🚫 `disbursement_letter` was removed (Feb 2026). Don't re-add.

### Bank NOCs
| NOC | Direction | Receives from buyer's bank | Purpose |
|---|---|---|---|
| HDFC, BOB, TATA | RRL → buyer's bank | Confirms clear title; permits mortgage | Buyer's loan disbursement |
| **Bajaj** (NEW Feb 2026) | RRL → Bajaj | Bajaj is **RRL's construction-finance lender** | Asks Bajaj to release the flat from their mortgage so buyer's bank can disburse |

* Bajaj NOC uses `customer.finance_bank` as the buyer's lender (defaults to "HDFC BANK LTD" if blank), `customer.self_contribution` or auto-computed `total − loan` as own contribution. Sanction date pulled from `custom_fields.bajaj_sanction_date` (fallback `"as on record"`).

### Master Template scrubber
Admin → Document Templates → "Save as Master Template" auto-scrubs customer-specific data (e.g. `Ramya` → `{customer_name}`) before persisting to `db.document_templates`. See `2026-02-12` entry in CHANGELOG.

---

## 5 · Email (Resend)

* Provider is **Resend**, not SendGrid. Use `resend==2.30.1`.
* All sending wrapped in `asyncio.to_thread` since the SDK is synchronous.
* Env keys: `RESEND_API_KEY`, `RESEND_FROM_EMAIL=crm@rrlbuildersanddevelopers.com`, `RESEND_FROM_NAME=RRL Group`.
* `/api/communication/email` accepts **`multipart/form-data`** (not JSON) — fixes the 422 bug.
* Legacy frontend reads `sendgrid_response` field — backend keeps the key name for compat, value is now `{provider:"resend", id, error, attachments}`.
* Welcome email auto-sent on `/api/public/booking-form` submit, with Price Breakup PDF attached.

---

## 6 · Roles & Access

| Role | Generate doc | Edit customer | Delete doc | Manage users | Accept/Reject lead |
|---|---|---|---|---|---|
| admin | ✅ | ✅ | ✅ | ✅ | ✅ |
| manager | ✅ | ✅ | ✅ | ❌ | ✅ |
| sales | ✅ | ✅ | ✅ | ❌ | ✅ (reject requires reason) |
| accounts | ✅ | ✅ (payments only) | ❌ | ❌ | ❌ |
| support | ✅ | view-only | ✅ | ❌ | ❌ |

Document delete buttons gated on `!isAccountsRole` in `DocumentsTab.jsx`. (2026-06-06 — initially hidden globally per user, then rolled back to original behaviour on user request — accounts blocked, everyone else allowed.)

---

## 7 · Data Model — `customers` (key fields only)

```
id, customer_id, name, phone, email,
co_applicant_name/phone/email/pan/aadhar/...,
project, tower, unit_number, bhk_type, floor, saleable_area, uds,
rate_per_sqft, base_price,
club_house_charges (₹3L default), additional_parking_charges (₹2L default),
additional_charges, additional_charges_description,
bescom_rate (₹/sqft),
labour_cess, gst_percentage(=5), gst_amount, interest_amount,
total_price, booking_amount, booking_date, agreement_date,
total_received, balance_amount, payment_received_percentage, payment_pending_percentage,
finance_type, finance_bank, loan_amount, self_contribution,
stage (pending_approval | qualified | agreement_pending | agreement_done | registration_done),
agreement_status (draft | sent | signed | completed | disbursement),
uploaded_documents (dict), custom_fields (dict).
```

`payment_transactions` keys to remember: `customer_id, amount, transaction_stage (booking|agreement|scheduled_disbursement|tds), receipt_number, transaction_date`.

---

## 8 · Critical API Endpoints

* `POST /api/public/booking-form` — public intake (no auth). Sends welcome email + Price Breakup PDF on success.
* `POST /api/documents/generate` — body `{customer_id, doc_type}`. Saves to `db.generated_documents`.
* `GET /api/documents/pdf/{doc_id}` — converts saved HTML → PDF download.
* `GET /api/documents/html/{doc_id}` — raw HTML for preview/edit.
* `PUT /api/documents/html/{doc_id}` — edit in-place before download (blocked for accounts).
* `POST /api/templates/snapshot/{doc_type}` — save customer-scrubbed doc as Master Template.
* `POST /api/communication/email` — multipart/form-data, attachments optional.
* `GET /api/customers/banks/registry` — canonical bank registry (HDFC + "HDFC BANK" + "hdfc bank" → "HDFC Bank").

---

## 9 · Pre-Deployment Checklist (for the user before pushing to rrlcrm.com)

1. ⬜ Backend boots clean — `tail -n 50 /var/log/supervisor/backend.err.log` shows `Application startup complete` and no traceback.
2. ⬜ Frontend builds — `yarn build` succeeds with **no eslint errors** (lint runs on each push).
3. ⬜ Pricing math reconciles for **Ramya test lead** (run `/api/customers/{ramya_id}` and recompute manually — see Section 1 verified test).
4. ⬜ All 11 document types generate PDFs (sales_agreement, allotment_letter, price_breakup, cost_breakup, welcome_letter, demand_letter, payment_schedule, **noc_hdfc, noc_bob, noc_tata, noc_bajaj**, payment_receipt).
5. ⬜ Welcome email auto-sends on booking submit (Resend message id returned).
6. ⬜ Master Template scrubber doesn't leak customer names.
7. ⬜ TDS Payable vs TDS Paid renders correctly in Demand Letter and Payment Tracking UI.
8. ⬜ No env keys hardcoded (`grep -rn 'localhost:\|api.resend.com' frontend/ backend/` should be empty outside `.env`/`config.py`).
9. ⬜ Master `test_credentials.md` is current — testing agent reads it.
10. ⬜ Database NOT seeded against production Mongo (only preview Mongo).

---

## 10 · Known Recurrence Pitfalls (regression hot-spots)

| Symptom | Likely cause | Fix |
|---|---|---|
| ₹2L phantom in Price Breakup | `additional_charges` legacy non-zero, but row missing | Render conditional row when `> 0` (`price_breakup.py`) |
| Car Parking / Amenities shows ₹0 in Cost Breakup | `.get(key, default)` returns `0` because key exists | Use `float(customer.get(key) or default)` |
| Demand Letter TDS is 1 % blanket | Forgot to sum `transaction_stage == 'tds'` rows | See `TDS_CALCULATION_LOGIC.md` |
| Bajaj NOC missing | Doc type not registered in `_NOC_GENERATORS` | Add to `generators.py` + `enums.py` + `__init__.py` + frontend lists |
| Welcome email = 422 | Endpoint expects multipart, sent JSON | Use `FormData` in frontend |
| `Tower-Tower 1` in NOCs | User typed "Tower 1" in `customer.tower`, code prefixed again | Strip-if-starts-with "tower" (only fixed in Bajaj NOC so far) |
| Old SendGrid env keys left in `.env` | Migration | Strip `SENDGRID_*` keys |

---

## 11 · File-of-Truth Index

| Topic | File |
|---|---|
| Product Requirements & history | `/app/memory/PRD.md` |
| Detailed change log | `/app/memory/CHANGELOG.md` |
| BESCOM logic | `/app/memory/BESCOM_LOGIC.md` |
| TDS logic | `/app/memory/TDS_CALCULATION_LOGIC.md` |
| PDF visual format | `/app/memory/DOCUMENT_FORMAT_REFERENCE.md` |
| Feature timeline | `/app/memory/FEATURE_TIMELINE.md` |
| Adjacent project spec | `/app/memory/NATURE_CRUST_NEW_PROJECT_SPEC.md` |
| Test credentials | `/app/memory/test_credentials.md` |
| **You are here** (deployment invariants) | `/app/memory/DEPLOYMENT_INVARIANTS.md` |

---

**Change only with explicit user confirmation. Every locked-in rule here has been signed off by RRL Builders.**
