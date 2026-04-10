"""Bank NOC document templates (HDFC, BOB, TATA Capital)."""
from datetime import datetime
from documents.templates.common import format_inr, COMPANY_NAME_FULL, format_customer_names

def generate_noc_hdfc_html(customer: dict) -> str:
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
    floor = customer.get('floor', '')
    floor_text = f"{floor}th" if floor else ""
    
    # Financial details
    total_price = customer.get('total_price', 0) or 0
    booking_amount = customer.get('booking_amount', 0) or 0
    balance = total_price - booking_amount
    loan_amount = customer.get('loan_amount', 0) or balance
    
    # Format amounts with words
    total_price_words = f"Rupees {number_to_words(total_price)} Only"
    booking_words = f"Rupees {number_to_words(booking_amount)} Only"
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
            @page {{ size: A4; margin: 25mm 20mm 25mm 20mm; }}
            body {{ font-family: 'Roboto', sans-serif; font-size: 12px; line-height: 1.8; color: #1A1A1A; }}
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
        <div class="header">
            <div class="header-title">Builder NOC</div>
        </div>
        
        <div class="date">Date: {today_date}</div>
        
        <div class="addressee">
            <p>To,</p>
            <p><strong>HDFC BANK LTD</strong></p>
            <p>NO.51, KASTURBA ROAD,</p>
            <p>BANGALORE – 560 001</p>
        </div>
        
        <div class="salutation">Dear Sir,</div>
        
        <div class="content">
            <p>This is to confirm that we have sold Flat No.{flat_no}, Tower-{tower}, {floor_text} Floor in the building called <strong>RRL PALM ALTEZZE</strong> situated at RRL Palm Altezze, SY NO: 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN - 560087, to <strong>{customer_names}</strong> for a total consideration of <strong>Rs.{format_inr(total_price)}/-</strong> ({total_price_words}) out of which <strong>Rs.{format_inr(booking_amount)}/-</strong> ({booking_words}) has been received by us and balance <strong>Rs.{format_inr(balance)}/-</strong> ({balance_words}) is due on {due_date}.</p>
            
            <p>We hereby assure you that the said flat appurtenant there to be not subject to any encumbrance, charge, or liability of any kind whatsoever and that the entire property is free and marketable. We further confirm that we have a clear legal and marketable title to the said property and every part thereof.</p>
            
            <p>We have no objection to your giving a loan of <strong>Rs.{format_inr(loan_amount)}/-</strong> ({loan_words}) to said <strong>{customer_names}</strong> owner/s of the said flat and his/their mortgaging the said flat with you by way of security for repayment notwithstanding anything to the contrary contained in our agreement dated {agreement_display} with {customer_names}.</p>
            
            <p>We have taken the construction finance from Bajaj Housing Finance Limited.</p>
            
            <p>We also undertake to inform and give proper notice to the Co-operative Housing Society as and when formed, about the flat being mortgaged. We hereby undertake to forward the original title deed for the undivided share in the land duly registered directly to HDFC without parting the same with the allotee of the flat during the pendency of the loan under intimation to the borrower.</p>
        </div>
        
        <div class="signature">
            <p><strong>For {COMPANY_NAME_FULL}</strong></p>
            <p class="signature-line" style="margin-top: 50px;">Authorized Signatory</p>
        </div>
    </body>
    </html>
    '''
    return html



def generate_noc_bob_html(customer: dict) -> str:
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
    floor = customer.get('floor', '')
    floor_text = f"{floor}th" if floor else ""
    
    total_price = customer.get('total_price', 0) or 0
    booking_amount = customer.get('booking_amount', 0) or 0
    balance = total_price - booking_amount
    loan_amount = customer.get('loan_amount', 0) or balance
    
    total_price_words = f"Rupees {number_to_words(total_price)} Only"
    booking_words = f"Rupees {number_to_words(booking_amount)} Only"
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
            @page {{ size: A4; margin: 25mm 20mm 25mm 20mm; }}
            body {{ font-family: 'Roboto', sans-serif; font-size: 12px; line-height: 1.8; color: #1A1A1A; }}
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
        <div class="header">
            <div class="header-title">Builder NOC</div>
        </div>
        
        <div class="date">Date: {today_date}</div>
        
        <div class="addressee">
            <p>To,</p>
            <p><strong>The Manager</strong></p>
            <p><strong>Bank of Baroda</strong></p>
            <p>Bangalore</p>
        </div>
        
        <div class="salutation">Dear Sir / Madam,</div>
        
        <div class="content">
            <p>This is to confirm that we have sold Flat No.{flat_no}, Tower-{tower}, {floor_text} Floor in the building called <strong>RRL PALM ALTEZZE</strong> situated at RRL Palm Altezze, SY NO: 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN - 560087, to <strong>{customer_names}</strong> for a total consideration of <strong>Rs.{format_inr(total_price)}/-</strong> ({total_price_words}) out of which <strong>Rs.{format_inr(booking_amount)}/-</strong> ({booking_words}) has been received by us and balance <strong>Rs.{format_inr(balance)}/-</strong> ({balance_words}) is due on {due_date}.</p>
            
            <p>We further confirm that we have a clear legal and marketable title to the said property and every part thereof. We have no objection to your giving a loan of <strong>Rs.{format_inr(loan_amount)}/-</strong> ({loan_words}) to said <strong>{customer_names}</strong> owner/s of the said flat and his/their mortgaging the said flat with you by way of security for repayment notwithstanding anything to the contrary contained in our agreement dated {agreement_display} with {customer_names}.</p>
        </div>
        
        <div class="signature">
            <p><strong>For {COMPANY_NAME_FULL}</strong></p>
            <p class="signature-line" style="margin-top: 50px;">Authorized Signatory</p>
        </div>
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
            @page {{ size: A4; margin: 25mm 20mm 25mm 20mm; }}
            body {{ font-family: 'Roboto', sans-serif; font-size: 12px; line-height: 1.8; color: #1A1A1A; }}
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
        <div class="header">
            <div class="header-title">Builder NOC</div>
        </div>
        
        <div class="date">Date: {today_date}</div>
        
        <div class="addressee">
            <p>To,</p>
            <p><strong>M/S TATA CAPITAL HOUSING FINANCE LIMITED</strong></p>
            <p>Bangalore.</p>
        </div>
        
        <div class="salutation">Dear Sirs,</div>
        
        <div class="re-section">
            <strong>Re:</strong> No Objection Certificate for Mortgaging Flat No.{flat_no}, Tower-{tower}, {floor_text} Floor in the building called RRL PALM ALTEZZE situated at SY NO: 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN - 560087.
        </div>
        
        <div class="content">
            <p>This is to confirm that {customer_names}, is the bonafide owner/s of Flat No.{flat_no}, Tower-{tower}, {floor_text} Floor of the building known as <strong>RRL PALM ALTEZZE</strong> situated at SY NO: 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN - 560087. hereinafter referred to as "Said Property") pursuant to an Agreement of Sale / Conveyance Deed dated {agreement_display}.</p>
            
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
    </body>
    </html>
    '''
    return html


