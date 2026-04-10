# RRL Builders Post-Sales CRM - Product Requirements Document

## Original Problem Statement
Build a web-based POST-SALES Internal CRM for a real estate developer called "RRL Builders". The CRM must manage the entire post-booking lifecycle of a real estate customer, replacing Excel sheets and automating processes.

## Core Requirements
- **Lead/Booking Intake:** Public-facing form for customer, co-applicant, and property data with document uploads
- **User & Role Management:** Admin user creation, permissions (roles), password reset
- **Customer Profile:** Detailed, editable customer profiles with tabs for details, calculator, payments, documents, communication, checklist, notes
- **Transaction Management:** Log and track all payments + PDF export
- **Payment Tracking:** Track payment schedules, calculate total received vs. pending, stage-wise TDS
- **Document Generation:** Templates for Demand Letters, Allotment Letters, Sales Agreements, Booking Form Previews, Cost Breakups, Bank NOCs, Terms & Conditions, Price Breakups (PDF)
- **Dashboard:** Key metrics - total revenue, pending payments, total customers, disbursement stage management
- **Automated Communications:** Email integration (SendGrid)

## Architecture
- **Backend:** FastAPI + Motor (async MongoDB) + WeasyPrint (PDF) + Pytest
- **Frontend:** React + TailwindCSS + Shadcn UI + Axios
- **Database:** MongoDB

### File Structure
```
/app/
├── backend/
│   ├── server.py
│   ├── auth/, customers/, documents/, dashboard/, email_service/, payments/, utils/
│   ├── documents/templates/
│   │   ├── __init__.py, common.py, default_template.py, logo_data.py
│   │   ├── allotment_letter.py, booking_form.py, cost_breakup.py
│   │   ├── demand_letter.py, email_templates.py, noc_templates.py
│   │   ├── payment_schedule.py, price_breakup.py, terms_conditions.py
│   │   ├── sales_agreement_html.py, sales_agreement_template.py
│   ├── tests/
│   ├── config.py, database.py
│   └── .env
└── frontend/
    ├── src/
    │   ├── App.js
    │   ├── components/customer/
    │   │   ├── DetailsTab.jsx, PaymentTrackingTab.jsx, EmailComposerDialog.jsx
    │   │   ├── DocumentsTab.jsx, UploadsTab.jsx, CommunicationTab.jsx
    │   │   ├── ChecklistTab.jsx, PaymentScheduleTab.jsx, NotesTab.jsx
    │   │   └── TransactionsCard.jsx, utils.js, index.js
    │   └── pages/
    │       ├── CustomerDetailPage.js, BookingFormPage.js, DashboardPage.js
    └── .env
```

## What's Been Implemented

### Completed Features (Core)
- User authentication (JWT), role-based access control (admin, manager, sales, accounts)
- Customer CRUD with detailed profiles
- Payment schedule management with cumulative percentages
- Transaction logging with stage tracking + PDF export
- Document generation (all 9+ types with PDF via WeasyPrint)
- Bank NOC generation (HDFC, BOB, TATA Capital)
- Document upload/download/preview
- Communication (Email via SendGrid, WhatsApp MOCKED)
- Document checklist tracking, Customer notes
- Dashboard with metrics + Disbursement Payment Stage management
- Admin-only inline editing of Booking Details
- Live price calculation during customer edit

### Session 2 Changes (April 10, 2026)

#### Co-Applicant Template Integration
- Price Breakup: Added co-applicant Name, Phone, Email
- Payment Schedule PDF/HTML: Added co-applicant details
- Terms & Conditions: Uses `format_customer_names()` (no Mr./Mrs.)

#### Dashboard Payment Stage Restore
- Restored admin-only "Disbursement Payment Stage" card with Select dropdown
- Shows overdue customer cards with amounts

#### Transaction PDF Export
- `GET /api/transactions/{customer_id}/export-html` - queries with $in for both UUID and RRL-XXXXX formats
- "Export PDF" button in PaymentTrackingTab

#### Cost Breakup Updates
- BESCOM fixed at Rs. 2,00,000
- TDS row added below Amenities (TDS = total_flat_value / 101)
- Basic cost reverse-calculated to keep total unchanged

#### NOC Document Updates
- Date format changed to DD/MM/YY (e.g., 10/04/26)
- "Due on" date = NOC generation date (today), not agreement date
- Signature interchanged: "For RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED" first, then "Authorized Signatory"

#### Demand Letter TDS
- TDS Payable = demand_raised / 101 (stage-based)
- TDS Paid = amount_paid / 101
- TDS Balance = Payable - Paid
- Values properly formatted with Indian currency

#### Stage-wise TDS in Payment Tracking
- New TDS section showing Payable, Paid, and Balance per current disbursement stage

#### Disbursement Documents UI Restored
- NOC generation card with HDFC/BOB/TATA buttons restored in Documents tab
- NOC documents separated from regular documents list

### Session 1 Changes (April 10, 2026)
- Fixed backend NameError crash from missing imports
- Refactored CustomerDetailPage.js (2457 -> 1333 lines)
- Updated all PDF templates with base64 logo, "Pvt. Ltd." company name
- Dynamic applicant/co-applicant formatting with age, Aadhaar, PAN
- Allotment Letter repo rate clause, Sales Agreement total_received update
- Co-applicant DOB field added

## Pending / Backlog

### P1 - In Progress
- Frontend refactoring of `BookingFormPage.js` (~1330 lines)

### P2 - Future
- WhatsApp integration via Twilio (currently MOCKED)
- Document Checklist for KYC tracking
- Activity Logs / audit trail
- Enhanced Dashboard with more charts
- Customer list column additions (Payment %)

### P3 - Low Priority
- User-uploadable email attachments
- Admin template editor for PDF templates

## Testing
- Test customer: "Ramya test lead" (ID: `6d902613-5106-4294-bc3e-b907f85127f7`)
- Latest test report: `/app/test_reports/iteration_24.json`
- Backend: 100% pass (14/14 tests)
- Frontend: 100% pass

## 3rd Party Integrations
- **SendGrid (Email)** - requires user API key
- **WhatsApp** - MOCKED (uses whatsapp:// link)
