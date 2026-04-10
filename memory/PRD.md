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
    │   ├── hooks/
    │   │   └── useCustomerPage.js (734 lines - extracted customer page logic)
    │   ├── components/
    │   │   ├── booking/ (7 extracted components - constants, steps, uploads, success)
    │   │   ├── customer/ (12 components - tabs, cards, dialogs, CustomerHeader, CustomerQuickInfo)
    │   │   ├── customers/ (3 components - CreateCustomerDialog, CustomerFilters, CustomerTable)
    │   │   ├── dashboard/ (8 components - StatsCards, RevenueCards, PaymentStageCard, ExportDataCard, PaymentStatusChart, UpcomingPayments, DueDateCountdown, RecentActivity)
    │   │   ├── settings/ (4 components - UserManagementCard, EditUserDialog, ResetPasswordDialog, GeneralSettingsTab)
    │   │   ├── layout/DashboardLayout.js
    │   │   └── ui/ (Shadcn components)
    │   ├── utils/safePreview.js
    │   └── pages/
    │       ├── BookingFormPage.js (231 lines, refactored from 1336)
    │       ├── CustomerDetailPage.js (246 lines, refactored from 1322)
    │       ├── SettingsPage.js (180 lines, refactored from 669)
    │       ├── CustomersPage.js (175 lines, refactored from 655)
    │       ├── DashboardPage.js (157 lines, refactored from 641)
    │       └── EmailLogsPage.js
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
- Security: DOMPurify for XSS, sessionStorage for auth, safePreview.js for HTML rendering
- Frontend refactoring complete: All 5 major pages broken into sub-components (Apr 2026)

## Pending / Backlog
### P1
- Backend complexity reduction (dashboard/routes.py, customers/routes.py, document templates)
- Backend server.py route extraction to modular files

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
- Latest: iteration_27.json — 100% pass (frontend refactoring validation)
- **CRITICAL:** Only use "Ramya test lead" for testing. Do NOT test with other customers.

## 3rd Party Integrations
- **SendGrid (Email)** - requires user API key
- **WhatsApp** - MOCKED (uses whatsapp:// link)
