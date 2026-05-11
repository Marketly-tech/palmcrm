"""
Document template generators for RRL CRM.
Split into individual modules by document type for maintainability.
All functions are re-exported here to maintain backward compatibility.
"""
from documents.templates.sales_agreement_template import generate_sales_agreement_template
from documents.templates.default_template import get_default_template
from documents.templates.price_breakup import generate_price_breakup_html
from documents.templates.cost_breakup import generate_cost_breakup_html
from documents.templates.noc_templates import generate_noc_hdfc_html, generate_noc_bob_html, generate_noc_tata_html
from documents.templates.booking_form import generate_booking_form_preview_html
from documents.templates.terms_conditions import generate_terms_and_conditions_html
from documents.templates.email_templates import generate_welcome_email_html, generate_document_email_html
from documents.templates.sales_agreement_html import generate_sales_agreement_html
from documents.templates.allotment_letter import generate_allotment_letter_html
from documents.templates.payment_schedule import generate_payment_schedule_pdf_html, generate_payment_schedule_html
from documents.templates.demand_letter import generate_demand_letter_html
from documents.templates.transactions_export import generate_transactions_export_html

__all__ = [
    'generate_sales_agreement_template',
    'get_default_template',
    'generate_price_breakup_html',
    'generate_cost_breakup_html',
    'generate_noc_hdfc_html',
    'generate_noc_bob_html',
    'generate_noc_tata_html',
    'generate_booking_form_preview_html',
    'generate_terms_and_conditions_html',
    'generate_welcome_email_html',
    'generate_document_email_html',
    'generate_sales_agreement_html',
    'generate_allotment_letter_html',
    'generate_payment_schedule_pdf_html',
    'generate_payment_schedule_html',
    'generate_demand_letter_html',
    'generate_transactions_export_html',
]
