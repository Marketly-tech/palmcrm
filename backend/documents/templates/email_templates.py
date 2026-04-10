"""Email HTML templates (Welcome, Document)."""
from datetime import datetime
from documents.templates.common import format_inr, get_logo_img_tag, COMPANY_NAME

def generate_welcome_email_html(customer: dict) -> str:
    """Generate the welcome email HTML with black and gold theme"""
    
    booking_date = customer.get('booking_date', datetime.now().strftime("%d/%m/%Y"))
    if booking_date and '-' in booking_date:
        try:
            dt = datetime.strptime(booking_date, "%Y-%m-%d")
            booking_date = dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            pass
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            
            body {{
                font-family: 'Roboto', sans-serif;
                background: #f5f5f5;
                padding: 30px;
                margin: 0;
                color: #1A1A1A;
            }}
            
            .email-container {{
                background: #fff;
                border: 2px solid #D4AF37;
                border-radius: 8px;
                padding: 35px 45px;
                max-width: 700px;
                margin: 0 auto;
                line-height: 1.8;
            }}
            
            .header {{
                display: flex;
                align-items: center;
                gap: 15px;
                padding-bottom: 20px;
                border-bottom: 3px solid #D4AF37;
                margin-bottom: 25px;
            }}
            
            .logo {{
                width: 100px;
            }}
            
            .logo img {{
                width: 100px;
                height: auto;
            }}
            
            .company-info {{
                flex: 1;
            }}
            
            .company-name {{
                font-size: 18px;
                font-weight: 700;
                color: #1A1A1A;
            }}
            
            .company-tagline {{
                font-size: 11px;
                color: #666;
            }}
            
            .greeting {{
                font-size: 18px;
                color: #1A1A1A;
                margin-bottom: 20px;
            }}
            
            .greeting span {{
                color: #D4AF37;
                font-weight: 600;
            }}
            
            .flat-highlight {{
                color: #D4AF37;
                font-weight: 600;
            }}
            
            .residence-details {{
                margin: 25px 0;
                padding: 20px 25px;
                background: #fafafa;
                border-left: 4px solid #D4AF37;
                border-radius: 0 8px 8px 0;
            }}
            
            .residence-details-title {{
                display: block;
                margin-bottom: 18px;
                color: #1A1A1A;
                font-size: 15px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                padding-bottom: 10px;
                border-bottom: 1px solid #e0e0e0;
            }}
            
            .detail-row {{
                display: table;
                width: 100%;
                margin: 12px 0;
                font-size: 14px;
            }}
            
            .detail-label {{
                display: table-cell;
                width: 40%;
                color: #666;
                padding: 8px 0;
            }}
            
            .detail-value {{
                display: table-cell;
                width: 60%;
                font-weight: 500;
                color: #D4AF37;
                padding: 8px 0;
                text-align: right;
            }}
            
            p {{
                margin-bottom: 18px;
                color: #333;
                font-size: 14px;
            }}
            
            .signature-section {{
                margin-top: 30px;
                padding: 20px;
                background: #fafafa;
                border-radius: 8px;
            }}
            
            .signature-name {{
                font-size: 15px;
                font-weight: 600;
                color: #1A1A1A;
                margin-bottom: 3px;
            }}
            
            .signature-title {{
                font-size: 12px;
                color: #D4AF37;
                font-weight: 500;
                margin-bottom: 12px;
            }}
            
            .signature-contact {{
                font-size: 12px;
                color: #666;
                line-height: 1.6;
            }}
            
            .signature-contact a {{
                color: #D4AF37;
                text-decoration: none;
            }}
            
            .footer {{
                margin-top: 25px;
                padding-top: 20px;
                border-top: 2px solid #D4AF37;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
            
            .footer-link {{
                color: #D4AF37;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">{get_logo_img_tag(100)}</div>
                <div class="company-info">
                    <div class="company-name">{COMPANY_NAME}</div>
                    <div class="company-tagline">Beyond homes. A lifestyle</div>
                </div>
            </div>
            
            <p class="greeting">Dear <span>{customer.get('name', 'Valued Customer')}</span>,</p>
            
            <p><strong>Greetings From {COMPANY_NAME}</strong></p>
            
            <p>It is our distinct pleasure to welcome you to {customer.get('project', 'RRL Palm Altezze')} and to congratulate you on the acquisition of your Residence <span class="flat-highlight">Flat No. {customer.get('unit_number', '')}</span>.</p>
            
            <p>Your decision reflects a refined appreciation for exceptional design, uncompromising quality, and a lifestyle that goes beyond the ordinary. At {COMPANY_NAME}, we create homes not merely as living spaces, but as enduring legacies—crafted with precision, discretion, and timeless elegance.</p>
            
            <p>{customer.get('project', 'RRL Palm Altezze')} has been envisioned for a select few who value privacy, sophistication, and exclusivity. Every element of your residence—from architecture and materials to amenities and services—has been thoughtfully curated to offer a living experience of rare distinction.</p>
            
            <div class="residence-details">
                <span class="residence-details-title">Residence Details</span>
                
                <div class="detail-row">
                    <span class="detail-label">Project</span>
                    <span class="detail-value">{customer.get('project', 'RRL PALM ALTEZZE').upper()}</span>
                </div>
                
                <div class="detail-row">
                    <span class="detail-label">Residence</span>
                    <span class="detail-value">Flat No. {customer.get('unit_number', '')}</span>
                </div>
                
                <div class="detail-row">
                    <span class="detail-label">Configuration</span>
                    <span class="detail-value">{customer.get('bhk_type', '').upper()}</span>
                </div>
                
                <div class="detail-row">
                    <span class="detail-label">Booking Date</span>
                    <span class="detail-value">{booking_date}</span>
                </div>
            </div>
            
            <p>Your dedicated Relationship Director will connect with you personally to ensure that every interaction with us is seamless and tailored to your expectations. We remain committed to delivering not only an exceptional home, but also an ownership experience defined by transparency, attention to detail, and quiet excellence.</p>
            
            <p>Please find attached the Price Breakup document for your reference.</p>
            
            <div class="signature-section">
                <div class="signature-name">John</div>
                <div class="signature-title">CRM MANAGER</div>
                <div class="signature-contact">
                    <strong>P:</strong> 9606579135<br>
                    <strong>E:</strong> <a href="mailto:crm@rrlbuildersanddevelopers.com">crm@rrlbuildersanddevelopers.com</a><br>
                    <strong>A:</strong> 4TH Floor, RRL Tower, Sompura gate, Sarjapura Bengaluru - 562125<br><br>
                    <a href="https://www.rrlbuildersanddevelopers.com">www.rrlbuildersanddevelopers.com</a>
                </div>
            </div>
            
            <div class="footer">
                <p><strong>{COMPANY_NAME}</strong></p>
                <p><a href="https://www.rrlbuildersanddevelopers.com" class="footer-link">www.rrlbuildersanddevelopers.com</a></p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

def generate_document_email_html(customer: dict, subject: str, body: str) -> str:
    """Generate email HTML with black and gold theme - same format as welcome mail"""
    
    # Convert body with line breaks to HTML
    body_html = body.replace('\n', '<br>')
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        </style>
    </head>
    <body style="font-family: 'Roboto', Arial, sans-serif; background: #f5f5f5; padding: 30px; margin: 0; color: #1A1A1A;">
        <div style="background: #fff; border: 2px solid #D4AF37; border-radius: 8px; max-width: 700px; margin: 0 auto; overflow: hidden;">
            <!-- Header -->
            <div style="background: #1A1A1A; padding: 20px; display: flex; align-items: center;">
                <div style="margin-right: 15px;">{get_logo_img_tag(80)}</div>
                <div>
                    <div style="color: #D4AF37; font-size: 18px; font-weight: 700;">{COMPANY_NAME}</div>
                    <div style="color: #999; font-size: 11px;">Beyond Homes. A Lifestyle</div>
                </div>
            </div>
            
            <!-- Content -->
            <div style="padding: 30px 35px; line-height: 1.8;">
                <div style="font-size: 14px; color: #333;">{body_html}</div>
                
                <!-- Signature -->
                <div style="margin-top: 30px; padding: 20px; background: #fafafa; border-radius: 8px;">
                    <div style="font-size: 15px; font-weight: 600; color: #1A1A1A; margin-bottom: 3px;">John</div>
                    <div style="font-size: 12px; color: #D4AF37; font-weight: 500; margin-bottom: 12px;">CRM MANAGER</div>
                    <div style="font-size: 12px; color: #666; line-height: 1.6;">
                        <strong>P:</strong> 9606579135<br>
                        <strong>E:</strong> <a href="mailto:crm@rrlbuildersanddevelopers.com" style="color: #D4AF37;">crm@rrlbuildersanddevelopers.com</a><br>
                        <strong>A:</strong> 4TH Floor, RRL Tower, Sompura gate, Sarjapura Bengaluru - 562125<br><br>
                        <a href="https://www.rrlbuildersanddevelopers.com" style="color: #D4AF37;">www.rrlbuildersanddevelopers.com</a>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #fafafa; padding: 15px; text-align: center; font-size: 11px; color: #888; border-top: 1px solid #e0e0e0;">
                <p style="margin: 0;">{COMPANY_NAME} | <a href="https://www.rrlbuildersanddevelopers.com" style="color: #D4AF37;">www.rrlbuildersanddevelopers.com</a></p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

