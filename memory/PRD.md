# RRL Builders Post-Sales CRM — Comprehensive PRD

> 🚨 **MANDATORY READING FOR ANY AGENT TOUCHING PDF TEMPLATES:**
> Always read `/app/memory/DOCUMENT_FORMAT_REFERENCE.md` BEFORE modifying any
> file in `/app/backend/documents/templates/`. It captures the
> user-approved visual layout (dark header band, footer band, gold accents,
> etc.) so format is never silently changed across sessions.

> 🚨 **MANDATORY READING FOR ANY AGENT TOUCHING TDS LOGIC:**
> Always read `/app/memory/TDS_CALCULATION_LOGIC.md` BEFORE modifying TDS
> Payable / TDS Paid / TDS To Be Paid in any file. Formulas are locked.

> 🚨 **MANDATORY READING FOR ANY AGENT TOUCHING BESCOM CHARGES:**
> Always read `/app/memory/BESCOM_LOGIC.md` BEFORE modifying BESCOM in
> any template / live calc / model. Formula and tax treatment are locked.

## 1. Product Overview
**Product Name:** RRL CRM  
**Domain:** https://rrlcrm.com  
**Type:** Internal Post-Sales CRM for Real Estate Developer  
**Purpose:** Replace Excel-based tracking with a full digital system managing the post-booking lifecycle of real estate customers.

---

## 2. User Roles & Access Control

| Role | Access Level |
|------|-------------|
| **Admin** | Full access — manage users, settings, all customers, documents, email, exports, payment stages |
| **Manager** | Create/edit customers, generate documents, send emails, export data |
| **Accounts** | View customers, manage transactions/payments — cannot delete customers or documents |
| **Sales** | View customers, limited edit access |
| **Support** | View-only access |

**Auth System:** JWT-based authentication with bcrypt password hashing. Admin can create users and reset passwords.

**Credentials:**
- Admin: `crm@rrlbuildersanddevelopers.com` / `#RRLnew2026`
- Accounts: `accounts@rrlbuilders.com` / `accounts123`

---

## 3. Features & Functionality — Complete Inventory

### 3.1 Dashboard
- [x] **Total Revenue Collected** — sum of all customer payments
- [x] **Total Pending Amount** — sum of all customer balance amounts
- [x] **Total Flat Value** — sum of all total_price
- [x] **Total Balance** — pending amount
- [x] **Pending Percentage** — overall pending %
- [x] **Total Customers Count**
- [x] **Pending Agreements Count**
- [x] **Payments Due This Week**
- [x] **Overdue Payments Count**
- [x] **Monthly Revenue Chart** (bar chart)
- [x] **Payment Status Breakdown** (pie chart)
- [x] **Current Disbursement Stage Display** — admin-settable global stage
- [x] **Stage-wise Overdue Count & Amount**
- [x] **Overdue Customers List** (with amounts)
- [x] **Recent Activities Feed** (last 20 actions)
- [x] **Upcoming Due Dates** 

### 3.2 Customer Management
- [x] **Customer List** with search (name, email, phone, ID, unit number)
- [x] **Filter by Project** (6 projects: RRL Palm Altezze, NC 216, Palacio, Nature Woods, Towers, Complex)
- [x] **Filter by Agreement Status** (Draft, Sent, Signed, Disbursement)
- [x] **Filter by Finance Bank** (HDFC, BOB, SBI, CANARA, TATA CAPITAL, etc.)
- [x] **Filter by Agreement Type** (Upcoming Due, Pending Agreement, Disbursement Overdue)
- [x] **Overdue Amount Column** — visible when bank filter is active, with cumulative total row
- [x] **Agreement Status Quick-Change** — inline dropdown per customer row
- [x] **Delete Customer** (admin/manager only)
- [x] **Export to CSV** 
- [x] **Export to Excel** (styled with RRL branding)
- [x] **Export Payments to CSV**

### 3.3 Customer Detail Page
**Tabs:**

#### 3.3.1 Details Tab
- [x] Personal info: Name, Father's Name, DOB, Gender, PAN, Aadhar, Address, Phone, Email
- [x] Co-Applicant info: Name, Father's Name, Phone, Email, PAN, Aadhar, Address, DOB
- [x] Property info: Project, Tower, Unit Number, Floor, BHK Type, Saleable Area, UDS
- [x] Finance info: Finance Type (Self/Loan/Mixed), Finance Bank, Loan Amount, Self Contribution
- [x] Bank details: Bank Name, Account Number, IFSC, Branch, Account Holder
- [x] Booking info: Booking Number, Booking Date, Booking Amount
- [x] Pricing: Rate/sqft, Base Price, Floor Rise, Club House, Additional Parking, Labour Cess, GST, Total Price
- [x] Edit mode toggle for all fields
- [x] Custom fields support

#### 3.3.2 Payment Tracking Tab
- [x] **Payment Progress Bar** (received vs total %)
- [x] **Overdue Status** — shows expected vs received per current disbursement slab
- [x] **Stage-wise TDS (1%)** — TDS Payable, TDS Paid, TDS Balance
- [x] **Disbursement Calculator** — calculate amount for custom % of total price
- [x] **Next Payment Due Date** — editable
- [x] **Transaction Records Table** — Stage, Date, Bank, Transaction No., Amount, Notes
- [x] **Add Transaction** (stages: Booking, Agreement, Scheduled Disbursement, **TDS**)
- [x] **Edit Transaction** 
- [x] **Delete Transaction**
- [x] **Export Transactions PDF** — branded HTML-to-PDF export

#### 3.3.3 Payment Schedule Tab
- [x] **Auto-generate Schedule** from payment stage templates
- [x] **Installment table** — name, milestone, amount, due date, status, payment date
- [x] **Edit schedule items** inline
- [x] **Delete schedule items**

#### 3.3.4 Documents Tab
- [x] **Generate Document** — dropdown to pick document type
- [x] **Preview Document** (HTML preview in new window)
- [x] **Download Document as PDF** — server-side WeasyPrint conversion
- [x] **Delete Generated Document** (admin/manager only)
- [x] **Document Types Available:**
  - Sales Agreement
  - Allotment Letter
  - Price Breakup
  - Cost Breakup (with project name in site address)
  - Welcome Letter
  - Demand Letter (based on current disbursement stage)
  - Payment Schedule PDF
  - Disbursement Letter
  - **Bank NOC — HDFC**
  - **Bank NOC — Bank of Baroda (BOB)**
  - **Bank NOC — TATA Capital**
  - **Bank NOC — Bajaj Housing Finance** (request to construction-finance lender for NOC-cum-Release)
- [x] **Disbursement Documents** subsection for NOCs

#### 3.3.5 Uploads Tab
- [x] Upload customer documents (KYC, PAN, Aadhar, etc.)
- [x] View uploaded documents
- [x] Delete uploaded documents
- [x] Preview/download uploaded documents

#### 3.3.6 Communication Tab
- [x] **Welcome Email** — with 3 PDF attachments (Booking Form Preview, Terms & Conditions, Price Breakup)
- [x] **Sales Agreement Email** — with Sale Agreement + Price Breakup PDFs
- [x] **Allotment Letter Email** — with Allotment Letter PDF
- [x] **Custom Email Composer** — subject, body, CC support
- [x] **WhatsApp Link** (MOCKED — opens `whatsapp://` URL)
- [x] **Communication History** — log of all emails/messages sent
- [x] **SendGrid Integration** for actual email delivery (requires API key)

#### 3.3.7 Checklist Tab
- [x] Document checklist items: KYC Documents, PAN Card, Aadhar, Agreement Copy, Bank Documents, Passport Photo, Address Proof
- [x] Toggle checklist items

#### 3.3.8 Notes Tab
- [x] Add notes to customer
- [x] Delete notes
- [x] Notes show author and timestamp

### 3.4 Quick Actions (Customer Header)
- [x] **Welcome Email** button
- [x] **Sales Agreement** button  
- [x] **Allotment Letter** button
- [x] **WhatsApp** button
- [x] **Edit** button
- [x] **Agreement Status** dropdown (inline change)

### 3.5 Leads Management
- [x] **Pending Leads Page** — show all `pending_approval` customers
- [x] **Approve Lead** → moves to `qualified`
- [x] **Reject Lead** → deletes customer and frees up unit
- [x] **Update Lead Stage** (pending_approval → qualified → agreement_pending → agreement_done → registration_done)

### 3.6 Public Booking Form
- [x] Multi-step public form: Personal Details, Property Details, Financial Details, Document Upload, Review
- [x] Auto-calculates total price from rate/sqft, floor rise, club house, parking, GST, labour cess
- [x] Document upload per step (PAN, Aadhar, etc.)
- [x] Auto-generates customer ID (RRL-XXXXX format)
- [x] Auto-creates document checklist
- [x] Auto-sends welcome email (if SendGrid configured)
- [x] Marks unit as unavailable

### 3.7 Document Templates
- [x] Template CRUD (create, update, list)
- [x] Default templates for Sales Agreement, Allotment Letter, Disbursement Letter
- [x] Custom template creation with placeholder support

### 3.8 Email Tracking
- [x] **Email Logs Page** — paginated list of all sent emails
- [x] Filter by status (sent, failed, mocked)
- [x] Search by customer name/email/subject
- [x] Shows customer info, timestamp, status

### 3.9 Reports Page
- [x] Accessible from sidebar

### 3.10 Settings
- [x] **Payment Stage Management** — admin can set current global disbursement stage (10 stages from Podium to Handover)
- [x] **User Management** — admin can create/edit/delete users, reset passwords
- [x] **Projects List** (6 predefined projects)
- [x] **Unit Pricing** — CRUD for unit configurations, bulk import

### 3.11 Payment Stage System (10 Stages)
| # | Stage Key | Stage Name | Percentage | Cumulative |
|---|-----------|-----------|-----------|------------|
| 1 | podium | On Completion of Podium Slab | 40% | 40% |
| 2 | 2nd_floor | Upon Completion of 2nd Floor Roof Slab | 5% | 45% |
| 3 | 6th_floor | Upon Completion of 6th Floor Roof Slab | 5% | 50% |
| 4 | 10th_floor | Upon Completion of 10th Floor Roof Slab | 5% | 55% |
| 5 | 14th_floor | Upon Completion of 14th Floor Roof Slab | 5% | 60% |
| 6 | 18th_floor | Upon Completion of 18th Floor Roof Slab | 5% | 65% |
| 7 | 22nd_floor | Upon Completion of 22nd Floor Roof Slab | 5% | 70% |
| 8 | top_roof | Upon Completion of Top Roof Slab | 10% | 80% |
| 9 | flooring | Upon Completion of Flooring of Particular Property | 10% | 90% |
| 10 | handover | Upon Handover / Possession / Registration | 10% | 100% |

### 3.12 Transaction Stages
| Stage | Label | Badge Color |
|-------|-------|-------------|
| booking | Booking | Blue |
| agreement | Agreement | Green |
| scheduled_disbursement | Scheduled Disbursement | Purple |
| tds | TDS | Amber |

---

## 4. Technical Architecture

### Backend
- **Framework:** FastAPI (Python 3.11)
- **Database:** MongoDB (Motor async client)
- **PDF Generation:** WeasyPrint (HTML → PDF)
- **Email:** SendGrid API
- **Auth:** JWT tokens + bcrypt hashing

### Frontend
- **Framework:** React 18
- **UI:** TailwindCSS + Shadcn UI components
- **HTTP Client:** Axios
- **Toast Notifications:** Sonner

### Code Structure
```
/app/backend/
├── server.py              # ~232 lines — thin init shell
├── config.py              # Environment settings (CORS, JWT, SendGrid, RERA)
├── database.py            # MongoDB connection + collection accessors
├── auth/                  # Login, register, JWT, user CRUD, role checks
├── customers/             # Customer CRUD, bank filter, overdue enrichment
├── payments/              # Schedules, transactions, calculator
├── dashboard/             # Stats, recent activities, upcoming dues
├── documents/             # Doc generation, PDF download, upload, checklist
│   └── templates/         # 12+ HTML template generators
├── email_service/         # Email previews, send, communication history
├── booking/               # Public form, Google Form webhook, leads
├── settings/              # Payment stages, notes, overdue, units, export, projects
└── utils/                 # Enums, currency formatting, payment helpers

/app/frontend/src/
├── pages/                 # Thin page wrappers
├── hooks/                 # useCustomerPage.js (shared logic)
├── components/
│   ├── customer/          # 10+ extracted components for customer detail
│   ├── customers/         # CustomerTable, CustomerFilters
│   ├── dashboard/         # DashboardCards, RevenueChart, etc.
│   ├── settings/          # SettingsTabs, UserManagement, etc.
│   └── ui/                # Shadcn UI components
└── utils/                 # safePreview.js, formatters
```

---

## 5. Key API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | /api/auth/login | Login |
| POST | /api/auth/register | Create user |
| GET | /api/auth/me | Current user |
| GET | /api/customers | List (with search, project, bank, status filters) |
| GET | /api/customers/banks | Unique bank names for filter |
| GET | /api/customers/{id} | Single customer |
| PUT | /api/customers/{id} | Update customer |
| DELETE | /api/customers/{id} | Delete customer |
| GET | /api/transactions/{cid} | Customer transactions |
| POST | /api/transactions/{cid} | Add transaction |
| PUT | /api/transactions/{cid}/{tid} | Edit transaction |
| DELETE | /api/transactions/{cid}/{tid} | Delete transaction |
| GET | /api/payments/schedule/{cid} | Payment schedule |
| POST | /api/payments/schedule/{cid} | Generate schedule |
| GET | /api/dashboard/stats | Dashboard metrics |
| GET | /api/dashboard/overdue-by-stage | Stage-based overdue list |
| POST | /api/documents/generate | Generate document |
| GET | /api/documents/pdf/{doc_id} | Download as PDF |
| GET | /api/documents/html/{doc_id} | Get HTML content |
| GET | /api/documents/{cid} | Customer's generated docs |
| POST | /api/communication/send-welcome-email/{cid} | Send welcome email |
| POST | /api/communication/send-document-email/{cid} | Send email with attachments |
| GET | /api/communication/{cid} | Communication history |
| GET | /api/email-logs | All email logs (paginated) |
| GET | /api/settings/payment-stages | 10 payment stages |
| GET/POST | /api/settings/current-stage | Get/set current stage |
| GET | /api/customers/{cid}/notes | Customer notes |
| POST | /api/customers/{cid}/notes | Add note |
| GET | /api/customers/{cid}/overdue | Customer overdue info |
| GET | /api/export/customers/csv | Export CSV |
| GET | /api/export/customers/excel | Export Excel |
| POST | /api/public/booking-form | Public booking form |
| GET | /api/leads/pending | Pending leads |

---

## 6. Database Collections

| Collection | Purpose |
|-----------|---------|
| users | User accounts with roles |
| customers | Customer profiles (40+ fields) |
| payment_transactions | Individual payment records |
| payment_schedules | Generated installment schedules |
| generated_documents | HTML content of generated PDFs |
| customer_documents | Uploaded document files (base64) |
| document_checklists | KYC checklist per customer |
| communication_logs | Email/WhatsApp logs |
| activity_logs | Audit trail |
| document_templates | Custom document templates |
| settings | App-wide config (current payment stage) |
| units | Unit pricing configurations |

---

## 7. 3rd Party Integrations

| Service | Status | Notes |
|---------|--------|-------|
| SendGrid (Email) | Active | Requires user API key in .env |
| WhatsApp (Twilio) | MOCKED | Uses `whatsapp://` link only |
| WeasyPrint | Active | Server-side PDF generation |

---

## 8. What's Been Implemented (Timeline)

- [x] Core CRM: Auth, Customers, Dashboard, Payments (Mar 2026)
- [x] Document Generation: 12+ document types with PDF export (Mar 2026)
- [x] Email System: Welcome, Sales Agreement, Allotment Letter emails (Mar 2026)
- [x] Public Booking Form with multi-step wizard (Mar 2026)
- [x] Bank NOC documents: HDFC, BOB, TATA Capital (Apr 2026)
- [x] Bank NOC document: Bajaj Housing Finance — request letter to construction-finance lender with mapped Purchaser/Property/Loan details (Feb 2026)
- [x] Frontend refactoring: All 4 major pages modularized (Apr 2026)
- [x] Backend refactoring: server.py 4200→232 lines (Apr 2026)
- [x] Bank-wise overdue tracking with cumulative totals (May 2026)
- [x] PDF download fix (server-side WeasyPrint conversion) (May 2026)
- [x] TDS transaction stage restored (May 2026)
- [x] TDS calculation fixed — maps to actual TDS transactions, not formula (May 2026)
- [x] Cost breakup: project name in site address (May 2026)
- [x] Welcome email: restored all 3 PDF attachments (Booking Form, T&C, Price Breakup) (May 2026)
- [x] Payment Schedule doc: now shows slab-wise schedule instead of transactions (May 2026)
- [x] Code Quality refactor — extracted `documents/generators.py` dispatcher + `documents/templates/transactions_export.py`; reduced `documents/routes.py` from 587→351 lines (Feb 2026)
- [x] Frontend component split — `DetailsTab` 751→79, `PaymentTrackingTab` 488→129, `CommunicationTab` 310→46 lines; new subfolders `customer/details`, `customer/payment`, `customer/communication`; removed unused `PaymentTrackingCard.jsx` & `TransactionsCard.jsx` (Feb 2026)
- [x] NOC HDFC/BOB "received by us" field now sums all transactions excluding TDS (was using booking_amount only) (Feb 2026)
- [x] PDF inline editing — every generated document can be edited in-place via `EditableDocumentDialog` (iframe + contenteditable + save/download) (Feb 2026)
- [x] Admin Template Editor — Settings → Document Templates tab. Snapshot built-in default → edit HTML with live preview → all future generations of that doc type use the override. Revert restores the built-in default. (Feb 2026)
- [x] **Payment Receipt** — new document type matching RRL physical receipt format. Auto-assigned receipt numbers (PAR-001, PAR-002, ...) on every transaction creation. Green Receipt button in Transactions Table generates + opens editable receipt for download. Backfills receipt numbers for legacy transactions. (Feb 2026)
- [x] **`/payments` page re-linked to sidebar** — orphaned during the April 10 refactor; now appears between Customers and Documents with IndianRupee icon. (Feb 2026)
- [x] **Disbursement Slab card** — prominent red summary tiles for "Overdue Customers" count + "Total Overdue Amount" added to Dashboard. (Feb 2026)
- [x] **FEATURE_TIMELINE.md** — chronological audit of every feature built since March 2026, saved at `/app/memory/FEATURE_TIMELINE.md`. (Feb 2026)
- [x] **Code Quality Round 2** — moved hardcoded test password to env var (`ADMIN_TEST_PASSWORD`); replaced production `console.error` calls with `logError` helper that no-ops in prod; refactored `get_dashboard_stats` into 3 helper functions; flattened nested ternaries in LoginPage / LeadsPage / CustomerQuickInfo; memoized `login` in AuthContext to prevent stale closures. Verified by re-running `tests/test_refactoring_iteration29.py` (19/19 pass). False-positive findings (safePreview, EmailComposerDialog XSS, `att`/`pdf_bytes`/`db` undefined) confirmed safe and skipped. (Feb 2026)
- [x] **Canonical bank registry** — `utils/banks.py` (backend) + `utils/banks.js` (frontend) provide a single source of truth for bank names. `/api/customers/banks` now deduplicates aliases (HDFC + HDFC BANK + hdfc bank → "HDFC Bank"). Customer list filter matches all aliases when filtering by canonical name. BookingDetailsCard edit form and public PaymentStep replaced free-text Input with Select (with "Other" fallback for legacy data). New endpoint `/api/customers/banks/registry`. (Feb 2026)
- [x] **Bank filter source corrected** — `/api/customers/banks` now sources from the **Bank Opted for Loan** field (`bank_name` + `bank_name_other` for "Others"), NOT the booking-form `finance_bank`. Filter query also follows the same field. The "opted for" bank is the authoritative one. (Feb 2026)
- [x] **Disbursement Slab dashboard tiles** — added 3 stat tiles to the Disbursement Slab card: Total Revenue (Expected at slab), Total Collected (Cumulative across all customers), Total Overdue at Slab. Also fixed a latent bug where the existing PaymentStageCard treated the API response as an array — overdue customer list now renders correctly. Tiles include % progress bars showing collected/overdue as fraction of expected. (Feb 2026)
- [x] **Co-applicant gender + dynamic S/o, D/o, W/o label** — Booking form and customer-profile CoApplicantCard now have a Gender Select with the same options as the primary applicant. Father/Spouse Name label dynamically reflects relation. Also fixes a latent bug where co_applicant_date_of_birth wasn't being saved from booking submissions. (Feb 2026)
- [x] **Lead Reject button + confirmation dialog** — Leads page now has a red Reject button on every row and in the View Lead dialog. Confirmation dialog with optional Reason input. Calls existing PUT /api/leads/{id}/reject which deletes the customer, releases the unit, and logs the activity. (Feb 2026)

---

## 9. Upcoming / Backlog

### P1 (High Priority)
- Comprehensive testing with real production data

### P2 (Medium Priority)
- Inbox View for Email Tracking (inbound replies via SendGrid Inbound Parse or IMAP)
- WhatsApp via Twilio (full API integration)
- Activity Logs UI (audit trail page)

### P3 (Low Priority)
- User-Uploadable Email Attachments
- ~~Admin Template Editor (UI for editing PDF templates)~~ **DONE — Feb 2026**

---

## 10. Critical Rules
- **Test Customer Only:** Use "Ramya test lead" (ID: `6d902613-5106-4294-bc3e-b907f85127f7`) for all testing
- **Never test with real customer data**
- **All backend routes prefixed with /api**
- **MongoDB _id excluded from all responses**
