# RRL Builders Post-Sales CRM - Product Requirements Document

## Original Problem Statement
Build a web-based POST-SALES Internal CRM for "RRL Builders" real estate developer. The CRM manages the entire post-booking lifecycle of a real estate customer, replacing Excel sheets and automating various processes.

## User Personas
- **Admin**: Full access to all features, user management, system configuration
- **Manager**: Lead approval, customer management, document generation
- **Accounts**: Payment tracking, disbursement management, financial reports
- **Sales Team**: Customer management, booking form handling
- **Customer Support**: Communication, document checklist

## Core Requirements (Modules)

### Module 1: Lead Intake & Approval ✅ COMPLETED
- Public booking form at `/booking-form` (4-step wizard)
- Auto-creates "Pending Approval" customer entry
- Admin can view, edit, approve, or reject leads
- Stage dropdown for approval workflow

### Module 2: Customer Profile ✅ COMPLETED
- Detailed customer profiles with personal details
- Property details with pricing calculations
- Co-applicant information
- Finance details (Self/Loan/Mixed)
- Document uploads and checklist

### Module 3: Price Breakup Calculator ✅ COMPLETED
- **Formula**: (Rate × Saleable Area) + Club House + Parking + Labour Cess (0.70%) + GST (5%)
- Unit selection (2BHK, 3BHK, 4BHK)
- Club House toggle (₹2L)
- Additional Parking (₹3L each)
- UDS calculation (Saleable Area × 0.495046)
- Number to words conversion (Indian format)

### Module 4: Payment Plan ✅ COMPLETED
- 13-milestone payment schedule template
- Auto-generate schedule based on total price
- Track payment status (Pending/Paid/Partial/Overdue)
- Disbursement calculator
- Payment tracking with percentages

### Module 5: Document Generation ✅ COMPLETED
- HTML templates for Sales Agreement, Allotment Letter, Disbursement Letter
- PDF generation for Price Breakup
- Pink-themed welcome email template
- Preview and download functionality

### Module 6: Agreement Management ✅ COMPLETED
- Agreement status tracking (Draft/Sent/Signed/Completed)
- Document storage in customer profile

### Module 7: Email Automation 🔶 MOCKED
- SendGrid integration prepared (MOCKED - no API key)
- Welcome email with PDF attachment
- Communication logs stored in database

### Module 8: WhatsApp Reminders 🔶 MOCKED
- Twilio integration prepared (MOCKED - no API key)
- Communication logs stored in database

### Module 9: Document Checklist ✅ COMPLETED
- Checklist for each customer (KYC, PAN, Aadhaar, Agreement, Bank docs, Photo, Address proof)
- Toggle checkboxes to track received documents

### Module 10: Dashboard ✅ COMPLETED
- KPIs: Total Customers, Pending Agreements, Due This Week, Overdue Payments
- Monthly Revenue Trend chart
- Payment Status Distribution chart
- Overdue Payments list
- Upcoming Payments list

### Module 11: User Roles ✅ COMPLETED
- Admin, Manager, Accounts, Sales, Support roles
- Role-based access control implemented
- JWT authentication

## Technical Architecture

### Backend (FastAPI)
- **Server**: `/app/backend/server.py`
- **Database**: MongoDB
- **Authentication**: JWT with bcrypt password hashing
- **APIs**: RESTful endpoints with role-based access

### Frontend (React)
- **Framework**: React with React Router
- **UI Components**: Shadcn/UI
- **Styling**: TailwindCSS
- **State Management**: React Context (AuthContext)

### Key API Endpoints
- `POST /api/auth/login` - User login
- `POST /api/public/booking-form` - Public booking submission
- `GET/PUT /api/leads/pending` - Lead management
- `POST /api/calculator/price` - Price calculation
- `POST /api/calculator/disbursement` - Disbursement calculation
- `GET /api/calculator/payment-schedule-template` - Payment milestones
- `POST /api/communication/send-welcome-email/{id}` - Send welcome email (MOCKED)
- `POST /api/documents/generate-pdf/{id}` - Generate price breakup PDF

## Test Credentials
- **Email**: admin@rrlbuilders.com
- **Password**: admin123

## What's Been Implemented (March 2026)

### Phase 1: Core Infrastructure ✅
- JWT authentication with role-based access
- MongoDB database connection
- User management with roles

### Phase 2: Lead Intake & Approval ✅
- Public booking form (4-step wizard)
- Pending leads dashboard
- Approve/Reject functionality
- Stage management

### Phase 3: Price Calculator ✅
- Price Breakup Calculator with all formulas from Excel
- Disbursement Calculator
- Payment Tracking Calculator
- Payment Schedule Template (13 milestones)

### Phase 4: Customer Management ✅
- Customer detail page with tabs
- Personal info, Property, Finance details
- Payment schedule management
- Document generation and storage
- File upload with preview/download

### Phase 5: Communication (MOCKED) ✅
- Welcome email generation
- Price breakup PDF generation
- Communication logging

## Prioritized Backlog

### P0 - High Priority
- None (core features complete)

### P1 - Medium Priority
- [ ] Configure SendGrid API for real email delivery
- [ ] Configure Twilio API for WhatsApp messages
- [ ] Unit pricing database with floor-wise rates
- [ ] Bulk import units from Excel

### P2 - Lower Priority
- [ ] Google Forms webhook integration
- [ ] Activity logs and audit trail
- [ ] Template editor for PDF layouts
- [ ] Multi-project branding support
- [ ] Reports and analytics enhancements
- [ ] Export to Excel functionality
- [ ] Automated payment reminders

## Known Limitations
1. Email and WhatsApp integrations are **MOCKED** - require API keys for production
2. Unit pricing is not pre-populated - must be entered manually or via bulk import
3. PDF generation uses HTML rendering - requires browser print for actual PDF

## Files of Reference
- `/app/backend/server.py` - Main backend with all APIs
- `/app/frontend/src/pages/LeadsPage.js` - Lead management
- `/app/frontend/src/pages/BookingFormPage.js` - Public booking form
- `/app/frontend/src/pages/CalculatorPage.js` - Price calculators
- `/app/frontend/src/pages/CustomerDetailPage.js` - Customer profile
