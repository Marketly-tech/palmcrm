"""Allotment Letter document template."""
from datetime import datetime
from utils import format_indian_currency
from utils.enums import DocumentType
from documents.templates.common import format_inr
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
    
    # Get the allotment letter template
    template = get_default_template(DocumentType.ALLOTMENT_LETTER)
    
    # Use string replacement to avoid CSS brace conflicts
    replacements = {
        '{customer_name}': customer.get('name', ''),
        '{phone}': customer.get('phone', ''),
        '{email}': customer.get('email', ''),
        '{pan_number}': customer.get('pan_number', ''),
        '{booking_date}': booking_date,
        '{unit_number}': customer.get('unit_number', ''),
        '{project}': customer.get('project', 'RRL PALM ALTEZZE'),
        '{tower}': customer.get('tower', ''),
        '{uds}': str(customer.get('uds', 0)),
        '{saleable_area}': str(customer.get('saleable_area', 0)),
        '{total_price_formatted}': format_indian_currency(customer.get('total_price', 0)),
        '{date}': datetime.now().strftime("%d/%m/%Y"),
        '{customer_id}': customer.get('customer_id', '')
    }
    
    filled_html = template
    for placeholder, value in replacements.items():
        filled_html = filled_html.replace(placeholder, str(value))
    
    return filled_html


