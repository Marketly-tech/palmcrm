# RRL Builders Post-Sales CRM - Product Requirements Document

## Original Problem Statement
Build a web-based POST-SALES Internal CRM for a real estate developer called "RRL Builders". The CRM must manage the entire post-booking lifecycle of a real estate customer, replacing Excel sheets and automating processes.

## Architecture
- **Backend:** FastAPI + Motor (async MongoDB) + WeasyPrint (PDF)
- **Frontend:** React + TailwindCSS + Shadcn UI + Axios
- **Database:** MongoDB

### Key Routes
- `/dashboard` — Main metrics + Disbursement Stage management (admin)
- `/customers` — Customer list with filters
- `/customers/:id` — Customer detail with tabs
- `/email-logs` — Centralized email tracking (admin/manager)
- `/booking-form` — Public booking form (no auth)
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
    │   ├── components/
    │   │   ├── booking/ (7 extracted components - constants, steps, uploads, success)
    │   │   ├── customer/ (10 extracted components - tabs, cards, dialogs)
    │   │   ├── layout/DashboardLayout.js
    │   │   └── ui/ (Shadcn components)
    │   └── pages/
    │       ├── BookingFormPage.js (231 lines, refactored from 1336)
    │       ├── CustomerDetailPage.js (1334 lines, refactored from 2457)
    │       ├── DashboardPage.js, CustomersPage.js, EmailLogsPage.js
    └── .env
```

## What's Been Implemented (Complete)
- JWT auth, role-based access (admin, manager, sales, accounts)
- Customer CRUD with detailed profiles, co-applicant support
- Payment schedule with cumulative %, stage-wise TDS
- Transaction logging + PDF export
- All 9+ document types with PDF (WeasyPrint)
- Bank NOC (HDFC, BOB, TATA Capital) with dedicated UI
- Email via SendGrid + Email Tracking page
- Document checklist, Notes, Communication history
- Dashboard with disbursement stage management
- Admin inline editing, live price calculator
- Co-applicant across all templates
- Sales Agreement: "Represented by its Managing Director Mr. Ram R"
- Cost Breakup: BESCOM Rs.2,00,000, TDS (total/101)
- NOC: DD/MM/YY date, signature interchanged, due_date=generation date
- Demand Letter: TDS auto-calculated from stage
- Frontend refactoring: BookingFormPage (1336→231), CustomerDetailPage (2457→1334)

## Pending / Backlog
### P1
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
- Latest: iteration_26.json — 100% pass
- **CRITICAL:** Only use "Ramya test lead" for testing. Do NOT test with other customers.

## 3rd Party Integrations
- **SendGrid (Email)** - requires user API key
- **WhatsApp** - MOCKED (uses whatsapp:// link)
