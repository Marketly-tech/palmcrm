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
│   ├── documents/templates/   # Split template package
│   │   ├── __init__.py, common.py, default_template.py, logo_data.py
│   │   ├── allotment_letter.py, booking_form.py, cost_breakup.py
│   │   ├── demand_letter.py, email_templates.py, noc_templates.py
│   │   ├── payment_schedule.py, price_breakup.py, terms_conditions.py
│   │   ├── sales_agreement_html.py, sales_agreement_template.py
│   ├── static/rrl_logo.png
│   ├── tests/
│   ├── config.py, database.py
│   └── .env
└── frontend/
    ├── src/
    │   ├── App.js
    │   ├── components/customer/  # Extracted tab components
    │   │   ├── DetailsTab.jsx, PaymentTrackingTab.jsx, EmailComposerDialog.jsx
    │   │   ├── DocumentsTab.jsx, UploadsTab.jsx, CommunicationTab.jsx
    │   │   ├── ChecklistTab.jsx, PaymentScheduleTab.jsx, NotesTab.jsx
    │   │   └── utils.js, index.js
    │   └── pages/
    │       ├── CustomerDetailPage.js (~1333 lines)
    │       ├── BookingFormPage.js (~1330 lines)
    │       └── DashboardPage.js
    └── .env
```

## What's Been Implemented

### Completed Features
- User authentication (login/register with JWT)
- Role-based access control (admin, manager, sales, accounts)
- Customer CRUD with detailed profiles
- Payment schedule management with cumulative percentages
- Transaction logging with stage tracking
- Document generation (all 9 types with PDF)
- Bank NOC generation (HDFC, BOB, TATA Capital)
- Document upload/download/preview
- Communication (Email via SendGrid, WhatsApp MOCKED)
- Document checklist tracking
- Customer notes
- Dashboard with metrics
- Admin-only inline editing of Booking Details
- Live price calculation during customer edit

### Co-Applicant Template Integration (April 10, 2026 - Session 2)
- **Price Breakup:** Added co-applicant Name, Phone, Email section
- **Payment Schedule PDF:** Added co-applicant Name, Phone, Email section
- **Payment Schedule HTML:** Added co-applicant Name
- **Terms & Conditions:** Replaced `Mr./Mrs.` with `format_customer_names()` for proper name handling

### Dashboard Payment Stage Restore (April 10, 2026 - Session 2)
- Restored admin-only "Disbursement Payment Stage" card with Select dropdown
- Dropdown shows all 10 construction milestones (Podium 40% to Handover 100%)
- Changing stage refreshes overdue customer data
- Shows overdue customer cards with amounts

### Transaction PDF Export (April 10, 2026 - Session 2)
- New backend endpoint: `GET /api/transactions/{customer_id}/export-html`
- Returns formatted HTML with customer details, co-applicant info, transaction table, and summary
- "Export PDF" button in PaymentTrackingTab (visible when transactions exist)
- Opens formatted HTML in new browser window for Print/Save as PDF

### Document Template Overhaul (April 10, 2026 - Session 1)
- **Company Name:** Updated to "RRL Builders and Developers Pvt. Ltd." in ALL documents
- **Logo:** Replaced with actual RRL Group logo image (base64-embedded PNG)
- **Applicant/Co-applicant Format:** Updated across all documents with age, Aadhaar, PAN
- **Allotment Letter Point 14:** Added repo rate text (7.15%)
- **Sales Agreement Point 2:** Updated to use total received from ALL transactions
- **Co-applicant DOB:** New field added to booking form and customer details

### Code Refactoring (April 3-10, 2026)
- Backend: Split `documents/templates.py` (~4500 lines) into modular package with 12 files
- Frontend: Extracted `CustomerDetailPage.js` from 2457 → 1333 lines (DetailsTab, PaymentTrackingTab, EmailComposerDialog)

## Pending / Backlog

### P1 - In Progress
- Frontend refactoring of `BookingFormPage.js` (~1330 lines)

### P2 - Future
- WhatsApp integration via Twilio (currently MOCKED)
- Document Checklist for KYC tracking
- Activity Logs / audit trail
- Enhanced Dashboard with more charts

### P3 - Low Priority
- User-uploadable email attachments
- Admin template editor for PDF templates

## Testing
- Test customer: "Ramya test lead" (ID: `6d902613-5106-4294-bc3e-b907f85127f7`)
- Latest test report: `/app/test_reports/iteration_23.json`
- Backend: 100% pass (12/12 tests)
- Frontend: 100% pass

## 3rd Party Integrations
- **SendGrid (Email)** - requires user API key
- **WhatsApp** - MOCKED (uses whatsapp:// link)
