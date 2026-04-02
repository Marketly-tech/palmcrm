# RRL Builders Post-Sales CRM - Product Requirements Document

## Original Problem Statement
Build a web-based POST-SALES Internal CRM for a real estate developer called "RRL Builders". The CRM must manage the entire post-booking lifecycle of a real estate customer, replacing Excel sheets and automating processes.

## Core Requirements
- **Lead/Booking Intake:** Public-facing form for customer, co-applicant, and property data with document uploads
- **User & Role Management:** Admin user creation, permissions (roles), password reset
- **Customer Profile:** Detailed, editable customer profiles with tabs for details, calculator, payments, documents, communication, checklist, notes
- **Transaction Management:** Log and track all payments made by customers
- **Payment Tracking:** Track payment schedules, calculate total received vs. pending
- **Document Generation:** Editable templates for Allotment Letters, Sales Agreements, Booking Form Previews, Cost Breakups, Bank NOCs, Terms & Conditions, Price Breakups (PDF)
- **Dashboard:** Key metrics - total revenue, pending payments, total customers, stage-wise overdue
- **Automated Communications:** Email integration (SendGrid)

## Architecture
- **Backend:** FastAPI + Motor (async MongoDB) + WeasyPrint (PDF) + Pytest
- **Frontend:** React + TailwindCSS + Shadcn UI + Axios
- **Database:** MongoDB

### File Structure
```
/app/
├── backend/
│   ├── server.py              # Main entry (~3827 lines, refactored)
│   ├── auth/, customers/, documents/, dashboard/, email_service/, payments/, utils/
│   ├── documents/templates.py # HTML template generators (extracted)
│   ├── tests/                 # Regression test files
│   ├── config.py, database.py
│   └── .env
└── frontend/
    ├── src/
    │   ├── App.js
    │   ├── components/
    │   │   ├── customer/      # Extracted tab components
    │   │   │   ├── DocumentsTab.jsx, UploadsTab.jsx, CommunicationTab.jsx
    │   │   │   ├── ChecklistTab.jsx, PaymentScheduleTab.jsx, NotesTab.jsx
    │   │   │   ├── PaymentTrackingCard.jsx, TransactionsCard.jsx
    │   │   │   └── utils.js, index.js
    │   │   └── ui/            # Shadcn components
    │   └── pages/
    │       └── CustomerDetailPage.js (~2380 lines, refactored)
    └── .env
```

## What's Been Implemented

### Completed Features
- User authentication (login/register with JWT)
- Role-based access control (admin, manager, sales, accounts)
- Customer CRUD with detailed profiles
- Payment schedule management with cumulative percentages
- Transaction logging with stage tracking
- Document generation (Sales Agreement, Allotment Letter, Price Breakup, Cost Breakup, Disbursement Letter, Payment Schedule, Demand Letter)
- Bank NOC generation (HDFC, Bank of Baroda, TATA Capital)
- Document upload/download/preview
- Communication (Email via SendGrid, WhatsApp MOCKED)
- Document checklist tracking
- Customer notes
- Dashboard with metrics
- Public booking form
- Lead management pipeline
- CSV/Excel export
- Welcome email with preview
- Email composer with attachment support

### Refactoring Completed (April 2026)
- **Backend:** Extracted ~4100 lines of HTML template generators from server.py → documents/templates.py
  - server.py reduced from 7925 → 3827 lines (51% reduction)
- **Frontend:** Extracted inline tab content from CustomerDetailPage.js → component files
  - CustomerDetailPage.js reduced from 3180 → 2380 lines (25% reduction)
  - Components: DocumentsTab, UploadsTab, CommunicationTab, ChecklistTab, PaymentScheduleTab, NotesTab

### Booking ID Import & Display (April 2026)
- Imported booking_number, agreement_date, and notes from Excel (PA_CB_16-MARCH-2026.xlsm) for 33 customers
- 4 remaining CRM customers auto-assigned sequential booking numbers
- Replaced customer_id display with booking_number (e.g., "RRL PAB035") across customer list and detail pages
- Search now supports booking_number
- Restored SOVARAJ PRUSTY's booking details (₹2,00,000 / 2026-02-28)
- Removed "Total Received" and "Balance" from Booking Details card (belong in Payment Tracking only)
- Protected booking details from accidental overwrite (frontend strips, backend blocks)

### Payment Tracking Double-Counting Fix (April 2026)
- **Bug:** booking_amount (from customer profile) was being added ON TOP of transaction totals, doubling the "Received" amount
- **Root cause:** booking payments are already recorded as individual transactions; adding booking_amount separately = 2x inflation
- **Fixed in:** Frontend (CustomerDetailPage.js, PaymentTrackingCard.jsx, utils.js), Backend (server.py overdue calculations, dashboard/routes.py revenue)
- **Impact:** Payment Tracking cards, Dashboard revenue, Overdue calculations all now use transactions as single source of truth
- **Auto-generation:** Added `auto_generate_booking_transaction` helper that creates a booking-stage transaction when a customer has `booking_amount` not covered by existing transactions
- **Booking Amount Restoration:** Updated all 37 customers' `booking_amount` to match their first transaction (actual initial token payment). For example, Kuldeep Khandelwal: ₹10,12,588 → ₹50,000
- **Sales Agreement:** Updated template to render actual transaction records (booking + agreement stages) instead of hardcoded booking_amount field

### UI Cleanup & Booking Details Edit (April 2026)
- Admin can now edit Booking Details (finance_type, finance_bank, booking_amount, booking_date) via dedicated PUT `/api/customers/{id}/booking-details` endpoint (admin-only, 403 for other roles)
- Removed: Disbursement Documents section from Documents tab
- Removed: Payments tab from sidebar navigation and App.js routes
- Removed: Overdue Payments (Stage Overdue Count card, Disbursement Slab selector, Overdue Payments list) from main dashboard

### Code Quality Improvements (April 2026)
- **Security:** DOMPurify sanitization on all `document.write` and `dangerouslySetInnerHTML` (XSS prevention)
- **Security:** Hardcoded credentials removed from all test files → centralized in `conftest_credentials.py` via env vars
- **Correctness:** React hook dependencies fixed (useCallback/useMemo) in AuthContext, DashboardPage, CustomerDetailPage
- **Performance:** Context value memoized in AuthContext, navigation filtering memoized in DashboardLayout
- **Quality:** Console statements removed from all production pages, array index keys replaced with stable IDs

## Prioritized Backlog

### P1 - In Progress
- Further backend route extraction (communication, leads, exports, settings routes still in server.py)

### P1 - Upcoming
- Comprehensive testing with real production data

### P2 - Future
- WhatsApp integration via Twilio (currently MOCKED)
- Document Checklist enhancement
- Enhanced Dashboard with charts/analytics
- Activity Logs / Audit Trail

### P3 - Backlog
- User-uploadable email attachments enhancement
- Admin template editor for PDFs

## Test Credentials
- **Admin:** crm@rrlbuildersanddevelopers.com / #RRLnew2026
- **Accounts:** accounts@rrlbuilders.com / accounts123
- **Test Customer:** Ramya test lead (ID: 6d902613-5106-4294-bc3e-b907f85127f7)

## 3rd Party Integrations
- **SendGrid (Email)** - requires User API Key
- **WhatsApp (Twilio)** - MOCKED (placeholder whatsapp:// link)
