"""Default document templates by type."""
from utils.enums import DocumentType
from documents.templates.sales_agreement_template import generate_sales_agreement_template
from documents.templates.common import get_logo_img_tag, COMPANY_NAME, COMPANY_NAME_UPPER, COMPANY_NAME_FULL

def get_default_template(doc_type: DocumentType) -> str:
    logo_img = get_logo_img_tag(120)
    templates = {
        DocumentType.SALES_AGREEMENT: generate_sales_agreement_template(),
        DocumentType.ALLOTMENT_LETTER: """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Roboto', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #1A1A1A;
            background: #fff;
            padding: 25px 40px;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #D4AF37;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        
        .logo-section {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .logo {
            width: 120px;
        }
        
        .logo img {
            width: 120px;
            height: auto;
        }
        
        .company-name {
            font-size: 16px;
            font-weight: 700;
            color: #1A1A1A;
        }
        
        .company-tagline {
            font-size: 10px;
            color: #666;
        }
        
        .document-title {
            background: #1A1A1A;
            color: #D4AF37;
            padding: 8px 18px;
            border-radius: 4px;
            font-weight: 500;
            font-size: 12px;
            text-transform: uppercase;
        }
        
        .recipient {
            margin-bottom: 15px;
            padding: 15px;
            background: #fafafa;
            border-left: 4px solid #D4AF37;
        }
        
        .recipient p {
            margin: 3px 0;
            font-size: 11px;
        }
        
        .highlight {
            color: #D4AF37;
            font-weight: 600;
        }
        
        .subject {
            margin: 15px 0;
            font-weight: 600;
            color: #1A1A1A;
        }
        
        .greeting {
            margin: 10px 0;
        }
        
        .content {
            text-align: justify;
            margin: 12px 0;
            font-size: 10.5pt;
        }
        
        .section-title {
            font-weight: 600;
            color: #D4AF37;
            margin: 18px 0 10px 0;
            padding-bottom: 5px;
            border-bottom: 2px solid #D4AF37;
            font-size: 11pt;
        }
        
        .terms {
            margin-left: 15px;
        }
        
        .terms p {
            margin: 10px 0;
            text-align: justify;
            font-size: 10pt;
        }
        
        .terms-number {
            font-weight: 600;
            color: #D4AF37;
        }
        
        table.details {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        
        table.details th, table.details td {
            border: 1px solid #D4AF37;
            padding: 8px 12px;
            text-align: left;
            font-size: 10.5pt;
        }
        
        table.details th {
            background: #1A1A1A;
            color: #D4AF37;
            font-weight: 500;
            width: 40%;
        }
        
        table.details td {
            background: #fafafa;
        }
        
        .signature-section {
            margin-top: 35px;
            display: flex;
            justify-content: space-between;
        }
        
        .signature-box {
            width: 45%;
        }
        
        .signature-line {
            border-top: 1px solid #1A1A1A;
            margin-top: 50px;
            padding-top: 5px;
        }
        
        .declaration {
            margin-top: 25px;
            padding: 15px;
            border: 2px solid #D4AF37;
            background: #fafafa;
            font-size: 10pt;
        }
        
        .bank-details {
            margin: 12px 0;
            padding: 12px;
            background: #1A1A1A;
            color: #fff;
            border-radius: 4px;
        }
        
        .bank-details p {
            margin: 3px 0;
            font-size: 10pt;
        }
        
        .bank-details strong {
            color: #D4AF37;
        }
        
        .footer {
            margin-top: 25px;
            padding-top: 15px;
            border-top: 2px solid #D4AF37;
            text-align: center;
            font-size: 9pt;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-section">
            <div class="logo">""" + logo_img + """</div>
            <div>
                <div class="company-name">""" + COMPANY_NAME + """</div>
                <div class="company-tagline">Beyond Homes. A Lifestyle</div>
            </div>
        </div>
        <div class="document-title">Allotment Letter</div>
    </div>
    
    <div class="recipient">
        <p><strong>To,</strong></p>
        {applicant_details}
    </div>
    
    <div class="subject">
        <p>Subject: Confirmation of Allotment</p>
    </div>
    
    <div class="greeting">
        <p>Dear Sir/Madam,</p>
    </div>
    
    <div class="content">
        <p>We are issuing this allotment letter pursuant to your submission of an expression of interest dated <span class="highlight">{booking_date}</span>, requesting unit No. <span class="highlight">{unit_number}</span> in our project being developed under the name of "<strong>{project}</strong>" RERA No. PRM/KA/RERA/1251/308/PR/141025/008167. Upon due consideration of your EOI, we are pleased to confirm your booking and allot Flat No. <span class="highlight">{unit_number}</span> in "{project}" subject to the Terms and conditions set out herein. We take this opportunity to welcome you to """ + '"' + COMPANY_NAME_FULL + '"' + """ family and are pleased that you have chosen to purchase your home from us.</p>
        
        <p style="margin-top: 12px;">You hereby acknowledge and confirm that the copies of title documents have been handed over to you and that you have scrutinized and are satisfied with the title of the Developer to the project being good and marketable.</p>
    </div>
    
    <div class="section-title">A. ALLOTMENT DETAILS</div>
    
    <table class="details">
        <tr>
            <th>Heading</th>
            <th>Particulars</th>
        </tr>
        <tr>
            <td>Name of the Project</td>
            <td><span class="highlight">{project}</span></td>
        </tr>
        <tr>
            <td>RERA No.</td>
            <td>PRM/KA/RERA/1251/308/PR/141025/008167</td>
        </tr>
        <tr>
            <td>Flat Number</td>
            <td><span class="highlight">{tower} - {unit_number}</span></td>
        </tr>
        <tr>
            <td>UDS (in Sqft)</td>
            <td><span class="highlight">{uds}</span></td>
        </tr>
        <tr>
            <td>Super Built-up Area (in Sq ft)</td>
            <td><span class="highlight">{saleable_area}</span></td>
        </tr>
        <tr>
            <td>Total Cost of the Flat including GST</td>
            <td><span class="highlight">Rs. {total_price_formatted}/-</span></td>
        </tr>
    </table>
    
    <div class="section-title">TERMS & CONDITIONS</div>
    
    <div class="terms">
        <p><span class="terms-number">1.</span> In consideration of and subject to the Allottee(s) complying with the terms and conditions of this letter, executing and registering necessary documents and agreements under applicable law, and agreeing to make and making timely payment of amounts due, the developer allots the Flat in the project "{project}" in the favour of <span class="highlight">{customer_names}</span>.</p>
        
        <p><span class="terms-number">2.</span> All payments to be made by A/c Payee Cheque/Banker Cheque/Pay order/Demand Draft at Bangalore only or through Electronic Fund Transfer (EFT) mode drawn in favor of/to the account of """ + '"' + COMPANY_NAME_FULL + '"' + """</p>
        
        <div class="bank-details">
            <p><strong>Account Holder's Name:</strong> RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED</p>
            <p><strong>Bank Name:</strong> HDFC BANK</p>
            <p><strong>Branch Name:</strong> SOMPURA</p>
            <p><strong>Account No.:</strong> 57500001802063</p>
            <p><strong>IFSC:</strong> HDFC0009590</p>
        </div>
        
        <p><span class="terms-number">3.</span> The Allottee shall be liable to pay the total sale consideration (more fully described in the cost sheet) and other charges as specified herein together with the applicable government taxes and levies as per the payment plan annexed herewith, time being of the essence.</p>
        
        <p><span class="terms-number">4.</span> The Allottee has applied for booking and allotment of Flat being fully aware of the cost of the Flat, and also of the tax regime of GST. The Applicant also confirms that he/she shall not claim any GST credit and/or claim any reduction in price of the Flat due to application of GST.</p>
        
        <p><span class="terms-number">5.</span> To avoid penal consequences under the Income Tax Act 1961, the Allottee is required to comply with provisions of section 194IA of the Income Tax Act, 1961, by deduction Tax at Source (TDS) at the prevailing rate from installment/payment. The Allottee shall be required to submit TDS Certificate and challan showing proof of deposition of the same within 7 (Seven) days from the date of tax so deposited to the Developer so that the appropriate credit may be allowed to the account of the Allottee.</p>
        
        <p><span class="terms-number">6.</span> Taxation particulars of Developer is as follows:</p>
        <p style="margin-left: 20px;">PAN No: AAKCR4125J</p>
        <p style="margin-left: 20px;">GST No: 29AAKCR4125J1Z2</p>
        
        <p><span class="terms-number">7.</span> If the upfront advance is paid by cheque, the confirmation of allotment is conditional upon realization of the cheque and funds being credited to the developer's account within 7 (Seven) days of submission of the EOI. In the event the cheque is dishonored for the first time, a sum of Rs.10,000/- (Rupees Ten Thousand Only) will be debited from the Allottee's account in addition to bank charges. In the event such default repeats for the second time, a sum of Rs.20,000/- (Rupees Twenty Thousand Only) will be debited from the Allottee's account in addition to bank charges. In the event such default repeats for the third time, the developer reserves the right to terminate this letter, at sole discretion.</p>
        
        <p><span class="terms-number">8.</span> In the event of cancellation and/or termination of documents and agreements executed and registered pursuant to this Letter, the Allottee agrees to forfeit, in the Developer's favor, the application amount paid by the Allottee plus an amount equal to 5% (Five percent) of the Total Sale Consideration for the allotted Flat and amounts paid by the Allottee on account of applicable GST. The balance amount, if any, shall be refunded to the Allottee, without interest, within 60 (sixty) days from the resale of the unit to a third party.</p>
        
        <p><span class="terms-number">9.</span> Stamp duty and registration charges on actuals and as per prevailing rates shall be payable by the Allottee over and above the Total Sale Consideration.</p>
        
        <p><span class="terms-number">10.</span> In the event any amount by the Allottee is prepaid, the Developer is entitled to retain and adjust the balance/excess amounts received against the next installment due, without paying any interest on such additional amounts.</p>
        
        <p><span class="terms-number">11.</span> For this Project, the schedule of payments is linked to stage-wise completion of the Flat, which schedule has been communicated to and accepted by the Allottee at the time of submitting the EOI. The payment schedule will also be included as an annexure to the agreement of sale.</p>
        
        <p><span class="terms-number">12.</span> Any delay or default in payment by the Allottee will attract penal interest as per the Rules on the Outstanding amount calculated from the applicable due dates till the date of actual receipt.</p>
        
        <p><span class="terms-number">13.</span> This Letter is neither transferable nor assignable, without the Developer's prior written consent and upon payment of including but not limited to such administrative charges as may be specified by the Developer in this regard.</p>
        
        <p><span class="terms-number">14.</span> Pre EMI (Interest Only) will be paid by the builder till the completion of the flat or ready for interior. Rate of interest will be calculated considering 30-year tenure irrespective of client's tenure period. As per the current repo rate, the banker is lending at 7.15% as the lower rate of interest, if there is any change in repo rate in the future, the changes will be auto applied.</p>
        
        <p><span class="terms-number">15.</span> <strong>Guidelines for External Vendors:</strong> Should you choose to engage a service provider other than the In-House Team, please be advised that the following security protocols will strictly apply to safeguard the property: Security Deposit of Rs.2,00,000 (Two Lakhs) must be maintained. The flat owner remains fully liable for any damages caused by their vendor to the premises.</p>
        
        <p><span class="terms-number">16.</span> Maintenance will be collected for 12 months, Rs. 3 Per sqft per month, should be paid before registration along with GST 18% on above maintenance. Corpus fund collected for 12 months at Rs. 2.5 Per sqft per month. Car parking will be allotted based on sequential basis.</p>
        
        <p><span class="terms-number">17.</span> These terms and conditions shall be deemed to be an integral part of the duly executed agreement for sale. Any and all disputes in relation to this Letter shall be referred exclusively to the jurisdictional Real Estate Regulatory Authority, for resolution in accordance with applicable procedure.</p>
    </div>
    
    <div class="declaration">
        <p>I/We, <span class="highlight">{customer_names}</span> have fully read and understood the terms and conditions as set out in this Letter and Schedules hereto. I/We undertake to abide by such terms and conditions including any amendment therein from time to time. I/We further declare that the details/information provided in the Letter are true and correct.</p>
    </div>
    
    <div class="signature-section">
        <div class="signature-box">
            <p><strong>FOR """ + COMPANY_NAME_UPPER + """</strong></p>
            <div class="signature-line">
                <p>Authorized Signatory</p>
            </div>
        </div>
        <div class="signature-box">
            <p><strong>ALLOTTEE SIGNATURES</strong></p>
            <div class="signature-line">
                <p>{customer_names}</p>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p><strong>""" + COMPANY_NAME + """</strong></p>
        <p>www.rrlbuildersanddevelopers.com</p>
        <p>Date: {date} | Ref: {customer_id}</p>
    </div>
</body>
</html>
""",
    }
    return templates.get(doc_type, "Template not found")

# ==================== PDF GENERATION ====================
