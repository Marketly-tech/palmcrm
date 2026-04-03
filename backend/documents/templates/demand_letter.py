"""Demand Letter document template."""
from datetime import datetime
from utils import number_to_indian_words, format_indian_currency, get_ordinal_suffix
from documents.templates.common import format_inr

def generate_demand_letter_html(customer: dict, transactions: list = None, stage_info: dict = None) -> str:
    """Generate Demand Letter / Installment Call Letter HTML with customer and payment data."""
    from datetime import datetime

    transactions = transactions or []
    stage_info = stage_info or {}

    # --- Customer Details ---
    customer_name = customer.get('name', '').upper()
    co_applicant = customer.get('co_applicant_name', '')
    if co_applicant:
        recipient_name = f"{customer_name} AND {co_applicant.upper()}"
    else:
        recipient_name = customer_name

    address = customer.get('address', '') or ''
    phone = customer.get('phone', '')
    email = customer.get('email', '')

    # --- Property Details ---
    project = customer.get('project', 'RRL Palm Altezze')
    tower = customer.get('tower', '')
    unit_number = customer.get('unit_number', '')
    floor_num = customer.get('floor', 0)

    def get_ordinal(n):
        n = int(n)
        if n == 0:
            return "Ground"
        suffix = 'th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"

    floor_display = get_ordinal(floor_num) + " Floor" if floor_num else "Ground Floor"
    flat_ref = f"Flat no. {unit_number}, Tower- {tower}, {floor_display}"

    # --- Financial Calculations ---
    total_basic_cost = float(customer.get('total_price', 0) or 0)
    booking_amount = float(customer.get('booking_amount', 0) or 0)

    # Current stage info
    stage_name = stage_info.get('name', 'As per schedule')
    stage_percentage = float(stage_info.get('percentage', 0) or 0)
    cumulative_percentage = float(stage_info.get('cumulative', 0) or 0)

    # Demand raised till date = cumulative % of total basic cost
    demand_raised = round((total_basic_cost * cumulative_percentage) / 100, 2) if cumulative_percentage else 0

    # Current due = stage % of total basic cost (this stage's individual share)
    current_due = round((total_basic_cost * stage_percentage) / 100, 2) if stage_percentage else 0

    # Amount paid till date from transactions
    txn_total = sum(float(t.get('amount', 0) or 0) for t in transactions)
    amount_paid = txn_total if txn_total >= booking_amount else booking_amount + txn_total

    # Outstanding
    total_outstanding = max(0, round(demand_raised - amount_paid, 2))

    # TDS (default 0)
    tds_payable = 0
    tds_paid = 0
    tds_to_be_paid = 0

    # Net amount payable
    net_amount_payable = max(0, round(total_outstanding - tds_payable, 2))

    # Amount in words
    net_amount_words = number_to_indian_words(int(net_amount_payable)).replace(" Rupees", "")
    amount_in_words = f"Rupees {net_amount_words} Only"

    # Format currency helper
    def fmt(amount):
        return format_indian_currency(amount, decimals=False)

    # Date
    today = datetime.now()
    date_str = today.strftime("%d-%m-%Y")

    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            @page {{
                size: A4;
                margin: 15mm 15mm 20mm 15mm;
            }}
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Roboto', Arial, sans-serif;
                font-size: 12px;
                line-height: 1.6;
                color: #1a1a1a;
                background: #fff;
            }}
            .page {{
                max-width: 210mm;
                margin: 0 auto;
                padding: 15mm;
            }}
            .header-bar {{
                background: #1A1A1A;
                color: #D4AF37;
                padding: 14px 24px;
                display: flex;
                align-items: center;
                border-radius: 4px 4px 0 0;
                margin-bottom: 0;
            }}
            .header-logo {{
                background: #D4AF37;
                color: #1A1A1A;
                font-weight: 700;
                font-size: 20px;
                padding: 8px 14px;
                border-radius: 4px;
                margin-right: 16px;
            }}
            .header-text {{
                flex: 1;
            }}
            .header-text h1 {{
                font-size: 16px;
                font-weight: 700;
                color: #D4AF37;
                margin: 0;
            }}
            .header-text p {{
                font-size: 10px;
                color: #999;
                margin: 2px 0 0;
            }}
            .title-bar {{
                background: #D4AF37;
                color: #1A1A1A;
                text-align: center;
                padding: 8px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 2px;
            }}
            .content {{
                border: 1px solid #ddd;
                border-top: none;
                padding: 24px;
                border-radius: 0 0 4px 4px;
            }}
            .date-line {{
                text-align: right;
                font-weight: 500;
                margin-bottom: 16px;
                font-size: 12px;
            }}
            .recipient {{
                margin-bottom: 14px;
                line-height: 1.7;
            }}
            .recipient strong {{
                font-size: 13px;
            }}
            .ref-box {{
                background: #f8f8f4;
                border-left: 3px solid #D4AF37;
                padding: 10px 14px;
                margin-bottom: 14px;
                font-size: 11.5px;
                line-height: 1.6;
            }}
            .ref-box strong {{
                color: #1A1A1A;
            }}
            .subject {{
                margin-bottom: 12px;
                font-size: 12px;
            }}
            .subject strong {{
                color: #1A1A1A;
            }}
            .body-text {{
                margin-bottom: 12px;
                font-size: 12px;
                line-height: 1.7;
            }}
            .stage-label {{
                background: #1A1A1A;
                color: #D4AF37;
                padding: 8px 14px;
                font-weight: 600;
                font-size: 11.5px;
                border-radius: 3px;
                margin-bottom: 10px;
            }}
            .payment-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 12px;
                font-size: 11px;
            }}
            .payment-table th {{
                background: #f5f5f0;
                border: 1px solid #ccc;
                padding: 8px 10px;
                text-align: left;
                font-weight: 600;
                font-size: 10.5px;
                color: #333;
            }}
            .payment-table td {{
                border: 1px solid #ccc;
                padding: 8px 10px;
                text-align: right;
                font-weight: 500;
                font-size: 11px;
            }}
            .payment-table tr.highlight td {{
                background: #fffbe6;
                font-weight: 700;
                color: #1A1A1A;
            }}
            .amount-words {{
                font-style: italic;
                font-weight: 600;
                color: #333;
                margin-bottom: 14px;
                font-size: 12px;
                padding: 6px 0;
                border-bottom: 1px dashed #ccc;
            }}
            .bank-details {{
                background: #fafaf6;
                border: 1px solid #e0dcd0;
                border-radius: 4px;
                padding: 14px 18px;
                margin: 14px 0;
            }}
            .bank-details h4 {{
                font-size: 12px;
                color: #1A1A1A;
                margin-bottom: 8px;
                font-weight: 600;
            }}
            .bank-details table {{
                font-size: 11.5px;
            }}
            .bank-details td {{
                padding: 3px 8px 3px 0;
            }}
            .bank-details td:first-child {{
                font-weight: 600;
                color: #555;
                white-space: nowrap;
            }}
            .closing {{
                margin-top: 20px;
                font-size: 12px;
                line-height: 1.8;
            }}
            .signature {{
                margin-top: 40px;
            }}
            .signature .for {{
                font-size: 11px;
                color: #666;
            }}
            .signature .company {{
                font-size: 13px;
                font-weight: 700;
                color: #1A1A1A;
            }}
            .footer {{
                margin-top: 24px;
                border-top: 2px solid #D4AF37;
                padding-top: 10px;
                text-align: center;
                font-size: 9.5px;
                color: #888;
            }}
            .footer a {{
                color: #D4AF37;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="page">
            <!-- Header -->
            <div class="header-bar">
                <div class="header-logo">RRL</div>
                <div class="header-text">
                    <h1>RRL Builders and Developers</h1>
                    <p>Beyond homes. A lifestyle</p>
                </div>
            </div>

            <!-- Title -->
            <div class="title-bar">DEMAND LETTER</div>

            <!-- Content -->
            <div class="content">
                <div class="date-line">Date: {date_str}</div>

                <div class="recipient">
                    <strong>{recipient_name}</strong><br>
                    {address.replace(chr(10), "<br>") if address else "Address on file"}<br>
                    Ph. {phone}
                </div>

                <div class="ref-box">
                    <strong>Ref:</strong> {flat_ref} at &ldquo;{project}&rdquo; situated at SY NO: 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN - 560087
                </div>

                <div class="subject">
                    <strong>Subject:</strong> Installment Call Letter
                </div>

                <p class="body-text">Dear Sir/Madam,</p>
                <p class="body-text">
                    Thank you for partnering with us. We are pleased to inform you that the following installments are due as per the payment schedule.
                </p>

                <!-- Payment Stage -->
                <div class="stage-label">
                    Payment Stage: {stage_name} &mdash; {int(cumulative_percentage)}% Total Basic Cost
                </div>

                <!-- Payment Table -->
                <table class="payment-table">
                    <tr>
                        <th>Total Basic Cost</th>
                        <td>{fmt(total_basic_cost)}</td>
                    </tr>
                    <tr>
                        <th>Demand Raised Till Date (A)</th>
                        <td>{fmt(demand_raised)}</td>
                    </tr>
                    <tr>
                        <th>Current Due (B)</th>
                        <td>{fmt(current_due)}</td>
                    </tr>
                    <tr>
                        <th>Installment Amount Paid Till Date (C)</th>
                        <td>{fmt(amount_paid)}</td>
                    </tr>
                    <tr>
                        <th>Interest (D)</th>
                        <td>0</td>
                    </tr>
                    <tr class="highlight">
                        <th>Total Outstanding as on date (A)-(C)</th>
                        <td>{fmt(total_outstanding)}</td>
                    </tr>
                    <tr>
                        <th>TDS Payable</th>
                        <td>{tds_payable}</td>
                    </tr>
                    <tr>
                        <th>TDS Paid</th>
                        <td>{tds_paid}</td>
                    </tr>
                    <tr>
                        <th>TDS To be Paid</th>
                        <td>{tds_to_be_paid}</td>
                    </tr>
                    <tr class="highlight">
                        <th>Net Amount Payable<br><small>(Total Outstanding - TDS Payable)</small></th>
                        <td style="font-size: 13px;">{fmt(net_amount_payable)}</td>
                    </tr>
                </table>

                <div class="amount-words">{amount_in_words}</div>

                <p class="body-text">We hereby request you to release this payment towards your flat.</p>
                <p class="body-text">Please remit payments via NEFT/RTGS to the bank details below:</p>

                <!-- Bank Details -->
                <div class="bank-details">
                    <h4>Bank Details for Payment</h4>
                    <table>
                        <tr><td>Account Name</td><td>: RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED</td></tr>
                        <tr><td>Account Number</td><td>: 57500001802063</td></tr>
                        <tr><td>Bank Name</td><td>: HDFC BANK</td></tr>
                        <tr><td>IFSC</td><td>: HDFC0009590</td></tr>
                        <tr><td>Branch Name</td><td>: SOMPURA</td></tr>
                    </table>
                </div>

                <div class="closing">
                    <p>Thanking you,</p>
                    <div class="signature">
                        <div class="for">For</div>
                        <div class="company">RRL Builders and Developers Private Limited</div>
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div class="footer">
                <p>4TH Floor, RRL Tower, Sompura Gate, Sarjapura, Bengaluru - 562125</p>
                <p><a href="https://www.rrlbuildersanddevelopers.com">www.rrlbuildersanddevelopers.com</a> | crm@rrlbuildersanddevelopers.com</p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html
