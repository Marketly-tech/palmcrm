"""Terms and Conditions document template."""
from documents.templates.common import get_logo_img_tag, COMPANY_NAME, COMPANY_NAME_FULL, COMPANY_NAME_UPPER, format_customer_names

def generate_terms_and_conditions_html(customer: dict) -> str:
    """Generate a Terms and Conditions PDF with the allotment letter terms"""
    
    project = customer.get('project', 'RRL Palm Altezze')
    customer_name = format_customer_names(customer)
    unit_number = customer.get('unit_number', '')
    
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
                padding: 20px 35px;
                margin: 0;
                color: #1A1A1A;
                font-size: 10px;
                line-height: 1.5;
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
                width: 80px;
            }}
            
            .logo img {{
                width: 80px;
                height: auto;
            }}
            
            .company-name {{
                font-size: 14px;
                font-weight: 700;
                color: #1A1A1A;
            }}
            
            .company-tagline {{
                font-size: 8px;
                color: #D4AF37;
                font-style: italic;
            }}
            
            .document-title {{
                font-size: 16px;
                font-weight: 700;
                color: #1A1A1A;
                text-align: right;
            }}
            
            .intro {{
                margin-bottom: 15px;
                padding: 10px;
                background: #f9f9f9;
                border-left: 3px solid #D4AF37;
            }}
            
            .terms-list {{
                counter-reset: term-counter;
            }}
            
            .term-item {{
                margin-bottom: 10px;
                padding: 8px 10px;
                background: #fafafa;
                border-radius: 4px;
                border-left: 2px solid #e0e0e0;
            }}
            
            .term-item:hover {{
                border-left-color: #D4AF37;
            }}
            
            .term-number {{
                display: inline-block;
                width: 20px;
                height: 20px;
                background: #1A1A1A;
                color: #D4AF37;
                border-radius: 50%;
                text-align: center;
                line-height: 20px;
                font-weight: 600;
                font-size: 9px;
                margin-right: 8px;
            }}
            
            .term-text {{
                display: inline;
            }}
            
            .highlight {{
                color: #D4AF37;
                font-weight: 600;
            }}
            
            .bank-details {{
                margin: 10px 0;
                padding: 8px;
                background: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }}
            
            .bank-details p {{
                margin: 3px 0;
            }}
            
            .acceptance {{
                margin-top: 20px;
                padding: 12px;
                background: #1A1A1A;
                color: #fff;
                border-radius: 6px;
            }}
            
            .acceptance .highlight {{
                color: #D4AF37;
            }}
            
            .signature-section {{
                margin-top: 30px;
                display: flex;
                justify-content: space-between;
            }}
            
            .signature-box {{
                text-align: center;
                width: 180px;
            }}
            
            .signature-line {{
                border-top: 1px solid #333;
                margin-top: 35px;
                padding-top: 5px;
                font-size: 9px;
            }}
            
            .footer {{
                margin-top: 15px;
                padding-top: 10px;
                border-top: 2px solid #D4AF37;
                font-size: 8px;
                color: #666;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo-section">
                <div class="logo">{get_logo_img_tag(80)}</div>
                <div>
                    <div class="company-name">{COMPANY_NAME}</div>
                    <div class="company-tagline">Beyond Homes. A Lifestyle</div>
                </div>
            </div>
            <div class="document-title">Terms & Conditions</div>
        </div>
        
        <div class="intro">
            <p>The following Terms and Conditions govern the allotment of <span class="highlight">Unit No. {unit_number}</span> 
            in project <span class="highlight">{project}</span> to <span class="highlight">{customer_name}</span>. 
            Please read carefully and acknowledge your understanding and acceptance.</p>
        </div>
        
        <div class="terms-list">
            <div class="term-item">
                <span class="term-number">1</span>
                <span class="term-text">In consideration of and subject to the Allottee(s) complying with the terms and conditions of this letter, executing and registering necessary documents and agreements under applicable law, and agreeing to make and making timely payment of amounts due, the developer allots the Flat in the project "{project}" in the favour of <span class="highlight">{customer_name}</span>.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">2</span>
                <span class="term-text">All payments to be made by A/c Payee Cheque/Banker Cheque/Pay order/Demand Draft at Bangalore only or through Electronic Fund Transfer (EFT) mode drawn in favor of/to the account of <strong>"{COMPANY_NAME_UPPER}"</strong></span>
                <div class="bank-details">
                    <p><strong>Account Holder's Name:</strong> RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED</p>
                    <p><strong>Bank Name:</strong> HDFC BANK</p>
                    <p><strong>Branch Name:</strong> SOMPURA</p>
                    <p><strong>Account No.:</strong> 57500001802063</p>
                    <p><strong>IFSC:</strong> HDFC0009590</p>
                </div>
            </div>
            
            <div class="term-item">
                <span class="term-number">3</span>
                <span class="term-text">The Allottee shall be liable to pay the total sale consideration (more fully described in the cost sheet) and other charges as specified herein together with the applicable government taxes and levies as per the payment plan annexed herewith, time being of the essence.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">4</span>
                <span class="term-text">The Allottee has applied for booking and allotment of Flat being fully aware of the cost of the Flat, and also of the tax regime of GST. The Applicant also confirms that he/she shall not claim any GST credit and/or claim any reduction in price of the Flat due to application of GST.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">5</span>
                <span class="term-text">To avoid penal consequences under the Income Tax Act 1961, the Allottee is required to comply with provisions of section 194IA of the Income Tax Act, 1961, by deduction Tax at Source (TDS) at the prevailing rate from installment/payment. The Allottee shall be required to submit TDS Certificate and challan showing proof of deposition of the same within 7 (Seven) days from the date of tax so deposited to the Developer.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">6</span>
                <span class="term-text">Taxation particulars of Developer: PAN - AAKCR4125J | GST - 29AAKCR4125J1Z2</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">7</span>
                <span class="term-text">If the upfront advance is paid by cheque, the confirmation of allotment is conditional upon realization of the cheque and funds being credited to the developer's account within 7 (Seven) days. In the event the cheque is dishonored, penalty charges will apply as per company policy.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">8</span>
                <span class="term-text">In the event of cancellation and/or termination, the Allottee agrees to forfeit, in the Developer's favor, the application amount paid plus an amount equal to 5% (Five percent) of the Total Sale Consideration and GST amounts paid. The balance amount shall be refunded within 60 days from the resale of the unit.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">9</span>
                <span class="term-text">Stamp duty and registration charges on actuals and as per prevailing rates shall be payable by the Allottee over and above the Total Sale Consideration.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">10</span>
                <span class="term-text">In the event any amount by the Allottee is prepaid, the Developer is entitled to retain and adjust the balance/excess amounts received against the next installment due, without paying any interest on such additional amounts.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">11</span>
                <span class="term-text">For this Project, the schedule of payments is linked to stage-wise completion of the Flat. The payment schedule will also be included as an annexure to the agreement of sale.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">12</span>
                <span class="term-text">Any delay or default in payment by the Allottee will attract penal interest as per the Rules on the Outstanding amount calculated from the applicable due dates till the date of actual receipt.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">13</span>
                <span class="term-text">This Letter is neither transferable nor assignable, without the Developer's prior written consent and upon payment of administrative charges as may be specified.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">14</span>
                <span class="term-text">Pre EMI (Interest Only) will be paid by the builder till the completion of the flat or ready for interior. Rate of interest will be calculated considering 30-year tenure irrespective of client's tenure period.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">15</span>
                <span class="term-text"><strong>Guidelines for External Vendors:</strong> Should you choose to engage a service provider other than the In-House Team, please be advised that a Security Deposit of Rs.2,00,000 (Two Lakhs) must be maintained. The flat owner remains fully liable for any damages caused by their vendor to the premises.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">16</span>
                <span class="term-text">Maintenance will be collected for 12 months at Rs. 3 Per sqft per month, payable before registration along with GST 18%. Corpus fund collected for 12 months at Rs. 2.5 Per sqft per month. Car parking will be allotted on sequential basis.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">17</span>
                <span class="term-text">These terms and conditions shall be deemed to be an integral part of the duly executed agreement for sale. Any disputes shall be referred exclusively to the jurisdictional Real Estate Regulatory Authority (RERA Karnataka).</span>
            </div>
        </div>
        
        <div class="acceptance">
            <p>I/We, <span class="highlight">Mr./Mrs. {customer_name}</span> have fully read and understood the terms and conditions as set out in this document. I/We undertake to abide by such terms and conditions including any amendment therein from time to time. I/We further declare that the details/information provided are true and correct.</p>
        </div>
        
        <div class="signature-section">
            <div class="signature-box">
                <div class="signature-line">Customer Signature</div>
            </div>
            <div class="signature-box">
                <div class="signature-line">Co-Applicant Signature</div>
            </div>
            <div class="signature-box">
                <div class="signature-line">For {COMPANY_NAME}</div>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>{COMPANY_NAME}</strong></p>
            <p>RERA No: PRM/KA/RERA/1251/308/PR/141025/008167 | CIN: U70109KA2015PTC081706</p>
            <p>www.rrlbuilders.in</p>
        </div>
    </body>
    </html>
    '''
    return html


