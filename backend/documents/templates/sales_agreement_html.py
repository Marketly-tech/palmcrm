"""Sales Agreement dynamic HTML generation."""
from datetime import datetime
from utils import number_to_indian_words, format_indian_currency, get_ordinal_suffix
from documents.templates.common import (
    format_inr, format_applicant_block, calculate_age, get_salutation,
    get_logo_img_tag, COMPANY_NAME, format_customer_names
)
from documents.templates.sales_agreement_template import generate_sales_agreement_template

def generate_sales_agreement_html(customer: dict, schedule_items: list, transactions: list = None) -> str:
    """Generate Sales Agreement HTML with customer data filled in"""
    
    # Helper function to convert year to words
    def year_to_words(year):
        """Convert year like 2026 to 'Two Thousand and Twenty Six'"""
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
                'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
                'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        year = int(year)
        thousands = year // 1000
        hundreds = (year % 1000) // 100
        remainder = year % 100
        
        result = []
        if thousands == 2:
            result.append("Two Thousand")
        elif thousands == 1:
            result.append("One Thousand")
        
        if hundreds > 0:
            result.append(ones[hundreds] + " Hundred")
        
        if remainder > 0:
            if result:
                result.append("and")
            if remainder < 20:
                result.append(ones[remainder])
            else:
                tens_word = tens[remainder // 10]
                ones_word = ones[remainder % 10]
                if ones_word:
                    result.append(tens_word + " " + ones_word)
                else:
                    result.append(tens_word)
        
        return " ".join(result)
    
    # Format dates - "14th Day of February, Two Thousand and Twenty Six- (14-02-2026)"
    agreement_date = datetime.now()
    day_ordinal = str(agreement_date.day) + get_ordinal_suffix(agreement_date.day)
    month_name = agreement_date.strftime("%B")
    year_words = year_to_words(agreement_date.year)
    date_numeric = agreement_date.strftime("%d-%m-%Y")
    agreement_date_text = f"{day_ordinal} Day of {month_name}, {year_words}- ({date_numeric})"
    
    possession_date = "30-09-2030"  # Fixed possession date for all agreements
    
    # Format currency amounts
    def fmt(amount):
        return format_indian_currency(amount)
    
    # Calculate age from date_of_birth using common utility
    age = calculate_age(customer.get('date_of_birth'))
    
    # Generate salutation based on gender using common utility
    salutation = get_salutation(customer.get('gender'))
    
    # Build applicant details block for the template
    applicant_block = format_applicant_block(customer)
    co_applicant_block = format_applicant_block(customer, prefix="co_applicant_")
    
    applicant_details_html = f'<p>{applicant_block}</p>'
    if co_applicant_block:
        applicant_details_html += f'<p style="margin-top: 10px;"><strong>Co-Applicant:</strong><br/>{co_applicant_block}</p>'
    
    # Generate floor ordinal (1st, 2nd, 3rd, etc.)
    floor = customer.get('floor', 0) or 0
    floor_int = int(floor) if floor else 0
    floor_ordinal = str(floor_int) + get_ordinal_suffix(floor_int) if floor_int > 0 else "Ground"
    
    # Additional parking text
    additional_parking = customer.get('additional_parking', 0) or 0
    additional_parking_text = f" + {additional_parking} additional parking space(s)" if additional_parking > 0 else ""
    
    # Get AADHAAR number from top-level field (not custom_fields)
    aadhaar_number = customer.get('aadhar_number', '') or customer.get('aadhaar_number', '') or ''
    
    # ==================== PAYMENT SCHEDULE (Milestones from Payment Schedule Tab) ====================
    payment_schedule_rows = ""
    total = customer.get('total_price', 0) or 0
    booking_amount = customer.get('booking_amount', 0) or 0
    cumulative_pct = 0  # Track cumulative percentage
    
    # Use schedule_items from Payment Schedule tab (the 13-point milestone schedule)
    if schedule_items and len(schedule_items) > 0:
        for i, item in enumerate(schedule_items, 1):
            milestone_name = item.get('installment_name', '') or item.get('milestone', '')
            percentage = item.get('percentage', 0) or 0
            amount = item.get('amount', 0) or 0
            cumulative_pct += percentage  # Add to cumulative
            
            # If amount is 0 but we have percentage and total, calculate
            if amount == 0 and percentage > 0 and total > 0:
                amount = total * percentage / 100
            
            payment_schedule_rows += f'''
            <tr>
                <td style="text-align: center;">{i}</td>
                <td>{milestone_name}</td>
                <td style="text-align: center;">{percentage}%</td>
                <td style="text-align: center;">{cumulative_pct}%</td>
                <td class="amount">{fmt(amount)}</td>
            </tr>
            '''
    else:
        # Use default 13-point payment schedule if no schedule_items
        default_milestones = [
            ("Initial Booking Amount (within 10 days of Booking)", 10),
            ("Post Execution of Agreement", 10),
            ("On Completion of Foundation", 10),
            ("On Completion of Podium Slab", 10),
            ("Upon Completion of 2nd Floor Roof Slab", 5),
            ("Upon Completion of 6th Floor Roof Slab", 5),
            ("Upon Completion of 10th Floor Roof Slab", 5),
            ("Upon Completion of 14th Floor Roof Slab", 5),
            ("Upon Completion of 18th Floor Roof Slab", 5),
            ("Upon Completion of 22nd Floor Roof Slab", 5),
            ("Upon Completion of Top Roof Slab", 10),
            ("Upon Completion of Flooring of Particular Property", 10),
            ("Upon Handover / Possession / Registration", 10),
        ]
        cumulative_pct = 0
        for i, (name, pct) in enumerate(default_milestones, 1):
            cumulative_pct += pct
            amount = total * pct / 100 if total > 0 else 0
            payment_schedule_rows += f'''
            <tr>
                <td style="text-align: center;">{i}</td>
                <td>{name}</td>
                <td style="text-align: center;">{pct}%</td>
                <td style="text-align: center;">{cumulative_pct}%</td>
                <td class="amount">{fmt(amount)}</td>
            </tr>
            '''
    
    # ==================== TRANSACTION DETAILS (Booking + Agreement Payments) ====================
    transaction_rows = ""
    total_received_amount = 0
    row_num = 1
    
    # Total received = sum of ALL transactions (not just booking/agreement)
    all_txn_total = sum(float(t.get('amount', 0) or 0) for t in (transactions or []))
    
    # Build transaction rows from actual transaction records
    if transactions and len(transactions) > 0:
        for txn in transactions:
            # Check both legacy 'transaction_type' and new 'transaction_stage' fields
            stage = (txn.get('transaction_stage', '') or txn.get('transaction_type', '') or '').lower()
            # Include booking and agreement stage transactions
            if stage in ['booking', 'booking_amount', 'agreement', 'agreement_amount', 'post_agreement']:
                amount = txn.get('amount', 0) or 0
                total_received_amount += amount
                stage_display = 'Booking' if 'booking' in stage else 'Agreement'
                txn_date = txn.get('transaction_date', '')
                bank = txn.get('bank_name', '') or ''
                txn_no = txn.get('transaction_number', '') or ''
                bank_ref = f"{bank} - {txn_no}" if bank or txn_no else stage_display + " Payment"
                
                transaction_rows += f'''
                <tr>
                    <td style="text-align: center;">{row_num}</td>
                    <td>{txn_date}</td>
                    <td>{stage_display}</td>
                    <td>{bank_ref}</td>
                    <td class="amount">{fmt(amount)}</td>
                </tr>
                '''
                row_num += 1
    
    # Fallback: if no booking transactions found but customer has booking_amount, add it
    if booking_amount > 0 and not any(
        (txn.get('transaction_stage', '') or txn.get('transaction_type', '') or '').lower() in ['booking', 'booking_amount']
        for txn in (transactions or [])
    ):
        total_received_amount += booking_amount
        booking_date_val = customer.get('booking_date', '')
        txn_bank = customer.get('transaction_bank', '') or ''
        txn_ref = customer.get('transaction_details', '') or ''
        bank_ref = f"{txn_bank} - {txn_ref}" if txn_bank or txn_ref else "Booking Payment"
        
        transaction_rows = f'''
        <tr>
            <td style="text-align: center;">1</td>
            <td>{booking_date_val}</td>
            <td>Booking</td>
            <td>{bank_ref}</td>
            <td class="amount">{fmt(booking_amount)}</td>
        </tr>
        ''' + transaction_rows
        # Re-number remaining rows
        row_num += 1
    
    # If no transactions and no booking amount
    if not transaction_rows:
        transaction_rows = '''
        <tr>
            <td colspan="5" style="text-align: center; color: #666; padding: 15px;">No payments received yet</td>
        </tr>
        '''
    
    # Get template and fill in values using string replacement to avoid CSS conflicts
    template = generate_sales_agreement_template()
    
    replacements = {
        '{agreement_date_text}': agreement_date_text,
        '{customer_name}': customer.get('name', ''),
        '{customer_names}': format_customer_names(customer),
        '{age}': age,
        '{salutation}': salutation,
        '{father_name}': customer.get('father_name', ''),
        '{address}': customer.get('address', ''),
        '{aadhaar_number}': aadhaar_number,
        '{pan_number}': customer.get('pan_number', ''),
        '{phone}': customer.get('phone', ''),
        '{project}': customer.get('project', 'RRL PALM ALTEZZE'),
        '{tower}': customer.get('tower', ''),
        '{unit_number}': customer.get('unit_number', ''),
        '{floor}': str(customer.get('floor', '')),
        '{floor_ordinal}': floor_ordinal,
        '{bhk_type}': customer.get('bhk_type', ''),
        '{saleable_area}': str(customer.get('saleable_area', 0)),
        '{uds}': str(customer.get('uds', 0)),
        '{additional_parking}': str(customer.get('additional_parking', 0)),
        '{additional_parking_text}': additional_parking_text,
        '{base_price_formatted}': fmt(customer.get('base_price', 0)),
        '{club_house_formatted}': fmt(customer.get('club_house_charges', 200000)),
        '{parking_charges_formatted}': fmt(customer.get('additional_parking_charges', 0)),
        '{labour_cess_formatted}': fmt(customer.get('labour_cess', 0)),
        '{gst_formatted}': fmt(customer.get('gst_amount', 0)),
        '{total_price_formatted}': fmt(customer.get('total_price', 0)),
        '{total_price_words}': number_to_indian_words(customer.get('total_price', 0)),
        '{booking_amount_formatted}': fmt(customer.get('booking_amount', 0)),
        '{booking_amount_words}': number_to_indian_words(customer.get('booking_amount', 0)),
        '{booking_date}': customer.get('booking_date', ''),
        '{possession_date}': possession_date,
        '{payment_schedule_rows}': payment_schedule_rows,
        '{transaction_rows}': transaction_rows,
        '{total_received_formatted}': fmt(all_txn_total),
        '{total_received_words}': number_to_indian_words(int(all_txn_total)),
        '{logo_img}': get_logo_img_tag(120),
        '{company_name}': COMPANY_NAME,
        '{applicant_details_block}': applicant_details_html,
        '{date}': datetime.now().strftime("%d/%m/%Y"),
        '{customer_id}': customer.get('customer_id', '')
    }
    
    filled_html = template
    for placeholder, value in replacements.items():
        filled_html = filled_html.replace(placeholder, str(value))
    
    return filled_html

