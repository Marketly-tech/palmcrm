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
- **Email Tracking:** Centralized outbound email log with search, status filter, pagination
- **Automated Communications:** Integration with Email (SendGrid)

## Architecture
- **Backend:** FastAPI + Motor (async MongoDB) + WeasyPrint (PDF) + Pytest
- **Frontend:** React + TailwindCSS + Shadcn UI + Axios
- **Database:** MongoDB

### Key Routes
- `/dashboard` — Main metrics + Disbursement Stage management (admin)
- `/customers` — Customer list with filters
- `/customers/:id` — Customer detail with tabs
- `/email-logs` — Centralized email tracking (admin/manager)
- `/settings` — User management (admin)

### File Structure
```
/app/
├── backend/
│   ├── server.py
│   ├── documents/templates/ (12 template files)
│   ├── auth/, customers/, dashboard/, email_service/, payments/, utils/
│   ├── tests/
│   └── .env
└── frontend/
    ├── src/
    │   ├── App.js
    │   ├── components/customer/ (10 extracted components)
    │   ├── components/layout/DashboardLayout.js
    │   └── pages/
    │       ├── CustomerDetailPage.js, BookingFormPage.js, DashboardPage.js
    │       ├── EmailLogsPage.js, CustomersPage.js
    │       └── ...
    └── .env
```

## What's Been Implemented

### Core Features (Complete)
- JWT auth, role-based access (admin, manager, sales, accounts)
- Customer CRUD with detailed profiles
- Payment schedule management with cumulative percentages
- Transaction logging with PDF export
- All 9+ document types with PDF generation via WeasyPrint
- Bank NOC (HDFC, BOB, TATA Capital) with dedicated UI
- Email via SendGrid, WhatsApp (MOCKED)
- Document checklist, Notes, Communication history
- Dashboard with disbursement stage management
- Admin inline editing of booking details
- Co-applicant support across all document templates

### Latest Changes (April 10, 2026 - Session 2)
- **Sales Agreement**: Added "Represented by its Managing Director Mr. Ram R" to VENDORS signature
- **Email Tracking Page**: New `/email-logs` page with search, status filter, pagination, customer enrichment
- **Sidebar**: Added "Email Tracking" navigation for admin/manager
- **CommunicationTab**: Enhanced status badges + inbox note
- **Transaction PDF Export**: Fixed customer_id mismatch (UUID vs RRL-XXXXX)
- **Cost Breakup**: BESCOM = Rs.2,00,000 fixed, TDS row (total/101) added
- **NOC Documents**: Date DD/MM/YY, signature interchanged, due_date = generation date
- **Demand Letter**: TDS auto-calculated from stage data
- **Stage-wise TDS**: New section in Payment Tracking tab
- **Co-applicant**: Added to Price Breakup, Payment Schedule, Terms & Conditions
- **Disbursement Documents UI**: NOC card restored in Documents tab
- **Dashboard Payment Stage**: Restored admin dropdown

## Pending / Backlog

### P1
- Frontend refactoring of `BookingFormPage.js` (~1330 lines)
- Customer list column additions (Payment %)

### P2
- WhatsApp via Twilio (currently MOCKED)
- Document Checklist for KYC tracking
- Activity Logs / audit trail
- Enhanced Dashboard with more charts
- SendGrid Inbound Parse for inbox replies

### P3
- User-uploadable email attachments
- Admin template editor for PDF templates

## Testing
- Test customer: "Ramya test lead" (ID: `6d902613-5106-4294-bc3e-b907f85127f7`)
- Latest test report: `/app/test_reports/iteration_25.json`
- All tests passing (100%)

## 3rd Party Integrations
- **SendGrid (Email)** - requires user API key
- **WhatsApp** - MOCKED (uses whatsapp:// link)
