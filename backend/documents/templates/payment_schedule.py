"""Payment Schedule document templates."""
from datetime import datetime
from documents.templates.common import format_inr

def generate_payment_schedule_pdf_html(customer: dict, transactions: list = None) -> str:
    """Generate Payment Schedule PDF HTML with customer data and transactions"""
    
    def fmt(amount):
        """Format amount in Indian Rupee style"""
        amount = float(amount) if amount else 0
        int_part = int(amount)
        decimal_part = f"{amount:.2f}".split('.')[1]
        
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
    
    # Build transactions table
    transactions_rows = ""
    total_received = 0
    
    if transactions and len(transactions) > 0:
        for i, txn in enumerate(transactions, 1):
            amount = txn.get('amount', 0) or 0
            total_received += amount
            txn_date = txn.get('transaction_date', '-')
            bank = txn.get('bank_name', '-') or '-'
            txn_no = txn.get('transaction_number', '-') or '-'
            stage = (txn.get('transaction_stage', '-') or 'Payment').replace('_', ' ').title()
            
            transactions_rows += f'''
            <tr>
                <td style="text-align: center; padding: 10px; border: 1px solid #ddd;">{i}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{txn_date}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{stage}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{bank}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{txn_no}</td>
                <td style="text-align: right; padding: 10px; border: 1px solid #ddd;">{fmt(amount)}</td>
            </tr>
            '''
    
    total_price = customer.get('total_price', 0) or 0
    balance = total_price - total_received
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; color: #1A1A1A; }}
            .header {{ text-align: center; border-bottom: 3px solid #D4AF37; padding-bottom: 20px; margin-bottom: 20px; }}
            .header h1 {{ color: #1A1A1A; margin: 0; font-size: 24px; }}
            .header p {{ color: #666; margin: 5px 0; }}
            .customer-info {{ background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
            .customer-info h3 {{ color: #D4AF37; margin-top: 0; }}
            .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
            .info-item {{ padding: 5px 0; }}
            .info-label {{ color: #666; font-size: 12px; }}
            .info-value {{ font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background: #1A1A1A; color: #D4AF37; padding: 12px; text-align: left; }}
            .summary {{ margin-top: 20px; background: #1A1A1A; color: white; padding: 15px; border-radius: 8px; }}
            .summary-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #333; }}
            .summary-row:last-child {{ border-bottom: none; }}
            .summary-label {{ color: #D4AF37; }}
            .summary-value {{ font-weight: bold; }}
            .balance {{ color: #ff6b6b; font-size: 1.2em; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>RRL BUILDERS AND DEVELOPERS</h1>
            <p>Beyond homes. A lifestyle</p>
            <h2 style="margin-top: 15px; color: #D4AF37;">PAYMENT SCHEDULE</h2>
        </div>
        
        <div class="customer-info">
            <h3>Customer Details</h3>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Customer Name</div>
                    <div class="info-value">{customer.get('name', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Customer ID</div>
                    <div class="info-value">{customer.get('customer_id', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Project</div>
                    <div class="info-value">{customer.get('project', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Unit Number</div>
                    <div class="info-value">{customer.get('tower', '')}-{customer.get('unit_number', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Phone</div>
                    <div class="info-value">{customer.get('phone', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Email</div>
                    <div class="info-value">{customer.get('email', '-')}</div>
                </div>
            </div>
        </div>
        
        <h3>Payment Transactions</h3>
        <table>
            <thead>
                <tr>
                    <th style="width: 5%;">#</th>
                    <th style="width: 15%;">Date</th>
                    <th style="width: 20%;">Type</th>
                    <th style="width: 20%;">Bank</th>
                    <th style="width: 20%;">Reference</th>
                    <th style="width: 20%; text-align: right;">Amount</th>
                </tr>
            </thead>
            <tbody>
                {transactions_rows if transactions_rows else '<tr><td colspan="6" style="text-align: center; padding: 20px; color: #666;">No transactions recorded</td></tr>'}
            </tbody>
        </table>
        
        <div class="summary">
            <div class="summary-row">
                <span class="summary-label">Total Unit Value</span>
                <span class="summary-value">{fmt(total_price)}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Total Received</span>
                <span class="summary-value" style="color: #4CAF50;">{fmt(total_received)}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Balance Pending</span>
                <span class="summary-value balance">{fmt(balance)}</span>
            </div>
        </div>
        
        <p style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
            Generated on {datetime.now().strftime("%d/%m/%Y at %H:%M")} | RRL Builders CRM
        </p>
    </body>
    </html>
    '''
    
    return html

def generate_payment_schedule_html(customer: dict, schedule_items: list) -> str:
    """Generate HTML for Payment Schedule PDF with black and gold theme"""
    
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
        except:
            pass
    
    # Generate schedule rows
    schedule_rows = ""
    cumulative_amount = 0
    cumulative_pct = 0
    for i, item in enumerate(schedule_items, 1):
        cumulative_amount += item.get('amount', 0)
        cumulative_pct += item.get('percentage', 0)
        status_color = "#28a745" if item.get('payment_status') == 'paid' else "#dc3545" if item.get('payment_status') == 'overdue' else "#D4AF37"
        schedule_rows += f'''
        <tr>
            <td style="text-align: center;">{i}</td>
            <td>{item.get('installment_name', '')}</td>
            <td style="text-align: center;">{item.get('percentage', 0)}%</td>
            <td style="text-align: center;">{cumulative_pct}%</td>
            <td style="text-align: right;">{format_inr(item.get('amount', 0))}</td>
            <td style="text-align: right; color: #D4AF37; font-weight: bold;">{format_inr(cumulative_amount)}</td>
            <td style="text-align: center;">{item.get('due_date', '-')}</td>
            <td style="text-align: center; color: {status_color}; font-weight: bold;">{item.get('payment_status', 'pending').upper()}</td>
        </tr>
        '''
    
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
                padding: 30px;
                max-width: 900px;
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
                width: 60px;
                height: 60px;
                background: #1A1A1A;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #D4AF37;
                font-weight: bold;
                font-size: 24px;
            }}
            
            .company-name {{
                font-size: 22px;
                font-weight: 700;
                color: #1A1A1A;
            }}
            
            .company-tagline {{
                font-size: 12px;
                color: #666;
            }}
            
            .document-title {{
                background: #1A1A1A;
                color: #D4AF37;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 14px;
            }}
            
            .customer-info {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-bottom: 25px;
                padding: 15px;
                background: #fafafa;
                border-radius: 8px;
                border-left: 4px solid #D4AF37;
            }}
            
            .info-item {{
                display: flex;
                justify-content: space-between;
            }}
            
            .info-label {{
                color: #666;
                font-size: 12px;
            }}
            
            .info-value {{
                font-weight: 500;
                color: #1A1A1A;
            }}
            
            .schedule-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            
            .schedule-table th {{
                background: #1A1A1A;
                color: #D4AF37;
                padding: 12px 10px;
                font-weight: 500;
                font-size: 12px;
                text-transform: uppercase;
            }}
            
            .schedule-table td {{
                padding: 10px;
                border-bottom: 1px solid #e0e0e0;
                font-size: 11px;
            }}
            
            .schedule-table tr:nth-child(even) {{
                background: #fafafa;
            }}
            
            .totals-section {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-top: 25px;
            }}
            
            .total-box {{
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }}
            
            .total-box.received {{
                background: #e8f5e9;
                border: 1px solid #28a745;
            }}
            
            .total-box.pending {{
                background: #fff3e0;
                border: 1px solid #D4AF37;
            }}
            
            .total-box.total {{
                background: #1A1A1A;
                color: #D4AF37;
            }}
            
            .total-label {{
                font-size: 11px;
                text-transform: uppercase;
            }}
            
            .total-value {{
                font-size: 18px;
                font-weight: 700;
                margin-top: 5px;
            }}
            
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                text-align: center;
                font-size: 10px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo-section">
                    <div class="logo">RRL</div>
                    <div>
                        <div class="company-name">RRL Builders and Developers</div>
                        <div class="company-tagline">Beyond homes. A lifestyle</div>
                    </div>
                </div>
                <div class="document-title">PAYMENT SCHEDULE</div>
            </div>
            
            <div class="customer-info">
                <div class="info-item">
                    <span class="info-label">Customer Name</span>
                    <span class="info-value">{customer.get('name', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Customer ID</span>
                    <span class="info-value">{customer.get('customer_id', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Project</span>
                    <span class="info-value">{customer.get('project', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Unit Number</span>
                    <span class="info-value">{customer.get('unit_number', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Total Value</span>
                    <span class="info-value">{format_inr(customer.get('total_price', 0))}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Booking Date</span>
                    <span class="info-value">{booking_date}</span>
                </div>
            </div>
            
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th style="width: 5%;">#</th>
                        <th style="width: 28%;">Particulars</th>
                        <th style="width: 7%;">%</th>
                        <th style="width: 10%;">Cumulative %</th>
                        <th style="width: 14%;">Amount</th>
                        <th style="width: 14%;">Cumulative Amt</th>
                        <th style="width: 12%;">Due Date</th>
                        <th style="width: 10%;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {schedule_rows}
                </tbody>
            </table>
            
            <div class="totals-section">
                <div class="total-box received">
                    <div class="total-label">Total Received</div>
                    <div class="total-value" style="color: #28a745;">{format_inr(customer.get('total_received', 0))}</div>
                </div>
                <div class="total-box pending">
                    <div class="total-label">Balance Pending</div>
                    <div class="total-value" style="color: #D4AF37;">{format_inr(customer.get('balance_amount', 0))}</div>
                </div>
                <div class="total-box total">
                    <div class="total-label">Total Property Value</div>
                    <div class="total-value">{format_inr(customer.get('total_price', 0))}</div>
                </div>
            </div>
            
            <div class="footer">
                <p>RRL Builders and Developers Pvt Ltd | www.rrlbuildersanddevelopers.com</p>
                <p>This is a computer-generated document. Generated on {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html



