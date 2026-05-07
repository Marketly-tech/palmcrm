# RRL Builders Post-Sales CRM - Product Requirements Document

## Original Problem Statement
Build a web-based POST-SALES Internal CRM for a real estate developer called "RRL Builders". The CRM must manage the entire post-booking lifecycle of a real estate customer, replacing Excel sheets and automating processes.

## Core Requirements
- **Lead/Booking Intake:** Public-facing booking form with document uploads
- **User & Role Management:** Admin user creation, permissions (admin/manager/accounts/sales/support)
- **Customer Profile:** Detailed editable profiles with tabs for personal details, price calculator, payment schedule, documents, communication
- **Transaction Management:** Log all customer payments
- **Payment Tracking:** Track schedules, calculate received vs pending, stage-based overdue
- **Document Generation:** PDF templates for Allotment Letters, Sales Agreements, Booking Form Previews, Cost Breakups, Bank NOCs, Terms & Conditions, Price Breakups, Demand Letters
- **Dashboard:** Key metrics, revenue, pending payments, stage-wise overdue counts
- **Automated Communications:** Email integration via SendGrid

## Architecture
```
/app/
├── backend/
│   ├── server.py              # Thin shell (~232 lines) - app init, CORS, routers, startup
│   ├── config.py              # Environment settings
│   ├── database.py            # MongoDB connection
│   ├── auth/                  # Auth routes, models, utils (login, register, JWT, roles)
│   ├── customers/             # Customer CRUD routes, models
│   ├── payments/              # Payment schedules, transactions, calculator
│   ├── dashboard/             # Stats, recent activities, upcoming dues
│   ├── documents/             # Document generation, templates, upload/download, checklist
│   │   └── templates/         # HTML template generators per doc type
│   ├── email_service/         # Email sending, previews, communication history
│   ├── booking/               # Public booking form, leads management
│   ├── settings/              # Payment stages, notes, overdue, units, export, projects
│   ├── utils/                 # Shared utilities, enums, payment helpers
│   └── tests/                 # Pytest test files
├── frontend/
│   └── src/
│       ├── components/
│       │   ├── customer/      # Extracted customer page components
│       │   ├── settings/      # Extracted settings components
│       │   ├── customers/     # Extracted customers list components
│       │   └── dashboard/     # Extracted dashboard components
│       └── pages/             # Thin page wrappers
└── memory/
    └── PRD.md
```

## What's Been Implemented
- [x] User authentication with JWT (admin, manager, accounts, sales roles)
- [x] **Backend refactoring: server.py reduced from ~4200 to ~232 lines** (Apr 2026)
- [x] Customer CRUD with detailed profiles
- [x] Public booking form with auto-email
- [x] Payment schedule management with templates
- [x] Transaction management with CRUD
- [x] Stage-based overdue calculation system
- [x] PDF document generation (12+ doc types including Bank NOCs)
- [x] Email integration via SendGrid
- [x] Dashboard with revenue metrics and stage tracking
- [x] CSV/Excel export
- [x] Document checklist
- [x] Activity logging
- [x] Customer notes
- [x] Unit pricing management
- [x] Frontend refactoring (all 4 major pages modularized)
- [x] **Bank-wise overdue tracking with cumulative totals** (May 2026)

## Upcoming Tasks (Prioritized)
### P1
- Backend function complexity reduction in `documents/templates/*.py`
- Comprehensive testing with real data on production

### P2
- Inbox View for Email Tracking (inbound replies)
- WhatsApp via Twilio integration (currently MOCKED)
- Implement Activity Logs UI (audit trail)

### P3
- User-Uploadable Email Attachments
- Template Editor (admin-facing UI for PDF templates)

## Technical Stack
- **Backend:** FastAPI, Python 3.11, Motor (async MongoDB), WeasyPrint (PDFs)
- **Frontend:** React, TailwindCSS, Shadcn UI
- **Database:** MongoDB
- **Email:** SendGrid (requires user API key)

## 3rd Party Integrations
- **SendGrid (Email)** - requires User API Key
- **WhatsApp** - MOCKED (uses whatsapp:// link)
