"""Sales Agreement dynamic HTML generation."""
from datetime import datetime
from utils import number_to_indian_words, format_indian_currency, get_ordinal_suffix
from documents.templates.common import (
    format_inr, calculate_age, get_salutation,
    get_logo_img_tag, COMPANY_NAME, format_customer_names,
    build_agreement_date_text, build_applicant_details_block,
    build_payment_schedule_rows_html, build_transaction_rows_html,
)
from documents.templates.sales_agreement_template import generate_sales_agreement_template


def generate_sales_agreement_html(customer: dict, schedule_items: list, transactions: list = None) -> str:
    """Generate Sales Agreement HTML with customer data filled in"""

    # Sales Agreement date string
    agreement_date_text = build_agreement_date_text(datetime.now())
    possession_date = "30-09-2030"  # Fixed possession date for all agreements

    # Format currency amounts (Rs. 12,34,567.00 style)
    def fmt(amount):
        return format_indian_currency(amount)

    # Personal details
    age = calculate_age(customer.get('date_of_birth'))
    salutation = get_salutation(customer.get('gender'))
    applicant_details_html = build_applicant_details_block(customer)

    # Floor ordinal (1st, 2nd, 3rd, etc.)
    floor = customer.get('floor', 0) or 0
    floor_int = int(floor) if floor else 0
    floor_ordinal = str(floor_int) + get_ordinal_suffix(floor_int) if floor_int > 0 else "Ground"

    additional_parking = customer.get('additional_parking', 0) or 0
    additional_parking_text = f" + {additional_parking} additional parking space(s)" if additional_parking > 0 else ""

    aadhaar_number = customer.get('aadhar_number', '') or customer.get('aadhaar_number', '') or ''

    # Payment schedule + transaction row HTML (shared with fallback renderer)
    payment_schedule_rows = build_payment_schedule_rows_html(customer, schedule_items)
    transaction_rows = build_transaction_rows_html(customer, transactions or [])

    # Total received = sum of ALL transactions
    all_txn_total = sum(float(t.get('amount', 0) or 0) for t in (transactions or []))

    # Fill template
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
        '{customer_id}': customer.get('customer_id', ''),
    }

    filled_html = template
    for placeholder, value in replacements.items():
        filled_html = filled_html.replace(placeholder, str(value))

    return filled_html
