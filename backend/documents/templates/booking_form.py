"""Booking Form Preview document template."""
from datetime import datetime
from documents.templates.common import (
    format_inr, calculate_age, get_salutation, get_logo_img_tag,
    COMPANY_NAME, tower_id
)

def generate_booking_form_preview_html(customer: dict) -> str:
    """Generate a PDF preview of the submitted booking form with all customer data"""
    
    # Format dates
    booking_date = customer.get('booking_date', '')
    if booking_date and '-' in str(booking_date):
        try:
            dt = datetime.strptime(str(booking_date), "%Y-%m-%d")
            booking_date = dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            pass
    
    dob = customer.get('date_of_birth', '')
    if dob and '-' in str(dob):
        try:
            dt = datetime.strptime(str(dob), "%Y-%m-%d")
            dob = dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            pass
    
    # Format amounts
    def format_currency(amount):
        try:
            return f"₹ {float(amount or 0):,.2f}"
        except (ValueError, TypeError):
            return "₹ 0.00"
    
    # Get gender display
    gender = customer.get('gender', '')
    if gender == 'male':
        gender_display = 'Male (S/o)'
    elif gender == 'female':
        gender_display = 'Female (D/o)'
    elif gender == 'spouse':
        gender_display = 'Spouse (W/o)'
    else:
        gender_display = gender or '-'
    
    # Finance type display
    finance_type = customer.get('finance_type', 'self')
    finance_display = {
        'self': 'Self Funded',
        'loan': 'Bank Loan',
        'mixed': 'Mixed (Self + Loan)'
    }.get(finance_type, finance_type)
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            
            body {{
                font-family: 'Roboto', sans-serif;
                background: #fff;
                padding: 20px 30px;
                margin: 0;
                color: #1A1A1A;
                font-size: 11px;
                line-height: 1.4;
            }}
            
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding-bottom: 15px;
                border-bottom: 3px solid #D4AF37;
                margin-bottom: 20px;
            }}
            
            .logo-section {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .logo {{
                width: 100px;
            }}
            
            .logo img {{
                width: 100px;
                height: auto;
            }}
            
            .company-name {{
                font-size: 16px;
                font-weight: 700;
                color: #1A1A1A;
            }}
            
            .company-tagline {{
                font-size: 9px;
                color: #D4AF37;
                font-style: italic;
            }}
            
            .document-title {{
                font-size: 18px;
                font-weight: 700;
                color: #1A1A1A;
                text-align: right;
            }}
            
            .document-subtitle {{
                font-size: 10px;
                color: #666;
                text-align: right;
            }}
            
            .section {{
                margin-bottom: 15px;
                background: #fafafa;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #eee;
            }}
            
            .section-title {{
                font-size: 12px;
                font-weight: 700;
                color: #1A1A1A;
                border-bottom: 2px solid #D4AF37;
                padding-bottom: 6px;
                margin-bottom: 10px;
            }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 8px;
            }}
            
            .info-grid-2 {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 8px;
            }}
            
            .info-item {{
                padding: 4px 0;
            }}
            
            .info-label {{
                color: #666;
                font-size: 9px;
                display: block;
                margin-bottom: 2px;
            }}
            
            .info-value {{
                font-weight: 500;
                color: #1A1A1A;
                font-size: 11px;
            }}
            
            .highlight {{
                color: #D4AF37;
                font-weight: 600;
            }}
            
            .price-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 8px;
            }}
            
            .price-table th, .price-table td {{
                padding: 8px;
                text-align: left;
                font-size: 10px;
            }}
            
            .price-table th {{
                background: #1A1A1A;
                color: #D4AF37;
                font-weight: 500;
            }}
            
            .price-table td {{
                border-bottom: 1px solid #e0e0e0;
            }}
            
            .price-table .total-row {{
                background: #1A1A1A !important;
                color: #D4AF37;
                font-weight: 700;
            }}
            
            .price-table .amount {{
                text-align: right;
            }}
            
            .footer {{
                margin-top: 20px;
                padding-top: 10px;
                border-top: 2px solid #D4AF37;
                font-size: 9px;
                color: #666;
            }}
            
            .signature-section {{
                margin-top: 30px;
                display: flex;
                justify-content: space-between;
            }}
            
            .signature-box {{
                text-align: center;
                width: 200px;
            }}
            
            .signature-line {{
                border-top: 1px solid #333;
                margin-top: 40px;
                padding-top: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo-section">
                <div class="logo">{get_logo_img_tag(100)}</div>
                <div>
                    <div class="company-name">{COMPANY_NAME}</div>
                    <div class="company-tagline">Beyond homes. A lifestyle</div>
                </div>
            </div>
            <div>
                <div class="document-title">Booking Form Preview</div>
                <div class="document-subtitle">Customer ID: {customer.get('customer_id', '-')}</div>
            </div>
        </div>
        
        <!-- Primary Applicant Details -->
        <div class="section">
            <div class="section-title">Primary Applicant Details</div>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Full Name</span>
                    <span class="info-value">{customer.get('name', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Father's/Husband's Name</span>
                    <span class="info-value">{get_salutation(customer.get('gender'))} {customer.get('father_name', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Gender</span>
                    <span class="info-value">{gender_display}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Date of Birth</span>
                    <span class="info-value">{dob or '-'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Age</span>
                    <span class="info-value">{calculate_age(customer.get('date_of_birth')) or '-'} {('years' if calculate_age(customer.get('date_of_birth')) else '')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Phone Number</span>
                    <span class="info-value">{customer.get('phone', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Email Address</span>
                    <span class="info-value">{customer.get('email', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">PAN Number</span>
                    <span class="info-value">{customer.get('pan_number', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Aadhaar Number</span>
                    <span class="info-value">{customer.get('aadhar_number', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Nationality</span>
                    <span class="info-value">{customer.get('nationality', 'Indian')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Company</span>
                    <span class="info-value">{customer.get('company', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Designation</span>
                    <span class="info-value">{customer.get('designation', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Profession</span>
                    <span class="info-value">{customer.get('profession', '-')}</span>
                </div>
            </div>
            <div class="info-grid-2" style="margin-top: 8px;">
                <div class="info-item">
                    <span class="info-label">Permanent Address</span>
                    <span class="info-value">{customer.get('address', '-')}</span>
                </div>
            </div>
        </div>
        
        <!-- Co-Applicant Details (if exists) -->
        {f"""
        <div class="section">
            <div class="section-title">Co-Applicant Details</div>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Full Name</span>
                    <span class="info-value">{customer.get('co_applicant_name', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Father's/Husband's Name</span>
                    <span class="info-value">{get_salutation(customer.get('gender', 'male'))} {customer.get('co_applicant_father_name', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Date of Birth</span>
                    <span class="info-value">{customer.get('co_applicant_date_of_birth', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Age</span>
                    <span class="info-value">{calculate_age(customer.get('co_applicant_date_of_birth')) or '-'} {('years' if calculate_age(customer.get('co_applicant_date_of_birth')) else '')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Phone Number</span>
                    <span class="info-value">{customer.get('co_applicant_phone', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Email Address</span>
                    <span class="info-value">{customer.get('co_applicant_email', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">PAN Number</span>
                    <span class="info-value">{customer.get('co_applicant_pan', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Aadhaar Number</span>
                    <span class="info-value">{customer.get('co_applicant_aadhar', '-')}</span>
                </div>
            </div>
            <div class="info-grid-2" style="margin-top: 8px;">
                <div class="info-item">
                    <span class="info-label">Address</span>
                    <span class="info-value">{customer.get('co_applicant_address', '-')}</span>
                </div>
            </div>
        </div>
        """ if customer.get('co_applicant_name') else ''}
        
        <!-- Property Details -->
        <div class="section">
            <div class="section-title">Property Details</div>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Project</span>
                    <span class="info-value highlight">{customer.get('project', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Tower</span>
                    <span class="info-value">{tower_id(customer.get('tower'))}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Unit Number</span>
                    <span class="info-value highlight">{customer.get('unit_number', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">BHK Type</span>
                    <span class="info-value">{customer.get('bhk_type', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Floor</span>
                    <span class="info-value">{customer.get('floor', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Saleable Area</span>
                    <span class="info-value">{customer.get('saleable_area', 0)} sq.ft</span>
                </div>
                <div class="info-item">
                    <span class="info-label">UDS</span>
                    <span class="info-value">{customer.get('uds', '-')} sq.ft</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Parking</span>
                    <span class="info-value">{customer.get('parking', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Additional Parking</span>
                    <span class="info-value">{customer.get('additional_parking', 0)}</span>
                </div>
            </div>
        </div>
        
        <!-- Price Details -->
        <div class="section">
            <div class="section-title">Price Details</div>
            <table class="price-table">
                <tr>
                    <th>Description</th>
                    <th class="amount">Amount</th>
                </tr>
                <tr>
                    <td>Rate per sq.ft</td>
                    <td class="amount">{format_currency(customer.get('rate_per_sqft', 0))}</td>
                </tr>
                <tr>
                    <td>Base Price ({customer.get('saleable_area', 0)} sq.ft × {format_currency(customer.get('rate_per_sqft', 0))})</td>
                    <td class="amount">{format_currency(customer.get('base_price', 0))}</td>
                </tr>
                <tr>
                    <td>Floor Rise Total</td>
                    <td class="amount">{format_currency(customer.get('floor_rise_total', 0))}</td>
                </tr>
                <tr>
                    <td>Club House Charges</td>
                    <td class="amount">{format_currency(customer.get('club_house_charges', 200000))}</td>
                </tr>
                <tr>
                    <td>Additional Charges</td>
                    <td class="amount">{format_currency(customer.get('additional_charges', 0))}</td>
                </tr>
                <tr>
                    <td>Labour Cess (0.70%)</td>
                    <td class="amount">{format_currency(customer.get('labour_cess', 0))}</td>
                </tr>
                <tr>
                    <td>GST (5%)</td>
                    <td class="amount">{format_currency(customer.get('gst_amount', 0))}</td>
                </tr>
                <tr class="total-row">
                    <td><strong>Total Flat Value</strong></td>
                    <td class="amount"><strong>{format_currency(customer.get('total_price', 0))}</strong></td>
                </tr>
            </table>
        </div>
        
        <!-- Booking & Finance Details -->
        <div class="section">
            <div class="section-title">Booking & Finance Details</div>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Booking Date</span>
                    <span class="info-value">{booking_date or '-'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Booking Amount</span>
                    <span class="info-value highlight">{format_currency(customer.get('booking_amount', 0))}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Finance Type</span>
                    <span class="info-value">{finance_display}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Finance Bank</span>
                    <span class="info-value">{customer.get('finance_bank', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Transaction Reference</span>
                    <span class="info-value">{customer.get('transaction_details', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Transaction Bank</span>
                    <span class="info-value">{customer.get('transaction_bank', '-')}</span>
                </div>
            </div>
            {f'<div class="info-item" style="margin-top: 8px;"><span class="info-label">Remarks</span><span class="info-value">{customer.get("remarks", "-")}</span></div>' if customer.get('remarks') else ''}
        </div>
        
        <!-- Signature Section -->
        <div class="signature-section">
            <div class="signature-box">
                <div class="signature-line">Customer Signature</div>
            </div>
            <div class="signature-box">
                <div class="signature-line">For {COMPANY_NAME}</div>
            </div>
        </div>
        
        <div class="footer">
            <p>This is a system-generated booking form preview. Please verify all details are correct.</p>
            <p><strong>{COMPANY_NAME}</strong> | www.rrlbuilders.in</p>
        </div>
    </body>
    </html>
    '''
    return html


