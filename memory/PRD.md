# RRL Builders POST-SALES Internal CRM - Product Requirements Document

## Original Problem Statement
Build a web-based POST-SALES Internal CRM for a real estate developer called "RRL Builders". The CRM must manage the entire post-booking lifecycle of a real estate customer, replacing Excel sheets and automating processes.

## Core Requirements

### 1. Lead/Booking Intake
- Public-facing form to capture customer, co-applicant, and property data
- Document uploads with camera capture functionality ✅

### 2. Customer Profile
- Detailed, editable customer profiles
- Tabs: Personal Details, Price Calculator, Payment Schedule, Documents, Communication History

### 3. Price Breakup Calculator
- Automated, live calculator for total property price ✅

### 4. Payment Plan
- Track payment schedules ✅

### 5. Document Generation
- Editable templates: Allotment Letters, Sales Agreements, Price Breakup
- Downloadable as PDFs ✅

### 6. Deletion Functionality
- Admin can delete leads, customers, documents with confirmation ✅

### 7. User Roles & Security
- Role-based access control (Admin, Manager, Sales) ✅

### 8. Automated Communications
- Email integration (SendGrid) ✅
- WhatsApp integration (Twilio) - Placeholder only

### 9. Dashboard
- KPIs and countdowns for important deadlines ✅
- Data export functionality ✅

---

## Technical Stack
- **Frontend:** React, TailwindCSS, Shadcn UI
- **Backend:** FastAPI, Python
- **Database:** MongoDB
- **Authentication:** JWT with RBAC
- **PDF Generation:** WeasyPrint
- **Email:** SendGrid
- **Excel Handling:** openpyxl

---

## What's Been Implemented

### March 18, 2026
- ✅ Removed "Carpet Area" from all PDFs, emails, customer details, documents, and forms
- ✅ Camera upload feature for booking form documents

### Previously Completed
- ✅ JWT authentication with role-based access
- ✅ Multi-step public booking form with file upload
- ✅ Lead management system
- ✅ Customer profile page with tabs
- ✅ Dynamic price calculator
- ✅ PDF document generation (Allotment Letter, Sales Agreement, Price Breakup)
- ✅ SendGrid email integration with unified composer
- ✅ Dashboard with key stats and data export
- ✅ Black and gold theme throughout

---

## Prioritized Backlog

### P0 - Critical
- None currently

### P1 - High Priority
1. **Data Import from Excel** - Import real customer data from `/app/customer_data.xlsm`
2. **Test Application with Real Data** - Verify all features after import

### P2 - Medium Priority
1. WhatsApp integration via Twilio (currently placeholder)
2. Document checklist feature for KYC tracking
3. Enhanced dashboard with more charts/analytics
4. Activity logs/audit trail
5. **Code Refactoring:**
   - Backend: Break down `server.py` (>4500 lines) into modular structure
   - Frontend: Decompose `CustomerDetailPage.js` (>2200 lines)

### P3 - Low Priority
1. User-uploadable email attachments
2. PDF template editor UI

---

## Key Files
- `/app/backend/server.py` - Monolithic backend (needs refactoring)
- `/app/frontend/src/pages/CustomerDetailPage.js` - Large component (needs refactoring)
- `/app/frontend/src/pages/BookingFormPage.js` - Booking form with camera feature
- `/app/customer_data.xlsm` - User's Excel data for import

---

## Test Credentials
- **Email:** admin@rrlbuilders.com
- **Password:** admin123

---

## Known Issues / Technical Debt
1. `server.py` is >4500 lines - urgent refactoring needed
2. `CustomerDetailPage.js` is >2200 lines - needs decomposition
3. WhatsApp integration is placeholder (`whatsapp://` link)
4. No pytest files for backend logic
