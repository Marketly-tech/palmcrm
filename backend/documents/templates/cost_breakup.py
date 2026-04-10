"""Cost Breakup document template."""
from datetime import datetime
from documents.templates.common import format_inr, get_logo_img_tag, COMPANY_NAME

def generate_cost_breakup_html(customer: dict) -> str:
    """Generate HTML for Cost Breakup PDF matching the user-provided template"""
    
    # Format currency in Indian format
    def format_inr(amount):
        """Format amount in Indian Rupee style without decimal places for cleaner look"""
        amount = float(amount) if amount else 0
        int_part = int(amount)
        
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
        
        return result
    
    def number_to_words(num):
        """Convert number to words in Indian format"""
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
                'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        if num == 0:
            return 'Zero'
        
        num = int(num)
        
        if num < 20:
            return ones[num]
        
        if num < 100:
            return tens[num // 10] + ('' if num % 10 == 0 else '-' + ones[num % 10])
        
        if num < 1000:
            return ones[num // 100] + ' Hundred' + ('' if num % 100 == 0 else ' ' + number_to_words(num % 100))
        
        if num < 100000:
            return number_to_words(num // 1000) + ' Thousand' + ('' if num % 1000 == 0 else ' ' + number_to_words(num % 1000))
        
        if num < 10000000:
            return number_to_words(num // 100000) + ' Lakh' + ('' if num % 100000 == 0 else ' ' + number_to_words(num % 100000))
        
        return number_to_words(num // 10000000) + ' Crore' + ('' if num % 10000000 == 0 else ' ' + number_to_words(num % 10000000))
    
    # Get customer details
    name = customer.get('name', '')
    co_applicant_name = customer.get('co_applicant_name', '')
    age = customer.get('age', '')
    co_applicant_age = customer.get('co_applicant_age', '')
    
    # Build customer text
    customer_text_parts = []
    if name:
        if customer.get('gender') == 'female':
            prefix = "Mrs." if customer.get('marital_status') == 'married' else "Ms."
        else:
            prefix = "Mr."
        age_text = f" aged about {age} years" if age else ""
        customer_text_parts.append(f"{prefix} {name}{age_text}")
    
    if co_applicant_name:
        co_age_text = f" aged about {co_applicant_age} years" if co_applicant_age else ""
        co_prefix = "Mrs." if customer.get('co_applicant_gender') == 'female' else "Mr."
        customer_text_parts.append(f"{co_prefix} {co_applicant_name}{co_age_text}")
    
    customer_names = " and ".join(customer_text_parts) if customer_text_parts else "Customer"
    
    # Property details
    flat_no = customer.get('unit_number', '-')
    tower = customer.get('tower', '1')
    saleable_area = customer.get('saleable_area', 0)
    uds = customer.get('uds', 0)
    # Estimate carpet area (approx 62.5% of saleable area)
    carpet_area = round(saleable_area * 0.625, 2) if saleable_area else 0
    
    # Pricing components mapping to cost breakup
    basic_cost = customer.get('base_price', 0)
    bescom = customer.get('infrastructure_charges', 150000)  # Default 1.5L for BESCOM
    car_parking = customer.get('additional_charges', 200000)  # Default 2L for car parking
    amenities = customer.get('club_house_charges', 150000)  # Amenities
    
    # Total - either use stored total or calculate
    total_value = customer.get('total_price', 0)
    if not total_value:
        total_value = basic_cost + bescom + car_parking + amenities
    
    # Get date
    booking_date = customer.get('booking_date', datetime.now().strftime("%Y-%m-%d"))
    if booking_date and '-' in str(booking_date):
        try:
            dt = datetime.strptime(str(booking_date), "%Y-%m-%d")
            date_display = dt.strftime("%d - %m - %Y")
        except (ValueError, TypeError):
            date_display = datetime.now().strftime("%d - %m - %Y")
    else:
        date_display = datetime.now().strftime("%d - %m - %Y")
    
    # Total in words
    total_words = f"Rupees {number_to_words(total_value)} Only"
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            @page {{
                size: A4;
                margin: 25mm 20mm 25mm 20mm;
            }}
            
            body {{
                font-family: 'Roboto', sans-serif;
                font-size: 12px;
                line-height: 1.6;
                color: #1A1A1A;
                background: #fff;
            }}
            
            .container {{
                max-width: 100%;
            }}
            
            .header {{
                text-align: right;
                margin-bottom: 30px;
                padding-bottom: 15px;
                border-bottom: 3px solid #D4AF37;
            }}
            
            .header-title {{
                font-size: 22px;
                font-weight: 700;
                color: #1A1A1A;
                margin-bottom: 5px;
            }}
            
            .header-subtitle {{
                font-size: 16px;
                font-weight: 600;
                color: #D4AF37;
            }}
            
            .customer-info {{
                margin-bottom: 25px;
                text-align: justify;
                font-size: 12px;
            }}
            
            .site-address {{
                margin-bottom: 25px;
            }}
            
            .site-address-title {{
                font-weight: 700;
                margin-bottom: 5px;
                font-size: 12px;
            }}
            
            .site-address-text {{
                font-size: 11px;
                color: #444;
            }}
            
            .price-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 25px 0;
            }}
            
            .price-table th {{
                background: #1A1A1A;
                color: #D4AF37;
                padding: 12px 15px;
                text-align: left;
                font-weight: 600;
                font-size: 13px;
                text-transform: uppercase;
            }}
            
            .price-table th.amount {{
                text-align: right;
            }}
            
            .price-table td {{
                padding: 10px 15px;
                border-bottom: 1px solid #e0e0e0;
                font-size: 12px;
            }}
            
            .price-table td.amount {{
                text-align: right;
                font-family: 'Roboto Mono', monospace;
                font-weight: 500;
            }}
            
            .price-table tr:nth-child(even) {{
                background: #f9f9f9;
            }}
            
            .price-table .total-row {{
                background: #1A1A1A !important;
            }}
            
            .price-table .total-row td {{
                color: #D4AF37;
                font-weight: 700;
                font-size: 14px;
                border-bottom: none;
            }}
            
            .total-words {{
                margin: 25px 0;
                font-size: 12px;
                text-align: justify;
            }}
            
            .total-words strong {{
                color: #D4AF37;
            }}
            
            .thank-you {{
                margin: 25px 0;
                font-size: 12px;
            }}
            
            .date-section {{
                margin-top: 30px;
                font-size: 12px;
            }}
            
            .footer {{
                margin-top: 40px;
                padding-top: 15px;
                border-top: 2px solid #D4AF37;
                text-align: center;
                font-size: 11px;
                color: #666;
            }}
            
            .footer strong {{
                color: #1A1A1A;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="header-title">RRL PALM ALTEZZE</div>
                <div class="header-subtitle">Cost Break Up</div>
            </div>
            
            <div class="customer-info">
                {customer_names} purchased Flat No. {flat_no}, Tower-{tower} measuring Super Builtup Area {saleable_area} Sq.ft. with UDS of {uds:.2f} Sq.ft, Carpet Area of {carpet_area} Sq.ft,
            </div>
            
            <div class="site-address">
                <div class="site-address-title">Site Address:</div>
                <div class="site-address-text">
                    Sy No. 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN - 560087.
                </div>
            </div>
            
            <table class="price-table">
                <thead>
                    <tr>
                        <th>PARTICULARS</th>
                        <th class="amount">AMOUNT</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>BASIC COST</td>
                        <td class="amount">{format_inr(basic_cost)}</td>
                    </tr>
                    <tr>
                        <td>BESCOM</td>
                        <td class="amount">{format_inr(bescom)}</td>
                    </tr>
                    <tr>
                        <td>CAR PARKING</td>
                        <td class="amount">{format_inr(car_parking)}</td>
                    </tr>
                    <tr>
                        <td>AMENITIES</td>
                        <td class="amount">{format_inr(amenities)}</td>
                    </tr>
                    <tr class="total-row">
                        <td><strong>TOTAL</strong></td>
                        <td class="amount"><strong>{format_inr(total_value)}</strong></td>
                    </tr>
                </tbody>
            </table>
            
            <div class="total-words">
                Total Sale Value is <strong>Rs. {format_inr(total_value)} /-</strong> ({total_words}).
            </div>
            
            <div class="thank-you">
                Thanking You.
            </div>
            
            <div class="date-section">
                Date : {date_display}
            </div>
            
            <div class="footer">
                <strong>{COMPANY_NAME}</strong><br>
                www.rrlbuildersanddevelopers.com
            </div>
        </div>
    </body>
    </html>
    '''
    return html


# ==================== BANK NOC DOCUMENT GENERATORS ====================

