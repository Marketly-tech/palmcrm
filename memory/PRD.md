# RRL Builders Post-Sales CRM - Product Requirements Document

## Original Problem Statement
Build a web-based POST-SALES Internal CRM for a real estate developer called "RRL Builders". The CRM must manage the entire post-booking lifecycle of a real estate customer, replacing Excel sheets and automating processes.

## Core Requirements
- **Lead/Booking Intake:** Public-facing form for customer, co-applicant, and property data with document uploads
- **User & Role Management:** Admin user creation, permissions (roles), password reset
- **Customer Profile:** Detailed, editable customer profiles with tabs for details, calculator, payments, documents, communication, checklist, notes
- **Transaction Management:** Log and track all payments made by customers
- **Payment Tracking:** Track payment schedules, calculate total received vs. pending
- **Document Generation:** Editable templates for Demand Letters, Allotment Letters, Sales Agreements, Booking Form Previews, Cost Breakups, Bank NOCs, Terms & Conditions, Price Breakups (PDF)
- **Dashboard:** Key metrics - total revenue, pending payments, total customers
- **Automated Communications:** Email integration (SendGrid)

## Architecture
- **Backend:** FastAPI + Motor (async MongoDB) + WeasyPrint (PDF) + Pytest
- **Frontend:** React + TailwindCSS + Shadcn UI + Axios
- **Database:** MongoDB

### File Structure
```
/app/
├── backend/
│   ├── server.py              # Main entry point
│   ├── auth/, customers/, documents/, dashboard/, email_service/, payments/, utils/
│   ├── documents/templates/   # Split template package (was templates.py)
│   │   ├── __init__.py, common.py, default_template.py
│   │   ├── allotment_letter.py, booking_form.py, cost_breakup.py
│   │   ├── demand_letter.py, email_templates.py, noc_templates.py
│   │   ├── payment_schedule.py, price_breakup.py
│   │   ├── sales_agreement_html.py, sales_agreement_template.py
│   │   └── terms_conditions.py
│   ├── tests/                 # Regression test files
│   ├── config.py, database.py
│   └── .env
└── frontend/
    ├── src/
    │   ├── App.js
    │   ├── components/
    │   │   ├── customer/      # Extracted tab components
    │   │   │   ├── DetailsTab.jsx, PaymentTrackingTab.jsx, EmailComposerDialog.jsx
    │   │   │   ├── DocumentsTab.jsx, UploadsTab.jsx, CommunicationTab.jsx
    │   │   │   ├── ChecklistTab.jsx, PaymentScheduleTab.jsx, NotesTab.jsx
    │   │   │   ├── PaymentTrackingCard.jsx, TransactionsCard.jsx
    │   │   │   └── utils.js, index.js
    │   │   └── ui/            # Shadcn components
    │   └── pages/
    │       ├── CustomerDetailPage.js (~1333 lines, refactored from ~2457)
    │       ├── BookingFormPage.js (~1280 lines, pending refactor)
    │       └── DashboardPage.js
    └── .env
```

## What's Been Implemented

### Completed Features
- User authentication (login/register with JWT)
- Role-based access control (admin, manager, sales, accounts)
- Customer CRUD with detailed profiles
- Payment schedule management with cumulative percentages
- Transaction logging with stage tracking (booking, agreement, scheduled_disbursement)
- Document generation (Sales Agreement, Allotment Letter, Price Breakup, Cost Breakup, Disbursement Letter, Payment Schedule, Demand Letter)
- Bank NOC generation (HDFC, Bank of Baroda, TATA Capital)
- Document upload/download/preview
- Communication (Email via SendGrid, WhatsApp MOCKED)
- Document checklist tracking
- Customer notes
- Dashboard with metrics (Total Revenue, Pending, Customer Count)
- Admin-only inline editing of Booking Details
- Agreement status tracking with dropdown
- Payment due date management
- Disbursement calculator
- Live price calculation during customer edit

### Code Refactoring Done (April 2026)
- **Backend:** Split `documents/templates.py` (~4500 lines) into modular `documents/templates/` package with 12 files
- **Frontend:** Extracted `CustomerDetailPage.js` from 2457 → 1333 lines by creating:
  - `DetailsTab.jsx` - Personal Info, Property & Pricing, Booking Details, Bank Details, Co-Applicant
  - `PaymentTrackingTab.jsx` - Payment Tracking, Disbursement Calculator, Transaction Records
  - `EmailComposerDialog.jsx` - Unified email composer dialog
- Fixed payment double-counting bug
- Auto-generated booking transactions for all customers
- Fixed transaction edit/save bug with legacy data normalization
- Addressed code quality issues (React hooks, empty catch blocks, hardcoded secrets)

## Pending / Backlog

### P1 - In Progress
- Frontend refactoring of `BookingFormPage.js` (~1280 lines)

### P2 - Future
- WhatsApp integration via Twilio (currently MOCKED with whatsapp:// link)
- Document Checklist for KYC tracking
- Activity Logs / audit trail
- Enhanced Dashboard with more charts

### P3 - Low Priority
- User-uploadable email attachments
- Admin template editor for PDF templates

## Testing
- Test customer: "Ramya test lead" (ID: `6d902613-5106-4294-bc3e-b907f85127f7`)
- Backend: 100% pass (27/27 tests in iteration 21)
- Frontend: 100% pass (all tabs and features verified)
- Test reports: `/app/test_reports/iteration_21.json`

## 3rd Party Integrations
- **SendGrid (Email)** - requires user API key
- **WhatsApp** - MOCKED (uses whatsapp:// link, Twilio integration pending)
