# RRL Builders CRM — Complete Feature Timeline
**Generated:** Feb 2026 (chronological audit from git history + memory/PRD.md)
**Project span:** March 3, 2026 → today

---

## ✅ What was built (chronological, by work date)

### Phase 1 — Core MVP (March 3 → 23, 2026)
**Backend foundation**
- JWT auth + bcrypt password hashing
- Role system: Admin, Manager, Accounts, Sales, Support
- MongoDB models: users, customers, payment_schedules, payment_transactions, generated_documents, document_templates, communication_logs, activity_logs, settings, units, document_checklists
- Health endpoint, base routing under `/api`

**Customer module**
- Customer CRUD (`/api/customers`)
- Customer list with search (name / email / phone / customer_id / unit_number)
- Customer Detail page with tabs (Details, Payment Tracking, Schedule, Documents, Uploads, Communication, Checklist, Notes)
- Personal Info, Property & Pricing, Booking Details, Bank Details, Co-Applicant cards (all editable)
- Customer ID + Unit Number auto-generation
- Notes per customer (add/delete)
- Document Checklist (KYC tracking)

**Dashboard**
- Revenue cards (Total Revenue Collected / Total Pending / Total Flat Value / Total Balance)
- Pending % indicators
- Total Customers Count
- Pending Agreements Count
- Payments Due This Week
- Overdue Payments count + amount
- Monthly Revenue chart (bar)
- Payment Status pie chart
- Current Disbursement Stage selector (admin-settable)
- Stage-wise Overdue Count & Amount
- Overdue Customers List
- Recent Activities feed (last 20 actions)
- Upcoming Due Dates
- Export CRM Data (Customers/Payments CSV/Excel)

**Payments & Transactions**
- Payment schedule generation (per customer)
- Payment items with status (pending/paid/partial)
- Transaction logging per customer (stage, date, bank, txn_no, amount, notes)
- Transaction stages: Booking, Agreement, Scheduled Disbursement, TDS
- Disbursement Calculator
- Stage-based Overdue calculation
- Bank-wise filter with cumulative overdue totals

**Documents (PDF Generation)**
- Sales Agreement (full multi-clause document)
- Allotment Letter
- Price Breakup
- Cost Breakup
- Demand Letter
- Payment Schedule
- Bank NOC: HDFC, Bank of Baroda, TATA Capital
- Booking Form Preview
- Terms & Conditions
- WeasyPrint PDF generation (server-side, real PDFs)
- Document Templates collection in DB

**Communication**
- Email send via SendGrid
- Welcome Email with attached PDFs (Booking Form, T&C, Price Breakup)
- Document Email (attachable PDFs from generated docs + uploaded docs)
- Communication history per customer
- WhatsApp link (MOCKED — opens wa.me link)
- Email logs page (`/email-logs`)

**Settings / Admin**
- User management (create / edit / activate / deactivate / delete)
- Password reset (admin → user)
- Disbursement Slab admin setting (cascades to dashboard + payment overdue calculations)

**Public**
- Public Booking Form (`/booking-form`) — multi-step wizard with applicant details, property details, payment step, document uploads, review

### Phase 2 — Reports & Refinement (March 29 → April 3, 2026)
- Reports page
- Leads page (separate from Customers, for pre-booking stage)
- Customer Filters component
- Calculator page (`/calculator`)

### Phase 3 — Refactoring & Stabilization (April 10, 2026)
- Backend modularization: `server.py` split into `auth/`, `customers/`, `dashboard/`, `documents/`, `email_service/`, `booking/`, `settings/`, `payments/`
- Frontend refactor: customer components split into `customer/`, `customers/`, `dashboard/`, `settings/`, `layout/`
- Custom hook: `useCustomerPage.js` for state management

### Phase 4 — Production Fixes (May 7 → 13, 2026)
- Cost breakup PDF: project name in site address
- Bank-wise overdue tracking with cumulative totals
- PDF download fixed (real `.pdf` via WeasyPrint, not preview link)
- TDS transaction stage restored to dropdowns + calculation fixed
- Welcome email: 3 attachments restored (Booking Form, T&C, Price Breakup)
- Payment Schedule doc: shows slab schedule, not transactions
- Code quality refactor: `documents/routes.py` 587→351 lines, dispatcher in `generators.py`
- Frontend component split: DetailsTab 751→79, PaymentTrackingTab 488→129, CommunicationTab 310→46 lines
- NOC HDFC/BOB "received by us" field: now sums transactions excluding TDS (was using booking_amount)
- **PDF Inline Editing (a)** — every generated document is editable via `EditableDocumentDialog` (iframe + contenteditable + save/download)
- **Admin Template Editor (b)** — Settings → Document Templates tab. Snapshot built-in default → edit HTML with live preview → all future generations of that doc type use the override. Revert restores built-in.

---

## ❌ What was reported missing in this conversation

### 1. Payment Receipt per transaction — **NEVER EXISTED**
- Searched git history (all commits across the project) for `payment_receipt`, `generate_receipt`, `PaymentReceipt`, `payment_voucher`, `receipt template`: **zero matches**.
- The PRD.md inventory of "12+ document types" does NOT list a payment receipt.
- The DocumentType enum has: `sales_agreement`, `allotment_letter`, `disbursement_letter`, `price_breakup`, `cost_breakup`, `welcome_letter`, `demand_letter`, `payment_schedule`, `noc_hdfc`, `noc_bob`, `noc_tata` — no `payment_receipt`.
- **Conclusion:** This feature was either (a) discussed/planned but never built, or (b) built in a separate fork that was never merged into this codebase. Either way it's not retrievable from git — but I can build it now in ~30 min as a first-class document type.

### 2. "Payments" as a sidebar nav item — **CODE EXISTS, JUST NOT WIRED**
- `frontend/src/pages/PaymentsPage.js` (330 lines) exists, last touched April 10, 2026.
- It is **not registered as a route** in `App.js` and **not in the sidebar** in `DashboardLayout.js`.
- The current sidebar only shows: Dashboard, Leads, Customers, Documents, Payment Tracking (`/calculator`), Email Tracking, Reports, Settings.
- Your screenshot shows: Dashboard, Leads, Customers, **Payments**, Documents, **Payment Tracking**, Reports, Settings — confirming Payments was at one point a separate menu item.
- **Conclusion:** Easy fix — add the route + sidebar link. The page logic already exists.

### 3. Anything else missing?
- I checked all dashboard cards in your screenshot against current code — every card (Current Disbursement Slab, Total Revenue Collected, Total Pending Payments, Total Flat Value, Total Balance, Export CRM Data, Payment Status Distribution) **does exist** in the current frontend (in `components/dashboard/`).
- If you've noticed other gaps (specific buttons, fields, PDF columns, calculations), please tell me which ones — I will check git history and the live state side-by-side.

---

## 🕒 No "April 20th vanishing event" detected
Commits occurred on these dates only: Mar 3, 12, 15, 17, 18, 20, 21, 23, 29 / Apr 1, 2, 3, 10 / May 7, 11, 12, 13. There is a natural gap between Apr 10 and May 7 (no work was committed in that window), but no code was deleted or reverted within that gap. The latest commits **add features, not remove them**.

The most likely cause of your perception:
- The `/payments` page got "orphaned" (route was removed when nav was reorganized around Apr 10).
- Several P2/P3 features that were on the backlog (Payment Receipt, WhatsApp Twilio, Inbox view, Activity Logs UI) may have been **expected** but were never actually built.
