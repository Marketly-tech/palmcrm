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
│   ├── server.py
│   ├── auth/, customers/, documents/, dashboard/, email_service/, payments/, utils/
│   ├── documents/templates/   # Split template package
│   │   ├── __init__.py, common.py, default_template.py, logo_data.py
│   │   ├── allotment_letter.py, booking_form.py, cost_breakup.py
│   │   ├── demand_letter.py, email_templates.py, noc_templates.py
│   │   ├── payment_schedule.py, price_breakup.py, terms_conditions.py
│   │   ├── sales_agreement_html.py, sales_agreement_template.py
│   ├── static/rrl_logo.png   # RRL Group logo (transparent)
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

### Document Template Overhaul (April 10, 2026)
- **Company Name:** Updated from "RRL Builders and Developers" to "RRL Builders and Developers Pvt. Ltd." in ALL documents, emails, and PDFs
- **Logo:** Replaced "R" text logo with actual RRL Group logo image (base64-embedded PNG) across all document templates
- **Applicant/Co-applicant Format:** Updated across all documents to include:
  - Name, Age (auto-calculated from DOB), S/o or D/o or W/o {father/spouse name}
  - Address, Aadhaar, PAN, Phone
  - Same format applied to co-applicant
- **Allotment Letter Point 14:** Added repo rate text: "As per the current repo rate, the banker is lending at 7.15%..."
- **Sales Agreement Point 2:** Updated to use total received from ALL transactions (not just booking amount)
- **Co-applicant DOB:** New field `co_applicant_date_of_birth` added to booking form and customer details

### Code Refactoring (April 3, 2026)
- Backend: Split `documents/templates.py` (~4500 lines) into modular package with 12 files
- Frontend: Extracted `CustomerDetailPage.js` from 2457 → 1333 lines (3 new components)
- Fixed payment double-counting bug
- Fixed transaction edit/save bug
- Addressed code quality issues

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
- Latest test report: `/app/test_reports/iteration_22.json`
- Backend: 100% pass (25/25 tests)
- Frontend: 100% pass

## 3rd Party Integrations
- **SendGrid (Email)** - requires user API key
- **WhatsApp** - MOCKED (uses whatsapp:// link)
