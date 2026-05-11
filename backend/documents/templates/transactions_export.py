"""
Transactions Export HTML template.
Generates the standalone HTML used to preview / print all customer transactions.
"""
from datetime import datetime, timezone

from documents.templates.common import get_logo_img_tag, COMPANY_NAME


def _fmt_inr(amount):
    """Format an amount in Indian Rupee notation (lakh/crore grouping)."""
    amount = float(amount) if amount else 0
    int_part = int(amount)
    s = str(int_part)
    if len(s) <= 3:
        return f"\u20b9{s}"
    result = s[-3:]
    s = s[:-3]
    while s:
        result = s[-2:] + ',' + result
        s = s[:-2]
    return f"\u20b9{result}"


def _build_co_applicant_row(customer):
    if not customer.get('co_applicant_name'):
        return ""
    return f'''
            <div class="info-item">
                <div class="info-label">Co-Applicant</div>
                <div class="info-value">{customer.get('co_applicant_name', '')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Co-Applicant Phone</div>
                <div class="info-value">{customer.get('co_applicant_phone', '') or '-'}</div>
            </div>'''


def _build_txn_rows(transactions):
    if not transactions:
        return '<tr><td colspan="7" style="text-align: center; padding: 20px; color: #666;">No transactions recorded</td></tr>'

    rows = []
    for i, txn in enumerate(transactions, 1):
        amount = txn.get('amount', 0) or 0
        stage = (txn.get('transaction_stage', '') or 'Payment').replace('_', ' ').title()
        txn_date = txn.get('transaction_date', '-')
        bank = txn.get('bank_name', '-') or '-'
        txn_no = txn.get('transaction_number', '-') or '-'
        notes = txn.get('notes', '') or ''
        rows.append(f'''
        <tr>
            <td style="text-align: center;">{i}</td>
            <td>{txn_date}</td>
            <td>{stage}</td>
            <td>{bank}</td>
            <td>{txn_no}</td>
            <td style="text-align: right; font-weight: 500;">{_fmt_inr(amount)}</td>
            <td>{notes}</td>
        </tr>''')
    return "".join(rows)


def generate_transactions_export_html(customer: dict, transactions: list) -> str:
    """Build the full HTML document for exporting a customer's transactions."""
    total_received = sum(float(t.get('amount', 0) or 0) for t in transactions)
    total_price = float(customer.get('total_price', 0) or 0)
    balance = total_price - total_received
    co_applicant_row = _build_co_applicant_row(customer)
    txn_rows = _build_txn_rows(transactions)

    return f'''<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Roboto', sans-serif; padding: 30px; color: #1A1A1A; background: #fff; }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #D4AF37; padding-bottom: 20px; margin-bottom: 25px; }}
            .logo-section {{ display: flex; align-items: center; gap: 15px; }}
            .logo img {{ width: 100px; height: auto; }}
            .company-name {{ font-size: 20px; font-weight: 700; color: #1A1A1A; }}
            .company-tagline {{ font-size: 11px; color: #666; }}
            .document-title {{ background: #1A1A1A; color: #D4AF37; padding: 10px 20px; border-radius: 4px; font-weight: 500; font-size: 13px; text-transform: uppercase; }}
            .customer-info {{ background: #fafafa; padding: 15px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #D4AF37; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
            .info-item {{ padding: 5px 0; }}
            .info-label {{ color: #666; font-size: 11px; }}
            .info-value {{ font-weight: 500; font-size: 12px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th {{ background: #1A1A1A; color: #D4AF37; padding: 10px 8px; text-align: left; font-size: 11px; font-weight: 500; }}
            td {{ padding: 10px 8px; border-bottom: 1px solid #e0e0e0; font-size: 11px; }}
            tr:nth-child(even) {{ background: #fafafa; }}
            .summary {{ margin-top: 20px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; }}
            .summary-box {{ padding: 15px; border-radius: 8px; text-align: center; }}
            .summary-box.total {{ background: #1A1A1A; color: #D4AF37; }}
            .summary-box.received {{ background: #e8f5e9; border: 1px solid #28a745; }}
            .summary-box.balance {{ background: #fff3e0; border: 1px solid #D4AF37; }}
            .summary-label {{ font-size: 10px; text-transform: uppercase; }}
            .summary-value {{ font-size: 18px; font-weight: 700; margin-top: 5px; }}
            .footer {{ margin-top: 30px; padding-top: 15px; border-top: 2px solid #D4AF37; text-align: center; font-size: 10px; color: #666; }}
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
                <div class="document-title">Transaction Details</div>
            </div>
            <div class="customer-info">
                <div class="info-item">
                    <div class="info-label">Customer Name</div>
                    <div class="info-value">{customer.get('name', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Phone</div>
                    <div class="info-value">{customer.get('phone', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Project</div>
                    <div class="info-value">{customer.get('project', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Unit Number</div>
                    <div class="info-value">{customer.get('tower', '')}-{customer.get('unit_number', '-')}</div>
                </div>
                {co_applicant_row}
            </div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 4%;">#</th>
                        <th style="width: 12%;">Date</th>
                        <th style="width: 16%;">Stage</th>
                        <th style="width: 16%;">Bank</th>
                        <th style="width: 18%;">Transaction No.</th>
                        <th style="width: 14%; text-align: right;">Amount</th>
                        <th style="width: 20%;">Notes</th>
                    </tr>
                </thead>
                <tbody>
                    {txn_rows}
                </tbody>
            </table>
            <div class="summary">
                <div class="summary-box total">
                    <div class="summary-label">Total Property Value</div>
                    <div class="summary-value">{_fmt_inr(total_price)}</div>
                </div>
                <div class="summary-box received">
                    <div class="summary-label">Total Received</div>
                    <div class="summary-value" style="color: #28a745;">{_fmt_inr(total_received)}</div>
                </div>
                <div class="summary-box balance">
                    <div class="summary-label">Balance Pending</div>
                    <div class="summary-value" style="color: #D4AF37;">{_fmt_inr(balance)}</div>
                </div>
            </div>
            <div class="footer">
                <p>{COMPANY_NAME} | www.rrlbuildersanddevelopers.com</p>
                <p>Generated on {datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")} UTC</p>
            </div>
        </div>
    </body>
    </html>'''
