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
- Co-applicant information (expanded with profession, nationality)
- Finance details (Self/Loan/Mixed)
- Document uploads and checklist
- **Edit functionality** for all key fields
- **Delete functionality** with confirmation dialog
- **Agreement Filter** in customer list:
  - Upcoming Due (Next 5 Days)
  - Pending Agreement
  - Agreement Signing Due

### Module 3: Price Breakup Calculator ✅ COMPLETED (Updated)
- **Formula**: (Rate/sqft × Saleable Area) + Floor Rise + Club House + Parking + Labour Cess (0.70%) + GST (5%)
- **Floor Rise**: Now a **manual input** field (₹/sqft) - user enters the cost per sqft
- Club House toggle (₹2L)
- Additional Parking (₹3L each)
- UDS calculation (Saleable Area × 0.495046)
- **Calculator tab in Customer Profile**: 
  - Editable with Edit/Cancel/Save buttons
  - **Real-time Live Price Preview** (green box) shows instant calculation as values change
  - Auto-saves to customer profile when Save is clicked
- **Variable Disbursement Calculator**: Custom percentage input (30%, 50%, 70%, 100% quick buttons)
- **Live Price Recalculation**: Price updates automatically in edit mode as values change

### Module 4: Payment Plan ✅ COMPLETED (Enhanced)
- 13-milestone payment schedule template
- Auto-generate schedule based on total price
- Track payment status (Pending/Paid/Partial/Overdue)
- Disbursement calculator (30%, 50%, 70% quick buttons)
- Payment tracking with percentages and progress bar
- **AUTO-SYNC Payment Tracking** (NEW - March 15, 2026):
  - When payment status changes → customer's total_received auto-updates
  - Balance amount recalculates automatically (total_price - total_received)
  - Payment percentages update in real-time
  - "Paid" items count as 100%, "Partial" items count as 50%
- **Payment Summary Section**: Shows Total Value, Total Received, Balance Pending, Progress indicator (X of Y installments paid)
- **Payment Schedule PDF Generation** (NEW - March 17, 2026):
  - Generate printable payment schedule PDF with black and gold theme
  - Shows all milestones with amounts, due dates, status, and cumulative totals

### Module 5: Document Generation ✅ COMPLETED
- HTML templates for Sales Agreement, Allotment Letter, Disbursement Letter
- PDF generation for Price Breakup
- Pink-themed welcome email template
- Preview and download functionality
- **Delete documents** with confirmation prompt
- Documents stored in customer's Documents tab

### Module 6: Agreement Management ✅ COMPLETED
- Agreement status tracking (Draft/Sent/Signed/Completed)
- Document storage in customer profile

### Module 7: Email Automation ✅ COMPLETED
- SendGrid integration configured and working
- Welcome email with HTML template
- General email notifications for payment reminders, document sharing
- **Email attachments**: Select from available/generated documents or upload from local disk
- Communication logs stored in database
- **From Email**: crm@rrlbuildersanddevelopers.com
- **From Name**: RRL Group

### Module 8: WhatsApp Reminders 🔶 MOCKED
- Twilio integration prepared (MOCKED - no API key)
- Communication logs stored in database

### Module 9: Document Checklist ✅ COMPLETED
- Checklist for each customer (KYC, PAN, Aadhaar, Agreement, Bank docs, Photo, Address proof)
- Toggle checkboxes to track received documents

### Module 10: Dashboard ✅ COMPLETED (Enhanced March 17, 2026)
- KPIs: Total Customers, Pending Agreements, Due This Week, Overdue Payments
- **Revenue & Pending Payments Cards** (NEW):
  - Total Revenue Collected with percentage
  - Total Pending Payments with percentage and progress bar
- Payment Status Distribution chart
- **Export CRM Data Section** (NEW):
  - Customers CSV export
  - Customers Excel export (with black/gold themed headers)
  - Payments CSV export
- **Payment Due Date Countdown**: Shows customers with payment due dates in next 5 days
  - Rule: Due date = Booking date + 10 days
  - Countdown badges: "Due Today!", "Due Tomorrow", "X days left"
  - Clickable cards navigate to customer profile

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
- **Styling**: TailwindCSS (Pink gradient theme)

### Key API Endpoints
- `POST /api/auth/login` - User login
- `POST /api/public/booking-form` - Public booking submission (no auth)
- `POST /api/public/upload-document/{customer_id}` - Public document upload
- `GET/PUT /api/leads/pending` - Lead management
- `GET /api/customers` - List customers
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer (requires admin/manager role)
- `POST /api/calculator/price` - Price calculation with floor rise

## Test Credentials
- **Email**: admin@rrlbuilders.com
- **Password**: admin123

## Recent Updates (March 17, 2026 - Session 4 continued part 2)

### Sales Agreement & Unified Email Composer
1. ✅ **Sales Agreement Template** - Created comprehensive HTML template with:
   - All customer details mapped (name, address, Aadhaar, PAN, phone)
   - Property details (project, tower, unit, area, UDS, parking)
   - Sale consideration breakdown (base price, club house, parking, labour cess, GST, total)
   - Payment schedule table with milestones and amounts
   - Bank details for payment
   - Terms & conditions (17 clauses)
   - Signature section
   - Black and gold theme with Roboto font
   
2. ✅ **Unified Email Composer** - New dialog with:
   - Editable Subject line
   - Editable Email Body text area
   - Auto-generated attachments shown as badges
   - 3 preview tabs: Email Preview, Document Attachment, Price Breakup
   - SendGrid status indicator
   - Cancel and Send Email buttons
   
3. ✅ **Three Email Buttons** on customer profile:
   - **Welcome Email** - Sends welcome message with Price Breakup PDF
   - **Sales Agreement** - Sends sale agreement draft with both Sales Agreement and Price Breakup PDFs
   - **Allotment Letter** - Sends allotment letter with Allotment Letter PDF
   
4. ✅ **Email Subject for Sales Agreement**: "SALE AGREEMENT DRAFT AND PRICE BREAK UP - {flat_number}"

5. ✅ **All emails include signature**:
   ```
   Pavitra S G
   CRM MANAGER
   P: 9606579135
   E: crm@rrlbuildersanddevelopers.com
   A: 4TH Floor, RRL Tower, Sompura gate, Sarjapura Bengaluru - 562125
   www.rrlbuildersanddevelopers.com
   ```

## Recent Updates (March 17, 2026 - Session 4 continued)

### Welcome Email Enhancements
1. ✅ **Fixed Residence Details formatting** - Added proper spacing with table-style layout for label/value pairs
2. ✅ **Email Preview with Price Breakup Attachment** - New workflow:
   - Click "Send Welcome Email" → Opens preview dialog
   - Shows email content in "Email Content" tab
   - Shows Price Breakup PDF preview in "Price Breakup (Attachment)" tab
   - "Cancel" or "Send Email" buttons
   - SendGrid status indicator
3. ✅ **Email Signature Added** to all emails:
   ```
   Pavitra S G
   CRM MANAGER
   P: 9606579135
   E: crm@rrlbuildersanddevelopers.com
   A: 4TH Floor, RRL Tower, Sompura gate, Sarjapura Bengaluru - 562125
   www.rrlbuildersanddevelopers.com
   ```
4. ✅ **General email template** updated to black & gold theme with signature

## Recent Updates (March 17, 2026 - Session 4)

### Dashboard & Export Enhancements
1. ✅ **Replaced Monthly Revenue Trend** with Revenue + Pending Payments side-by-side cards
   - Total Revenue Collected with percentage
   - Total Pending Payments with percentage and progress bar
2. ✅ **Export CRM Data** section on dashboard:
   - Customers CSV export
   - Customers Excel export (with black/gold themed headers using openpyxl)
   - Payments CSV export
3. ✅ **Payment Schedule PDF** - New endpoint to generate payment schedule PDF with black/gold theme

### PDF & Email Theme Update (Black & Gold)
4. ✅ **Updated all PDF/Email templates** to use:
   - **Font**: Roboto (Google Fonts)
   - **Primary Color**: #D4AF37 (Gold)
   - **Secondary Color**: #1A1A1A (Black)
   - **Logo**: RRL in black box with gold text
5. ✅ **Allotment Letter** - Removed yellow highlights, now uses gold text highlights
6. ✅ **Price Breakup PDF** - Updated to black/gold theme
7. ✅ **Welcome Email** - Updated to black/gold professional design

## Recent Updates (March 15, 2026 - Session 3)

### Payment Schedule Auto-Sync with Payment Tracking
1. ✅ **Connected payment schedule with payment tracking** - When payment status changes:
   - `total_received` auto-calculates from all "paid" items (100%) + "partial" items (50%)
   - `balance_amount` = total_price - total_received
   - `payment_received_percentage` and `payment_pending_percentage` auto-update
   - Customer record updated in database automatically
2. ✅ **Payment Summary UI** - Added summary section below payment schedule showing:
   - Total Value, Total Received (with %), Balance Pending (with %), Progress bar with "X of Y installments paid"
3. ✅ **Real-time UI Updates** - No page refresh needed; frontend updates immediately from API response
4. ✅ **Toast notifications** - Shows "Payment marked as paid - Received: ₹X" confirmation

## Recent Updates (March 15, 2026 - Session 2)

### Booking Form Enhancements
1. ✅ Added **Profession** dropdown field (Salaried, Self-Employed, Business Owner, etc.)
2. ✅ Added **Document Upload** section (PAN Card, Aadhaar Card, Passport for NRI/OCI)
3. ✅ Expanded **Co-Applicant** section (Father/Spouse Name, Address, Profession, Nationality)
4. ✅ Changed **Tower** from dropdown to text input
5. ✅ **Removed carpet_area** field as requested
6. ✅ Added **Floor Rise** as manual input field (₹/sqft)
7. ✅ Added **Terms and Conditions** section with checkbox validation

### Delete Functionality
1. ✅ Added delete button to Customers page
2. ✅ Implemented AlertDialog confirmation with detailed warning
3. ✅ DELETE /api/customers/{id} cleans up all related data (payment schedules, documents, etc.)

### Bug Fixes
1. ✅ Fixed customer ID generation race condition (now uses atomic counter)

## Prioritized Backlog

### P1 - Medium Priority
- [ ] Configure Twilio API for WhatsApp messages (requires API key)
- [ ] Sales Agreement PDF template (when user provides template)

### P2 - Lower Priority
- [ ] Sales Agreement PDF template
- [ ] Google Forms webhook integration
- [ ] Activity logs and audit trail
- [ ] Template editor for PDF layouts
- [ ] Multi-project branding support

## Files of Reference
- `/app/backend/server.py` - Main backend with all APIs
- `/app/frontend/src/pages/BookingFormPage.js` - Public booking form with document uploads
- `/app/frontend/src/pages/CustomerDetailPage.js` - Customer profile with Calculator tab
- `/app/frontend/src/pages/CustomersPage.js` - Customer list with delete functionality
- `/app/frontend/src/pages/LeadsPage.js` - Lead management
