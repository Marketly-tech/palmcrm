"""Allotment Letter document template."""
from datetime import datetime
from utils import format_indian_currency
from utils.enums import DocumentType
from documents.templates.common import format_inr, format_applicant_block, format_customer_names, format_tower
from documents.templates.default_template import get_default_template

def generate_allotment_letter_html(customer: dict) -> str:
    """Generate Allotment Letter HTML with customer data filled in"""
    
    # Format booking date
    booking_date = customer.get('booking_date', datetime.now().strftime("%d/%m/%Y"))
    if booking_date and '-' in booking_date:
        try:
            dt = datetime.strptime(booking_date, "%Y-%m-%d")
            booking_date = dt.strftime("%d/%m/%Y")
        except:
            pass
    
    # Build applicant block
    applicant_html = format_applicant_block(customer)
    co_applicant_html = format_applicant_block(customer, prefix="co_applicant_")
    
    recipient_block = f'<p>{applicant_html}</p>'
    if co_applicant_html:
        recipient_block += f'<p style="margin-top: 8px;"><strong>Co-Applicant:</strong><br/>{co_applicant_html}</p>'
    
    # Get the allotment letter template
    template = get_default_template(DocumentType.ALLOTMENT_LETTER)
    
    # Use string replacement to avoid CSS brace conflicts
    replacements = {
        '{customer_name}': customer.get('name', ''),
        '{customer_names}': format_customer_names(customer),
        '{phone}': customer.get('phone', ''),
        '{email}': customer.get('email', ''),
        '{pan_number}': customer.get('pan_number', ''),
        '{booking_date}': booking_date,
        '{unit_number}': customer.get('unit_number', ''),
        '{project}': customer.get('project', 'RRL PALM ALTEZZE'),
        '{tower}': format_tower(customer.get('tower', '')),
        '{uds}': str(customer.get('uds', 0)),
        '{saleable_area}': str(customer.get('saleable_area', 0)),
        '{total_price_formatted}': format_indian_currency(customer.get('total_price', 0)),
        '{date}': datetime.now().strftime("%d/%m/%Y"),
        '{customer_id}': customer.get('customer_id', ''),
        '{applicant_details}': recipient_block,
    }
    
    filled_html = template
    for placeholder, value in replacements.items():
        filled_html = filled_html.replace(placeholder, str(value))
    
    return filled_html
