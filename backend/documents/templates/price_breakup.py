"""Price Breakup document template."""
from datetime import datetime
from documents.templates.common import format_inr, get_logo_img_tag, COMPANY_NAME, format_customer_names

def generate_price_breakup_html(customer: dict) -> str:
    """Generate HTML for Price Breakup PDF with black and gold theme"""
    
    # Format currency in Indian format
    def format_inr(amount):
        """Format amount in Indian Rupee style without L/Cr abbreviations"""
        amount = float(amount) if amount else 0
        int_part = int(amount)
        decimal_part = f"{amount:.2f}".split('.')[1]
        
        # Format with Indian comma system
        s = str(int_part)
        if len(s) > 3:
            result = s[-3:]
            s = s[:-3]
            while s:
                result = s[-2:] + ',' + result
                s = s[:-2]
        else:
            result = s
        
        return f"₹{result}.{decimal_part}"
    
    booking_date = customer.get('booking_date', datetime.now().strftime("%d/%m/%Y"))
    if booking_date and '-' in booking_date:
        try:
            dt = datetime.strptime(booking_date, "%Y-%m-%d")
            booking_date = dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            pass

    interest_amount = customer.get('interest_amount', 0) or 0
    interest_row = (
        f'<tr><td>Interest Amount</td><td class="amount">{format_inr(interest_amount)}</td></tr>'
        if interest_amount else ''
    )

    # BESCOM = rate × saleable area; shown in subtotal (before GST + labour cess)
    bescom_rate = float(customer.get('bescom_rate', 0) or 0)
    saleable_area = float(customer.get('saleable_area', 0) or 0)
    bescom_amount = round(bescom_rate * saleable_area)
    bescom_row = (
        f'<tr><td>BESCOM Charges (&#8377;{bescom_rate:g}/sq.ft &times; {saleable_area:g})</td>'
        f'<td class="amount">{format_inr(bescom_amount)}</td></tr>'
        if bescom_amount else ''
    )

    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            body {{
                font-family: 'Roboto', sans-serif;
                background: #f5f5f5;
                padding: 30px;
                color: #1A1A1A;
            }}
            
            .container {{
                background: #fff;
                border: 2px solid #D4AF37;
                border-radius: 8px;
                padding: 35px;
                max-width: 800px;
                margin: 0 auto;
            }}
            
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 3px solid #D4AF37;
                padding-bottom: 20px;
                margin-bottom: 25px;
            }}
            
            .logo-section {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .logo {{
                width: 100px;
            }}
            
            .logo img {{
                width: 100px;
                height: auto;
            }}
            
            .company-name {{
                font-size: 20px;
                font-weight: 700;
                color: #1A1A1A;
            }}
            
            .company-tagline {{
                font-size: 11px;
                color: #666;
            }}
            
            .document-title {{
                background: #1A1A1A;
                color: #D4AF37;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 13px;
                text-transform: uppercase;
            }}
            
            .section {{
                margin-bottom: 20px;
            }}
            
            .section-title {{
                font-size: 14px;
                color: #1A1A1A;
                font-weight: 600;
                margin-bottom: 10px;
                padding-bottom: 5px;
                border-bottom: 2px solid #D4AF37;
            }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }}
            
            .info-item {{
                display: flex;
                justify-content: space-between;
                padding: 8px 10px;
                background: #fafafa;
                border-left: 3px solid #D4AF37;
            }}
            
            .info-label {{
                color: #666;
                font-size: 12px;
            }}
            
            .info-value {{
                color: #1A1A1A;
                font-weight: 500;
                font-size: 12px;
            }}
            
            .price-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            
            .price-table th, .price-table td {{
                padding: 12px;
                text-align: left;
                font-size: 12px;
            }}
            
            .price-table th {{
                background: #1A1A1A;
                color: #D4AF37;
                font-weight: 500;
            }}
            
            .price-table td {{
                border-bottom: 1px solid #e0e0e0;
            }}
            
            .price-table tr:nth-child(even) {{
                background: #fafafa;
            }}
            
            .price-table .total-row {{
                background: #1A1A1A !important;
                color: #D4AF37;
                font-weight: 700;
                font-size: 14px;
            }}
            
            .price-table .amount {{
                text-align: right;
                font-family: 'Roboto Mono', monospace;
            }}
            
            .footer {{
                margin-top: 25px;
                padding-top: 15px;
                border-top: 2px solid #D4AF37;
                font-size: 11px;
                color: #666;
            }}
            
            .footer-note {{
                margin-bottom: 8px;
            }}
            
            .footer-company {{
                margin-top: 15px;
                text-align: center;
                color: #1A1A1A;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo-section">
                    <div class="logo">{get_logo_img_tag(100)}</div>
                    <div>
                        <div class="company-name">{COMPANY_NAME}</div>
                        <div class="company-tagline">Beyond homes. A lifestyle</div>
                    </div>
                </div>
                <div class="document-title">Price Break-Up</div>
            </div>
            
            <div class="section">
                <div class="section-title">Customer Details</div>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Name:</span>
                        <span class="info-value">{customer.get('name', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Contact:</span>
                        <span class="info-value">{customer.get('phone', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Email:</span>
                        <span class="info-value">{customer.get('email', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Booking Date:</span>
                        <span class="info-value">{booking_date}</span>
                    </div>
                </div>
                {'<div class="section-title" style="margin-top: 15px;">Co-Applicant Details</div><div class="info-grid"><div class="info-item"><span class="info-label">Name:</span><span class="info-value">' + customer.get('co_applicant_name', '-') + '</span></div><div class="info-item"><span class="info-label">Contact:</span><span class="info-value">' + (customer.get('co_applicant_phone', '') or '-') + '</span></div><div class="info-item"><span class="info-label">Email:</span><span class="info-value">' + (customer.get('co_applicant_email', '') or '-') + '</span></div></div>' if customer.get('co_applicant_name') else ''}
            </div>
            
            <div class="section">
                <div class="section-title">Unit Details</div>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Unit No.:</span>
                        <span class="info-value">{customer.get('unit_number', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Tower:</span>
                        <span class="info-value">{customer.get('tower', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Unit Type:</span>
                        <span class="info-value">{customer.get('bhk_type', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Floor:</span>
                        <span class="info-value">{customer.get('floor', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Saleable Area:</span>
                        <span class="info-value">{customer.get('saleable_area', 0)} sq.ft</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">UDS:</span>
                        <span class="info-value">{customer.get('uds', 0)}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Rate/Sq.ft:</span>
                        <span class="info-value">₹{customer.get('rate_per_sqft', 0):,.0f}</span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Price Breakdown</div>
                <table class="price-table">
                    <thead>
                        <tr>
                            <th>Particulars</th>
                            <th class="amount">Amount (₹)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Base Price ({customer.get('saleable_area', 0)} sq.ft × ₹{customer.get('rate_per_sqft', 0):,.0f})</td>
                            <td class="amount">{format_inr(customer.get('base_price', 0))}</td>
                        </tr>
                        <tr>
                            <td>Club House, Infrastructure & One Covered Car Parking</td>
                            <td class="amount">{format_inr(customer.get('club_house_charges', 200000))}</td>
                        </tr>
                        <tr>
                            <td>Additional Car Parking ({customer.get('additional_parking', 0)} nos.)</td>
                            <td class="amount">{format_inr(customer.get('additional_parking_charges', 0))}</td>
                        </tr>
                        {bescom_row}
                        <tr>
                            <td>Labour Cess (0.70%)</td>
                            <td class="amount">{format_inr(customer.get('labour_cess', 0))}</td>
                        </tr>
                        <tr>
                            <td>GST (5%)</td>
                            <td class="amount">{format_inr(customer.get('gst_amount', 0))}</td>
                        </tr>
                        {interest_row}
                        <tr class="total-row">
                            <td><strong>GRAND TOTAL</strong></td>
                            <td class="amount"><strong>{format_inr(customer.get('total_price', 0))}</strong></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="footer">
                <p class="footer-note">* Maintenance charges will attract GST as applicable</p>
                <p class="footer-note">* Registration as per government norms</p>
                <p class="footer-company">
                    <strong>{COMPANY_NAME}</strong><br>
                    www.rrlbuildersanddevelopers.com<br>
                    Thank you for choosing RRL Palm Altezze
                </p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html


