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
- Form captures: Applicant details, Property details (Project, Tower, Unit, BHK, Floor, Areas, Rate), Payment info
- Auto-creates "Pending Approval" customer entry with calculated pricing
- Admin can view, edit, approve, or reject leads
- Stage dropdown for workflow management

### Module 2: Customer Profile ✅ COMPLETED
- Detailed customer profiles with personal details
- Property details with editable pricing fields
- Co-applicant information
- Finance details (Self/Loan/Mixed)
- Document uploads and checklist
- **Edit functionality** for all key fields

### Module 3: Price Breakup Calculator ✅ COMPLETED
- **Formula**: (Rate × Saleable Area) + Floor Rise + Club House + Parking + Labour Cess (0.70%) + GST (5%)
- **Floor Rise**: ₹50/sqft per floor (editable)
- Club House toggle (₹2L)
- Additional Parking (₹3L each)
- UDS calculation (Saleable Area × 0.495046)
- **Calculator tab in Customer Profile**
- "Recalculate & Save Price" button

### Module 4: Payment Plan ✅ COMPLETED
- 13-milestone payment schedule template
- Auto-generate schedule based on total price
- Track payment status (Pending/Paid/Partial/Overdue)
- Disbursement calculator (30%, 50%, 70% quick buttons)
- Payment tracking with percentages and progress bar

### Module 5: Document Generation ✅ COMPLETED
- HTML templates for Sales Agreement, Allotment Letter, Disbursement Letter
- PDF generation for Price Breakup
- Pink-themed welcome email template
- Preview and download functionality
- Documents stored in customer's Documents tab

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

### Module 11: User Roles ✅ COMPLETED
- Admin, Manager, Accounts, Sales, Support roles
- Role-based access control implemented
- JWT authentication

## Technical Architecture

### Backend (FastAPI)
- **Server**: `/app/backend/server.py`
- **Database**: MongoDB
- **Authentication**: JWT with bcrypt password hashing

### Frontend (React)
- **Framework**: React with React Router
- **UI Components**: Shadcn/UI
- **Styling**: TailwindCSS

### Key API Endpoints
- `POST /api/auth/login` - User login
- `POST /api/public/booking-form` - Public booking submission (no auth)
- `GET/PUT /api/leads/pending` - Lead management
- `PUT /api/customers/{id}` - Update customer (supports edit)
- `POST /api/calculator/price` - Price calculation with floor rise
- `POST /api/communication/send-welcome-email/{id}` - Send welcome email (MOCKED)

## Test Credentials
- **Email**: admin@rrlbuilders.com
- **Password**: admin123

## Recent Fixes (March 15, 2026)
1. ✅ Customer data from booking form now includes all fields (BHK, Floor, Areas, Rate, etc.)
2. ✅ Edit customer functionality fixed - all Property & Pricing fields editable
3. ✅ Booking form accessible at `/booking-form` - shows live price calculation preview
4. ✅ Calculator added as tab in customer profile (not just standalone page)
5. ✅ Labour Cess (0.70%) prominently displayed in all calculators
6. ✅ Floor-based pricing editable - Floor rise ₹50/sqft per floor

## Prioritized Backlog

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

## Files of Reference
- `/app/backend/server.py` - Main backend with all APIs
- `/app/frontend/src/pages/BookingFormPage.js` - Public booking form with live calculator
- `/app/frontend/src/pages/CustomerDetailPage.js` - Customer profile with Calculator tab and Edit mode
- `/app/frontend/src/pages/CalculatorPage.js` - Standalone price calculators
- `/app/frontend/src/pages/LeadsPage.js` - Lead management
