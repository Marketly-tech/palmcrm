"""Bank NOC document templates (HDFC, BOB, TATA Capital)."""
from datetime import datetime
from documents.templates.common import (
    format_inr,
    COMPANY_NAME,
    COMPANY_NAME_FULL,
    format_customer_names,
    get_logo_img_tag,
    format_tower,
)


# Company contact constants used in NOC footer band — match the format used in
# RRL's existing/legacy NOCs (pre-Feb-2026). Do not change without explicit
# confirmation from the user — see /app/memory/DOCUMENT_FORMAT_REFERENCE.md.
RRL_ADDRESS = "4th Floor, RRL TOWERS, Sompura Gate, Sarjapura Road, Bengaluru - 562125"
RRL_WEBSITE = "www.rrlbuildersanddevelopers.com"
RRL_EMAIL = "crm@rrlbuildersanddevelopers.com"
RRL_RERA = "PRM/KA/RERA/1251/308/PR/141025/008167"


def _letterhead_styles() -> str:
    """Shared CSS for the RRL letterhead at the top of all builder NOCs.

    Matches the original PDF format: dark charcoal band, gold logo on left,
    company name + tagline on right (light text on dark)."""
    return """
            .letterhead {
                background: #1A1A1A;
                color: #FFFFFF;
                padding: 18px 20mm;
                margin: 0 -20mm 22px -20mm;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            .letterhead-logo img {
                width: 70px !important;
                height: auto !important;
                display: block;
            }
            .letterhead-text {
                text-align: right;
                line-height: 1.25;
            }
            .letterhead-company {
                font-size: 18px;
                font-weight: 700;
                color: #FFFFFF;
                letter-spacing: 0.3px;
            }
            .letterhead-tagline {
                font-size: 11px;
                color: #D4AF37;
                margin-top: 2px;
                font-style: italic;
            }
            .doc-title {
                text-align: center;
                font-size: 15px;
                font-weight: 700;
                color: #1A1A1A;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 22px;
                padding-bottom: 6px;
                border-bottom: 1px solid #D4AF37;
            }
            .footer-band {
                position: fixed;
                bottom: 0;
                left: -20mm;
                right: -20mm;
                background: #F5F5F5;
                border-top: 2px solid #D4AF37;
                padding: 8px 20mm;
                font-size: 9px;
                color: #1A1A1A;
                text-align: center;
                line-height: 1.5;
            }
            .footer-band .sep {
                color: #D4AF37;
                margin: 0 6px;
            }
    """


def _letterhead_html() -> str:
    """Shared HTML block for the RRL letterhead — gold RRL GROUP logo on the
    left, company name + tagline on the right, on a dark band."""
    return f"""
        <div class="letterhead">
            <div class="letterhead-logo">{get_logo_img_tag(70)}</div>
            <div class="letterhead-text">
                <div class="letterhead-company">{COMPANY_NAME}</div>
                <div class="letterhead-tagline">Beyond Homes. A Lifestyle</div>
            </div>
        </div>
    """


def _doc_title_html(bank_label: str) -> str:
    """Centered document title placed below the dark header band."""
    return f'<div class="doc-title">Builder NOC &mdash; {bank_label}</div>'


def _footer_band_html(customer: dict) -> str:
    """Bottom footer band with company contact, RERA and reference details."""
    today = datetime.now().strftime("%d/%m/%y")
    ref = customer.get('customer_id') or customer.get('id', '')
    return f"""
        <div class="footer-band">
            {RRL_ADDRESS}
            <span class="sep">|</span> {RRL_WEBSITE}
            <span class="sep">|</span> {RRL_EMAIL}
            <br/>
            RERA: {RRL_RERA}
            <span class="sep">|</span> Document Generated: {today}
            <span class="sep">|</span> Ref: {ref}
        </div>
    """

def generate_noc_hdfc_html(customer: dict, transactions: list = None) -> str:
    """Generate HDFC Bank NOC (No Objection Certificate) for disbursement"""
    
    def format_inr(amount):
        """Format amount in Indian Rupee style"""
        amount = float(amount) if amount else 0
        return "{:,.0f}".format(amount).replace(",", ",")
    
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
            return tens[num // 10] + ('' if num % 10 == 0 else ' ' + ones[num % 10])
        if num < 1000:
            return ones[num // 100] + ' Hundred' + ('' if num % 100 == 0 else ' ' + number_to_words(num % 100))
        if num < 100000:
            return number_to_words(num // 1000) + ' Thousand' + ('' if num % 1000 == 0 else ' ' + number_to_words(num % 1000))
        if num < 10000000:
            return number_to_words(num // 100000) + ' Lakh' + ('' if num % 100000 == 0 else ' ' + number_to_words(num % 100000))
        return number_to_words(num // 10000000) + ' Crore' + ('' if num % 10000000 == 0 else ' ' + number_to_words(num % 10000000))
    
    # Customer details
    name = customer.get('name', '')
    co_applicant_name = customer.get('co_applicant_name', '')
    
    # Build customer names string
    customer_names = format_customer_names(customer)
    
    # Property details
    flat_no = customer.get('unit_number', '')
    tower = customer.get('tower', '1')
    tower_display = format_tower(tower)
    floor = customer.get('floor', '')
    floor_text = f"{floor}th" if floor else ""
    
    # Financial details
    total_price = customer.get('total_price', 0) or 0
    booking_amount = customer.get('booking_amount', 0) or 0
    # Received = sum of all transactions excluding TDS (fallback to booking_amount)
    if transactions:
        received_amount = sum(
            float(t.get('amount', 0) or 0)
            for t in transactions
            if (t.get('transaction_stage') or t.get('transaction_type')) != 'tds'
        )
    else:
        received_amount = booking_amount
    received_amount = int(round(received_amount))
    balance = total_price - received_amount
    loan_amount = customer.get('loan_amount', 0) or balance

    # Format amounts with words
    total_price_words = f"Rupees {number_to_words(total_price)} Only"
    received_words = f"Rupees {number_to_words(received_amount)} Only"
    balance_words = f"Rupees {number_to_words(balance)} Only"
    loan_words = f"Rupees {number_to_words(loan_amount)} Only"
    
    # Dates
    booking_date = customer.get('booking_date', datetime.now().strftime("%Y-%m-%d"))
    agreement_date = customer.get('agreement_date', booking_date)
    today_date = datetime.now().strftime("%d/%m/%y")
    
    if agreement_date and '-' in str(agreement_date):
        try:
            dt = datetime.strptime(str(agreement_date), "%Y-%m-%d")
            agreement_display = dt.strftime("%d/%m/%y")
        except:
            agreement_display = today_date
    else:
        agreement_display = today_date
    
    # Due date is the date of NOC generation
    due_date = today_date
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
            @page {{ size: A4; margin: 0 20mm 30mm 20mm; }}
            body {{ font-family: 'Roboto', sans-serif; font-size: 12px; line-height: 1.8; color: #1A1A1A; }}
            {_letterhead_styles()}
            .header {{ text-align: right; margin-bottom: 20px; }}
            .header-title {{ font-size: 16px; font-weight: 700; }}
            .date {{ text-align: right; margin-bottom: 20px; }}
            .addressee {{ margin-bottom: 20px; }}
            .addressee p {{ margin: 0; }}
            .salutation {{ margin-bottom: 15px; }}
            .content {{ text-align: justify; margin-bottom: 15px; }}
            .signature {{ margin-top: 40px; }}
            .signature-line {{ margin-top: 30px; font-weight: 500; }}
        </style>
    </head>
    <body>
        {_letterhead_html()}

        {_doc_title_html("HDFC Bank")}

        <div class="date">Date: {today_date}</div>
        
        <div class="addressee">
            <p>To,</p>
            <p><strong>HDFC BANK LTD</strong></p>
            <p>NO.51, KASTURBA ROAD,</p>
            <p>BANGALORE – 560 001</p>
        </div>
        
        <div class="salutation">Dear Sir,</div>
        
        <div class="content">
            <p>This is to confirm that we have sold Flat No.{flat_no}, {tower_display}, {floor_text} Floor in the building called <strong>RRL PALM ALTEZZE</strong> situated at RRL Palm Altezze, SY NO: 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN - 560087, to <strong>{customer_names}</strong> for a total consideration of <strong>Rs.{format_inr(total_price)}/-</strong> ({total_price_words}) out of which <strong>Rs.{format_inr(received_amount)}/-</strong> ({received_words}) has been received by us and balance <strong>Rs.{format_inr(balance)}/-</strong> ({balance_words}) is due on {due_date}.</p>
            
            <p>We hereby assure you that the said flat appurtenant there to be not subject to any encumbrance, charge, or liability of any kind whatsoever and that the entire property is free and marketable. We further confirm that we have a clear legal and marketable title to the said property and every part thereof.</p>
            
            <p>We have no objection to your giving a loan of <strong>Rs.{format_inr(loan_amount)}/-</strong> ({loan_words}) to said <strong>{customer_names}</strong> owner/s of the said flat and his/their mortgaging the said flat with you by way of security for repayment notwithstanding anything to the contrary contained in our agreement dated {agreement_display} with {customer_names}.</p>
            
            <p>We have taken the construction finance from Bajaj Housing Finance Limited.</p>
            
            <p>We also undertake to inform and give proper notice to the Co-operative Housing Society as and when formed, about the flat being mortgaged. We hereby undertake to forward the original title deed for the undivided share in the land duly registered directly to HDFC without parting the same with the allotee of the flat during the pendency of the loan under intimation to the borrower.</p>
        </div>
        
        <div class="signature">
            <p><strong>For {COMPANY_NAME_FULL}</strong></p>
            <p class="signature-line" style="margin-top: 50px;">Authorized Signatory</p>
        </div>

        {_footer_band_html(customer)}
    </body>
    </html>
    '''
    return html



def generate_noc_bob_html(customer: dict, transactions: list = None) -> str:
    """Generate Bank of Baroda (BOB) NOC for disbursement"""
    
    def format_inr(amount):
        amount = float(amount) if amount else 0
        return "{:,.0f}".format(amount).replace(",", ",")
    
    def number_to_words(num):
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
                'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        if num == 0:
            return 'Zero'
        num = int(num)
        if num < 20:
            return ones[num]
        if num < 100:
            return tens[num // 10] + ('' if num % 10 == 0 else ' ' + ones[num % 10])
        if num < 1000:
            return ones[num // 100] + ' Hundred' + ('' if num % 100 == 0 else ' ' + number_to_words(num % 100))
        if num < 100000:
            return number_to_words(num // 1000) + ' Thousand' + ('' if num % 1000 == 0 else ' ' + number_to_words(num % 1000))
        if num < 10000000:
            return number_to_words(num // 100000) + ' Lakh' + ('' if num % 100000 == 0 else ' ' + number_to_words(num % 100000))
        return number_to_words(num // 10000000) + ' Crore' + ('' if num % 10000000 == 0 else ' ' + number_to_words(num % 10000000))
    
    name = customer.get('name', '')
    co_applicant_name = customer.get('co_applicant_name', '')
    customer_names = format_customer_names(customer)
    
    flat_no = customer.get('unit_number', '')
    tower = customer.get('tower', '1')
    tower_display = format_tower(tower)
    floor = customer.get('floor', '')
    floor_text = f"{floor}th" if floor else ""
    
    total_price = customer.get('total_price', 0) or 0
    booking_amount = customer.get('booking_amount', 0) or 0
    # Received = sum of all transactions excluding TDS (fallback to booking_amount)
    if transactions:
        received_amount = sum(
            float(t.get('amount', 0) or 0)
            for t in transactions
            if (t.get('transaction_stage') or t.get('transaction_type')) != 'tds'
        )
    else:
        received_amount = booking_amount
    received_amount = int(round(received_amount))
    balance = total_price - received_amount
    loan_amount = customer.get('loan_amount', 0) or balance

    total_price_words = f"Rupees {number_to_words(total_price)} Only"
    received_words = f"Rupees {number_to_words(received_amount)} Only"
    balance_words = f"Rupees {number_to_words(balance)} Only"
    loan_words = f"Rupees {number_to_words(loan_amount)} Only"
    
    today_date = datetime.now().strftime("%d/%m/%y")
    agreement_date = customer.get('agreement_date', customer.get('booking_date', ''))
    if agreement_date and '-' in str(agreement_date):
        try:
            dt = datetime.strptime(str(agreement_date), "%Y-%m-%d")
            agreement_display = dt.strftime("%d/%m/%y")
        except:
            agreement_display = today_date
    else:
        agreement_display = today_date
    
    # Due date is the date of NOC generation
    due_date = today_date
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
            @page {{ size: A4; margin: 0 20mm 30mm 20mm; }}
            body {{ font-family: 'Roboto', sans-serif; font-size: 12px; line-height: 1.8; color: #1A1A1A; }}
            {_letterhead_styles()}
            .header {{ text-align: right; margin-bottom: 20px; }}
            .header-title {{ font-size: 16px; font-weight: 700; }}
            .date {{ text-align: right; margin-bottom: 20px; }}
            .addressee {{ margin-bottom: 20px; }}
            .addressee p {{ margin: 0; }}
            .salutation {{ margin-bottom: 15px; }}
            .content {{ text-align: justify; margin-bottom: 15px; }}
            .signature {{ margin-top: 40px; }}
            .signature-line {{ margin-top: 30px; font-weight: 500; }}
        </style>
    </head>
    <body>
        {_letterhead_html()}

        {_doc_title_html("Bank of Baroda")}

        <div class="date">Date: {today_date}</div>
        
        <div class="addressee">
            <p>To,</p>
            <p><strong>The Manager</strong></p>
            <p><strong>Bank of Baroda</strong></p>
            <p>Bangalore</p>
        </div>
        
        <div class="salutation">Dear Sir / Madam,</div>
        
        <div class="content">
            <p>This is to confirm that we have sold Flat No.{flat_no}, {tower_display}, {floor_text} Floor in the building called <strong>RRL PALM ALTEZZE</strong> situated at RRL Palm Altezze, SY NO: 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN - 560087, to <strong>{customer_names}</strong> for a total consideration of <strong>Rs.{format_inr(total_price)}/-</strong> ({total_price_words}) out of which <strong>Rs.{format_inr(received_amount)}/-</strong> ({received_words}) has been received by us and balance <strong>Rs.{format_inr(balance)}/-</strong> ({balance_words}) is due on {due_date}.</p>
            
            <p>We further confirm that we have a clear legal and marketable title to the said property and every part thereof. We have no objection to your giving a loan of <strong>Rs.{format_inr(loan_amount)}/-</strong> ({loan_words}) to said <strong>{customer_names}</strong> owner/s of the said flat and his/their mortgaging the said flat with you by way of security for repayment notwithstanding anything to the contrary contained in our agreement dated {agreement_display} with {customer_names}.</p>
        </div>
        
        <div class="signature">
            <p><strong>For {COMPANY_NAME_FULL}</strong></p>
            <p class="signature-line" style="margin-top: 50px;">Authorized Signatory</p>
        </div>

        {_footer_band_html(customer)}
    </body>
    </html>
    '''
    return html



def generate_noc_tata_html(customer: dict) -> str:
    """Generate TATA Capital Housing Finance NOC for disbursement"""
    
    def format_inr(amount):
        amount = float(amount) if amount else 0
        return "{:,.0f}".format(amount).replace(",", ",")
    
    def number_to_words(num):
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
                'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        if num == 0:
            return 'Zero'
        num = int(num)
        if num < 20:
            return ones[num]
        if num < 100:
            return tens[num // 10] + ('' if num % 10 == 0 else ' ' + ones[num % 10])
        if num < 1000:
            return ones[num // 100] + ' Hundred' + ('' if num % 100 == 0 else ' ' + number_to_words(num % 100))
        if num < 100000:
            return number_to_words(num // 1000) + ' Thousand' + ('' if num % 1000 == 0 else ' ' + number_to_words(num % 1000))
        if num < 10000000:
            return number_to_words(num // 100000) + ' Lakh' + ('' if num % 100000 == 0 else ' ' + number_to_words(num % 100000))
        return number_to_words(num // 10000000) + ' Crore' + ('' if num % 10000000 == 0 else ' ' + number_to_words(num % 10000000))
    
    name = customer.get('name', '')
    co_applicant_name = customer.get('co_applicant_name', '')
    
    # Build customer names using common utility
    customer_names = format_customer_names(customer)
    
    flat_no = customer.get('unit_number', '')
    tower = customer.get('tower', '1')
    tower_display = format_tower(tower)
    floor = customer.get('floor', '')
    floor_text = f"{floor}th" if floor else ""
    
    today_date = datetime.now().strftime("%d/%m/%y")
    agreement_date = customer.get('agreement_date', customer.get('booking_date', ''))
    if agreement_date and '-' in str(agreement_date):
        try:
            dt = datetime.strptime(str(agreement_date), "%Y-%m-%d")
            agreement_display = dt.strftime("%d/%m/%y")
        except:
            agreement_display = today_date
    else:
        agreement_display = today_date
    
    # Due date is the date of NOC generation
    due_date = today_date
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
            @page {{ size: A4; margin: 0 20mm 30mm 20mm; }}
            body {{ font-family: 'Roboto', sans-serif; font-size: 12px; line-height: 1.8; color: #1A1A1A; }}
            {_letterhead_styles()}
            .header {{ text-align: right; margin-bottom: 20px; }}
            .header-title {{ font-size: 16px; font-weight: 700; }}
            .date {{ text-align: right; margin-bottom: 20px; }}
            .addressee {{ margin-bottom: 20px; }}
            .addressee p {{ margin: 0; }}
            .salutation {{ margin-bottom: 15px; }}
            .content {{ text-align: justify; margin-bottom: 15px; }}
            .re-section {{ margin-bottom: 20px; padding: 10px; background: #f5f5f5; }}
            .signature {{ margin-top: 40px; }}
            .signature-line {{ margin-top: 30px; font-weight: 500; }}
        </style>
    </head>
    <body>
        {_letterhead_html()}

        {_doc_title_html("TATA Capital")}

        <div class="date">Date: {today_date}</div>
        
        <div class="addressee">
            <p>To,</p>
            <p><strong>M/S TATA CAPITAL HOUSING FINANCE LIMITED</strong></p>
            <p>Bangalore.</p>
        </div>
        
        <div class="salutation">Dear Sirs,</div>
        
        <div class="re-section">
            <strong>Re:</strong> No Objection Certificate for Mortgaging Flat No.{flat_no}, {tower_display}, {floor_text} Floor in the building called RRL PALM ALTEZZE situated at SY NO: 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN - 560087.
        </div>
        
        <div class="content">
            <p>This is to confirm that {customer_names}, is the bonafide owner/s of Flat No.{flat_no}, {tower_display}, {floor_text} Floor of the building known as <strong>RRL PALM ALTEZZE</strong> situated at SY NO: 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN - 560087. hereinafter referred to as "Said Property") pursuant to an Agreement of Sale / Conveyance Deed dated {agreement_display}.</p>
            
            <p>We confirm that we have obtained necessary permissions/approvals/sanctions for construction of the said Building from all the concerned competent authorities and the construction of the building as well as flat is in accordance with the approved plans. We assure that the said flat as well as the said building and the land appurtenant thereto are not subject to any encumbrance, charge or liability of any kind whatsoever and that the entire property is free and marketable. We have a clear, legal and marketable title to the Said Property and every part thereof.</p>
            
            <p>We confirm that possession of the said property has been given/shall be given in due course to (i) {customer_names}. We are aware that {customer_names}, has approached Tata Capital Housing Finance Ltd for a loan against the Said Property and Tata Capital Housing Finance Ltd. has agreed to sanction/grant the loan/Overdraft facility ("said Loan") to {customer_names}, to purchase the Said Property and have agreed to mortgage the Said Property in your favour/in favour of your security trustee as security for due repayment of the dues under the said Loan. We hereby confirm that we have no objection to the said {customer_names}, mortgaging the Said Property to your Company/in favour of your security trustee as a security for due repayment of the said Loan.</p>
            
            <p>We hereby agree to note the aforesaid charge in our books in respect of the Said Property and {customer_names}, will not be permitted to transfer, assign, sell off/cancel or in any other way/manner deal with the Said Property prejudicial to your rights/interest as the mortgagee without your prior written consent.</p>
            
            <p>We agree to inform and give proper notice to the Co-operative Society as and when formed, about the Said Property being mortgaged to your Company and to issue the Share certificate directly to your Company.</p>
            
            <p>We have taken construction finance from Bajaj Housing Finance Limited.</p>
        </div>
        
        <div class="signature">
            <p>Yours faithfully</p>
            <p style="margin-top: 15px;"><strong>For {COMPANY_NAME_FULL}</strong></p>
            <p class="signature-line" style="margin-top: 50px;">Authorized Signatory</p>
        </div>

        {_footer_band_html(customer)}
    </body>
    </html>
    '''
    return html




def _fmt_ddmmyyyy(date_str: str) -> str:
    """Convert YYYY-MM-DD (or any parseable date string) to DD-MM-YYYY.
    Returns empty string if not parseable."""
    if not date_str:
        return ""
    s = str(date_str)
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s.split("T")[0], fmt).strftime("%d-%m-%Y")
        except ValueError:
            continue
    return s


def generate_noc_bajaj_html(customer: dict) -> str:
    """Generate the Bajaj Housing Finance NOC-cum-Release request letter.

    Unlike the HDFC/BOB/TATA NOCs (which are NOCs issued *by* RRL to the
    purchaser's lender), this is a request *from* RRL *to* Bajaj Housing
    Finance (RRL's construction-finance lender) asking them to release the
    flat from their mortgage so the purchaser's bank can disburse the loan.
    """
    customer_names = format_customer_names(customer)

    flat_no = customer.get('unit_number', '') or ''
    tower_raw = (customer.get('tower') or '1').strip()
    tower_display = format_tower(tower_raw)
    saleable_area = customer.get('saleable_area', 0) or 0
    try:
        saleable_area_display = f"{int(round(float(saleable_area)))}"
    except (TypeError, ValueError):
        saleable_area_display = str(saleable_area)

    total_price = float(customer.get('total_price', 0) or 0)
    loan_amount = float(customer.get('loan_amount', 0) or 0)
    own_contribution = float(customer.get('self_contribution', 0) or 0)
    if own_contribution <= 0 and total_price > 0:
        own_contribution = max(total_price - loan_amount, 0)

    purchaser_phone = customer.get('phone', '') or ''
    lender_name = (customer.get('finance_bank') or '').strip() or 'HDFC BANK LTD'

    booking_date_disp = _fmt_ddmmyyyy(customer.get('booking_date', ''))
    agreement_date_disp = _fmt_ddmmyyyy(customer.get('agreement_date', ''))
    today_date = datetime.now().strftime("%d-%m-%Y")

    # Bajaj sanction date / ref — allow override via custom_fields, fallback to "as on record"
    bajaj_sanction_date = (
        (customer.get('custom_fields') or {}).get('bajaj_sanction_date')
        or 'as on record'
    )

    ref_no = customer.get('customer_id') or customer.get('id', '')[:8]

    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
            @page {{ size: A4; margin: 0 20mm 30mm 20mm; }}
            body {{ font-family: 'Roboto', sans-serif; font-size: 12px; line-height: 1.6; color: #1A1A1A; }}
            {_letterhead_styles()}
            .meta-row {{ display: flex; justify-content: space-between; margin-bottom: 16px; }}
            .meta-row .ref {{ font-weight: 500; }}
            .addressee {{ margin-bottom: 14px; }}
            .addressee p {{ margin: 0; }}
            .attn {{ margin-bottom: 14px; font-weight: 600; }}
            .subject {{ margin-bottom: 12px; text-align: justify; }}
            .subject strong {{ font-weight: 700; }}
            .ref-section {{ margin-bottom: 14px; }}
            .salutation {{ margin-bottom: 10px; }}
            .content {{ text-align: justify; margin-bottom: 14px; }}
            .details-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 12px 0 18px 0;
                font-size: 11.5px;
                table-layout: fixed;
            }}
            .details-table th {{
                background: #F5F5F5;
                text-align: left;
                padding: 8px 10px;
                border: 1px solid #D4AF37;
                font-weight: 700;
                color: #1A1A1A;
                width: 42%;
                vertical-align: top;
                word-wrap: break-word;
                overflow-wrap: anywhere;
            }}
            .details-table td {{
                padding: 8px 10px;
                border: 1px solid #E5E5E5;
                color: #1A1A1A;
                vertical-align: top;
                word-wrap: break-word;
                overflow-wrap: anywhere;
            }}
            /* Prevent rows from being split across pages — the long address
               row was wrapping then overlapping the next row's border. */
            .details-table tr {{
                page-break-inside: avoid;
                break-inside: avoid;
            }}
            .details-table .section-header td {{
                background: #1A1A1A;
                color: #FFFFFF;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.4px;
                padding: 8px 10px;
                text-align: center;
                border: 1px solid #1A1A1A;
            }}
            .signature {{ margin-top: 36px; }}
            .signature-line {{ margin-top: 50px; font-weight: 500; }}
        </style>
    </head>
    <body>
        {_letterhead_html()}

        {_doc_title_html("Bajaj Housing Finance")}

        <div class="meta-row">
            <div class="ref">Ref. No.: RRL/BAJAJ/{ref_no}</div>
            <div>Date: {today_date}</div>
        </div>

        <div class="addressee">
            <p>To,</p>
            <p><strong>M/s. Bajaj Housing Finance Ltd.</strong></p>
            <p>4<sup>th</sup> Floor, Bajaj Finserv Corporate Office,</p>
            <p>Off Pune-Ahmednagar Road,</p>
            <p>Viman Nagar, Pune &mdash; 411 014.</p>
        </div>

        <div class="attn">Kind Attention: Mr. Naveen Kumar</div>

        <div class="subject">
            <strong>Subject:</strong> Issue of <strong>NOC-cum-Release letter</strong> of Flat No. {flat_no} in &lsquo;{tower_display}&rsquo; of the building known as &lsquo;<strong>RRL PALM ALTEZZE</strong>&rsquo; situated at SY NO: 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN &mdash; 560087.
        </div>

        <div class="ref-section">
            <strong>Ref.:</strong> 1. Bajaj Housing Finance Sanction Letter dated {bajaj_sanction_date}
        </div>

        <div class="salutation">Respected Sir / Madam,</div>

        <div class="content">
            <p>We have sold the following Flat and you are requested to issue the <strong>NOC-cum-Release letter</strong> for the said unit at the earliest. The Purchaser/s has taken a loan from <strong>{lender_name}</strong> and their disbursement is pending. Hence, you are requested to issue the <strong>NOC-cum-Release letter</strong> at the earliest.</p>
        </div>

        <table class="details-table">
            <tr class="section-header"><td colspan="2">Details of Purchaser</td></tr>
            <tr><th>Purchaser&rsquo;s Full Name</th><td>{customer_names}</td></tr>
            <tr><th>Purchaser&rsquo;s Mobile No.</th><td>{purchaser_phone}</td></tr>
            <tr><th>Flat No.</th><td>{flat_no}</td></tr>
            <tr><th>Wing / Tower</th><td>{tower_display}</td></tr>
            <tr><th>Area (in Sq.ft)</th><td>{saleable_area_display}</td></tr>
            <tr><th>Project Name</th><td>RRL PALM ALTEZZE</td></tr>
            <tr><th>Project Location / Address</th><td>SY NO: 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN &mdash; 560087</td></tr>
            <tr><th>Consideration / Agreement Value</th><td>Rs. {format_inr(total_price)}/-</td></tr>
            <tr><th>Loan Amount</th><td>Rs. {format_inr(loan_amount)}/-</td></tr>
            <tr><th>Lender&rsquo;s Name</th><td>{lender_name}</td></tr>
            <tr><th>Own Contribution given to us</th><td>Rs. {format_inr(own_contribution)}/-</td></tr>
            <tr><th>Booking Date</th><td>{booking_date_disp or '-'}</td></tr>
            <tr><th>Agreement for Sale Date</th><td>{agreement_date_disp or '-'}</td></tr>
        </table>

        <div class="content">
            <p>Kindly do the needful at the earliest.</p>
            <p>Thanking you in anticipation.</p>
        </div>

        <div class="signature">
            <p>Yours faithfully,</p>
            <p style="margin-top: 12px;"><strong>For {COMPANY_NAME_FULL}</strong></p>
            <p class="signature-line">Authorized Signatory</p>
        </div>

        {_footer_band_html(customer)}
    </body>
    </html>
    '''
    return html
